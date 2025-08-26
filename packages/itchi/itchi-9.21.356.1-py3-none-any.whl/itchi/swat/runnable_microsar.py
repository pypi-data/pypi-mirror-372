import logging
import itchi.type_enum
from itchi.runnable.instrumentation import (
    get_rte_runnable_hooks_vector,
    get_rte_hooks,
    get_runnable_type_enum,
)
from itchi.swat.state import SwatState
from itchi.swat import render
from itchi.config import RunnableInstrumentationConfig
from itchi.profilerxml.model import ProfilerObject, TypeEnum, SwatObjectProperties
from itchi.swat.encoding import (
    ObjectEncoding,
    OBJECT_ENCODING_RUNNABLES_TYPE_NAME,
    size_to_mask,
    bits_required,
)


def patch_runnable_object_for_swat(state: SwatState, runnable_object: ProfilerObject):
    if state.num_cores == 1:
        core = state.orti.orti_core_to_soc_core.get(0, 0)
        logging.warning(
            f"Adding <Core>{core}</Core> to Profiler XML Runnable object. "
            "This is required for single core applications. Please remap the core via "
            "`running_taskisr.orti_core_to_soc_core` if your application does not run "
            f"on SoC core `{core}`."
        )
        runnable_object.core = str(core)


def do_microsar_runnable_profiler_xml_config(state: SwatState):
    """Adds the necessary `Object` and `TypeEnums` for MICROSAR Runnable profiling to
    the `state.profiler_xml`."""
    assert state.microsar_runnable_encoding is not None
    assert state.config.runnable_instrumentation is not None
    runnable_config = state.config.runnable_instrumentation

    runnable_type_enum = get_runnable_mapping_type_enum(runnable_config)
    state.profiler_xml.set_type_enum(runnable_type_enum)

    runnable_object = get_runnable_object_swat(state.microsar_runnable_encoding)
    patch_runnable_object_for_swat(state, runnable_object)
    state.profiler_xml.set_object(runnable_object)


def get_runnable_mapping_type_enum(config: RunnableInstrumentationConfig) -> TypeEnum:
    runnable_hooks = get_rte_hooks(config)
    return get_runnable_type_enum(runnable_hooks)


def get_runnable_object_swat(runnable_encoding: ObjectEncoding) -> ProfilerObject:
    """Get ProfilerObject for SWAT Runnable Profiling."""
    assert runnable_encoding.type_id_name == OBJECT_ENCODING_RUNNABLES_TYPE_NAME

    data_size = (
        runnable_encoding.core_id_size
        + runnable_encoding.state_id_size
        + runnable_encoding.object_id_size
    )
    data_offset = runnable_encoding.type_id_size

    # Offset relative to data start
    runnable_offset = runnable_encoding.core_id_size + runnable_encoding.state_id_size
    runnable_mask = size_to_mask(runnable_encoding.object_id_size, runnable_offset)

    # Take runnable message data encoding and convert it to the Profiler XML SWAT format.
    swat_object_properties = SwatObjectProperties(
        type_value=runnable_encoding.type_id_key,
        data_size=data_size,
        data_offset=data_offset,
        runnable_mask_core=size_to_mask(runnable_encoding.core_id_size),
        runnable_mask_id=runnable_mask,
        runnable_exit_value="0",
    )

    return ProfilerObject(
        name="Runnables",
        description="Runnables",
        definition="Runnables_Definition",
        type=itchi.type_enum.RUNNABLE_MAPPING,
        level="Runnable",
        signaling="SWAT",
        swat_object_properties=swat_object_properties,
    )


def get_microsar_runnable_encoding(state: SwatState) -> ObjectEncoding:
    """Clones and transforms `ObjectEncoding` into Vector MICROSAR Runnables encoding."""
    config = state.config.runnable_instrumentation
    assert config is not None

    obj = state.generic_encoding.model_copy()
    obj.type_id_key = state.type_id_key
    obj.type_id_name = OBJECT_ENCODING_RUNNABLES_TYPE_NAME
    payload_offset = obj.get_payload_offset()

    # Runnables don't have state IDs
    obj.state_id_offset = payload_offset
    obj.state_id_size = 0

    hooks = get_rte_runnable_hooks_vector(config.rte_hook_h, config.regex)
    num_runnables = len(hooks) // 2  # there is a start and return hook for each runnable
    obj.object_id_offset = obj.state_id_offset + obj.state_id_size
    obj.object_id_size = bits_required(num_runnables + 1)
    payload_size = obj.state_id_size + obj.object_id_size

    max_payload_size = obj.get_max_payload_size()

    if (num_runnables + 1) > 2**16:
        # The object ID '0' is reserved for Runnable exits
        raise ValueError(f"SWAT cannot encode more than {2**16 - 1} Runnables")
    if payload_size > max_payload_size:
        m = f"Used {payload_size} out of {max_payload_size} bits for MICROSAR Runnables."
        logging.warning(m)
        raise ValueError("SWAT does not have enough bits to encode Runnables")
    return obj


def runnable_microsar(state: SwatState):
    if state.config.runnable_instrumentation is None:
        m = "runnable_instrumentation must be configured for --runnable_swat command"
        raise ValueError(m)

    if not state.config.runnable_instrumentation.rte_hook_h.is_file():
        m = "Rte_Hook.h file must be configured and exist for SWAT Runnable instrumentation"
        raise ValueError(m)

    logging.info("Create SWAT configuration for Vector MICROSAR Runnable tracing.")
    state.microsar_runnable_encoding = get_microsar_runnable_encoding(state)
    do_microsar_runnable_profiler_xml_config(state)
    render.microsar_vfb_runnable_hooks(state.config.runnable_instrumentation)
