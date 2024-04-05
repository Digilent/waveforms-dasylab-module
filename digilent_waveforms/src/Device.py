from ctypes import *  # type: ignore
import sys

from digilent_waveforms.src.Types import DeviceType


class Device:
    device_index: int = -1
    device_handle: c_int
    name: str = ""
    type: DeviceType
    revision: int = -1
    serial_number: str = ""

    analog_input_count = 0
    analog_output_count = 0

    def __init__(
        self, device_index: int, device_handle: c_int, name: str, type: DeviceType, revision: int, serial_number: str
    ):

        # Open dwf and store device handle
        if sys.platform.startswith("win"):
            self.dwf = cdll.dwf
        elif sys.platform.startswith("darwin"):
            self.dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
        else:
            self.dwf = cdll.LoadLibrary("libdwf.so")

        self.dwf = cdll.dwf
        self.device_index = device_index
        self.device_handle = device_handle
        self.name = name
        self.device_type = type
        self.revision = revision
        self.serial_number = serial_number

        # ---------- Enumerate device IO ----------
        self.analog_input_count = self._get_analog_input_count()
        self.analog_output_count = self._get_analog_output_count()

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
