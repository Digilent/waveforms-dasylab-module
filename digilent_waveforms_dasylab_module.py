import Ly  # type: ignore
from digilent_waveforms import DwfException
from typing import Union
import lys  # type: ignore
from enum import Enum
import logging

from digilent_waveforms_dasylab._version import __version__
from ctypes import *  # type: ignore
from digilent_waveforms import Manager, Device, DeviceInfo
from digilent_waveforms_dasylab.components.Logger import Logger

# Config logging level
DEBUG = True
Logger.setLevel(logging.DEBUG)

# If debugging is enabled, import the debugpy library and start listening for the debugger (VScode is recommended)
if DEBUG:
    import debugpy

    debugpy.listen(5678, in_process_debug_adapter=True)

module_name = "AI Rec"


class SettingName(Enum):
    SelectedDevice = "Device"
    SampleRate = "Sample rate"
    Range = "Input range"


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


class info(object):
    """
    Object to store peristent data (i.e. saved as part of the DASYLab worksheet file)
    """

    def __init__(self):
        self.selected_device_serial_number: str = ""
        # NOTE: Remove Sample Rate self.sample_rate: float = 1000

        self.range_names: list[str] = []
        self.range_values: list[float] = []
        self.selected_range_index: int = 0


class pvar(object):
    """
    Object to store temporary variables (not persisted to DASYLab worksheet file)
    """

    def __init__(self):
        Logger.debug("pvar.__init__()")
        self.m_outputs_done: list[int] = [0] * 16  # Initialize for up to 16 outputs

        self.wf_manager: Manager

        self.device_manager: DeviceManager
        self.selected_device_serial_number: str = ""

        self.devices_info: list[DeviceInfo] = []

        self.wf_device: Device = None
        self.num_channels: int
        # NOTE: Remove Sample Rate self.sample_rate_min: float  # In S/s
        # NOTE: Remove Sample Rate self.sample_rate_max: float  # In S/s
        self.range_min: float
        self.range_max: float
        self.range_steps: float

        self.ai_data_buffer: list[list[float]]
        # self.logger: logging.Logger

        import math

        self.math = math


