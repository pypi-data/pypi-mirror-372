import logging
import itchi.type_enum
import itchi.swat.render

from dataclasses import dataclass
from itchi.swat.state import SwatState
from itchi.swat import encoding
from itchi.swat.encoding import ObjectEncoding, bits_required, size_to_mask
from itchi.profilerxml.model import Enum, TypeEnum, ProfilerObject, SwatObjectProperties
from itchi.taskstate import instrumentation_microsar
from itchi.taskstate import thread_mapping_microsar


@dataclass
class MicrosarStateMapping:
    id: int
    state: str
    # attribute to indicate how the state should be displayed in the Analyzer
    task_state_property: str


# These MICROSAR state mappings are specific to Vector MICROSAR with SWAT
# because MICROSAR stores each state as an individual bit. However, for SWAT
# we convert these bits into a compressed state representation.
# See the macro `SWAT_MICROSAR_STATE_MASK_TO_VAL` in the observer code.
MICROSAR_STATE_MAPPINGS = [
    MicrosarStateMapping(2, "TERMINATED_ISR", "TERMINATED"),
    MicrosarStateMapping(3, "WAITING_EVENT", "WAITING"),
    MicrosarStateMapping(4, "WAITING_SEM", "WAITING"),
    MicrosarStateMapping(5, "READY", "READY"),
    MicrosarStateMapping(6, "RUNNING", "RUNNING"),
    MicrosarStateMapping(7, "NEW", "ACTIVE"),
    # This is the default state used by the Analyzer and has to be the last entry:
    MicrosarStateMapping(1, "TERMINATED_TASK", "TERMINATED"),
]


def get_thread_state_mapping_type_enum() -> TypeEnum:
    """Returns MICROSAR state mapping as a TypeEnum that can be added to
    the ProfilerXml object."""
    return TypeEnum(
        name=itchi.type_enum.TASK_STATE_MAPPING,
        enums=[
            Enum(m.state, str(m.id), task_state_property=m.task_state_property)
            for m in MICROSAR_STATE_MAPPINGS
        ],
    )


def get_btf_mapping_type_enum() -> TypeEnum:
    states = [m.state for m in MICROSAR_STATE_MAPPINGS]
    btf_thread_type_enum = itchi.type_enum.get_btf_mapping_type_enum(states)
    btf_thread_type_enum.name = itchi.type_enum.BTF_MAPPING
    return btf_thread_type_enum


def get_swat_object_properties(encoding: ObjectEncoding) -> SwatObjectProperties:
    data_size = encoding.core_id_size + encoding.state_id_size + encoding.object_id_size
    data_offset = encoding.type_id_size

    # The following offsets are relative to the data offset in contrast
    # to the offsets in the ObjectEncoding which are relative to the
    # message as a whole.
    mask_core = size_to_mask(encoding.core_id_size)
    state_offset = encoding.core_id_size
    mask_state = size_to_mask(encoding.state_id_size, state_offset)

    thread_offset = state_offset + encoding.state_id_size
    mask_thread = size_to_mask(encoding.object_id_size, thread_offset)

    return SwatObjectProperties(
        type_value=encoding.type_id_key,
        data_size=data_size,
        data_offset=data_offset,
        task_state_mask_core=mask_core,
        task_state_mask_state=mask_state,
        task_state_mask_thread_id=mask_thread,
        task_state_type_enum_name=itchi.type_enum.TASK_STATE_MAPPING,
    )


def get_thread_object(thread_encoding: ObjectEncoding) -> ProfilerObject:
    """Get ProfilerObject for SWAT MICROSAR Thread Profiling."""
    assert thread_encoding.type_id_name == encoding.OBJECT_ENCODING_THREADS_TYPE_NAME

    return ProfilerObject(
        name="Threads",
        description="Threads",
        definition="Threads_Definition",
        type=itchi.type_enum.THREAD_MAPPING,
        level="Task",
        signaling="SWAT",
        swat_object_properties=get_swat_object_properties(thread_encoding),
        btf_mapping_type=itchi.type_enum.BTF_MAPPING,
    )


def get_microsar_thread_encoding(state: SwatState, num_threads: int) -> ObjectEncoding:
    """Clones and transforms `ObjectEncoding` into Vector MICROSAR Threads encoding."""
    obj = state.generic_encoding.model_copy()
    obj.type_id_key = state.type_id_key
    obj.type_id_name = encoding.OBJECT_ENCODING_THREADS_TYPE_NAME

    payload_offset = obj.get_payload_offset()
    obj.state_id_offset = payload_offset
    obj.state_id_size = bits_required(len(MICROSAR_STATE_MAPPINGS))

    obj.object_id_offset = payload_offset + obj.state_id_size
    obj.object_id_size = bits_required(num_threads)

    payload_size = obj.state_id_size + obj.object_id_size
    max_payload_size = obj.get_max_payload_size()
    logging.debug(f"Used {payload_size} out of {max_payload_size} bits for MICROSAR threads.")

    if num_threads > 256:
        raise ValueError("SWAT cannot encode more than 256 threads")

    if payload_size > max_payload_size:
        raise ValueError("SWAT cannot encode MICROSAR thread payload")
    return obj


def task_state_swat_microsar(state: SwatState):
    logging.info("Create SWAT configuration for Vector MICROSAR Thread tracing.")
    if state.config.task_state_inst_microsar is None:
        m = "task_state_inst_microsar must be configured for --task_state_swat_microsar command"
        raise ValueError(m)

    btf_thread_type_enum = get_btf_mapping_type_enum()
    state.profiler_xml.set_type_enum(btf_thread_type_enum)

    mappings = thread_mapping_microsar.get_thread_mapping(
        state.orti, state.config.task_state_inst_microsar.os_types_lcfg_h
    )
    thread_mappings_type_enum = instrumentation_microsar.get_thread_mapping_type_enum(mappings)
    state.profiler_xml.set_type_enum(thread_mappings_type_enum)

    thread_state_mapping_type_enum = get_thread_state_mapping_type_enum()
    state.profiler_xml.set_type_enum(thread_state_mapping_type_enum)

    encoding = get_microsar_thread_encoding(state, len(thread_mappings_type_enum.enums))
    thread_object = get_thread_object(encoding)
    state.microsar_thread_encoding = encoding

    if state.num_cores == 1:
        core = state.orti.orti_core_to_soc_core.get(0, 0)
        logging.warning(
            f"Adding <SourceCore>{core}</SourceCore> to Profiler XML thread object. "
            "This is required for single core applications. Please remap the core via "
            "`running_taskisr.orti_core_to_soc_core` if your application does not run "
            f"on SoC core `{core}`."
        )
        thread_object.source_core = str(0)

    state.profiler_xml.set_object(thread_object)

    itchi.swat.render.microsar_timing_hooks(state.config.task_state_inst_microsar)
