import itchi.runningtask.basic
from itchi.config import ItchiConfig
from itchi.profilerxml.model import ProfilerXml, Sampling, ProfilerObject, Enum, TypeEnum
from itchi.ortilib.orti import Orti


def running_taskisr_sampling(orti: Orti, profiler_xml: ProfilerXml, config: ItchiConfig):
    """
    Populates ProfilerXml objects with the data from the Orti
    object that is required for running Task/ISR sampling.

    See: https://docs.google.com/document/d/1Y6w5ipKYQRftOA_e8T2spIndabr99llYIhTkFX6qmxM/edit#heading=h.wryhke45nk1j

    :param orti: reference to Orti object
    :param profilerXml: reference to ProfilerXml object
    :param config: iTCHi config object
    """

    if config.task_state and config.task_state.autocore_mk_gen_config_h.is_file():
        """(FelixM)
        This is an ugly workaround for the Elektrobit AutoCore OS on Infineon AURIX
        microcontrollers. EB is no longer using Tasks and ISRs according to the ORTI
        specification, but uses threads instead. We can only handle this case if the Mk_gen_config.h file is part of the iTCHi config task_state object.
        """
        running_thread_sampling_eb(orti, profiler_xml, config)
        return

    postfix = " (Sampling)"
    sampling = Sampling(acquisition="DAQ", sample_pool=100)
    tasks = itchi.runningtask.basic.get_task_objects(orti, postfix)
    isr2s = itchi.runningtask.basic.get_isr2_objects(orti, postfix)
    for task, isr in zip(tasks, isr2s):
        task.sampling = sampling
        profiler_xml.set_object(task)
        isr.sampling = sampling
        profiler_xml.set_object(isr)

    itchi.runningtask.basic.pointer_warning(orti)


def running_thread_sampling_eb(orti: Orti, profiler_xml: ProfilerXml, config: ItchiConfig):
    """Procedure to support Thread profiling for the AutoCore OS on AURIX
    specifically implemented for Halla. Very quick and very dirty.

    Args:
        orti (Orti): ORTI object
        profiler_xml (ProfilerXml): Profiler XML object
        config (ItchiConfig): iTCHi config object
    """

    if config.task_state is None:
        return

    # Add thread objects to profiler XML
    _TYPE_ENUM_THREAD_MAPPING = "TypeEnum_ThreadMapping"
    threads = orti.get_attribute_defs("OS", "vs_RUNNINGTHREAD")
    postfix = " (Sampling)"
    threads = [
        ProfilerObject(
            name=t["attribute_name"] + postfix,
            definition=t["attribute_name"] + postfix,
            description=f"{t['soc_name']}: Threads{postfix}",
            type=_TYPE_ENUM_THREAD_MAPPING,
            default_value="NO_THREAD",
            expression=t["formula"].replace("->name", ""),
            level="Task",  # lowest IRQ level in Profiler XML
            core=str(t["soc_core"]),
            sampling=Sampling(acquisition="DAQ", sample_pool=100),
        )
        for t in threads
    ]

    for t in threads:
        profiler_xml.set_object(t)

    # Update meta data
    profiler_xml.orti = ""
    profiler_xml.num_cores = len(threads)

    # Extract thread mappings and add to Profiler XML
    type_enum = TypeEnum(
        name=_TYPE_ENUM_THREAD_MAPPING,
        enums=[
            Enum("mk_idle_thread_core0", "&MK_c0_idleThread"),
            Enum("mk_aux1_thread_core0", "&MK_c0_aux1Thread"),
            Enum("mk_aux2_thread_core0", "&MK_c0_aux2Thread"),
            Enum("mk_qmos_thread_core0", "&MK_c0_qmosThreadConfig"),
        ],
    )

    # taskName = "#define MK_TASKCFG_"
    task_name_define_start = "#define MK_TASKCFG_"
    isr_name_define_start = "#define MK_ISRCFG_"
    thread_expression_string = "Threads["
    core_id_string = "/* core"
    with open(config.task_state.autocore_mk_gen_config_h) as f:
        thread_name, thread_expression, _core_id = "", "", ""
        for line in f:
            if line.startswith(task_name_define_start):
                thread_name = line.replace(task_name_define_start, "").split()[0]
            elif line.startswith(isr_name_define_start):
                thread_name = line.replace(isr_name_define_start, "").split()[0]
            elif thread_expression_string in line:
                thread_expression = line.split(",")[0].strip()
            elif core_id_string in line:
                _core_id = line.split(",")[0].strip()
                if thread_name and thread_expression:
                    enum = Enum(thread_name, thread_expression)
                    type_enum.enums.append(enum)
                    thread_name, thread_expression = "", ""
    profiler_xml.set_type_enum(type_enum)
