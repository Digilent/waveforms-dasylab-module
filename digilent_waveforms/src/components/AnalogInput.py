from ctypes import *  # type: ignore
import time

# Digilent WaveForms Imports
from digilent_waveforms.src.components.DwfAi import DwfAi
from digilent_waveforms.src.components.DwfException import DwfException
from digilent_waveforms.src.components.utils.Logger import Logger
from digilent_waveforms.src.constants.ai_types import AiAcquisitionMode, InstrumentState
from digilent_waveforms.src.constants.dwfconstants import *
from digilent_waveforms.src.constants.error_codes import AnalogInputErorr


class AnalogIn:
    dwf = any
    device_handle: c_int
    dwf_ai: DwfAi
    channel_count: int = 0
    mode: AiAcquisitionMode

    _ai_sample_count = 0
    _ai_lost_count = 0
    _ai_corrupted_count = 0

    def __init__(self, dwf: CDLL, device_handle: c_int, channel_count: int):
        self.device_handle = device_handle
        self.channel_count = channel_count
        self.dwf = dwf
        self.dwf_ai = DwfAi(self.dwf, self.device_handle)

    def set_sample_rate(self, sample_rate: float) -> None:
        self.dwf.FDwfAnalogInFrequencySet(self.device_handle, c_double(sample_rate))

    def set_buffer_size(self, buffer_size: int) -> None:
        self.dwf.FDwfAnalogInBufferSizeSet(self.device_handle, c_int(buffer_size))

    # ---------- Channel enable / disable ----------
    def set_channels_enabled(self, channels: list[int], enabled: list[bool]) -> None:
        try:
            self._check_channels(channels, enabled, "set_channels_enabled", "enables")
            for i in range(0, len(channels)):
                self.dwf.FDwfAnalogInChannelEnableSet(self.device_handle, c_int(channels[i]), c_int(enabled[i]))
        except Exception as e:
            raise e

    def enable_channel(self, channel: int) -> None:
        self.set_channels_enabled([channel], [True])

    def enable_channels(self, channels: list[int]) -> None:
        self.set_channels_enabled(channels, [True] * len(channels))

    def enable_all_channels(self) -> None:
        self.dwf.enable_channel(-1)

    def disable_channel(self, channel: int) -> None:
        self.set_channels_enabled([channel], [False])

    def disable_channels(self, channels: list[int]) -> None:
        self.set_channels_enabled(channels, [False] * len(channels))

    def disable_all_channels(self) -> None:
        self.dwf.disable_channel(-1)

    # ---------- Range ----------
    def set_input_ranges(self, channels: list[int], ranges: list[float]) -> None:
        try:
            self._check_channels(channels, ranges, "set_input_ranges", "ranges")
            for i in range(0, len(channels)):
                self.dwf.FDwfAnalogInChannelRangeSet(self.device_handle, c_int(channels[i]), c_double(ranges[i]))
        except Exception as e:
            raise e

    def set_input_range(self, channel: int, range: float) -> None:
        return self.set_input_ranges([channel], [range])

    def set_input_range_all_channels(self, range: float) -> None:
        return self.set_input_range(-1, range)

    # ---------- Record Mode ----------
    def set_record_length(self, length: float) -> None:
        self.dwf.FDwfAnalogInRecordLengthSet(self.device_handle, c_double(length))

    def record(self, channels: list[int], sample_rate: int, num_samples: float = -1, range: int = 5):
        try:
            self.enable_channels(channels)
            self.set_input_ranges(channels, [range] * len(channels))
            self.set_acquisition_mode(AiAcquisitionMode.Record)
            self.set_sample_rate(sample_rate)
            self.set_record_length(-1 if num_samples < 0 else sample_rate / num_samples)
            self.start()
        except DwfException as e:
            raise e

    def get_record_status(self) -> tuple[int, int, int]:
        available_buffer = c_int()
        lost_buffer = c_int()
        corrupted_buffer = c_int()
        self.dwf.FDwfAnalogInStatusRecord(
            self.device_handle, byref(available_buffer), byref(lost_buffer), byref(corrupted_buffer)
        )
        return (available_buffer.value, lost_buffer.value, corrupted_buffer.value)

    # ---------- State & Status----------
    def get_state(self) -> InstrumentState:
        status_buffer = c_byte()
        self.dwf.FDwfAnalogInStatus(self.device_handle, c_int(1), byref(status_buffer))
        return InstrumentState(status_buffer.value)

    def set_acquisition_mode(self, mode: AiAcquisitionMode) -> None:
        self.dwf.FDwfAnalogInAcquisitionModeSet(self.device_handle, c_int(mode.value))
        self._ai_mode = mode

    def apply_config(self, reset_trigger: bool = True, start_acquisition: bool = False) -> None:
        self.dwf.FDwfAnalogInConfigure(self.device_handle, c_int(reset_trigger), c_int(start_acquisition))
        self._reset_soft_counters()

    def start(self, reset_trigger: bool = True) -> None:
        self.dwf.FDwfAnalogInConfigure(self.device_handle, c_int(reset_trigger), c_int(1))
        self._reset_soft_counters()

    # ---------- Read ----------
    def read_sample_buffer(self, channel: int, num_samples: int) -> list[float]:
        data_buffer = (c_double * num_samples)()
        self.dwf.FDwfAnalogInStatusData(self.device_handle, c_int(channel), byref(data_buffer), num_samples)
        dblPtr = cast(data_buffer, POINTER(c_double))
        floatList = [dblPtr[i] for i in range(num_samples)]
        return floatList

    def read_available_samples(self, channels: list[int]) -> tuple[list[list[float]], int, int]:
        try:
            # Initialize data container with correct dimensions
            data: list[list[float]] = self._get_data_container(channels)
            mode = self.dwf_ai.get_acquisition_mode()

            if mode == AiAcquisitionMode.Record:
                ai_state = self.get_state()

                if self._ai_sample_count == 0 and (
                    ai_state in [InstrumentState.Config, InstrumentState.Prefill, InstrumentState.Armed]
                ):
                    # Acquisition has not yet started
                    return (data, 0, 0)

                samples_available, samples_lost, samples_corrupted = self.get_record_status()
                self._ai_lost_count += samples_lost
                self._ai_corrupted_count += samples_corrupted

                if samples_available == 0:
                    return (data, self._ai_lost_count, self._ai_corrupted_count)

                for channel_index in range(0, len(channels)):
                    samples = self.read_sample_buffer(channels[channel_index], samples_available)
                    data[channel_index] += samples

                return (data, self._ai_lost_count, self._ai_corrupted_count)

            else:
                raise DwfException(message=f"The selected AI Mode ({self._ai_mode}) is not yet implemented")
        except DwfException as e:
            raise e

    def read_samples_blocking(
        self, ai_channels: list[int], num_samples: int, timeout_ms: float = 5000
    ) -> tuple[list[list[float]], int, int]:
        timeout_time = time.time() + timeout_ms / 1000
        sample_count = 0
        lost_count = 0
        corrupt_count = 0
        sample_data = self._get_data_container(ai_channels)
        while sample_count < num_samples:
            if time.time() > timeout_time:
                msg = f"Timeout waiting for AI sample data.  Read ({sample_count}) out of requested ({num_samples}) samples in ({timeout_ms / 1000}) seconds."
                raise DwfException(AnalogInputErorr.TIMEOUT_WAITING_SAMPLES.value, msg, msg)

            iteration_data, iteration_lost_count, iteration_corrupt_count = self.read_available_samples(ai_channels)
            lost_count += iteration_lost_count
            corrupt_count += iteration_corrupt_count

            for channel_index in range(0, len(ai_channels)):
                sample_data[channel_index] += iteration_data[channel_index]

            sample_count += len(iteration_data[0])
            time.sleep(0.1)

        return (sample_data, lost_count, corrupt_count)

    def get_sample_rate_min_max(self) -> tuple[float, float]:
        min = c_double()
        max = c_double()
        self.dwf.FDwfAnalogInFrequencyInfo(self.device_handle, byref(min), byref(max))

        return (min.value, max.value)

    # ---------- Utilities ----------
    def _check_channels(self, channels: list[int], values: list, function_name: str, value_name: str) -> None:
        # Ensure the number of channels matches the number of values
        if len(channels) != len(values):
            msg = f"When calling AnalogInput.{function_name}(), the specified number of channels ({len(channels)}) must match the specified number of {value_name} ({len(values)})"
            Logger.error(msg)
            raise DwfException(AnalogInputErorr.INTPUT_LENGTH_MISMATCH.value, msg, msg)

    def _reset_soft_counters(self) -> None:
        self._ai_sample_count = 0
        self._ai_lost_count = 0
        self._ai_corrupted_count = 0

    def _get_data_container(self, channels: list[int]) -> list[list[float]]:
        data = []
        for channel in channels:
            data.append([])
        return data

    def _ai_validate_channels(self, channels: list[int]) -> None:
        # Check if specified AI channels are valid
        for channel in channels:
            if channel not in range(0, self.channel_count):
                raise DwfException(
                    message=f"The specified AI channel ({channel}) does not exist on the selected device."
                )
