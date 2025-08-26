import logging

from itchi.config import SignalsSwatTypeEnum
from itchi.swat.state import SwatState
from itchi.swat.encoding import ObjectEncoding
from itchi.profilerxml.model import (
    ProfilerObject,
    SwatObjectProperties,
)


def get_swat_signal_object(signal_encoding: ObjectEncoding) -> ProfilerObject:
    swat_object_properties = SwatObjectProperties(
        type_value=signal_encoding.type_id_key,
        data_offset=signal_encoding.state_id_offset,
        data_size=signal_encoding.state_id_size,
    )

    signal_name = signal_encoding.type_id_name
    return ProfilerObject(
        name=signal_name,
        definition=signal_name,
        description=signal_name,
        signaling="SWAT",
        level="None",
        swat_object_properties=swat_object_properties,
    )


def signals_swat(state: SwatState):
    if state.config.signals_swat is None:
        m = "signals_swat must be configured for --signals_swat command"
        raise ValueError(m)

    logging.info("Create SWAT configuration for signals.")
    for signal_name, signal_type in state.config.signals_swat.signals.items():
        type_id_key = state.type_id_key  # side effect: increments type_id_key
        signal_encoding = state.generic_encoding.model_copy()
        if signal_type is SignalsSwatTypeEnum.U32:
            signal_encoding = signal_encoding.into_signal_u32(type_id_key, signal_name)
        elif signal_type is SignalsSwatTypeEnum.U8:
            signal_encoding = signal_encoding.into_signal_u8(type_id_key, signal_name)
        else:
            m = f"Unsupported signal type: {signal_type}"
            raise ValueError(m)
        state.signal_encodings.append(signal_encoding)
        signal_object = get_swat_signal_object(signal_encoding)
        state.profiler_xml.set_object(signal_object)
