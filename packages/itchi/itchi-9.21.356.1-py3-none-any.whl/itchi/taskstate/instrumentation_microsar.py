import logging

from pathlib import Path
from typing import List, Tuple

import itchi.type_enum

from itchi.templates.render import render_template_from_templates, render_string
from itchi.config import (
    ItchiConfig,
    TaskStateInstMicrosarConfig,
    InstrumentationTypeEnum,
    SpinlockInstMicrosarConfig,
)
from itchi.taskstate.thread_mapping_microsar import ThreadIdMapping
from itchi.taskstate import thread_mapping_microsar
from itchi.ortilib.orti import Orti
from itchi.profilerxml.model import ProfilerXml, ProfilerObject
from itchi.profilerxml.model import Enum, StateInfo, TypeEnum, TaskState


def task_state_instrumentation_microsar(orti: Orti, profiler_xml: ProfilerXml, config: ItchiConfig):
    """Thread state (aka task state and ISR) profiling for Vector MICROSAR Timing Hooks based profiling."""

    logging.info("Running task_state_instrumentation_vector.")
    if config.task_state_inst_microsar is None:
        raise ValueError("Configuration attribute 'task_state_inst_microsar' is not set.")

    # Get Vector MICROSAR Thread ID Mapping and add TypeEnum to Profiler XML.
    os_types_lcfg_h = config.task_state_inst_microsar.os_types_lcfg_h
    thread_mapping = thread_mapping_microsar.get_thread_mapping(orti, os_types_lcfg_h)
    type_enum = get_thread_mapping_type_enum(thread_mapping)
    profiler_xml.set_type_enum(type_enum)

    # Get Vector MICROSAR State Mapping and add TypeEnum to Profiler XML.
    state_type_enum = get_state_mapping_vector_microsar()
    profiler_xml.set_type_enum(state_type_enum)

    # Transform Thread states into BTF event mapping and add TypeEnum to Profiler XML.
    states = [enum.name for enum in state_type_enum.enums]
    btf_type_enum = itchi.type_enum.get_btf_mapping_type_enum(states)
    btf_type_enum.name = itchi.type_enum.BTF_MAPPING
    profiler_xml.set_type_enum(btf_type_enum)

    # Add ARTI MDF4 TypeEnum to Profiler XML for MDF4 export.
    mdf4_type_enum = get_arti_mdf4_type_enum()
    profiler_xml.set_type_enum(mdf4_type_enum)

    # Write instrumentation and add main thread object to Profiler XML.
    write_instrumentation_code(config, config.task_state_inst_microsar)
    thread = get_thread_object(config.task_state_inst_microsar)
    profiler_xml.set_object(thread)


def write_instrumentation_code(config: ItchiConfig, task_config: TaskStateInstMicrosarConfig):
    """Write Vector MICROSAR timing-hooks header and source file."""

    if task_config.trace_variable_definition:
        s = render_string(
            task_config.trace_variable_definition, trace_variable=task_config.trace_variable
        )
        if s is not None:
            task_config.trace_variable_definition = s

    # If spinlock instrumentation is configured, update kwargs accordingly.
    kwargs = dict(task_config)
    if (
        config.commands
        and config.commands.spinlock_instrumentation_microsar
        and config.spinlock_inst_microsar
    ):
        replace_spinlock_trace_variable(config.spinlock_inst_microsar)
        kwargs.update(config.spinlock_inst_microsar)
        kwargs["spinlock_generate_instrumentation"] = True

    files_to_render: List[Tuple[str, Path]] = [
        ("Os_TimingHooks_isystem.c", task_config.vector_os_timing_hooks_c),
        ("Os_TimingHooks_isystem.h", task_config.vector_os_timing_hooks_h),
    ]
    for template_file, destination_file in files_to_render:
        # Do not render empty path.
        if destination_file == Path():
            continue

        include_guard = str(destination_file.name).upper().replace(".", "_")
        kwargs["include_guard_str"] = include_guard

        content = render_template_from_templates(Path(template_file), kwargs)
        if not isinstance(content, str):
            logging.error(f"Could not render '{destination_file}'.")
            continue

        logging.info(f"Render template '{template_file}' into '{destination_file}'.")
        with open(destination_file, "w", encoding="utf-8") as f:
            f.write(content)


