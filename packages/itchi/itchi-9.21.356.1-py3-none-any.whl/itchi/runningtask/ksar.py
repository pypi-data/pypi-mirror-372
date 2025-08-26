import logging
import re
from itchi.ortilib.orti import Orti
from itchi.profilerxml.model import ProfilerXml, ProfilerObject, TypeEnum, Enum

_TYPE_ENUM_THREADS = "TypeEnum_Threads"


def running_taskisr_ksar(orti: Orti, profiler_xml: ProfilerXml) -> ProfilerXml:
    """Update the Profiler XML object with the objects for Running Task/ISR
    tracing. In general, winIDEA can handle this use case by itself. However,
    we might want to override the default object, get rid of pointers, or
    we might need this objects for advanced use cases.

    Args:
        orti (Orti): ORTI object
        profiler_xml (ProfilerXml): Profiler XML object

    Returns:
        ProfilerXml: The same updated Profiler XML object
    """
    logging.info("Running 'running_taskisr_ksar'.")

    # No dependency on ORTI for KSAR. All information is part of the Profiler XML.
    profiler_xml.orti = None

    # RUNNINGTASK and RUNNINGISR contain the same information for KSAR. Therefore,
    # we only care about RUNNINGTASK and then process it into a Thread Profiler object.
    for task_object in orti.get_attribute_defs_runningtask():
        if task_object["attribute_name"].startswith("RUNNINGTASK"):
            p = get_profiler_object(orti, task_object)
            profiler_xml.set_object(p)

    type_enum_threads = get_type_enum_threads(orti)
    profiler_xml.set_type_enum(type_enum_threads)

    return profiler_xml


def get_profiler_object(orti: Orti, orti_task_object) -> ProfilerObject:

    # RUNNINGTASK is misleading because Tasks and ISRs are handled under the
    # same object. Thread is more accurate.
    name = orti_task_object["attribute_name"]
    name = name.replace("RUNNINGTASK", "RUNNINGTHREAD")
    core_name = orti_task_object["soc_name"]
    core_id = orti_task_object["soc_core"]

    # By default KSAR has a complex RUNNINGTASK expression. That expression
    # simplifies down to a sign running Task variable that is part of a struct.
    # For single core applications it's `(Os_GSddCoreState).pStaticTask`
    # (probably, I am guessing, honestly) and for # multi-core
    # `(Os_GSddCoreState0).pStaticTask` where the decimal indicates the core.
    # So, we search for a decimal in square brackets. If we find it we use that
    # as the core decimal, otherwise, we use the expression without the
    # decimal.
    formula = orti_task_object["formula"]
    if m := re.findall(r"State\[(\d+)\]", formula):
        core_index = m[0]
        formula = f"(Os_GSddCoreState{core_index}).pStaticTask"
    else:
        formula = "(Os_GSddCoreState).pStaticTask"

    p = ProfilerObject(
        name=name,
        definition=name,
        description=f"{core_name}: Threads",
        type=_TYPE_ENUM_THREADS,
        default_value=orti.get_default_task(),
        expression=formula,
        level="Task",
        core=str(core_id),
    )
    return p


def get_type_enum_threads(orti: Orti) -> TypeEnum:
    # KSAR has a single running thread variable per core. Therefore, we merge
    # the Task and ISR2 Enums into a single Profiler XML Enum that is then
    # reference from the Profiler Thread objects.
    orti_enums = orti.get_enum_elements_runningtask()
    orti_enums += orti.get_enum_elements_runningisr2()

    enums = []
    for orti_enum in orti_enums:
        name = orti_enum.desc
        value = ""

        if isinstance(orti_enum.const, int):
            value = hex(orti_enum.const)
        if orti_enum.formula:
            value = orti_enum.formula

        # Os_Sleep has the same name for every core so we add an index to
        # differentiate between them. The second last character in the formula
        # is the ID of the thread within the thread struct array.
        if name == "Os_Sleep":
            thread_array_id = value[-2]
            name = "Os_Sleep_" + thread_array_id

        e = Enum(name=name, value=value)
        enums.append(e)

    return TypeEnum(
        name=_TYPE_ENUM_THREADS,
        enums=enums,
    )
