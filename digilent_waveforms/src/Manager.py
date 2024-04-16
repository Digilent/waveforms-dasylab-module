from digilent_waveforms._version import __version__
from ctypes import *  # type: ignore
from digilent_waveforms.src.Device import Device
from digilent_waveforms.src.constants.dwfconstants import *
from digilent_waveforms.src.components.DwfException import DwfException
from digilent_waveforms.src.constants.dwf_types import DeviceType, DeviceCloseBehavior, DeviceInfo
import sys


class Manager:
    module_version = "-.-.-"

    def __init__(self):
        # Open dwf shared object
        if sys.platform.startswith("win"):
            self.dwf = cdll.dwf
        elif sys.platform.startswith("darwin"):
            self.dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
        else:
            self.dwf = cdll.LoadLibrary("libdwf.so")

        self.module_version = __version__

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
            raise DwfException(error=f"Failed to open device at index ({device_index})", message=szerr.value)

        actual_device_index = 0 if device_index < 0 else device_index
        type, revision = self.get_device_type_and_revision(actual_device_index)
        return Device(
            self.dwf,
            device_index=actual_device_index,
            device_handle=device_handle,
            name=self.get_device_name(actual_device_index),
            type=DeviceType(type),
            revision=revision,
            serial_number=self.get_device_serial_number(actual_device_index),
        )

    def open_first_device(self) -> Device:
        return self.open_device(-1)

    def close_all_devices(self) -> None:
        self.dwf.FDwfDeviceCloseAll()

    # Refresh the device list and return the number of devices
    def refresh_device_list(self) -> int:
        retval = c_int()
        self.dwf.FDwfEnum(0, byref(retval))
        return retval.value

    def get_num_devices(self) -> int:
        return self.refresh_device_list()

    def get_device_name(self, device_index: int) -> str:
        name_buffer = create_string_buffer(64)
        self.dwf.FDwfEnumDeviceName(c_int(device_index), name_buffer)
        return name_buffer.value.decode("utf-8")

    def get_device_type_and_revision(self, device_index: int) -> tuple[int, int]:
        iDevId = c_int()
        iDevRev = c_int()
        self.dwf.FDwfEnumDeviceType(c_int(device_index), byref(iDevId), byref(iDevRev))
        return (iDevId.value, iDevRev.value)

    def get_device_serial_number(self, device_index: int) -> str:
        serial_number_buffer = create_string_buffer(16)
        self.dwf.FDwfEnumSN(device_index, serial_number_buffer)
        return serial_number_buffer.value.decode("utf-8")

    def set_device_close_behavior(self, option: DeviceCloseBehavior) -> None:
        self.dwf.FDwfParamSet(DwfParamOnClose, c_int(option.value))

    def get_device_list(self) -> list[str]:
        num_devices = self.get_num_devices()
        devices: list[str] = []
        for i in range(0, num_devices):
            name = self.get_device_name(i)
            serial_number = self.get_device_serial_number(i)
            devices.append(f"{name} ({serial_number})")
        return devices

    def get_devices_info(self) -> list[DeviceInfo]:
        num_devices = self.get_num_devices()
        devices: list[DeviceInfo] = []

        for i in range(0, num_devices):
            devices.append(self.get_device_info(i))
        return devices

    def get_device_info(self, index: int) -> DeviceInfo:
        type, revision = self.get_device_type_and_revision(index)
        name = self.get_device_name(index)
        serial_number = self.get_device_serial_number(index)

        return DeviceInfo(index, DeviceType(type), name, serial_number, revision)
