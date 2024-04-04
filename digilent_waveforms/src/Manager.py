from ctypes import *  # type: ignore
from digilent_waveforms.src.Device import Device
from digilent_waveforms.src.constants.dwfconstants import *
from digilent_waveforms.src.components.DwfException import DwfException


class Manager:
    def __init__(self):
        self.dwf = cdll.dwf

    def get_waveforms_version(self) -> str:
        version = create_string_buffer(16)
        self.dwf.FDwfGetVersion(version)
        return str(version.value)

    def open_device(self, device_index) -> Device:
        device_handle = c_int()
        self.dwf.FDwfDeviceOpen(c_int(device_index), byref(device_handle))

        # Check if device opened successfully
        if device_handle.value == hdwfNone.value:
            szerr = create_string_buffer(512)
            self.dwf.FDwfGetLastErrorMsg(szerr)
            raise DwfException(error=f"Failed to open device at index ({device_index}", message=szerr.value)

        return Device(device_handle)

    def open_first_device(self) -> Device:
        return self.open_device(-1)

    def close_all_devices(self) -> None:
        self.dwf.FDwfDeviceCloseAll()
