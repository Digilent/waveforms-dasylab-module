import Ly  # type: ignore
from digilent_waveforms import DwfException
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


class info(object):
    """
    Object to store peristent data (i.e. saved as part of the DASYLab worksheet file)
    """

    selected_device: str = ""
    sample_rate: float = 1000
    selected_range: str = ""

    def __init__(self):
        pass


class pvar(object):
    """
    Object to store temporary variables (not persisted to DASYLab worksheet file)
    """

    def __init__(self):
        Logger.debug("pvar.__init__()")
        self.m_outputs_done = 0

        self.wf_manager: Manager
        self.devices_info: list[DeviceInfo] = []
        self.devices_selection_options: list[str] = []
        self.range_options: list[str] = []

        self.wf_device: Device
        self.sample_rate_min: float  # In S/s
        self.sample_rate_max: float  # In S/s
        self.range_min: float
        self.range_max: float
        self.range_steps: float

        self.ai_data_buffer: list[float]
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

        # Refresh device options list each time dialog is opened
        self.refresh_device_options()
        self.update_input_validation()

        # Device
        dlg.AppendEnum(
            SettingName.SelectedDevice.value,
            "\n".join(self.pvar.devices_selection_options),
            self.info.selected_device,
            "Choose Digilent WaveForms device.",
        )

        # Sample rate
        dm.AppendFloat(SettingName.SampleRate.value, self.info.sample_rate, "Samples per second")

        # Range
        dlg.AppendEnum(
            SettingName.Range.value,
            "\n".join(self.pvar.range_options),
            self.info.selected_range,
            "Analog input range in volts.",
        )

    def DlgOk(self, dlg):
        """
        Handle module dialog OK clicked
          - Save module settings values
        """
        dom = lys.DialogOkManager(dlg)
        dom.SelectModulePage()

        # Save module settings
        self.info.selected_device = dom.GetValue(SettingName.SelectedDevice.value)
        self.info.sample_rate = float(dom.GetValue(SettingName.SampleRate.value))
        self.info.selected_range = dom.GetValue(SettingName.Range.value)

        dom.SelectChannelPage()
        # Configure Inputs and Outputs
        # (Covers moduls which have only outputs and at least one of them.
        # You need to adjust this section if you have chosen another relation
        # setting. You can find more information how to do this in the help)
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

        if label == SettingName.SampleRate.value:
            self.coerce_sample_rate(dlg)

        if label == SettingName.Range.value:
            self.coerce_range(dlg)

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
        self.validate_selected_device()

    def Start(self):
        """
        One time setup on start of measurement
        """
        Logger.debug("Start()")
        try:
            if not self.info.selected_device:
                print(f"Module {module_name} - No device selected, aborting.")
                return False  # Return false to abort worksheet execution

            self.pvar.wf_device = self.open_selected_device()

            if not self.pvar.wf_device:
                print(f"Module {module_name} - The selected device ({self.info.selected_device}) is not available")
                return False  # Return false to abort worksheet execution

            # Configure analog inputs and enable channel 0
            self.pvar.wf_device.AnalogInput.record([0], sample_rate=self.info.sample_rate, range=10)

            self.pvar.m_outputs_done = 0
            self.pvar.ai_data_buffer = []

        except DwfException as e:
            print(e.message)
            print(e.error)
            return False  # Return false to abort worksheet execution

        return True

    def Stop(self):
        # One time clean up at end of measurement
        try:
            self.pvar.wf_manager.close_all_devices()
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

        # print(f"block_time = {block_time}")
        # print(f"v = {v}")
        # print(f"pvar = {pvar}")

        return self.pvar.math.sin(start_time + sample_index * delta_t)

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
        this_time = Ly.GetTimeBaseTime(2)
        next_time = self.pvar.m_outputs_done * block_length_sec

        # print(f"bsize = {bsize}    sdist = {sdist}   btime = {btime}")
        # print(f"self.pvar.m_outputs_done = {self.pvar.m_outputs_done}")
        # print(f"this_time = {this_time}  next_time = {next_time}")

        # Read data and append to software sample buffer
        try:
            ai_read_data, lost_count, corrupt_count = self.pvar.wf_device.AnalogInput.read_available_samples([0])
            self.pvar.ai_data_buffer += ai_read_data[0]

            if len(self.pvar.ai_data_buffer) >= samples_per_block:
                # Full block of data ready, output it

                # Build output buffer
                # buffer_num_samples = len(ai_read_data)
                # buffer_size_seconds = buffer_num_samples * deltaT
                # buffer_start_time = this_time - buffer_size_seconds

                OutBuff = self.GetOutputBlock(0)
                for i in range(samples_per_block):
                    OutBuff[i] = self.pvar.ai_data_buffer[i]
                OutBuff.StartTime = next_time
                OutBuff.SampleDistance = deltaT
                OutBuff.BlockSize = samples_per_block
                OutBuff.Release()

                # Increment block output count and removed output data from sample buffer
                self.pvar.m_outputs_done += 1
                self.pvar.ai_data_buffer = self.pvar.ai_data_buffer[samples_per_block:]

        except Exception as e:
            print(e)

        return True

    def selected_device_change_handler(self, dlg) -> None:
        self.update_input_validation()

        # Validate user selections
        self.coerce_sample_rate(dlg)
        self.coerce_range(dlg)

    def coerce_sample_rate(self, dlg) -> None:
        Logger.debug(f"Supported sample rate ({self.pvar.sample_rate_min})-({self.pvar.sample_rate_max}) S/s")
        selected_sample_rate = dlg.GetProperty(SettingName.SampleRate.value)
        if selected_sample_rate < self.pvar.sample_rate_min:
            dlg.SetProperty(SettingName.SampleRate.value, self.pvar.sample_rate_min)
            print(
                f"Analog input sample rate increased from {selected_sample_rate} to min rate of {self.pvar.sample_rate_min} S/s"
            )

        if selected_sample_rate > self.pvar.sample_rate_max:
            dlg.SetProperty(SettingName.SampleRate.value, self.pvar.sample_rate_max)
            print(
                f"Analog input sample rate reduced from {selected_sample_rate} to max rate of {self.pvar.sample_rate_max} S/s"
            )

    def coerce_range(self, dlg) -> None:
        selected_range = dlg.GetProperty(SettingName.Range.value)
        dlg.SetProperty(SettingName.Range.value, selected_range)

    def refresh_device_info(self) -> None:
        self.pvar.devices_info = self.pvar.wf_manager.get_devices_info()

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

    def refresh_device_options(self) -> None:
        self.refresh_device_info()
        self.pvar.devices_selection_options = []
        for device_info in self.pvar.devices_info:
            self.pvar.devices_selection_options.append(f"{device_info.name} ({device_info.serial_number})")

    def validate_selected_device(self) -> None:
        # Refresh Digilent device list
        self.refresh_device_options()

        # Warn user if no device has been selected
        print(f"self.info.selected_device={self.info.selected_device}")
        if not self.info.selected_device:
            Logger.warn(f"Module {module_name} - No Digilent WaveForms device selected.")  # TODO - Print help link

        # Use device saved in the worksheet.
        if self.info.selected_device in self.pvar.devices_selection_options:
            print(f"Module {module_name} - Using {self.info.selected_device}")

    def open_selected_device(self) -> Device:
        # Close any existing device handles and refresh the device list
        self.pvar.wf_manager.close_all_devices()
        self.refresh_device_info()

        # Find the selected device index and open a new device handle
        device_index = self.get_device_index_by_selection_name(self.info.selected_device)
        return self.pvar.wf_manager.open_device(device_index)

    def close_selected_device(self) -> None:
        self.pvar.wf_manager.close_device(self.pvar.wf_device)

    def update_input_validation(self) -> None:
        Logger.debug("update_input_options()")
        device = self.open_selected_device()

        # Update device parameters for user selection validation
        rate_min, rate_max = device.AnalogInput.get_sample_rate_min_max()
        self.pvar.sample_rate_min = rate_min
        self.pvar.sample_rate_max = rate_max

        range_min, range_max, range_steps = device.AnalogInput.get_range_min_max_num_steps()
        self.pvar.range_min = range_min
        self.pvar.range_max = range_max
        self.pvar.range_steps = range_steps
        range_float_list = device.AnalogInput.get_range_steps()

        range_options: list[str] = []
        for p2p_range in range_float_list:
            full_range = ("%f" % (p2p_range / 2)).rstrip("0").rstrip(".")
            Logger.debug(full_range)
            range_options.append(f"±{full_range}")
        self.pvar.range_options = range_options

        Logger.debug(f"self.pvar.range_options = {self.pvar.range_options}")

        self.pvar.wf_manager.close_device(device)
