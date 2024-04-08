from ctypes import *  # type: ignore
from digilent_waveforms.src.components.DwfException import DwfException
from digilent_waveforms.src.constants.dwfconstants import *
from digilent_waveforms.src.constants.ao_types import OutputFunction, InstrumentStartMode
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
        # Ensure the number of channels matches the number of enabled states
        if len(channels) != len(enabled):
            msg = f"The specified number of channels ({len(channels)}) must match the specified number of enabled states ({len(enabled)})"
            raise DwfException(AnalogOutError.INTPUT_LENGTH_MISMATCH.value, msg, msg)

        for i in range(0, len(channels)):
            self.dwf.FDwfAnalogOutEnableSet(self.device_handle, c_int(channels[i]), c_int(enabled[i]))

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
        # Ensure the number of channels matches the number of offsets states
        if len(channels) != len(functions):
            msg = f"The specified number of channels ({len(channels)}) must match the specified number of output functions ({len(functions)})"
            raise DwfException(AnalogOutError.INTPUT_LENGTH_MISMATCH.value, msg, msg)

        for i in range(0, len(channels)):
            self.dwf.FDwfAnalogOutFunctionSet(self.device_handle, c_int(channels[i]), functions[i])

    def set_output_function(self, channel: int, function: OutputFunction) -> None:
        return self.set_output_functions([channel], [function])

    def set_output_function_all_channels(self, function: OutputFunction) -> None:
        return self.dwf.set_output_functions(-1, function)

    # ---------- Offset ----------
    def set_offets(self, channels: list[int], offsets: list[float]) -> None:
        # Ensure the number of channels matches the number of offsets states
        if len(channels) != len(offsets):
            msg = f"The specified number of channels ({len(channels)}) must match the specified number of offsets ({len(offsets)})"
            raise DwfException(AnalogOutError.INTPUT_LENGTH_MISMATCH.value, msg, msg)

        for i in range(0, len(channels)):
            self.dwf.FDwfAnalogOutOffsetSet(self.device_handle, c_int(channels[i]), c_double(offsets[i]))

    def set_offet(self, channel: int, offset: float) -> None:
        return self.set_offets([channel], [offset])

    def set_offset_all_channels(self, offset: float) -> None:
        return self.set_offet(-1, offset)

    # ---------- Configure ----------
    def configure_channels(self, channels: list[int], start_mode: list[InstrumentStartMode]) -> None:
        # Ensure the number of channels matches the number of start modes
        if len(channels) != len(start_mode):
            msg = f"The specified number of channels ({len(channels)}) must match the specified number of start modes ({len(start_mode)})"
            raise DwfException(AnalogOutError.INTPUT_LENGTH_MISMATCH.value, msg, msg)

        for i in range(0, len(channels)):
            self.dwf.FDwfAnalogOutConfigure(self.device_handle, c_int(channels[i]), c_int(start_mode[i].value))

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
