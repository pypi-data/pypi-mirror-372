import re
import os
import logging
import sys
import datetime
import dataclasses
import shutil
import xml.etree.ElementTree as ET
from typing import List
from pathlib import Path
from itchi.templates.render import render_template, render_string
from itchi.config import (
    ItchiConfig,
    RunnableInstrumentationConfig,
    InstrumentationTypeEnum,
    RteStackSupplierTypeEnum,
)
from itchi.profilerxml.model import ProfilerXml, ProfilerObject, TypeEnum, Enum, RunnableState
from itchi.type_enum import RUNNABLE_MAPPING


@dataclasses.dataclass
class RteHook:
    declaration: str
    name: str
    start_return: str
    id: str


def get_rte_runnable_hooks_eb(rte_xdm_file: Path) -> List[RteHook]:
    def find_rte_vfb_trace_function(element):
        """<d:lst name="RteVfbTraceFunction">"""
        for elem in element:
            attr = elem.attrib
            if "name" in attr and attr["name"] == "RteVfbTraceFunction":
                return elem
            result = find_rte_vfb_trace_function(elem)
            if result is not None and len(result) > 0:
                return result
        return None

    def get_rte_hooks_vfb_trace_elem(rte_vfb_trace_elem):
        """
        Searches the rteVfbTraceElem for RTE hook functions. Each function is
        returned as a hook. Start functions must get a unique ID while return
        functions always have the ID '0'.

        <d:var type="FUNCTION-NAME"
               value="Rte_Runnable_LOW_BRK_FLD_Sensor_SWC_RE_LOW_BRK_FLD_Sensor_SWC_Return"/>
        """
        hooks = []
        id_counter = 1
        for elem in rte_vfb_trace_elem:
            value = elem.attrib["value"]
            if value.endswith("_Start"):
                name = value.replace("_Start", "")
                start_or_return = "Start"
                current_id = id_counter
                id_counter += 1
            elif value.endswith("_Return"):
                name = value.replace("_Return", "")
                start_or_return = "Return"
                current_id = 0
            else:
                raise Exception(f"Unexpected ending of '{value}'.")
            declaration = f"void {value}(void)"
            hooks.append(RteHook(declaration, name, start_or_return, str(current_id)))
        return hooks

    xml_root = ET.parse(rte_xdm_file).getroot()
    rte_vfb_trace_elem = find_rte_vfb_trace_function(xml_root)
    hooks = get_rte_hooks_vfb_trace_elem(rte_vfb_trace_elem)
    return hooks


def get_datetime() -> str:
    # This is a terrible hack to make sure that the date strings do not cause
    # our regression tests to fail. If you go to the test definition you will see
    # that I manipulate sys.argv to set up the configuration for the respective
    # test case. While doing that I write "itchi-test.py" into the argument zero.
    # It would usually be "itchi.py" when executed from VS Code or the terminal,
    # and "itchi-bin.exe" when executed from the executable. I don't know if there
    # is a better way of doing this, but for now it shouldn't have any evil
    # consequences either so it should be okay.
    if sys.argv[0] == "itchi-test.py":
        return "Feb 05, 2020"
    return datetime.datetime.now().strftime("%b %d, %Y")


def get_rte_runnable_hooks_vector(rte_hook_h: Path, regex: str) -> List[RteHook]:
    """
    Function returns a list of RteHooks.

    A hook looks as follows. It consists of Rte_Runnable, the name of the
    SWC, and then the name of the Runnable itself. We are not really able to
    tell which part is the runnable name and which part is the SWC. So, we
    just treat the whole part from Rte_Runnable_ till _Start/Return as the
    Runnable name.

        FUNC(void, RTE_APPL_CODE) \
        Rte_Runnable_SWC_Core2_SWC_Core2_Runnable_100ms_Start(void)

    felixm(2018-08-17):

    It turns out that Runnables can have arguments different than void:
        FUNC(void, RTE_APPL_CODE) \
        Rte_Runnable_MODULE_DataServices_Data_CPU_Load_Read_ReadData_Start\
        (Var A, P2VAR(TYPE, AUTOMATIC, RTE_VAR) Data)

    We account for that by allow arbitrary arguments:
        "([^\n]+)" #  match anything that is not a newline

    felixm(2020-02-05):
        I added a configuration item runnable_instrumentation.regex
        to enable the user to change the regex. If that argument is empty
        we fall back to the previous regex.
    """

    if not regex:
        regex = "(FUNC\\(void, RTE_APPL_CODE\\) Rte_Runnable_(\\w+)_(Start|Return)\\([^\\n]+\\))"
    msg = f"{regex=}"
    logging.debug(msg)
    r = re.compile(regex)

    with open(rte_hook_h, "r") as f:
        matches = [m.groups() for line in f if (m := r.match(line))]

    hooks = []
    runnable_id_counter = 1
    for match in matches:
        if len(match) != 3:
            logging.error("The number of groups in the Runnable regex is not three.")
            logging.error("Use non-capturing '(?:foo)' groups to avoid this error.")
            sys.exit(-1)

        if match[2] == "Return":
            runnable_id = 0
        else:
            runnable_id = runnable_id_counter
            runnable_id_counter += 1
        h = RteHook(match[0], match[1], match[2], str(runnable_id))
        hooks.append(h)

    if not hooks:
        msg = f"No hooks for {regex=} in {rte_hook_h=}."
        logging.error(msg)
    return hooks


