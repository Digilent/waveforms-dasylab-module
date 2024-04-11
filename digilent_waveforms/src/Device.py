from ctypes import *  # type: ignore

# Digilent WaveForms Imports
from digilent_waveforms.src.constants.dwfconstants import *
from digilent_waveforms.src.constants.dwf_types import DeviceType
from digilent_waveforms.src.constants.ai_types import AiAcquisitionMode
from digilent_waveforms.src.components.AnalogOut import AnalogOut
from digilent_waveforms.src.components.AnalogInput import AnalogIn


class Device:
    device_index: int = -1
    device_handle: c_int
    name: str = ""
    type: DeviceType
    revision: int = -1
    serial_number: str = ""

    # Subsystems
    AnalogOutput: AnalogOut
    AnalogInput: AnalogIn

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
        self.AnalogInput = AnalogIn(self.dwf, self.device_handle, self.ai_count)

        # Prevent config options from being applied at each call.  Instead apply config options only when FDwfAnalogInConfigure is called.
        self.dwf.FDwfDeviceAutoConfigureSet(self.device_handle, c_int(0))

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

    def _get_analog_input_count(self) -> int:
        retval = c_int()
        self.dwf.FDwfAnalogInChannelCount(self.device_handle, byref(retval))
        return retval.value

    def _get_analog_output_count(self) -> int:
        retval = c_int()
        self.dwf.FDwfAnalogOutCount(self.device_handle, byref(retval))
        return retval.value
