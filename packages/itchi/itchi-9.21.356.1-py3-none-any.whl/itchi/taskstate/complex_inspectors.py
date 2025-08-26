import logging
import itchi.runningtask.basic
import itchi.runningtask.btf
import itchi.type_enum
from itchi.inspectors.taskstate import TaskStateInspectors
from itchi.config import ItchiConfig
from itchi.profilerxml.model import ProfilerXml, ProfilerObject, TaskState
from itchi.profilerxml.model import TypeEnum
from itchi.ortilib.orti import Orti


def task_state_complex_inspectors(orti: Orti, profiler_xml: ProfilerXml, config: ItchiConfig):
    """
    Create Profiler XML and Inspectors JSON file for task state tracing
    based on a complex expression. The first part is to generate the Inspector
    JSON file. You never want to understand how that works. Eventually MaticK
    will implement this directly in winIDEA, but until then FelixM is the only
    one who has to understand it (hopefully). The second part configures the Profiler
    XML for Running Task/ISR analysis. The create Inspectors then add the states.

    Args:
        orti (Orti): ORTI object
        profiler_xml (ProfilerXml): Profiler XML object is updated for this use case
        config (ItchiConfig): iTCHi Configuration
    """

    # Log error if task_state_inspectors is not configured and abort.
    if config.task_state_inspectors is None:
        logging.error("iTCHi config task_state_inspectors section missing.")
        return

    # Output to the user that we are remapping task cores.
    task_core_to_core_name = config.task_state_inspectors.task_core_to_core_name
    if task_core_to_core_name:
        logging.info("Remapping Task cores to SoC core names.")
        logging.info(f"  task_core -> core_name")
        for task_core, core_name in task_core_to_core_name.items():
            logging.info(f"  {task_core:>9} -> {core_name}")

    # Create Inspector JSON file. Try to avoid reading the code.
    tsi = TaskStateInspectors(orti, config.task_state_inspectors)
    tsi.addIsrInspectors()
    tsi.save()

    # Add data areas if so configured to avoid adding them in winIDEA.
    if config.task_state_inspectors.create_data_areas:
        for data_area in tsi.dataAreaVarNames:
            add_data_area(data_area, profiler_xml)

    # Configure Inspector reference from Profiler XML based on iTCHi config.
    if config.task_state_inspectors.reference_inspectors_file_from_xml:
        profiler_xml.inspector_path = str(config.task_state_inspectors.inspectors_file)
    else:
        profiler_xml.inspector_path = None

    # Add Tasks and ISRs in the same way as we would for Running Task/ISR.
    # The Inspectors will than add the states.
    for task in itchi.runningtask.basic.get_task_objects(orti):
        task.task_state = TaskState(
            mask_id="0",
            mask_state="0",
            mask_core="0",
            state_infos=[],
            btf_mapping_type=itchi.type_enum.BTF_TASK_MAPPING,
        )
        profiler_xml.set_object(task)

    for isr in itchi.runningtask.basic.get_isr2_objects(orti):
        isr.task_state = TaskState(
            mask_id="0",
            mask_state="0",
            mask_core="0",
            state_infos=[],
            btf_mapping_type=itchi.type_enum.BTF_ISR_MAPPING,
        )
        profiler_xml.set_object(isr)

    # Create and add the TypeEnum for the BTF Task export.
    states = [enum.desc for enum in orti.get_enum_elements_task_state()]
    states.append("READY_ISR")
    task_btf_type_enum = itchi.type_enum.get_btf_mapping_type_enum(states)
    task_btf_type_enum.name = itchi.type_enum.BTF_TASK_MAPPING
    prefix = config.task_state_inspectors.inspector_group_btf_states_prefix
    add_prefix_if_given(task_btf_type_enum, prefix)
    profiler_xml.set_type_enum(task_btf_type_enum)

    # Create and add the TypeEnum for the BTF ISR export.
    isr_btf_type_enum = itchi.runningtask.btf.get_btf_export_type_enum()
    isr_btf_type_enum.name = itchi.type_enum.BTF_ISR_MAPPING
    add_prefix_if_given(isr_btf_type_enum, prefix)
    profiler_xml.set_type_enum(isr_btf_type_enum)


def add_prefix_if_given(type_enum: TypeEnum, prefix: str):
    """Add prefix to each Enum.name of the TypeEnum."""
    if prefix:
        for enum in type_enum.enums:
            enum.name = prefix + enum.name


def add_data_area(data_area: str, profiler_xml: ProfilerXml):
    signal = ProfilerObject(
        name=data_area,
        definition=data_area,
        description=data_area,
        expression=data_area,
        type="TypeEnum_States",
        level="None",
    )
    profiler_xml.set_object(signal)