def get_thread_object(config: TaskStateInstMicrosarConfig) -> ProfilerObject:
    """Get ProfilerObject for Vector MICROSAR OS Thread profiling."""
    p = ProfilerObject(
        definition="Threads_Definition",
        description="All Cores: Threads",
        type=itchi.type_enum.THREAD_MAPPING,
        name="Threads",
        level="Task",
        default_value="NO_THREAD",
        arti_mdf4_mapping_type=itchi.type_enum.ARTI_MDF4,
    )

    p.task_state = get_task_state()
    if config.software_based_coreid_gen is False:
        p.task_state.mask_core = None

    if config.instrumentation_type == InstrumentationTypeEnum.STM_TRACE:
        p.signaling = f"STM({config.stm_channel})"
    elif config.instrumentation_type == InstrumentationTypeEnum.SOFTWARE_TRACE:
        p.signaling = f"DBPUSH({config.sft_dbpush_register})"
    elif config.instrumentation_type == InstrumentationTypeEnum.DATA_TRACE:
        p.expression = config.trace_variable
    else:
        m = f"Unexpected {config.instrumentation_type=}"
        raise ValueError(m)
    return p


def get_task_state() -> TaskState:
    """Get TaskState object for Vector MICROSAR OS profiling."""
    return TaskState(
        mask_id="0x0000FFFF",
        mask_state="0x00FF0000",
        mask_core="0xFF000000",
        type=itchi.type_enum.TASK_STATE_MAPPING,
        btf_mapping_type=itchi.type_enum.BTF_MAPPING,
    )


def get_state_infos() -> List[StateInfo]:
    return [
        StateInfo("RUNNING", "Run"),
        StateInfo("RUNNING_ISR", "Run"),
        StateInfo("TERMINATED_TASK", "Terminate"),
        StateInfo("TERMINATED_ISR", "Terminate"),
        StateInfo("WAITING_EVENT", "Terminate"),
        StateInfo("WAITING_SEM", "Terminate"),
    ]


def get_thread_mapping_type_enum(thread_mappings: list[ThreadIdMapping]) -> TypeEnum:
    """Transform Vector MICROSAR Thread Mapping into TypeEnum.

    Args:
        thread_mapping (list[ThreadIdMapping]): thread mappings.

    Returns:
        TypeEnum: to be added to Profiler XML object
    """
    return TypeEnum(
        name=itchi.type_enum.THREAD_MAPPING,
        enums=[Enum(mapping.name, mapping.id) for mapping in thread_mappings],
    )


def get_state_mapping_vector_microsar() -> TypeEnum:
    return TypeEnum(
        name=itchi.type_enum.TASK_STATE_MAPPING,
        enums=[
            Enum("NEW", "11", task_state_property="ACTIVE"),
            Enum("READY", "16", task_state_property="READY"),
            Enum("RUNNING_ISR", "31", task_state_property="RUNNING"),
            Enum("TERMINATED_ISR", "2", task_state_property="TERMINATED"),
            Enum("WAITING_EVENT", "4", task_state_property="WAITING"),
            Enum("WAITING_SEM", "8", task_state_property="WAITING"),
            Enum("RUNNING", "29", task_state_property="RUNNING"),
            Enum("TERMINATED_TASK", "1", task_state_property="TERMINATED"),
        ],
    )


def get_arti_mdf4_type_enum() -> TypeEnum:
    return TypeEnum(
        name=itchi.type_enum.ARTI_MDF4,
        enums=[
            Enum("NEW", "Ready"),
            Enum("READY", "Ready"),
            Enum("RUNNING", "Running"),
            Enum("TERMINATED_TASK", "Suspended"),
            Enum("WAITING_EVENT", "Waiting"),
            Enum("WAITING_SEM", "Waiting"),
            Enum("RUNNING_ISR", "Active"),
            Enum("TERMINATED_ISR", "Inactive"),
        ],
    )


def replace_spinlock_trace_variable(config: SpinlockInstMicrosarConfig):
    """Replace '{{ spinlock_trace_variable }}' in trace_variable_definition."""
    if not config.spinlock_trace_variable_definition:
        return

    new_trace_variable_definition = render_string(
        config.spinlock_trace_variable_definition,
        spinlock_trace_variable=config.spinlock_trace_variable,
        trace_variable=config.spinlock_trace_variable,
    )
    if new_trace_variable_definition:
        config.spinlock_trace_variable_definition = new_trace_variable_definition
