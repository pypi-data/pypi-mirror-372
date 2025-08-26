import json
import logging
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class RunningTaskIsrConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    default_task: str = ""
    default_isr2: str = ""
    search_replace_list: Dict[str, str] = {}
    orti_core_to_soc_core: Dict[int, int] = {}
    orti_core_to_core_name: Dict[int, str] = {}

    @classmethod
    def default_factory(cls):
        return cls()


class TaskStateConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_to_core_mapping: Dict[str, int] = {}
    task_to_core_heuristic: bool = False
    autocore_os_config_h: Path = Path()
    autocore_mk_gen_config_h: Path = Path()

    @classmethod
    def default_factory(cls):
        return cls()


class TaskStateInspectorsConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    inspector_group_btf_states_prefix: str = ""
    constant_variables: Dict[str, int] = {}
    create_data_areas: bool = False
    create_preemption_aware_running_state: bool = False
    default_state: str = ""
    inspectors_file: Path = Field(default=Path("inspectors.json"))
    parent_area_template: str = "Data/{core_name}: Tasks/{task_name}"
    reference_inspectors_file_from_xml: bool = True
    task_core_to_core_name: Dict[int, str] = {}

    @classmethod
    def default_factory(cls):
        return cls()


class TaskStateComplexConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    constant_variables: Dict[str, int] = {}

    @classmethod
    def default_factory(cls):
        return cls()


class InstrumentationTypeEnum(str, Enum):
    DATA_TRACE = "data_trace"
    STM_TRACE = "stm_trace"
    SOFTWARE_TRACE = "software_trace"
    SWAT = "swat"


class TaskStateInstMicrosarConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    vector_os_timing_hooks_h: Path = Field(default=Path("Os_TimingHooks_winidea.h"))
    vector_os_timing_hooks_c: Path = Field(default=Path("Os_TimingHooks_winidea.c"))
    os_types_lcfg_h: Path = Path()
    instrumentation_type: InstrumentationTypeEnum = InstrumentationTypeEnum.DATA_TRACE
    software_based_coreid_gen: bool = True
    trace_variable: str = "winidea_trace"
    trace_variable_definition: str = ""
    stm_base_address: str = "0x0"
    stm_channel: str = "0x0"
    sft_dbpush_register: int = 0

    @classmethod
    def default_factory(cls):
        return cls()


class TaskStateInstAutocoreConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dbg_h: Path = Field(default=Path("Dbg.h"))
    dbg_c: Path = Field(default=Path("Dbg.c"))
    trace_variable_task: str = "winidea_os_task"
    trace_variable_isr: str = "winidea_os_isr"

    @classmethod
    def default_factory(cls):
        return cls()


class RteStackSupplierTypeEnum(str, Enum):
    ETAS = "etas"
    VECTOR = "vector"


class RunnableInstrumentationConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    impl_vfb_hooks_c: Path = Path("rte_vfb_impl.c")
    rte_hook_h: Path = Path()
    rte_xdm: Path = Path()
    rte_arxml: Path = Path()
    rte_stack_supplier: RteStackSupplierTypeEnum = RteStackSupplierTypeEnum.ETAS
    rte_vsmd_path: str = ""
    regex: str = (
        "("  # group[0] matches whole expression
        "FUNC\\(void, RTE_APPL_CODE\\) "
        "Rte_Runnable_"
        "(\\w+)"  # group[1] matches Runnable name
        "_(Start|Return)"  # group[2] matches start/return
        "\\([^\\n]+\\)"  # match any kind of argument declaration
        ")"  # end group[0]
    )
    trace_variable: str = "winidea_trace_runnable"
    trace_variable_definition: str = ""
    template_file: Path = Path()
    instrumentation_type: InstrumentationTypeEnum = InstrumentationTypeEnum.DATA_TRACE
    software_based_coreid_gen: bool = True
    stm_base_address: str = "0x0"
    stm_channel: str = "0x0"
    sft_dbpush_register: int = 0
    sft_dbtag: bool = True

    @classmethod
    def default_factory(cls):
        return cls()


class RunnableProgramFlowConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    runnables: List[str]
    csv_file: Path = Path()
    csv_column_name: str = ""
    csv_column_id: str = ""

    @classmethod
    def default_factory(cls):
        return cls(runnables=[])


class SignalsConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    signals: List[str]

    @classmethod
    def default_factory(cls):
        return cls(signals=[])


class SignalsSwatTypeEnum(str, Enum):
    U8 = "u8"
    U32 = "u32"


class SignalsSwatConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    signals: dict[str, SignalsSwatTypeEnum]

    @classmethod
    def default_factory(cls):
        return cls(signals={})


class SpinlockInstMicrosarConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    spinlock_trace_variable: str = "winidea_trace_spinlock"
    spinlock_trace_variable_definition: str = ""


class ArtiConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    os_trace_variable: str = "arti_os_trace"
    rte_trace_variable: str = "arti_rte_trace"
    os_trace_c: str = "ARTI_Os_Trace.c"
    os_trace_h: str = "ARTI_Os_Trace.h"
    rte_trace_c: str = "ARTI_Rte_Trace.c"
    rte_trace_h: str = "ARTI_RTe_Trace.h"
    software_based_coreid_gen: bool = False

    @classmethod
    def default_factory(cls):
        return cls()


class SwatTimestampModeEnum(str, Enum):
    SWAT_TIMESTAMP_16BIT = "16-bit"
    SWAT_TIMESTAMP_32BIT = "32-bit"
    SWAT_TIMESTAMP_AUTO = "auto"


class SwatConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    swat_config_h: Path = Path("swat_config.h")
    time_right_shift: int = 4
    slot_count: int = 512
    max_retries: int = 16
    swat_target_struct: str = "SWAT_ring"
    time_address: str = ""
    polling_interval: int = 1
    timestamp_mode: SwatTimestampModeEnum = SwatTimestampModeEnum.SWAT_TIMESTAMP_AUTO

    @classmethod
    def default_factory(cls):
        return cls()


class CommandConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    arti: bool = False
    running_taskisr: bool = False
    running_taskisr_btf: bool = False
    running_taskisr_sampling: bool = False
    task_state_single_variable: bool = False
    task_state_complex_expression: bool = False
    task_state_complex_native: bool = False
    task_state_instrumentation_microsar: bool = False
    task_state_instrumentation_autocore: bool = False
    task_state_swat_microsar: bool = False
    runnable_instrumentation: bool = False
    runnable_program_flow: bool = False
    runnable_swat: bool = False
    signals: bool = False
    signals_swat: bool = False
    spinlock_instrumentation_microsar: bool = False
    log_trace_symbols: bool = False

    @classmethod
    def default_factory(cls):
        return cls()

    def is_swat_enabled(self) -> bool:
        """Check if SWAT commands are enabled in the configuration."""
        swat_cmd_names = ["task_state_swat_microsar", "runnable_swat", "signals_swat"]
        swat_active = any(getattr(self, cmd) for cmd in swat_cmd_names)
        if swat_active:
            non_swat_active = any(
                value for attr, value in vars(self).items() if attr not in swat_cmd_names
            )
            if non_swat_active:
                raise ValueError("SWAT flags must not be used together with non-SWAT commands")
        return swat_active

    @classmethod
    def get_required_sections(cls, cmd: str) -> list[str]:
        """Return a list of configuration attributes (sections) that are potentially
        required for a specific command."""
        cmd_to_sections: Dict[str, list[str]] = {
            "running_taskisr": ["running_taskisr"],
            "running_taskisr_btf": ["running_taskisr"],
            "running_taskisr_sampling": ["running_taskisr"],
            "task_state_single_variable": ["running_taskisr", "task_state"],
            "task_state_complex_expression": [
                "running_taskisr",
                "task_state",
                "task_state_inspectors",
            ],
            "task_state_complex_native": ["running_taskisr", "task_state_complex"],
            "task_state_instrumentation_microsar": ["task_state_inst_microsar"],
            "task_state_instrumentation_autocore": ["task_state_inst_autocore"],
            "task_state_swat_microsar": ["swat", "task_state_inst_microsar"],
            "runnable_instrumentation": ["runnable_instrumentation"],
            "runnable_program_flow": ["runnable_program_flow"],
            "runnable_swat": ["swat", "runnable_instrumentation"],
            "signals": ["signals"],
            "signals_swat": ["swat", "signals_swat"],
            "spinlock_instrumentation_microsar": ["spinlock_inst_microsar"],
        }
        return cmd_to_sections.get(cmd, list())

    def all_false(self) -> bool:
        return not any(vars(self).values())


class ItchiConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    orti_file: Path
    profiler_xml_file: Path
    running_taskisr: Optional[RunningTaskIsrConfig] = None
    task_state: Optional[TaskStateConfig] = None
    task_state_inspectors: Optional[TaskStateInspectorsConfig] = None
    task_state_complex: Optional[TaskStateComplexConfig] = None
    task_state_inst_microsar: Optional[TaskStateInstMicrosarConfig] = None
    task_state_inst_autocore: Optional[TaskStateInstAutocoreConfig] = None
    runnable_instrumentation: Optional[RunnableInstrumentationConfig] = None
    runnable_program_flow: Optional[RunnableProgramFlowConfig] = None
    signals: Optional[SignalsConfig] = None
    signals_swat: Optional[SignalsSwatConfig] = None
    spinlock_inst_microsar: Optional[SpinlockInstMicrosarConfig] = None
    arti: Optional[ArtiConfig] = None
    swat: Optional[SwatConfig] = None
    commands: CommandConfig = CommandConfig.default_factory()

    @classmethod
    def default_factory(cls):
        return cls(
            orti_file=Path("OS.ort"),
            profiler_xml_file=Path("profiler.xml"),
            arti=ArtiConfig.default_factory(),
            running_taskisr=RunningTaskIsrConfig.default_factory(),
            task_state=TaskStateConfig.default_factory(),
            task_state_inspectors=TaskStateInspectorsConfig.default_factory(),
            task_state_complex=TaskStateComplexConfig.default_factory(),
            task_state_inst_microsar=TaskStateInstMicrosarConfig.default_factory(),
            task_state_inst_autocore=TaskStateInstAutocoreConfig.default_factory(),
            runnable_instrumentation=RunnableInstrumentationConfig.default_factory(),
            runnable_program_flow=RunnableProgramFlowConfig.default_factory(),
            signals=SignalsConfig.default_factory(),
            signals_swat=SignalsSwatConfig.default_factory(),
            swat=SwatConfig.default_factory(),
            spinlock_inst_microsar=SpinlockInstMicrosarConfig(),
            commands=CommandConfig.default_factory(),
        )

    def add_args(self, args):
        for arg in args:
            if hasattr(self.commands, arg):
                setattr(self.commands, arg, True)


def write_default_config(config_file: Path) -> ItchiConfig:
    def patch_pathlib_path(config: ItchiConfig):
        """
        This is a hack replacing Path(".") with "" to avoid writing "." into
        the Path attributes of the default configuration.
        """

        for field, value in config:
            if issubclass(type(value), BaseModel):
                patch_pathlib_path(value)
            elif value == Path(""):
                setattr(config, field, "")

    config: ItchiConfig = ItchiConfig.default_factory()
    patch_pathlib_path(config)
    with open(config_file, "w") as f:
        f.write(config.model_dump_json(indent=4))
    return config


