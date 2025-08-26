import logging
from itchi.ortilib.orti import Orti
from itchi.profilerxml.model import ProfilerXml, ProfilerObject
from itchi.profilerxml.model import TypeEnum, Spinlock, Enum
from itchi.config import ItchiConfig
from itchi.taskstate.instrumentation_microsar import get_state_mapping_vector_microsar
import itchi.type_enum as type_enum


def spinlock_instrumentation_microsar(orti: Orti, profiler_xml: ProfilerXml, config: ItchiConfig):
    """Update the Profiler XML object and TypeEnums for MICROSAR spinlock profiling."""

    if config.commands is not None and not config.commands.task_state_instrumentation_microsar:
        m = "Use --spinlock_instrumentation together with --task_state_instrumentation_microsar."
        raise ValueError(m)
    if not config.spinlock_inst_microsar:
        raise ValueError("Spinlock instrumentation configuration is not set.")

    logging.info("Running spinlock_instrumentation.")
    spinlock_name = "Spinlocks"
    spinlock_profiler_object = ProfilerObject(
        name=spinlock_name,
        definition=spinlock_name,
        description=spinlock_name,
        type=type_enum.SPINLOCKS,
        level="Spinlock",
        expression=config.spinlock_inst_microsar.spinlock_trace_variable,
        spinlock=Spinlock(type=type_enum.SPINLOCK_STATE),
    )

    try:
        spinlocks = orti.get_attribute_decl("TASK", "vs_LOCKED")
    except AssertionError:
        logging.error("No spinlocks found for 'vs_LOCKED'.")
        return

    state_mapping_type_enum = get_state_mapping_vector_microsar()
    state_mapping_type_enum.enums.append(
        Enum(name="POLLING", value="0x100", task_state_property="POLLING")
    )

    spinlockstate_type_enum = TypeEnum(
        name=type_enum.SPINLOCK_STATE,
        enums=[
            Enum(name="FREE", value="2", spinlock_state_property="Unlocked"),
            Enum(name="LOCKED", value="1", spinlock_state_property="Locked"),
            Enum(name="REQUESTED", value="0", spinlock_state_property="Requested"),
        ],
    )

    # This is Vector MICROSAR specific. The implementation is based on the example
    # from MaticK. I don't know why spinlockstate_type_enum and spinlocks_type_enum
    # have to be like they are.
    spinlocks_type_enum = TypeEnum(
        name=type_enum.SPINLOCKS,
        enums=[
            Enum(name=e.formula.replace(".Lock", "").replace("&", ""), value=e.desc)
            for e in spinlocks["attribute_type"]["enum_elements"]
            if e.desc != "-"
        ],
    )

    profiler_xml.set_object(spinlock_profiler_object)
    profiler_xml.set_type_enum(state_mapping_type_enum)
    profiler_xml.set_type_enum(spinlockstate_type_enum)
    profiler_xml.set_type_enum(spinlocks_type_enum)
