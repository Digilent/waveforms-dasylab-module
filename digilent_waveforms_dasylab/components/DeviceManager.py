from digilent_waveforms import Manager
from .Logger import Logger

class DeviceManager:

    def __init__(self, wf_manager: Manager):
        self.wf_manager = wf_manager
        self.names = []
        self.serial_numbers = []
        self.device_details = []
        self.enumerate_devices()

        Logger.debug(f"Device names: {self.names}")
        Logger.debug(f"serial_numbers: {self.serial_numbers}")
        # Logger.debug(f"device_details: {self.device_details}")

    def enumerate_devices(self) -> None:
        self.device_details = self.wf_manager.get_devices_info()

        self.names = []
        for device_info in self.device_details:
            self.names.append(f"{device_info.name} ({device_info.serial_number})")
            self.serial_numbers.append(device_info.serial_number)

    def get_all_device_names(self) -> list[str]:
        return self.names

    def get_all_device_serial_numbers(self) -> list[str]:
        return self.serial_numbers

    def get_device_name_by_sn(self, serial_number: str) -> str:
        try:
            index = self.get_index_by_sn(serial_number)
            return self.names[index]
        except Exception as e:
            raise e

    def get_device_sn_by_name(self, device_name: str) -> str:
        try:
            index = self.get_index_by_name(device_name)
            return self.serial_numbers[index]
        except Exception as e:
            raise e

    def get_index_by_sn(self, serial_number: str) -> int:
        try:
            index = self.serial_numbers.index(serial_number)
            return index
        except Exception as e:
            # If a device with the specified name does not exist, raise exception
            msg = f"A device with the specified serial number ({serial_number}) is not available"
            raise Exception(msg)

    def get_index_by_name(self, device_name: str) -> int:
        try:
            return self.names.index(device_name)
        except Exception as e:
            # If a device with the specified name does not exist, raise exception
            msg = f"A device with the specified name ({device_name}) is not available - {e}"
            raise Exception(msg)

    def open_device_by_serial_number(self, serial_number: str):
        try:
            # Close any existing device handles and re-enumerate device devices
            self.wf_manager.close_all_devices()            
            self.enumerate_devices()

            # Find device index by serial number
            index = self.get_index_by_sn(serial_number)

            # If a device with the specified serial number does not exist, bail
            if index <= -1:
                msg = f"A device with the specified serial number ({serial_number}) is not available"
                raise Exception(msg)

            # Open the device and return it
            device = self.wf_manager.open_device(index)
            return device
        except Exception as e:
            self.wf_manager.close_all_devices()         
            raise e
