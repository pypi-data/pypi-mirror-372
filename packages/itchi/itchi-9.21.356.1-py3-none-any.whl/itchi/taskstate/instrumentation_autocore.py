import logging
import itchi.type_enum
from pathlib import Path
from itchi.templates.render import render_template_from_templates, render_string
from itchi.config import ItchiConfig, TaskStateInstAutocoreConfig
from itchi.ortilib.orti import Orti
from itchi.profilerxml.model import ProfilerXml, ProfilerObject
from itchi.profilerxml.model import Enum, StateInfo, TypeEnum, TaskState
from typing import List, Tuple, Dict


def task_state_instrumentation_autocore(orti: Orti, profiler_xml: ProfilerXml, config: ItchiConfig):
    """Task state and ISR profiling for EB AutoCore utilizing the Dbg hooks."""

    logging.info("Running task_state_instrumentation_autocore.")
    if config.task_state_inst_autocore is None:
        logging.error("Missing task_state_inst_autocore config.")
        return

    write_instrumentation_code(config, config.task_state_inst_autocore)

    state_type_enum = get_state_mapping()
    profiler_xml.set_type_enum(state_type_enum)

    states = [enum.name for enum in state_type_enum.enums]
    btf_type_enum = itchi.type_enum.get_btf_mapping_type_enum(states)
    btf_type_enum.name = itchi.type_enum.BTF_MAPPING
    profiler_xml.set_type_enum(btf_type_enum)

    mdf4_type_enum = get_mdf4_mapping()
    profiler_xml.set_type_enum(mdf4_type_enum)

    task = get_task_object(config.task_state_inst_autocore)
    profiler_xml.set_object(task)

    isr = get_isr_object(config.task_state_inst_autocore)
    profiler_xml.set_object(isr)


def write_instrumentation_code(config: ItchiConfig, task_config: TaskStateInstAutocoreConfig):
    """Write EB AutoCore header and source file."""

    files_to_render: List[Tuple[str, Path]] = [
        ("Eb_Dbg.c", task_config.dbg_c),
        ("Eb_Dbg.h", task_config.dbg_h),
    ]
    for template_file, destination_file in files_to_render:
        # Do not render empty path.
        if destination_file == Path():
            continue

        kwargs = dict(task_config)
        content = render_template_from_templates(Path(template_file), kwargs)
        if not isinstance(content, str):
            logging.error(f"Could not render '{destination_file}'.")
            continue

        logging.info(f"Render template '{template_file}' into '{destination_file}'.")
        with open(destination_file, "w", encoding="utf-8") as f:
            f.write(content)


def get_task_object(config: TaskStateInstAutocoreConfig) -> ProfilerObject:
    """Get ProfilerObject for EB AutoCore OS Task profiling."""
    return ProfilerObject(
        definition="TASKSTATE",
        description="Tasks",
        type="OS:vs_SIGNAL_RUNNINGTASK",
        default_value="NO_TASK",
        name="TASKSTATE",
        level="Task",
        expression=config.trace_variable_task,
        task_state=get_task_state(),
        arti_mdf4_mapping_type=itchi.type_enum.ARTI_MDF4,
    )


def get_isr_object(config: TaskStateInstAutocoreConfig) -> ProfilerObject:
    """Get ProfilerObject for EB AutoCore OS ISR profiling."""
    return ProfilerObject(
        definition="ISRSTATE",
        description="ISRs2",
        type="OS:vs_SIGNAL_RUNNINGISR2",
        default_value="NO_ISR",
        name="ISRSTATE",
        level="IRQ3",
        expression=config.trace_variable_isr,
        task_state=get_task_state(),
        arti_mdf4_mapping_type=itchi.type_enum.ARTI_MDF4,
    )


def get_task_state() -> TaskState:
    """Get TaskState object for Vector MICROSAR OS profiling."""
    return TaskState(
        mask_id="0x000000FF",
        mask_state="0x0000FF00",
        # No mask_core to get core ID from trace (instead of instrumentation)
        type=itchi.type_enum.TASK_STATE_MAPPING,
        btf_mapping_type=itchi.type_enum.BTF_MAPPING,
        state_infos=get_state_infos(),
    )


def get_state_infos() -> List[StateInfo]:
    return [
        StateInfo("RUNNING", "Run"),
        StateInfo("SUSPENDED", "Terminate"),
        StateInfo("QUARANTINED", "Terminate"),
        StateInfo("WAITING", "Terminate"),
    ]


def get_state_mapping() -> TypeEnum:
    return TypeEnum(
        name=itchi.type_enum.TASK_STATE_MAPPING,
        enums=[
            Enum("SUSPENDED", "0"),
            Enum("QUARANTINED", "1"),
            Enum("NEW", "2"),
            Enum("READY_SYNC", "3"),
            Enum("READY_ASYNC", "4"),
            Enum("RUNNING", "5"),
            Enum("WAITING", "6"),
        ],
    )


def get_mdf4_mapping() -> TypeEnum:
    return TypeEnum(
        name=itchi.type_enum.ARTI_MDF4,
        enums=[
            Enum("SUSPENDED", "Suspended"),
            Enum("QUARANTINED", "Suspended"),
            Enum("NEW", "Ready"),
            Enum("READY_SYNC", "Ready"),
            Enum("READY_ASYNC", "Ready"),
            Enum("RUNNING", "Running"),
            Enum("WAITING", "Waiting"),
        ],
    )