class pscript(lys.mclass):
    def __init__(self, magic):
        Logger.debug("pscript.__init__()")
        self.info = info()
        self.pvar = pvar()

        # Print this package's version number
        print(f"Digilent WaveForms DASYLab Module version {__version__}")

        # Initialize the Digilent WaveForms Manager
        self.pvar.wf_manager = Manager()
        self.pvar.device_manager = DeviceManager(self.pvar.wf_manager)

        # Print WaveForms python module and WaveForms SDK version information
        print(f"Digilent WaveForms Python Module version {self.pvar.wf_manager.module_version}")
        print(f"Digilent WaveForms SDK version {self.pvar.wf_manager.get_waveforms_version()}")

    def Create(self):
        """
        Called when the module is added to the worksheet.
        Specify the number of inputs and outputs and the channel assignment.
        """
        Logger.debug("Create()")
        return True

    def Delete(self):
        """
        Called when the module is removed from the worksheet.
        Perform clean up operations such as closing files or disconnecting hardware.
        """
        pass

    def DlgInit(self, dlg):
        """
        Called when the module dialog is loaded
        Handle module dialog box initialization
        """
        Logger.debug("DlgInit()")

        # Set dialog title
        dlg.title = "Digilent - Analog Input Record"

        # Setup dialog parameters
        dm = lys.DialogManager(self, dlg)
        dm.SelectModulePage()

        # Variables for dialog props
        selected_device_name = "---"
        selected_device_range = "---"

        # If the worksheet is running, no need to enumerate devices, just display the active device params
        worksheet_is_running = False
        if self.pvar.wf_device:
            Logger.debug("Worksheet is running - will not enumerate devices")
            worksheet_is_running = True
            selected_device_name = self.pvar.device_manager.get_device_name_by_sn(
                self.pvar.selected_device_serial_number
            )
            selected_device_range = self.info.range_names[self.info.selected_range_index]            

        # No wf_device means no device handle is open.  Assume this means the worksheet is NOT running
        else:
            # TODO: Determine best action.  First device may be busy, but that may be better than none selected
            # NOTE: If a device has been saved in the worksheet (ie in info) it has already been loaded into pvar in the load() function
            # If no device has been selected, default to first device  
               # NOTE: Probably not a good idea to do this since the device may be in use.  either handle that case or just make the user select the device manually
            if not self.pvar.selected_device_serial_number:
                Logger.debug("No device selected - defaulting to first device")
                self.pvar.device_manager.enumerate_devices()
                self.pvar.selected_device_serial_number = self.pvar.device_manager.serial_numbers[0]
                

            # Update device parameter options
            if self.pvar.selected_device_serial_number:
                try:
                    Logger.debug(f"Using device ({self.pvar.selected_device_serial_number})")
                    self.refresh_device_parameter_options()
                    selected_device_name = self.pvar.device_manager.get_device_name_by_sn(
                        self.pvar.selected_device_serial_number
                    )
                    selected_device_range = self.info.range_names[self.info.selected_range_index]
                except Exception as e:
                    Logger.warn(e)

            else:
                # TODO: handle case when no devices are present
                pass

        # Device
        dlg.AppendEnum(
            SettingName.SelectedDevice.value,
            "\n".join(self.pvar.device_manager.get_all_device_names()),
            selected_device_name,
            "Choose Digilent WaveForms device.",
        )
       
        # Range
        # Logger.debug(f"self.info.range_names = {self.info.range_names}")
        dlg.AppendEnum(
            SettingName.Range.value,
            "\n".join(self.info.range_names),
            selected_device_range,
            "Analog input range in volts.",
        )

        # If worksheet is running disable all properties
        if worksheet_is_running:
            dlg.EnableAll(False)

    def DlgOk(self, dlg):
        """
        Handle module dialog OK clicked
          - Save module settings values
        """
        dom = lys.DialogOkManager(dlg)
        dom.SelectModulePage()

        # Save selected device
        # selected_device_name = dom.GetValue(SettingName.SelectedDevice.value)
        # self.info.selected_device_serial_number = self.pvar.device_manager.get_device_sn_by_name(selected_device_name)
        self.info.selected_device_serial_number = self.pvar.selected_device_serial_number
        Logger.debug(f"Saved selected device serial number ({self.info.selected_device_serial_number})")

        # Save selected sample rate
        # NOTE: Remove Sample Rate self.info.sample_rate = float(dom.GetValue(SettingName.SampleRate.value))

        # Save selected range
        selected_range_name = dom.GetValue(SettingName.Range.value)
        if selected_range_name:
            selected_range_index = self.info.range_names.index(selected_range_name)
            self.info.selected_range_index = selected_range_index
            Logger.debug(f"Range [{selected_range_index}] selected = {selected_range_name}")

        dom.SelectChannelPage()

        # Configure Inputs and Outputs
        # (Covers moduls which have only outputs and at least one of them.
        # You need to adjust this section if you have chosen another relation
        # setting. You can find more information how to do this in the help)
        Logger.debug(f"self.DlgNumChannels : {self.DlgNumChannels }")
        self.SetConnectors(0, self.DlgNumChannels)

    def DlgCancel(self, dlg):
        # (oo)
        # Cancel button clicked.
        # Click on the help button to get more information.
        pass

    def DlgEvent(self, dlg, label, value):
        Logger.debug(f"DlgEvent({label}, {value})")

        if label == SettingName.SelectedDevice.value:
            self.selected_device_change_handler(dlg)

        # NOTE: Remove Sample Rate if label == SettingName.SampleRate.value:
        # NOTE: Remove Sample Rate     self.coerce_sample_rate(dlg)

        if label == SettingName.Range.value:
            self.update_range_options(dlg)

    def Save(self):
        # (oo)
        # Prepare data before worksheet will be saved (if needed)
        # Click on the help button to get more information.
        pass

    def Load(self):
        """
        Called once when worksheet is loaded.  Use to validate / init saved variables
        """
        print("load()")
        self.load_saved_selected_device()
        self.refresh_device_parameter_options()

    def Start(self):
        """
        One time setup on start of measurement
        """
        Logger.debug("Start()")
        try:
            if not self.pvar.selected_device_serial_number:
                Logger.warn(f"Module {module_name} - No device selected.  Aborting.")
                return False  # Return false to abort worksheet execution

            device = self.pvar.device_manager.open_device_by_serial_number(self.pvar.selected_device_serial_number)

            if not device:
                Logger.warn(
                    f"Module {module_name} - The selected device with serial number ({self.pvar.selected_device_serial_number}) is not available.  Aborting."
                )
                return False  # Return false to abort worksheet execution

            self.pvar.wf_device = device

            # Configure and start analog input record
            range_index = self.info.selected_range_index
            range_value = self.info.range_values[range_index]
            Logger.debug(f"self.NumOutChannel = {self.NumOutChannel }")
            enabled_channels = list(range(0, self.NumOutChannel))

            Logger.debug(f"Range index [{range_index}] = {range_value}")
            Logger.debug(f"Enabled channels {enabled_channels}")

            sample_rate = 1 / Ly.GetTimeBaseSampleDistance(2)

            self.pvar.wf_device.AnalogInput.record(enabled_channels, sample_rate, range=range_value)

            self.pvar.m_outputs_done = [0] * 16  # Initialize for up to 16 outputs
            self.pvar.ai_data_buffer = self.pvar.wf_device.AnalogInput._get_data_container(enabled_channels)

        except DwfException as e:
            Logger.error(e)
            return False  # Return false to abort worksheet execution

        return True

    def Stop(self):
        # One time clean up at end of measurement
        try:
            self.pvar.wf_manager.close_all_devices()
            self.pvar.wf_device = None
        except Exception as e:
            print(e)
            Ly.StopExperiment()

    def SetupFifo(self, channel):
        # (oo)
        # Setup flags, types and max. block size of a channel (if needed)
        # Click on the help button to get more information.
        # Comment out the lines below if you want to overwrite the settings
        # of the channel property dialog.

        self.SetSampleDistance(channel, Ly.GetTimeBaseSampleDistance(2))
        self.SetMaxBlockSize(channel, Ly.GetTimeBaseBlockSize(2))
        self.SetChannelType(channel, Ly.CT_NORMAL)
        self.SetChannelFlags(channel, Ly.CF_NORMAL)
        return True

    def ProcessValue(self, v, c):
        # (oo)
        # Process single value
        # Click on the help button to get more information.

        start_time, sample_index, delta_t = v
        pass

    def ProcessData(self):
        """
        Generate and output data blocks
        """
        # Process data blocks
        # Click on the help button to get more information.

        # Process the channels
        samples_per_block = Ly.GetTimeBaseBlockSize(2)
        deltaT = Ly.GetTimeBaseSampleDistance(2)
        block_length_sec = samples_per_block * deltaT

        # Read data and append to software sample buffer
        enabled_channels = list(range(0, self.NumOutChannel))
        try:
            ai_read_data, lost_count, corrupt_count = self.pvar.wf_device.AnalogInput.read_available_samples(
                enabled_channels
            )

            # Logger.debug(f"enabled_channels : {enabled_channels}")
            # Logger.debug(f"ai_read_data : [{len(ai_read_data[0])}][{len(ai_read_data[1])}]")
            # Logger.debug(f"self.pvar.ai_data_buffer : [{len(self.pvar.ai_data_buffer[0])}][{len(self.pvar.ai_data_buffer[1])}]")
            # self.write_csv(self.pvar.ai_data_buffer)

            for channel_index in enabled_channels:
                next_time = self.pvar.m_outputs_done[channel_index] * block_length_sec
                self.pvar.ai_data_buffer[channel_index] += ai_read_data[channel_index]

                # Blocks for all channels should populate at same rate since sample rate is not per channel
                if len(self.pvar.ai_data_buffer[channel_index]) >= samples_per_block:
                    OutBuff = self.GetOutputBlock(channel_index)
                    for sample_index in range(samples_per_block):
                        OutBuff[sample_index] = self.pvar.ai_data_buffer[channel_index][sample_index]
                    OutBuff.StartTime = next_time
                    OutBuff.SampleDistance = deltaT
                    OutBuff.BlockSize = samples_per_block
                    OutBuff.Release()

                    # Increment block output count and removed output data from sample buffer
                    self.pvar.m_outputs_done[channel_index] += 1
                    self.pvar.ai_data_buffer[channel_index] = self.pvar.ai_data_buffer[channel_index][
                        samples_per_block:
                    ]

                    # Logger.debug(f"Blocks output: {self.pvar.m_outputs_done}")

        except Exception as e:
            Logger.error(e)

        return True

    def selected_device_change_handler(self, dlg) -> None:
        self.pvar.device_manager.enumerate_devices()

        selected_device_name = dlg.GetProperty(SettingName.SelectedDevice.value)
        selected_device_sn = self.pvar.device_manager.get_device_sn_by_name(selected_device_name)
        self.pvar.selected_device_serial_number = selected_device_sn

        self.refresh_device_parameter_options()

        # Validate user selections
        # NOTE: Remove Sample Rate self.coerce_sample_rate(dlg)
        self.update_range_options(dlg)

    # NOTE: Remove Sample Rate
    # def coerce_sample_rate(self, dlg) -> None:
    #     Logger.debug(f"Supported sample rate ({self.pvar.sample_rate_min})-({self.pvar.sample_rate_max}) S/s")
    #     selected_sample_rate = dlg.GetProperty(SettingName.SampleRate.value)
    #     if selected_sample_rate < self.pvar.sample_rate_min:
    #         dlg.SetProperty(SettingName.SampleRate.value, self.pvar.sample_rate_min)
    #         print(
    #             f"Analog input sample rate increased from {selected_sample_rate} to min rate of {self.pvar.sample_rate_min} S/s"
    #         )

    #     if selected_sample_rate > self.pvar.sample_rate_max:
    #         dlg.SetProperty(SettingName.SampleRate.value, self.pvar.sample_rate_max)
    #         print(
    #             f"Analog input sample rate reduced from {selected_sample_rate} to max rate of {self.pvar.sample_rate_max} S/s"
    #         )

    def update_range_options(self, dlg) -> None:
        selected_range = dlg.GetProperty(SettingName.Range.value)

        if not selected_range:
            selected_range = self.info.range_names[0]

        dlg.SetProperty(SettingName.Range.value, selected_range)

    def get_device_index_by_selection_name(self, selection_name: str) -> int:
        for i in range(len(self.pvar.devices_info)):
            if self.pvar.devices_info[i].serial_number in selection_name:
                return i
        return -1

    # def open_wf_device(self) -> Device:
    #     return self.pvar.wf_manager.open_device()

    def wait_for_debug_client(self) -> None:
        if DEBUG:
            print("Waiting for debugger to connect")
            debugpy.wait_for_client()

    def load_saved_selected_device(self) -> None:
        # Load selected device serail number from info into pvar
        self.pvar.selected_device_serial_number = self.info.selected_device_serial_number

        # Refresh Digilent device list
        self.pvar.device_manager.enumerate_devices()

        # Warn user if no device has been selected
        if not self.pvar.selected_device_serial_number:
            Logger.warn(f"Module {module_name} - No device selected.")  # TODO: Print help link

        # Warn user if selected device is not available
        try:
            self.pvar.device_manager.get_device_name_by_sn(self.pvar.selected_device_serial_number)
        except Exception as e:
            Logger.warn(
                f"Module {module_name} - The selected device with serial number ({self.pvar.selected_device_serial_number}) is not available."
            )

        Logger.debug(f"Using device with serial number ({self.pvar.selected_device_serial_number})")

    def close_selected_device(self) -> None:
        self.pvar.wf_manager.close_device(self.pvar.wf_device)

    def refresh_device_parameter_options(self) -> None:
        try:
            Logger.debug("refresh_device_parameter_options()")
            device = self.pvar.device_manager.open_device_by_serial_number(self.pvar.selected_device_serial_number)

            if not device:
                error = self.pvar.wf_manager.get_error()
                Logger.error(error)
                raise Exception(f"Failed to open device - {error}")

            # Update device parameters for user selection validation
            self.pvar.num_channels = device.AnalogInput.channel_count
            self.DlgMaxChannels = self.pvar.num_channels

            # NOTE: Remove Sample Rate rate_min, rate_max = device.AnalogInput.get_sample_rate_min_max()
            # NOTE: Remove Sample Rate self.pvar.sample_rate_min = rate_min
            # NOTE: Remove Sample Rate self.pvar.sample_rate_max = rate_max

            self.info.range_values = device.AnalogInput.get_range_steps()

            range_names: list[str] = []
            for p2p_range in self.info.range_values:
                full_range = ("%f" % (p2p_range / 2)).rstrip("0").rstrip(".")
                Logger.debug(full_range)
                range_names.append(f"±{full_range}")

            # Logger.debug(f"self.info.range_names = {self.info.range_names}")
            self.info.range_names = range_names

        except Exception as e:
            Logger.error(e)

        finally:
            self.pvar.wf_manager.close_all_devices()
            self.pvar.wf_device = None
