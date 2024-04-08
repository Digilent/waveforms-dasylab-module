from ctypes import *  # type: ignore
import sys

from digilent_waveforms.src.constants.dwfconstants import *
from digilent_waveforms.src.components.DwfException import DwfException
from digilent_waveforms.src.constants.dwf_types import DeviceType
from digilent_waveforms.src.constants.ai_types import AiAcquisitionMode, InstrumentState
from digilent_waveforms.src.components.AnalogOut import AnalogOut


class Device:
    device_index: int = -1
    device_handle: c_int
    name: str = ""
    type: DeviceType
    revision: int = -1
    serial_number: str = ""

    # Subsystems
    AnalogOutput: AnalogOut

    ai_count = 0
    ao_count = 0

    _ai_mode: AiAcquisitionMode
    _ai_sample_count: int = 0
    _ai_lost_count: int = 0
    _ai_corrupted_count: int = 0

    def __init__(
        self,
        dwf: CDLL,
        device_index: int,
        device_handle: c_int,
        name: str,
        type: DeviceType,
        revision: int,
        serial_number: str,
    ):

        self.dwf = dwf
        self.device_index = device_index
        self.device_handle = device_handle
        self.name = name
        self.device_type = type
        self.revision = revision
        self.serial_number = serial_number

        # ---------- Enumerate device IO ----------
        self.ai_count = self._get_analog_input_count()
        self.ao_count = self._get_analog_output_count()

        # Instantiate subsystems
        self.AnalogOutput = AnalogOut(self.dwf, self.device_handle, self.ao_count)

    def ai_config(self, sample_frequency: float, buffer_size: int, reset_trigger=True, start_acquisition=True) -> None:
        # Prevent config options from being applied at each call.  Instead apply config options only when FDwfAnalogInConfigure is called.
        self.dwf.FDwfDeviceAutoConfigureSet(self.device_handle, c_int(0))

        # set up acquisition
        self.ai_set_sample_rate(sample_frequency)
        self.ai_set_buffer_size(buffer_size)

    def ai_set_sample_rate(self, sample_rate: float) -> None:
        self.dwf.FDwfAnalogInFrequencySet(self.device_handle, c_double(sample_rate))

    def ai_set_buffer_size(self, buffer_size: int) -> None:
        self.dwf.FDwfAnalogInBufferSizeSet(self.device_handle, c_int(buffer_size))

    def ai_set_channel_enabled(self, channel: int, enabled: bool) -> None:
        self.dwf.FDwfAnalogInChannelEnableSet(self.device_handle, c_int(channel), c_int(enabled))

    def ai_set_channels_enabled(self, channels: list[int], enabled: bool) -> None:
        self._ai_validate_channels(channels)
        for channel in channels:
            self.ai_set_channel_enabled(channel, enabled)

    def ai_enable_channel(self, channel: int) -> None:
        self.ai_set_channel_enabled(channel, True)

    def ai_disable_channel(self, channel: int) -> None:
        self.ai_set_channel_enabled(channel, False)

    def ai_enable_channels(self, channels: list[int]) -> None:
        self.ai_set_channels_enabled(channels, True)

    def ai_disable_channels(self, channels: list[int]) -> None:
        self.ai_set_channels_enabled(channels, False)

    def ai_set_record_length(self, length: float) -> None:
        self.dwf.FDwfAnalogInRecordLengthSet(self.device_handle, c_double(length))

    def ai_set_range(self, channel: int, volts: float = 5) -> None:
        self.dwf.FDwfAnalogInChannelRangeSet(self.device_handle, c_int(channel), c_double(volts))

    def ai_set_ranges(self, channels: list[int], range: float = 5) -> None:
        try:
            self._ai_validate_channels(channels)
            for channel in channels:
                self.ai_set_range(channel, range)
        except DwfException as e:
            raise e

    # # ---------- Range ----------
    # def set_ranges(self, channels: list[int], ranges: list[float]) -> None:
    #     # Ensure the number of channels matches the number of offsets states
    #     if len(channels) != len(ranges):
    #         msg = f"The specified number of channels ({len(channels)}) must match the specified number of ranges ({len(ranges)})"
    #         raise DwfException(AnalogOutError.INTPUT_LENGTH_MISMATCH.value, msg, msg)

    #     for i in range(0, len(channels)):
    #         self.dwf.FDwfAnalogInChannelRangeSet(self.device_handle, c_int(channels[i]), c_double(ranges[i]))

    # def set_range(self, channel: int, range: float) -> None:
    #     return self.set_ranges([channel], [range])

    # def set_range_all_channels(self, range: float) -> None:
    #     return self.set_range(-1, range)

    def ai_apply_config(self, reset_trigger: bool = True, start_acquisition: bool = False) -> None:
        self.dwf.FDwfAnalogInConfigure(self.device_handle, c_int(reset_trigger), c_int(start_acquisition))
        self._reset_ai_internal_counters()

    def ai_start(self, reset_trigger: bool = True) -> None:
        self.dwf.FDwfAnalogInConfigure(self.device_handle, c_int(reset_trigger), c_int(1))
        self._reset_ai_internal_counters()

    def ai_record(self, channels: list[int], sample_rate: int, num_samples: float = -1, range: int = 5):
        try:
            self.ai_enable_channels(channels)
            self.ai_set_ranges(channels, range)
            self.ai_set_acquisition_mode(AiAcquisitionMode.Record)
            self.ai_set_sample_rate(sample_rate)
            self.ai_set_record_length(-1 if num_samples < 0 else sample_rate / num_samples)
            self.ai_start()
        except DwfException as e:
            raise e

    def ai_set_acquisition_mode(self, mode: AiAcquisitionMode) -> None:
        self.dwf.FDwfAnalogInAcquisitionModeSet(self.device_handle, c_int(mode.value))
        self._ai_mode = mode

    def ai_get_state(self) -> InstrumentState:
        status_buffer = c_byte()
        self.dwf.FDwfAnalogInStatus(self.device_handle, c_int(1), byref(status_buffer))
        return InstrumentState(status_buffer.value)

    def ai_get_record_status(self) -> tuple[int, int, int]:
        available_buffer = c_int()
        lost_buffer = c_int()
        corrupted_buffer = c_int()
        self.dwf.FDwfAnalogInStatusRecord(
            self.device_handle, byref(available_buffer), byref(lost_buffer), byref(corrupted_buffer)
        )
        return (available_buffer.value, lost_buffer.value, corrupted_buffer.value)

    def ai_read_sample_buffer(self, channel: int, num_samples: int) -> list[float]:
        data_buffer = (c_double * num_samples)()
        self.dwf.FDwfAnalogInStatusData(self.device_handle, c_int(channel), byref(data_buffer), num_samples)
        dblPtr = cast(data_buffer, POINTER(c_double))
        floatList = [dblPtr[i] for i in range(num_samples)]
        return floatList

    def ai_read_samples(self, channels: list[int]) -> tuple[list[list[float]], int, int]:
        try:
            # Initialize data container with correct dimensions
            data: list[list[float]] = self.ai_get_data_container(channels)

            if self._ai_mode == AiAcquisitionMode.Record:
                ai_state = self.ai_get_state()

                if self._ai_sample_count == 0 and (
                    ai_state in [InstrumentState.Config, InstrumentState.Prefill, InstrumentState.Armed]
                ):
                    # Acquisition has not yet started
                    return (data, 0, 0)

                samples_available, samples_lost, samples_corrupted = self.ai_get_record_status()
                self._ai_lost_count += samples_lost
                self._ai_corrupted_count += samples_corrupted

                if samples_available == 0:
                    return (data, self._ai_lost_count, self._ai_corrupted_count)

                for channel_index in range(0, len(channels)):
                    samples = self.ai_read_sample_buffer(channels[channel_index], samples_available)
                    data[channel_index] += samples

                return (data, self._ai_lost_count, self._ai_corrupted_count)

            else:
                raise DwfException(message=f"The selected AI Mode ({self._ai_mode}) is not yet implemented")
        except DwfException as e:
            raise e

    def get_device_info_str(self) -> str:
        return (
            "Type:".ljust(16)
            + str(self.device_type.to_str()).ljust(64)
            + "\r\n"
            + "Name:".ljust(16)
            + str(self.name).ljust(64)
            + "\r\n"
            + "Serail number:".ljust(16)
            + str(self.serial_number).ljust(64)
            + "\r\n"
            + "Revision:".ljust(16)
            + str(self.revision).ljust(64)
        )

    def ai_get_data_container(self, channels: list[int]) -> list[list[float]]:
        data = []
        for channel in channels:
            data.append([])
        return data

    def _ai_validate_channels(self, channels: list[int]) -> None:
        # Check if specified AI channels are valid
        for channel in channels:
            if channel not in range(0, self.ai_count):
                raise DwfException(
                    message=f"The specified AI channel ({channel}) does not exist on the selected device."
                )

    def _get_analog_input_count(self) -> int:
        retval = c_int()
        self.dwf.FDwfAnalogInChannelCount(self.device_handle, byref(retval))
        return retval.value

    def _get_analog_output_count(self) -> int:
        retval = c_int()
        self.dwf.FDwfAnalogOutCount(self.device_handle, byref(retval))
        return retval.value

    def _reset_ai_internal_counters(self) -> None:
        self._ai_sample_count = 0
        self._ai_lost_count = 0
        self._ai_corrupted_count = 0
