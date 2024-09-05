from ctypes import *  # type: ignore

# Digilent WaveForms Imports
from digilent_waveforms.src.components.DwfException import DwfException
from digilent_waveforms.src.constants.ao_types import OutputFunction, InstrumentStartMode
from digilent_waveforms.src.constants.dwfconstants import *
from digilent_waveforms.src.constants.error_codes import AnalogOutError


class AnalogOut:
    dwf = any
    device_handle: c_int
    channel_count: int = 0

    def __init__(self, dwf: CDLL, device_handle: c_int, channel_count: int):
        self.device_handle = device_handle
        self.channel_count = channel_count
        self.dwf = dwf

    # ---------- Channel enable / disable ----------
    def set_channels_enabled(self, channels: list[int], enabled: list[bool]) -> None:
        try:
            self._check_channels(channels, enabled)
            for i in range(0, len(channels)):
                self.dwf.FDwfAnalogOutEnableSet(self.device_handle, c_int(channels[i]), c_int(enabled[i]))
        except Exception as e:
            raise e

    def enable_channel(self, channel: int) -> None:
        self.set_channels_enabled([channel], [True])

    def enable_channels(self, channels: list[int]) -> None:
        self.set_channels_enabled(channels, [True])

    def enable_all_channels(self) -> None:
        self.dwf.FDwfAnalogOutEnableSet(self.device_handle, c_int(-1), c_int(1))

    def disable_channel(self, channel: int) -> None:
        self.set_channels_enabled([channel], [False])

    def disable_channels(self, channels: list[int]) -> None:
        self.set_channels_enabled(channels, [False])

    def disable_all_channels(self) -> None:
        self.dwf.FDwfAnalogOutEnableSet(self.device_handle, c_int(-1), c_int(0))

    # ---------- Output function ----------
    def set_output_functions(self, channels: list[int], functions: list[OutputFunction]) -> None:
        try:
            self._check_channels(channels, functions)
            for i in range(0, len(channels)):
                self.dwf.FDwfAnalogOutFunctionSet(self.device_handle, c_int(channels[i]), functions[i].value)
        except Exception as e:
            raise e

    def set_output_function(self, channel: int, function: OutputFunction) -> None:
        return self.set_output_functions([channel], [function])

    def set_output_function_all_channels(self, function: OutputFunction) -> None:
        return self.set_output_function(-1, function)

    # ---------- Offset ----------
    def set_offets(self, channels: list[int], offsets: list[float]) -> None:
        try:
            self._check_channels(channels, offsets)
            for i in range(0, len(channels)):
                self.dwf.FDwfAnalogOutOffsetSet(self.device_handle, c_int(channels[i]), c_double(offsets[i]))
        except Exception as e:
            raise e

    def set_offet(self, channel: int, offset: float) -> None:
        return self.set_offets([channel], [offset])

    def set_offset_all_channels(self, offset: float) -> None:
        return self.set_offet(-1, offset)

    # ---------- Limit ----------
    def set_limits(self, channels: list[int], limits: list[float]) -> None:
        try:
            self._check_channels(channels, limits)
            for i in range(0, len(channels)):
                self.dwf.FDwfAnalogOutLimitationSet(self.device_handle, c_int(channels[i]), c_double(limits[i]))
        except Exception as e:
            raise e

    def set_limit(self, channel: int, limit: float) -> None:
        return self.set_limits([channel], [limit])

    def set_limit_all_channels(self, offset: float) -> None:
        return self.set_limit(-1, offset)

    # ---------- Configure ----------
    def configure_channels(self, channels: list[int], start_mode: list[InstrumentStartMode]) -> None:
        try:
            self._check_channels(channels, start_mode)
            for i in range(0, len(channels)):
                self.dwf.FDwfAnalogOutConfigure(self.device_handle, c_int(channels[i]), c_int(start_mode[i].value))
        except Exception as e:
            raise e

        # Ensure the number of channels matches the number of start modes
        if len(channels) != len(start_mode):
            msg = f"The specified number of channels ({len(channels)}) must match the specified number of start modes ({len(start_mode)})"
            raise DwfException(AnalogOutError.INTPUT_LENGTH_MISMATCH.value, msg, msg)

    def configure_channel(self, channel: int, start_mode: InstrumentStartMode) -> None:
        return self.configure_channels([channel], [start_mode])

    def configure_all_channels(self, start_mode: InstrumentStartMode) -> None:
        return self.configure_channel(-1, start_mode)

    # ---------- Start ----------
    def start_channels(self, channels: list[int]) -> None:
        return self.configure_channels(channels, [InstrumentStartMode.START] * len(channels))

    def start_channel(self, channel: int) -> None:
        return self.start_channels([channel])

    def start_all_channels(self) -> None:
        return self.start_channel(-1)

    # ---------- Stop ----------
    def stop_channels(self, channels: list[int]) -> None:
        return self.configure_channels(channels, [InstrumentStartMode.STOP] * len(channels))

    def stop_channel(self, channel: int) -> None:
        return self.stop_channels([channel])

    def stop_all_channels(self) -> None:
        return self.stop_channel(-1)

    # ---------- Utilities ----------
    def _check_channels(self, channels: list[int], values: list) -> None:
        # Ensure the number of channels matches the number of values
        if len(channels) != len(values):
            msg = f"The specified number of channels ({len(channels)}) must match the specified number of values ({len(values)})"
            raise DwfException(AnalogOutError.INTPUT_LENGTH_MISMATCH.value, msg, msg)
