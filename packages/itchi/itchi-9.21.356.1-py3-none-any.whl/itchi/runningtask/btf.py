import logging
from typing import List
import itchi.runningtask.basic
from itchi.ortilib.orti import Orti
from itchi.profilerxml.model import (
    ProfilerXml,
    ProfilerObject,
    TaskState,
    BtfTransition,
    TypeEnum,
    Enum,
)

_TYPE_ENUM_STATES_TO_BTF = "TypeEnum_States_to_BTF"
_TYPE_ENUM_STATES = "TypeEnum_States"


def running_taskisr_btf(orti: Orti, profiler_xml: ProfilerXml) -> ProfilerXml:
    """
    Same as running_taskisr but with additional TypeEnums and TaskState objects
    to support BTF export via RUNNING and TERMINATED pseudo states.

    Args:
        orti(Orti): ORTI file object
        profilerXml(ProfilerXml): Profiler XML object

    Returns:
        profiler_xml(ProfilerXml): Update Profiler XML object
    """
    logging.info("Running 'running_taskisr_btf'.")

    # Get Task and ISR objects from runningtask basic use case and
    # add task_state information to allow BTF export.
    for task in get_task_objects(orti):
        profiler_xml.set_object(task)

    for isr in get_isr2_objects(orti):
        profiler_xml.set_object(isr)

    # Add TypeEnums required for BTF export to Profiler XML.
    profiler_xml.set_type_enum(get_btf_export_type_enum())
    profiler_xml.set_type_enum(get_fake_states_type_enum())

    itchi.runningtask.basic.pointer_warning(orti)
    return profiler_xml


def get_task_objects(orti: Orti) -> List[ProfilerObject]:
    """Get profiler task objects with BTF export TypeEnums."""
    tasks = itchi.runningtask.basic.get_task_objects(orti)
    for task in tasks:
        task.task_state = get_task_state_object()
    return tasks


def get_isr2_objects(orti: Orti) -> List[ProfilerObject]:
    """Get profiler ISR2 objects including BTF export TypeEnums."""
    isrs = itchi.runningtask.basic.get_isr2_objects(orti)
    for isr in isrs:
        isr.task_state = get_task_state_object()
    return isrs


def get_task_state_object() -> TaskState:
    """
    Create a TaskState object that references the fake state mapping and BTF
    mapping for the fake states.

    Returns:
        TaskState: TaskState object to assign to ProfilerObject
    """
    return TaskState(
        type=_TYPE_ENUM_STATES,
        btf_mapping_type=_TYPE_ENUM_STATES_TO_BTF,
    )


def get_btf_export_type_enum() -> TypeEnum:
    """Create TypeEnum for BTF export for only TERMINATED and RUNNING states.

    Returns:
        TypeEnum: TypeEnum to assign to ProfilerXml TypeEnums
    """
    return TypeEnum(
        name=_TYPE_ENUM_STATES_TO_BTF,
        properties=[
            BtfTransition(text="Terminated-Running:Active,Running"),
            BtfTransition(text="Unknown-Running:Active,Running"),
            BtfTransition(text="Unknown-Terminated:Active,Running,Terminated"),
        ],
        enums=[
            Enum("TERMINATED", "Terminated"),
            Enum("RUNNING", "Running"),
        ],
    )


def get_fake_states_type_enum() -> TypeEnum:
    """
    Return TypeEnum that generates RUNNING and TERMINATED pseudo states for BTF
    export. Please ask the Analyzer team for why the ENUM has to be like that.

    Returns:
        TypeEnum: TypeEnum to assign to ProfilerXml TypeEnums
    """
    return TypeEnum(
        name=_TYPE_ENUM_STATES,
        enums=[
            Enum("TERMINATED", "0x0", task_state_property="Terminate"),
            Enum("RUNNING", "0x1", task_state_property="Run"),
        ],
    )
