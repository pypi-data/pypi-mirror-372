import logging
from typing import Dict, Union, List
import itchi.runningtask.basic
import itchi.runningtask.btf
import itchi.type_enum
from itchi.config import ItchiConfig
from itchi.profilerxml.model import ProfilerXml
from itchi.profilerxml.model import Enum, TypeEnum, TaskState
from itchi.ortilib.orti import Orti
from itchi.ortilib.formula import Formula


def task_state_complex_native(orti: Orti, profiler_xml: ProfilerXml, config: ItchiConfig):
    """
    Args:
        orti (Orti): ORTI object
        profiler_xml (ProfilerXml): Profiler XML object is updated for this use case
        config (ItchiConfig): iTCHi Configuration
    """
    logging.info("Running task_state_complex_native.")

    # Create TypeEnum for state IDs to state names.
    task_state_type_enum = get_state_mapping_orti(orti)
    profiler_xml.set_type_enum(task_state_type_enum)

    # Create TypeEnum for task names to task formula and expression.
    task_state_enum = get_state_expressions(orti)
    profiler_xml.set_type_enum(task_state_enum)

    # Simplify task state expressions.
    if config.task_state_complex and config.task_state_complex.constant_variables:
        vars = config.task_state_complex.constant_variables
        for enum in task_state_enum.enums:
            if enum.context_state_formula:
                formula = enum.context_state_formula
                enum.context_state_formula = simplify_formula(formula, vars)

    # Create task objects and reference the right TypeEnums.
    for task in itchi.runningtask.basic.get_task_objects(orti):
        task.task_state_type = itchi.type_enum.TASK_STATE_MAPPING
        task.type = itchi.type_enum.TASK_MAPPING
        task.task_state = TaskState(btf_mapping_type=itchi.type_enum.BTF_TASK_MAPPING)
        profiler_xml.set_object(task)

    # Create ISR objects. Only one TypeEnum for BTF is necessary.
    for isr in itchi.runningtask.basic.get_isr2_objects(orti):
        isr.task_state = TaskState(btf_mapping_type=itchi.type_enum.BTF_ISR_MAPPING)
        profiler_xml.set_object(isr)

    # Create and add the TypeEnum for the BTF Task export.
    states = [enum.desc for enum in orti.get_enum_elements_task_state()]
    states.append("READY_ISR")
    task_btf_type_enum = itchi.type_enum.get_btf_mapping_type_enum(states)
    task_btf_type_enum.name = itchi.type_enum.BTF_TASK_MAPPING
    profiler_xml.set_type_enum(task_btf_type_enum)

    # Create and add the TypeEnum for the BTF ISR export.
    isr_btf_type_enum = itchi.runningtask.btf.get_btf_export_type_enum()
    isr_btf_type_enum.name = itchi.type_enum.BTF_ISR_MAPPING
    profiler_xml.set_type_enum(isr_btf_type_enum)


def get_state_mapping_orti(orti: Orti) -> TypeEnum:
    # One state (aka enum_desc) can have multiple IDs (aka constants)
    enum_desc_to_constant: Dict[str, List[str]] = {}
    for enum in orti.get_enum_elements_task_state():
        const = str(enum.const)
        if enum.desc in enum_desc_to_constant:
            enum_desc_to_constant[enum.desc].append(const)
        else:
            enum_desc_to_constant[enum.desc] = [const]

    state_name_to_task_state = {
        "RUNNING": "RUNNING",
        "SUSPENDED": "TERMINATED",
        "WAITING": "TERMINATED",
        "UNKNOWN": "UNKNOWN",
    }

    enums = []
    for desc, consts in enum_desc_to_constant.items():
        e = Enum(desc, consts[0])
        if len(consts) > 1:
            e.additional_values_property = consts[1:]
        if desc in state_name_to_task_state:
            e.task_state_property = state_name_to_task_state[desc]
        enums.append(e)

    t = TypeEnum(name=itchi.type_enum.TASK_STATE_MAPPING, enums=enums)
    return t


def get_state_expressions(orti: Orti) -> TypeEnum:
    def get_expr(task):
        return [
            attr["formula"] for attr in task["attributes"] if attr["attribute_name"] == "STATE"
        ][0]

    # Create a dict that maps task names to complex expression.
    task_name_to_expr = {
        task["object_name"]: get_expr(task) for task in orti.get_object_defs_task()
    }

    # Create an enum for each task. Some tasks don't have a complex
    # expression and context_state_formula should be None.
    enums = []
    for task_enum in orti.get_enum_elements_runningtask():
        name = task_enum.desc
        value = task_enum.formula if task_enum.formula else ""
        expr = None
        if name in task_name_to_expr:
            expr = task_name_to_expr[name]
        e = Enum(name=name, value=value, context_state_formula=expr)
        enums.append(e)

    return TypeEnum(name=itchi.type_enum.TASK_MAPPING, enums=enums)


def simplify_formula(formula: str, const_vars: Dict[str, int]) -> str:
    invalid_expression = "Unsupported expression: '{}'"
    supported_operators = [
        "&&",
        "||",
        "<=",
        ">=",
        "!=",
        "==",
        ">",
        "<",
        "+",
        "-",
        "*",
        "<<",
        ">>",
        "&",
    ]

    def resolve_ternary(exp: dict) -> str:
        cond = resolve(exp["condition"])
        exp_true = str(resolve(exp["expression_true"]))
        exp_false = str(resolve(exp["expression_false"]))
        if cond == "1":
            return exp_true
        elif cond == "0":
            return exp_false
        else:
            return f"{cond} ? {exp_true} : {exp_false}"

    def resolve_variable(exp: str) -> str:
        if exp in const_vars:
            return str(const_vars[exp])
        return exp

    def resolve_operation(exp: dict) -> str:
        operator = exp["type"]
        exp1 = str(resolve(exp["expression_1"]))
        exp2 = str(resolve(exp["expression_2"]))

        # Check some conditions that allow trivial result
        if exp1 == "1" and operator == "*":
            return exp2
        if exp2 == "1" and operator == "*":
            return exp1
        if exp1 == "0" and operator == "+":
            return exp2
        if exp2 == "0" and operator == "+":
            return exp1
        if (exp1 == "0" or exp2 == "0") and operator == "*":
            return "0"

        try:
            # See if we can evaluate the expression.
            r = f"{int(exp1)} {operator[:2]} {int(exp2)}"
            # pylint: disable = eval-used
            # No security risk because we only allow two op chars
            r = str(int(eval(r)))
        except Exception:
            r = "({} {} {})"
            r = r.format(exp1, operator, exp2)
        return r

    def resolve(exp: Union[str, int, dict]) -> Union[str, bool]:
        if isinstance(exp, str):
            return resolve_variable(exp)
        if isinstance(exp, int):
            return str(exp)
        if isinstance(exp, dict):
            if exp["type"] == "ternary":
                return resolve_ternary(exp)
            elif exp["type"] in supported_operators:
                return resolve_operation(exp)
            raise Exception(invalid_expression.format(exp))
        raise Exception(invalid_expression.format(exp))

    return str(resolve(Formula(formula)["formula"]))
