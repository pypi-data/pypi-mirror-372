import logging
from itchi.swat import render
from itchi.swat.runnable_microsar import runnable_microsar
from itchi.swat.task_state_microsar import task_state_swat_microsar
from itchi.swat.signals import signals_swat
from itchi.swat.encoding import size_to_mask
from itchi.swat.state import SwatState
from itchi.config import ItchiConfig
from itchi.ortilib.orti import Orti
from itchi.profilerxml.model import (
    ProfilerXml,
    SwatConfigProperties,
    ProfilerObject,
)


def create_swat_default_config(state: SwatState):
    """Create SWAT `ProfilerObject`, `ObjectEncoding`, and `TypeEnum` for status messages."""
    logging.info("Create SWAT default configuration.")
    type_id_key = state.type_id_key
    if type_id_key != 0:
        raise ValueError("Type ID key for status must be zero (but is {type_id_key}).")

    status_encoding = state.generic_encoding.model_copy().into_status(type_id_key)
    swat_var = state.swat_config.swat_target_struct
    if swat_var != "SWAT_ring":
        raise ValueError("SWAT target struct name must be `SWAT_ring`.")

    swat_config_properties = SwatConfigProperties(
        type_mask=size_to_mask(status_encoding.type_id_size),
        time_offset=status_encoding.timestamp_offset,
        time_size=status_encoding.timestamp_size,
        time_right_shift=state.swat_config.time_right_shift,
        structure=f"{swat_var}",
        target_version=state.version.target_version_profiler_xml_str(),
        target_interface=state.version.target_interface_profiler_xml_str(),
        time_address=state.swat_config.time_address,
        polling_interval=state.swat_config.polling_interval,
    )

    swat_object = ProfilerObject(
        name="SWAT_Config",
        definition="SWAT_Config",
        description="SWAT_Config",
        level="SWAT",
        swat_config_properties=swat_config_properties,
    )

    state.profiler_xml.set_object(swat_object)


def swat(orti: Orti, profiler_xml: ProfilerXml, config: ItchiConfig):
    logging.info("Running SWAT.")

    # ORTI file is not required for this use case.
    profiler_xml.orti = None

    state = SwatState(orti, profiler_xml, config)
    if state.num_types >= 256:
        logging.critical("The maximum type size is currently 8.")
        return

    create_swat_default_config(state)

    if config.commands.task_state_swat_microsar:
        task_state_swat_microsar(state)

    if config.commands.runnable_swat:
        runnable_microsar(state)

    if config.commands.signals_swat:
        signals_swat(state)

    render.swat_config_h(state)
