import logging
from dataclasses import dataclass
from typing import Optional
from itchi.ortilib.orti import Orti
from itchi.profilerxml.model import ProfilerXml
from itchi.config import ItchiConfig, SwatConfig, SwatTimestampModeEnum
from itchi.swat.encoding import ObjectEncoding
from itchi.swat.version import SwatVersion


@dataclass
class SwatState:
    """Object to keep track of global state during SWAT profiler XML and code generation."""

    orti: Orti
    profiler_xml: ProfilerXml
    config: ItchiConfig
    swat_config: SwatConfig
    generic_encoding: ObjectEncoding
    signal_encodings: list[ObjectEncoding]
    version: SwatVersion
    num_cores: int = 0
    num_types: int = 0
    microsar_thread_encoding: Optional[ObjectEncoding] = None
    microsar_runnable_encoding: Optional[ObjectEncoding] = None
    _type_id_key: int = 0

    def __init__(self, orti: Orti, profiler_xml: ProfilerXml, config: ItchiConfig):
        self.orti = orti
        self.profiler_xml = profiler_xml
        self.config = config
        self.swat_config = config.swat if config.swat is not None else SwatConfig.default_factory()
        self.version = SwatVersion()
        self.signal_encodings = list()
        self.num_cores = self.orti.get_number_of_cores()
        self.num_types = self._calculate_num_types()

        if self.swat_config.timestamp_mode == SwatTimestampModeEnum.SWAT_TIMESTAMP_AUTO:
            logging.info("Swat timestamp mode auto defaults to 16-bit.")
            self.swat_config.timestamp_mode = SwatTimestampModeEnum.SWAT_TIMESTAMP_16BIT

        if self.swat_config.timestamp_mode == SwatTimestampModeEnum.SWAT_TIMESTAMP_32BIT:
            logging.error("SWAT 32-bit timestamp mode is not supported by the target-code!")
            if self.swat_config.time_right_shift > 0:
                self.swat_config.time_right_shift = 0
                logging.warning("Forcing `time_right_shift` to 0 for 32-bit timestamp mode.")

        self.generic_encoding = ObjectEncoding(
            self.num_cores, self.num_types, self.swat_config.timestamp_mode
        )

    def _calculate_num_types(self) -> int:
        """Calculate total number of types. This number should be equal to number of Profiler XML
        objects plus one as one type ID is always required for status messages."""
        num_types = 1  # Always need one type for the status messages
        if (
            self.config.commands.task_state_swat_microsar
            and self.config.task_state_inst_microsar is not None
        ):
            num_types += 1

        if self.config.commands.runnable_swat and self.config.runnable_instrumentation is not None:
            num_types += 1

        if self.config.commands.signals_swat and self.config.signals_swat is not None:
            num_types += len(self.config.signals_swat.signals)
        return num_types

    @property
    def type_id_key(self) -> int:
        current_key = self._type_id_key
        self._type_id_key += 1
        return current_key
