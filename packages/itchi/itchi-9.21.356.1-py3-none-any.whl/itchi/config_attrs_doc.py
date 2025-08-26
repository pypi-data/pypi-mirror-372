import logging
from typing import Dict, Union


CONFIG_ATTRS_DOC: Dict[str, Union[str, Dict[str, str]]] = {
    "orti_file": "Mandatory path to the OS ORTI file.",
    "profiler_xml_file": "Mandatory path to the Profiler XML file that iTCHi will generate.",
    "running_taskisr": {
        "default_task": "Name of default task; only required if ORTI file does not include NO_TASK or INVALID_TASK.",
        "default_isr2": "Name of default ISR; only required if ORTI file does not include NO_ISR or INVALID_ISR.",
        "search_replace_list": "Rename Task or ISR variable to a static symbol if it includes a pointer. iTCHi will consecutively replace the key with the value.",
        "orti_core_to_soc_core": "Map an AUTOSAR OS core to a different physical core. For example, to remap AUTOSAR core 0 to SoC core 3, enter '0' and '3'.",
        "orti_core_to_core_name": "Rename an AUTOSAR OS core. For example, to rename AUTOSAR core 0 to 'Cortex-M4.1', enter '0' and 'Cortex-M4-1'.",
    },
    "task_state": {
        "task_to_core_mapping": "Explicitly map tasks to AUTOSAR cores if 'task_to_core_heuristic' does not work.",
        "task_to_core_heuristic": "If 'true', iTCHi tries to extract the core ID for each task from the ORTI STATE attribute.",
        "autocore_os_config_h": "For Elektrobit tresos AutoCore OS, point this attribute to the 'OsConfig.h' file.",
        "autocore_mk_gen_config_h": "For Elektrobit tresos Safety OS, point this attribute to the 'MkGenConfig.h' file.",
    },
    "task_state_inspectors": {
        "inspector_group_btf_states_prefix": "iTCHi prefixes the BTF TypeEnums with this string. This is helpful when using Inspector groups.",
        "constant_variables": "Use this attribute to map specific symbols (variables) to a specific value for task state based profiling. This is helpful when a variable only changes once during startup.",
        "create_data_areas": "If 'true', iTCHi adds the required data areas for the Task Inspectors to the Profiler XML.",
        "create_preemption_aware_running_state": "If 'true', iTCHi adds a second Inspector for each task that provides a second 'RUNNING_' state with correct preempt statistics.",
        "default_state": "Default state for Inspectors; usually it is SUSPENDED or UNKNOWN.",
        "inspectors_file": "iTCHi generates the Inspectors into this file. It should have a '.json' file ending.",
        "parent_area_template": "References the parent object for the Inspectors. The default should be fine.",
        "reference_inspectors_file_from_xml": "If 'true', the Profiler XML references the Inspectors file and winIDEA loads them automatically. To import the Inspectors manually, use 'false'.",
        "task_core_to_core_name": "Map a SoC Task core ID to a different core name. If a Task on core 0 should reference CPU2, enter '0' and 'CPU2'",
    },
    "task_state_complex": {
        "constant_variables": "Use this attribute to map specific symbols (variables) to a specific value for task state based profiling. This is helpful when a variable only changes once during startup."
    },
    "task_state_inst_microsar": {
        "vector_os_timing_hooks_h": "Header file into which iTCHi generates the Vector OS Timing Hooks instrumentation code.",
        "vector_os_timing_hooks_c": "Source file into which iTCHi generates the data trace instrumentation variable definition.",
        "os_types_lcfg_h": "Path to MICROSAR 'Os_Types_Lcfg.h' file. If provided, iTCHi extracts the thread IDs from this file.",
        "instrumentation_type": "Select the trace type. It can be 'data_trace', 'stm_trace', or 'software_trace'. The default is 'data_trace'.",
        "software_based_coreid_gen": "If 'true', use core ID from timing hooks. If 'false', use core ID from trace.",
        "trace_variable": "If 'instrumentation_type' is 'data_trace', this specifies the name of the Thread instrumentation trace variable.",
        "trace_variable_definition": "Override the definition of the trace variable. Useful when using vendor specific MemMap includes.",
        "stm_base_address": "If 'instrumentation_type' is 'stm_trace', this specifies the STM base address.",
        "stm_channel": "If 'instrumentation_type' is 'stm_trace', this specifies the STM Thread channel.",
        "sft_dbpush_register": "If 'instrumentation_type' is 'software_trace' this specifies the Thread DB Push register.",
    },
    "task_state_inst_autocore": {
        "dbg_h": "Header file into which iTCHi generates the EB tresos AutoCore Dbg hooks.",
        "dbg_c": "Source file into which iTCHi generates the EB tresos AutoCore Dbg trace variable definitions",
        "trace_variable_task": "Name of the task instrumentation variable.",
        "trace_variable_isr": "Name of the ISR instrumentation variable.",
    },
    "runnable_instrumentation": {
        "impl_vfb_hooks_c": "Path to the VFB hook implementation file that iTCHi generates.",
        "rte_hook_h": "If you use Vector MICROSAR Classic RTE, point this attribute to the 'RteHook.h' file.",
        "rte_xdm": "If you use Elektrobit tresos AutoCore RTE, point this attribute to the 'RTE.xdm' file.",
        "rte_arxml": "If the active RTE hooks shall be derived from the RTE configuration file, point this attribute to the RTE EcuC file.",
        "rte_stack_supplier": "If 'rte_arxml' is used, specify the RTE stack supplier.",
        "rte_vsmd_path": "If 'rte_arxml' is used but the used RTE stack supplier isn't supported yet, specify the vendor specific reference to the VFB trace function.",
        "regex": "A regular expression to extract hooks from 'RteHook.h'. Adapt this to find other hooks, but preserve the three Python regex matching groups.",
        "trace_variable": "If Runnable 'instrumentation_type' is 'data_trace', this specifies the name of the Runnable trace variable.",
        "trace_variable_definition": "Override the definition of the trace variable. Useful when using vendor specific MemMap includes.",
        "template_file": "If specified, iTCHi writes the VFB trace template into it. The user can then adapt it, and iTCHi will use it in the following runs.",
        "instrumentation_type": "Select the Runnable trace type. It can be 'data_trace', 'stm_trace', or 'software_trace'. Default is 'data_trace'.",
        "software_based_coreid_gen": "If 'true', uses core ID from core ID method in the generated file. If 'false', uses core ID from trace (if available).",
        "stm_base_address": "If 'instrumentation_type' is 'stm_trace', this specifies the STM base address.",
        "stm_channel": "If 'instrumentation_type' is 'stm_trace', this specifies the STM Runnable channel.",
        "sft_dbpush_register": "If 'instrumentation_type' is 'software_trace' this specifies the Runnable DB Push register.",
        "sft_dbtag": "If 'instrumentation_type' is 'software_trace' and this is 'true', DBTAG instrumentation is used.",
    },
    "runnable_program_flow": {
        "runnables": "List of functions that should be treated as Runnables. Adding regular functions as Runnables will likely lead to undesired behavior.",
        "csv_file": "Optional path to CSV file listing functions that should be treated as Runnables",
        "csv_column_name": "Column name of interest in csv_file (either column_name or column_id has to be specified)",
        "csv_column_id": "Column index of interest in csv_file (either column_name or column_id has to be specified)",
    },
    "signals": {
        "signals": "List of signals (variables) that should be visualized as separate objects in the Profiler timeline. These signals are also exported to BTF."
    },
    "signals_swat": {
        "signals": "Dictionary that maps signal names to signal types. The supported signal types are 'u8' and 'u32'."
    },
    "spinlock_inst_microsar": {
        "spinlock_trace_variable": "Name of of the spinlock trace variable. Defaults to 'isystem_trace_spinlock'.",
        "spinlock_trace_variable_definition": "Override the definition of the trace variable. Useful when using vendor specific MemMap includes.",
    },
    "swat": {
        "swat_config_h": "Path to the `swat_config.h` file that includes the project specific configuration of the target code. The latest version of this file must be part of the build.",
        "time_right_shift": "Shift value for timestamp reduction. Controls how many bits to shift right when encoding timestamps, affecting precision vs range. Defaults to 4.",
        "slot_count": "Number of 32-bit slots in the SWAT ring buffer. Must be less than 0x8000 (32768). Defaults to 512.",
        "max_retries": "Maximum number of retries for compare-and-swap operations before marking a failure. Controls how persistent the buffer is when under contention. Defaults to 16.",
        "swat_target_struct": "Name of the global SWAT ring buffer structure. Keep 'SWAT_ring', otherwise, the target code has to be updated accordingly.",
        "time_address": "Address of the memory mapped address of the on-chip counter that is used for the timestamps. This must be configured for synchronized trace (trace with other trace sources in addition to SWAT) and match the arch specific target code.",
        "polling_interval": "Period in milliseconds for how often the SWAT streamer polls the target. Defaults to 1. Set to 0 for maximum sampling rate.",
        "timestamp_mode": "Configure the number of bits used for timestamping. `16-bit` or `32-bit` mode are supported. If `auto` is selected iTCHI sets this option based on the current configuration.",
    },
    "arti": {
        "os_trace_c": "ARTI OS instrumentation C file.",
        "os_trace_h": "ARTI OS instrumentation H file.",
        "os_trace_variable": "ARTI OS instrumentation variable.",
        "rte_trace_c": "ARTI RTE instrumentation C file.",
        "rte_trace_h": "ARTI RTE instrumentation H file.",
        "rte_trace_variable": "ARTI RTE instrumentation variable.",
        "software_based_coreid_gen": "If 'true', uses core ID from core ID method in the generated file. If 'false', uses core ID from trace (if available).",
    },
}


def log_attrs_doc():
    """Log all available attributes and their documentation."""
    logging.info("Printing all attributes with documentation string.")
    for top_level_key, value in CONFIG_ATTRS_DOC.items():
        if type(value) is str:
            logging.info(f"  {top_level_key}: {value}")
        elif type(value) is dict:
            logging.info(f"  {top_level_key}:")
            for sub_level_key, sub_value in value.items():
                logging.info(f"     {sub_level_key}: {sub_value}")
        else:
            assert False, "Unexpected attribute documentation type"