def get_rte_runnable_hooks_arxml(
    rte_arxml: Path, rte_stack_supplier: str, rte_vsmd_path: str
) -> List[RteHook]:
    """
    Function returns a list of RteHooks.

    It uses the RTE EcuC file as input to identify all configured VFB trace hooks.
    Via the RTE EcuC file it's only possible to identify the name of the configured VFB trace hook.
    We assume that the VFB trace hook doesn't have arguments, i.e., void hook (void).
    There are cases in which the VFB trace hook will use arguments. This will cause a compilation error.

    Example EcuC snippet:
        <ECUC-TEXTUAL-PARAM-VALUE>
            <DEFINITION-REF DEST="ECUC-FUNCTION-NAME-DEF">/AUTOSAR_Rte/EcucModuleDefs/Rte/RteGeneration/RteVfbTraceFunction</DEFINITION-REF>
            <VALUE>Rte_Runnable_Acc_StandaloneMode_Acc_StandaloneMode_Runnable_Start</VALUE>
        </ECUC-TEXTUAL-PARAM-VALUE>
    """

    def get_vsmd_path(stack_supplier):
        # Depending on the stack supplier, the reference to the VFB trace function parameter in the VSMD differs
        if stack_supplier == RteStackSupplierTypeEnum.ETAS:
            vsmd_path = "/AUTOSAR_Rte/EcucModuleDefs/Rte/RteGeneration/RteVfbTraceFunction"
        elif stack_supplier == RteStackSupplierTypeEnum.VECTOR:
            vsmd_path = "/MICROSAR/Rte/RteGeneration/RteVfbTraceFunction"
        else:
            logging.error("Please select a supported rte_stack_supplier.")
            raise Exception("Please select a supported rte_stack_supplier.")
        return vsmd_path

    def get_rte_hooks_vfb_trace_elem(rte_vfb_trace_elem):
        hooks = []
        id_counter = 1
        for elem in rte_vfb_trace_elem:
            if elem.text.endswith("_Start"):
                name = elem.text.replace("_Start", "")
                start_return = "Start"
                current_id = id_counter
                id_counter += 1
            elif elem.text.endswith("_Return"):
                name = elem.text.replace("_Return", "")
                start_return = "Return"
                current_id = 0
            else:
                raise Exception("Unexpected ending for {elem.text}.")
            declaration = f"void {elem.text}(void)"
            hooks.append(RteHook(declaration, name, start_return, str(current_id)))
        return hooks

    try:
        xml_config = ET.parse(rte_arxml)
    except ET.ParseError:
        msg = f"The input file '{rte_arxml}' isn't a valid ARXML file. Please inspect this file and run iTCHi again."
        logging.error(msg)
        raise Exception(msg)
    xml_root = xml_config.getroot()
    if rte_vsmd_path.strip():
        # Use the user provided VSMD path
        vsmd_rte_vfb_trace_function = rte_vsmd_path
    else:
        vsmd_rte_vfb_trace_function = get_vsmd_path(rte_stack_supplier)
    # Use XPath expression to find relevant child elements, {*}bla selects tags named bla in any or no namespace
    xpath_expression = ".//*/.[{*}DEFINITION-REF='" + vsmd_rte_vfb_trace_function + "']/{*}VALUE"
    vfb_trace_hooks = xml_root.findall(xpath_expression)
    if not vfb_trace_hooks:
        msg = f"No VFB trace hooks found in '{rte_arxml}' (expected VSMD path: '{vsmd_rte_vfb_trace_function}')."
        logging.warning(msg)
    hooks = get_rte_hooks_vfb_trace_elem(vfb_trace_hooks)
    return hooks