def patch_data(data):
    """Patch config to maintain better backwards compatibility."""

    # (FelixM 15-Mar-2023) Make task_mapping_file obsolete.
    if "task_state_instrumentation" in data:
        if "task_mapping_file" in data["task_state_instrumentation"]:
            del data["task_state_instrumentation"]["task_mapping_file"]
            m = "Attribute task_state_instrumentation.task_mapping_file is obsolete. Please delete this attribute from your config."
            logging.warning(m)

    # (FelixM 15-Mar-2023) Update signals configuration to match other config sections.
    if "signals" in data and type(data["signals"]) is list:
        data["signals"] = {"signals": data["signals"]}

    # (FelixM 17-Apr-2023) Obsolete template_directory attribute.
    if "task_state_instrumentation" in data:
        task_state_inst = data["task_state_instrumentation"]
        if "template_directory" in task_state_inst:
            del task_state_inst["template_directory"]
            m = "Attribute 'task_state_instrumentation.template_directory' is obsolete."
            logging.warning(m)
            m = "Please use 'vector_os_timing_hooks_c' and 'vector_os_timing_hooks_h' instead."
            logging.warning(m)

    # (FelixM 12-Jun-2023) Rename SpinlockInstrumentationConfig generate_instrumentation.
    if "spinlock_instrumentation" in data:
        spin = data["spinlock_instrumentation"]
        if "generate_instrumentation" in spin:
            spin["spinlock_generate_instrumentation"] = spin["generate_instrumentation"]
            del spin["generate_instrumentation"]

    # (FelixM 20-Jun-2023) Split task_state_instrumentation into microsar and autocore
    if "task_state_instrumentation" in data:
        data["task_state_inst_microsar"] = data["task_state_instrumentation"]
        del data["task_state_instrumentation"]
    if "commands" in data:
        commands = data["commands"]
        if "task_state_instrumentation" in commands:
            commands["task_state_instrumentation_microsar"] = commands["task_state_instrumentation"]
            del commands["task_state_instrumentation"]

    # (FelixM 29-Jun-2023) Rename spinlock_instrumentation to spinlock_inst_microsar
    if "spinlock_instrumentation" in data:
        spin = data["spinlock_instrumentation"]
        data["spinlock_inst_microsar"] = spin
        del data["spinlock_instrumentation"]
        if "spinlock_generate_instrumentation" in spin:
            del spin["spinlock_generate_instrumentation"]
    if "commands" in data:
        commands = data["commands"]
        if "spinlock_instrumentation" in commands:
            commands["spinlock_instrumentation_microsar"] = commands["spinlock_instrumentation"]
            del commands["spinlock_instrumentation"]

    # (FelixM 27-Jun-2024) `search_replace_list` is the only list of tuples item in the config.
    # Change it into a dict for better consistency and compatability with the GUI.
    if "running_taskisr" in data:
        key = "search_replace_list"
        taskisr = data["running_taskisr"]
        if key in taskisr and type(taskisr[key]) is list:
            taskisr[key] = {key: value for (key, value) in taskisr[key]}

    # (FelixM 08-Apr-2025) Rename `isystem_vfb_hooks_c` to `impl_vfb_hooks_c`.
    if "runnable_instrumentation" in data:
        runnable = data["runnable_instrumentation"]
        if "isystem_vfb_hooks_c" in runnable:
            runnable["impl_vfb_hooks_c"] = runnable["isystem_vfb_hooks_c"]
            del runnable["isystem_vfb_hooks_c"]

    # (FelixM 28-May-2025) Remove swat from commands. Users should use the more
    # explicit `task_state_swat_microsar` and `runnable_swat` commands.
    if "commands" in data and "swat" in data["commands"]:
        m = "Please use the `task_state_swat_microsar` or `runnable_swat` commands instead of `swat`."
        logging.warning(m)
        del data["commands"]["swat"]


def load_config(config_file: Path) -> ItchiConfig:
    with open(config_file, "r") as f:
        data = json.load(f)
    patch_data(data)
    config = ItchiConfig(**data)
    return config
