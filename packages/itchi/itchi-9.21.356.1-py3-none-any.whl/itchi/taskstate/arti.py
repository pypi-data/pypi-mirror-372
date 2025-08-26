import logging
import os
import itchi.type_enum
from pathlib import Path
from itchi.templates.render import render_template_from_templates
from itchi.config import ItchiConfig, ArtiConfig
from itchi.ortilib.orti import Orti
from itchi.profilerxml.model import ProfilerXml, ProfilerObject
from itchi.profilerxml.model import Enum, TypeEnum, TaskState
from itchi.taskstate.thread_mapping_microsar import get_thread_mapping_orti
from itchi.taskstate import instrumentation_microsar


def arti(orti: Orti, profiler_xml: ProfilerXml, config: ItchiConfig):
    """ARTI state profiling for Vector MICROSAR Timing Hooks.

    Args:
        orti (Orti): ORTI object
        profiler_xml (ProfilerXml): Profiler XML object
        config (ItchiConfig): iTCHi Config object
    """

    if config.arti is None:
        logging.error("Missing arti config.")
        return

    logging.info("Running arti.")
    write_arti_os_instrumentation(config.arti)

    # No need to reference ORTI file for ARTI because everything is in the Profiler XML.
    profiler_xml.orti = None

    thread_mapping = get_thread_mapping_orti(orti)
    type_enum = instrumentation_microsar.get_thread_mapping_type_enum(thread_mapping)
    profiler_xml.set_type_enum(type_enum)

    state_type_enum = get_state_mapping_arti()
    profiler_xml.set_type_enum(state_type_enum)

    states = [enum.name for enum in state_type_enum.enums]
    btf_type_enum = itchi.type_enum.get_btf_mapping_type_enum(states)
    profiler_xml.set_type_enum(btf_type_enum)

    mdf4_type_enum = instrumentation_microsar.get_arti_mdf4_type_enum()
    profiler_xml.set_type_enum(mdf4_type_enum)

    thread = get_thread_object(config.arti)
    profiler_xml.set_object(thread)


def write_arti_os_instrumentation(config: ArtiConfig):
    to_render = [
        ("Os_TimingHooks_arti.c", config.os_trace_c),
        ("Os_TimingHooks_arti.h", config.os_trace_h),
    ]
    for template_file, output_file in to_render:
        kwargs = {
            "filename": os.path.basename(output_file),
            "trace_variable": config.os_trace_variable,
            "CallerCoreId": "| CallerCoreId " if config.software_based_coreid_gen else "",
            "DestCoreId": "| DestCoreId " if config.software_based_coreid_gen else "",
        }
        content = render_template_from_templates(Path(template_file), kwargs)
        if content is None:
            logging.error(f"Could not render '{output_file}'.")
            break
        logging.info(f"Write ARTI instrumentation into '{output_file}'.")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)


def get_state_mapping_arti() -> TypeEnum:
    """State mapping per ARTI specification.

    /** ARTI OS Task/ISR state transitions **/
    /** AR_CP_OSARTI_TASK **/
    #define ARTI_OSARTITASK_ACTIVATE     0
    #define ARTI_OSARTITASK_START        1
    #define ARTI_OSARTITASK_WAIT         2
    #define ARTI_OSARTITASK_RELEASE      3
    #define ARTI_OSARTITASK_PREEMPT      4
    #define ARTI_OSARTITASK_TERMINATE    5
    #define ARTI_OSARTITASK_RESUME       6
    #define ARTI_OSARTITASK_CONTINUE     7
    /** AR_CP_OSARTI_CAT2ISR  **/
    #define ARTI_OSCAT2ISR_START         16
    #define ARTI_OSCAT2ISR_STOP          17
    #define ARTI_OSCAT2ISR_ACTIVATE      18
    #define ARTI_OSCAT2ISR_PREEMPT       19
    #define ARTI_OSCAT2ISR_RESUME        20
    """
    return TypeEnum(
        name=itchi.type_enum.TASK_STATE_MAPPING,
        enums=[
            # Tasks
            Enum("NEW", "0"),
            Enum("RUNNING", "1", additional_values_property=["6", "7"]),
            Enum("WAITING_EVENT", "2"),
            Enum("READY", "4"),
            Enum("RELEASED", "3"),
            Enum("TERMINATED_TASK", "5"),
            # ISRs
            Enum("NEW_ISR", "18"),
            Enum("READY_ISR", "19"),
            Enum("RUNNING_ISR", "16", additional_values_property=["20"]),
            Enum("TERMINATED_ISR", "17"),
        ],
    )


def get_thread_object(arti_config: ArtiConfig) -> ProfilerObject:
    """Get ProfilerObject for ARTI OS profiling."""
    p = ProfilerObject(
        definition="ARTI_OS_Definition",
        description="ARTI OS",
        expression=arti_config.os_trace_variable,
        type=itchi.type_enum.THREAD_MAPPING,
        name="ARTI_OS",
        level="Task",
        default_value="NO_THREAD",
        arti_mdf4_mapping_type=itchi.type_enum.ARTI_MDF4,
        task_state=get_task_state(arti_config),
    )
    return p


def get_task_state(arti_config: ArtiConfig) -> TaskState:
    """Get TaskState object for ARTI OS profiling."""
    return TaskState(
        mask_id="0xFFFF0000",
        mask_state="0x00007F00",
        mask_core="0x000000FF" if arti_config.software_based_coreid_gen else None,
        type=itchi.type_enum.TASK_STATE_MAPPING,
        btf_mapping_type=itchi.type_enum.BTF_MAPPING,
        state_infos=instrumentation_microsar.get_state_infos(),
    )