def write_rte_hook_file(runnable_hooks: list[RteHook], config: RunnableInstrumentationConfig):
    template_file = get_template_file_path(config)
    vfb_hooks_c = config.impl_vfb_hooks_c
    kwargs = {
        "filename": os.path.basename(vfb_hooks_c),
        "date": get_datetime(),
        "runnable_hooks": runnable_hooks,
    }

    if config.trace_variable_definition:
        s = render_string(config.trace_variable_definition, trace_variable=config.trace_variable)
        if s is not None:
            config.trace_variable_definition = s

    kwargs.update(config)
    content = render_template(template_file, kwargs)
    if content is None:
        logging.error(f"Could not render '{vfb_hooks_c}'.")
        return
    logging.info(f"Render '{template_file}' into '{vfb_hooks_c}'.")
    with open(vfb_hooks_c, "w") as f:
        f.write(content)


def get_runnable_type_enum(runnable_hooks: List[RteHook]):
    enums = [Enum(hook.name, hook.id) for hook in runnable_hooks if hook.start_return == "Start"]
    return TypeEnum(name=RUNNABLE_MAPPING, enums=enums)


def get_runnable_object(config: RunnableInstrumentationConfig) -> ProfilerObject:
    p = ProfilerObject(
        definition="Runnables_Definition",
        level="Runnable",
        name="Runnables",
        description="All Cores: Runnables",
        type=RUNNABLE_MAPPING,
        default_value="0",
    )

    p.runnable_state = RunnableState(mask_id="0xFFFFFF00", mask_core="0x000000FF", exit_value=0)

    if config.instrumentation_type == InstrumentationTypeEnum.STM_TRACE:
        # format as hex and pad to 10 characters
        p.signaling = f"STM({config.stm_channel})"
    elif config.instrumentation_type == InstrumentationTypeEnum.SOFTWARE_TRACE:
        p.runnable_state.mask_id = "0xFFFFFFFF"
        p.runnable_state.mask_core = None
        if config.sft_dbtag is True:
            p.signaling = "DBTAG"
        else:
            p.signaling = f"DBPUSH({config.sft_dbpush_register})"
        if config.software_based_coreid_gen is True:
            logging.info(
                "Attribute 'software_based_coreid_gen' does not have an effect for RH850 SFT"
            )
    elif config.instrumentation_type == InstrumentationTypeEnum.DATA_TRACE:
        p.expression = config.trace_variable
    else:
        m = f"Unexpected {config.instrumentation_type=}"
        logging.error(m)
        raise ValueError(m)

    if config.software_based_coreid_gen is False:
        p.runnable_state.mask_core = None
    return p


def get_template_file_path(config: RunnableInstrumentationConfig) -> Path:
    directory = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../templates")
    template_file = "Rte_Hook_isystem.template.c"
    template_file_path = os.path.join(directory, template_file)

    if config.template_file != Path():
        user_template_path = os.path.join(os.getcwd(), config.template_file)
        # If user wants to provide their own config file and it does not
        # yet exist we copy our template for the user.
        os.makedirs(os.path.dirname(user_template_path), exist_ok=True)
        if not os.path.isfile(user_template_path):
            shutil.copyfile(template_file_path, user_template_path)
        template_file_path = user_template_path

    return Path(template_file_path)


def get_rte_hooks(config: RunnableInstrumentationConfig) -> list[RteHook]:
    if [config.rte_hook_h.is_file(), config.rte_xdm.is_file(), config.rte_arxml.is_file()].count(
        True
    ) > 1:
        logging.warning(
            "More than one input file is configured to derive the VFB trace hooks from. "
            "Configure either rte_hook_h, rte_xdm or rte_arxml."
        )

    msg = "VFB trace hooks derived from '{}'."
    if config.rte_arxml.is_file():
        logging.info(msg.format(config.rte_arxml))
        hooks = get_rte_runnable_hooks_arxml(
            config.rte_arxml, config.rte_stack_supplier, config.rte_vsmd_path
        )
    elif config.rte_hook_h.is_file():
        logging.info(msg.format(config.rte_hook_h))
        hooks = get_rte_runnable_hooks_vector(config.rte_hook_h, config.regex)
    elif config.rte_xdm.is_file():
        msg = f"VFB trace hooks derived from '{config.rte_xdm}'."
        logging.info(msg)
        hooks = get_rte_runnable_hooks_eb(config.rte_xdm)
    else:
        raise ValueError("Configure one of rte_hook_h, rte_xdm or rte_arxml.")
    return hooks


def runnable_instrumentation(profiler_xml: ProfilerXml, config: ItchiConfig):
    logging.info("Running runnable_instrumentation.")
    if config.runnable_instrumentation is None:
        raise ValueError("runnable_instrumentation configuration is missing")

    hooks = get_rte_hooks(config.runnable_instrumentation)
    write_rte_hook_file(hooks, config.runnable_instrumentation)

    runnable_type_enum = get_runnable_type_enum(hooks)
    profiler_xml.set_type_enum(runnable_type_enum)

    runnable_object = get_runnable_object(config.runnable_instrumentation)
    profiler_xml.set_object(runnable_object)
