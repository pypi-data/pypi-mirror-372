import logging
import itchi.runningtask.basic
import itchi.runningtask.btf
import itchi.type_enum
from typing import List, Dict
from itchi.config import ItchiConfig
from itchi.ortilib.orti import Orti
from itchi.profilerxml.model import (
    BtfTransition,
    ProfilerXml,
    ProfilerObject,
    StateInfo,
    TaskState,
    TypeEnum,
    Enum,
    BtfTransition,
)


def task_state_single_variable(orti: Orti, profiler_xml: ProfilerXml, config: ItchiConfig):
    """Implement task state profiling based on a single state variable.

    Args:
        orti (Orti): ORTI object
        profiler_xml (ProfilerXml): Profiler XML object
        config (ItchiConfig): iTCHi config object
    """

    logging.info("Running 'task_state_single_variable'.")

    # Pointer warning is relevant for this use case.
    itchi.runningtask.basic.pointer_warning(orti)

    for isr in itchi.runningtask.basic.get_isr2_objects(orti):
        isr.task_state = TaskState(btf_mapping_type=itchi.type_enum.BTF_ISR_MAPPING)
        profiler_xml.set_object(isr)

    # Create Tasks objects specifically for this use case.
    for task in get_task_objects(orti):
        profiler_xml.set_object(task)

    # Type enums for ID to state and ID to task name mappings.
    profiler_xml.set_type_enum(get_task_state_type_enum(orti))
    for type_enum in get_task_mapping_type_enums(orti):
        profiler_xml.set_type_enum(type_enum)

    # Add BTF ISR mapping.
    isr_btf_type_enum = itchi.runningtask.btf.get_btf_export_type_enum()
    isr_btf_type_enum.name = itchi.type_enum.BTF_ISR_MAPPING
    profiler_xml.set_type_enum(isr_btf_type_enum)

    # Add BTF mapping for task states.
    states = [enum.desc for enum in orti.get_enum_elements_task_state()]
    task_btf_type_enum = itchi.type_enum.get_btf_mapping_type_enum(states)
    profiler_xml.set_type_enum(task_btf_type_enum)

    return profiler_xml


def get_state_infos(orti: Orti) -> List[StateInfo]:
    """The ORTI file includes the possible task states.
    We tell winIDEA how to visualize each state via the StateInfo
    objects. The default state is Ready, so we only map Terminate
    and Run.

    Args:
        orti (Orti): ORTI object

    Returns:
        List[StateInfo]: State info objects to assign to TaskState object
    """
    state_infos: List[StateInfo] = []
    for enum in orti.get_enum_elements_task_state():
        state = enum.desc
        if state in ["SUSPENDED", "WAITING", "QUARANTINED", "MK_THS_IDLE"]:
            state_info = StateInfo(state, "Terminate")
            state_infos.append(state_info)
        elif state in ["RUNNING", "MK_THS_RUNNING"]:
            state_info = StateInfo(state, "Run")
            state_infos.append(state_info)
    return state_infos


def get_task_state(orti: Orti) -> TaskState:
    """Get the TaskState object for task state single
    variable tracing. The key points are that we use only mask_state
    because the other information is encoded via the TypeEnum.
    We also add the correct state_infos so that winIDEA can visualize
    the states correctly.

    Args:
        orti (Orti): ORTI file

    Returns:
        TaskState: TaskState attribute for ProfilerObject
    """
    state_infos = get_state_infos(orti)
    task_state = TaskState(
        mask_id="0x0",
        mask_state="0xFF",
        mask_core="0x0",
        type=itchi.type_enum.TASK_STATE_MAPPING,
        btf_mapping_type=itchi.type_enum.BTF_MAPPING,
        state_infos=state_infos,
    )
    return task_state


def get_task_objects(orti: Orti) -> List[ProfilerObject]:
    """Create Task ProfilerObjects for tracing based on a single
    state variable for each core. The key is to use $(EnumType) for the
    expression. Each task then gets it's own Enum object referenced via
    <Type>.

    Args:
        orti (Orti): ORTI object

    Returns:
        List[ProfilerObject]: Task Profiler Object for each core
    """
    tasks = orti.get_attribute_defs_runningtask()
    task_state = get_task_state(orti)
    return [
        ProfilerObject(
            name=t["attribute_name"],
            definition=t["attribute_name"],
            description=f"{t['soc_name']}: Tasks",
            type=itchi.type_enum.TASK_MAPPING_MULTI_CORE.format(t["soc_core"]),
            default_value=orti.get_default_task(),
            expression="$(EnumType)",
            level="Task",
            core=str(t["soc_core"]),
            task_state=task_state,
        )
        for t in tasks
    ]


def get_task_state_type_enum(orti: Orti) -> TypeEnum:
    """Generate TypeEnum for task states. This tells winIDEA
    how to map state IDs to state strings.

    Args:
        orti (Orti): ORTI object

    Returns:
        TypeEnum: Task State TypeEnum to assign to Profiler TypeEnums
    """
    enums = [
        Enum(enum.desc, str(enum.const))
        for enum in orti.get_enum_elements_task_state()
        if isinstance(enum.const, int)
    ]
    return TypeEnum(name=itchi.type_enum.TASK_STATE_MAPPING, enums=enums)


def get_task_mapping_type_enums(orti: Orti) -> List[TypeEnum]:
    """Generate task state TypeEnums. Each core has its own TypeEnum.

    Args:
        orti (Orti): ORTI object

    Returns:
        List[TypeEnum]: List of TypeEnums to assign to Profiler TypeEnums
    """

    # Each core gets its own TypeEnum with at least NO_TASK.
    default_task = orti.get_default_task()
    core_id_to_type_enum: Dict[int, TypeEnum] = {
        task["soc_core"]: TypeEnum(
            name=itchi.type_enum.TASK_MAPPING_MULTI_CORE.format(task["soc_core"]),
            enums=[Enum(default_task, "0xff")],
        )
        for task in orti.get_attribute_defs_runningtask()
    }

    # For each task add Task Enum to the respective core's TypeEnum
    for index, task_def in enumerate(orti.get_object_defs_task()):
        # task_core_index can be added by calling one of the
        # 'update_orti_task_defs_*' procedures in core.preprocess.py
        core_id = task_def.get("task_core_index", 0)

        task_name = task_def["object_name"]
        for attr in task_def["attributes"]:
            if attr["attribute_name"] == "STATE":
                formula = attr["formula"]
                break
        else:
            formula = ""

        # Create an Enum object for the task. The Enum name is the
        # task name and the value is a unique index. Then, use
        # name_property and value_property to assign a single global
        # variable as the expression for that task.
        if formula:
            task_enum = Enum(
                task_name, str(index), name_property="Expression", value_property=formula
            )
            core_id_to_type_enum[core_id].enums.append(task_enum)
    type_enums = list(core_id_to_type_enum.values())
    return type_enums
