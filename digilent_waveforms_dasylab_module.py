import Ly  # type: ignore
from digilent_waveforms import DwfException
import lys  # type: ignore
import sys
from enum import Enum
import logging


from digilent_waveforms_dasylab._version import __version__
from ctypes import *  # type: ignore
from digilent_waveforms import Manager, Device, DeviceInfo
from digilent_waveforms_dasylab.components.Logger import Logger

# Config logging level
Logger.setLevel(logging.DEBUG)


class SettingName(Enum):
    SelectedDevice = "Device"
    SampleRate = "Sample rate"


class info(object):
    selected_device: str = ""
    sample_rate = 1000

    def __init__(self):
        print("info()")


class pvar(object):
    def __init__(self):
        """
        Object to store temporary variables (not persisted to DASYLab worksheet file)
        """
        self.m_outputs_done = 0

        self.wf_manager: Manager
        self.devices_info: list[DeviceInfo] = []
        self.devices_selection_options: list[str] = []
        self.selected_device: str = ""

        self.wf_device: Device
        self.sample_rate_min: float  # In S/s
        self.sample_rate_max: float  # In S/s
        self.ai_data_buffer: list[float]
        # self.logger: logging.Logger

        import math

        self.math = math


class pscript(lys.mclass):
    def __init__(self, magic):
        self.info = info()
        self.pvar = pvar()

        # self.pvar.logger = self.init_logger()

        # Print this package's version number
        print(f"Digilent WaveForms DASYLab Module version {__version__}")

        # Initialize the Digilent WaveForms Manager
        self.pvar.wf_manager = Manager()

        # Print WaveForms python module and WaveForms SDK version information
        print(f"Digilent WaveForms Python Module version {self.pvar.wf_manager.module_version}")
        print(f"Digilent WaveForms SDK version {self.pvar.wf_manager.get_waveforms_version()}")

    def Create(self):
        # (oo)
        # Module initialization
        # Click on the help button to get more information.

        return True

    def Delete(self):
        # (oo)
        # Tidy up on deletion of the module (if needed)
        # Click on the help button to get more information.
        pass

    def DlgInit(self, dlg):
        """
        Handle module dialog box initialization
        """

        # Set dialog title
        dlg.title = "Digilent - Analog Input Record"

        # Setup dialog parameters
        dm = lys.DialogManager(self, dlg)
        dm.SelectModulePage()

        # Refresh device list
        self.refresh_device_info()
        self.pvar.devices_selection_options = []
        for device_info in self.pvar.devices_info:
            self.pvar.devices_selection_options.append(f"{device_info.name} ({device_info.serial_number})")

        # Load saved device or default to first available device
        if self.info.selected_device:
            self.pvar.selected_device = (
                self.info.selected_device if self.info.selected_device else self.pvar.devices_selection_options[0]
            )

        # Device
        dlg.AppendEnum(
            SettingName.SelectedDevice.value,
            "\n".join(self.pvar.devices_selection_options),
            self.pvar.selected_device,
            "Choose device.",
        )

        # TODO - Handle case where selected device no longer exists

        # # If no device has been selected default to first device in list
        # if self.pvar.selected_device == "":
        #     self.pvar.selected_device = self.pvar.devices_selection_options[0]

        # Sample rate
        dm.AppendInt(SettingName.SampleRate.value, self.info.sample_rate, "Samples per second")

    def DlgOk(self, dlg):
        """
        Handle module dialog OK clicked
          - Save module settings values
        """
        dom = lys.DialogOkManager(dlg)
        dom.SelectModulePage()

        # Save module settings
        self.info.selected_device = dom.GetValue(SettingName.SelectedDevice.value)
        self.info.sample_rate = dom.GetValue(SettingName.SampleRate.value)

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
        if label == SettingName.SelectedDevice.value:
            self.selected_device_change_handler()

        if label == SettingName.SampleRate.value:
            Logger.debug(f"{SettingName.SampleRate} value changed")
            self.coerce_sample_rate(dlg)

    def Save(self):
        # (oo)
        # Prepare data before worksheet will be saved (if needed)
        # Click on the help button to get more information.
        pass

    def Load(self):
        # (oo)
        # Prepare data after worksheet has been loaded (if needed)
        # Click on the help button to get more information.
        print("load()")
        print(self.info)
        pass

    def Start(self):
        """
        One time setup on start of measurement
        """

        print(sys.path)
        try:

            # Print device information
            print(self.pvar.wf_device.get_device_info_str())

            # Configure analog inputs and enable channel 0
            self.pvar.wf_device.AnalogInput.record([0], sample_rate=1000, range=10)

            self.pvar.m_outputs_done = 0
            self.pvar.ai_data_buffer = []

        except DwfException as e:
            print(e.message)
            print(e.error)
            Ly.StopExperiment()

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
        # (oo)
        # Process data blocks
        # Click on the help button to get more information.

        # Process the channels
        bsize = Ly.GetTimeBaseBlockSize(2)
        sdist = Ly.GetTimeBaseSampleDistance(2)
        btime = bsize * sdist
        this_time = Ly.GetTimeBaseTime(2)
        next_time = self.pvar.m_outputs_done * btime

        # print(f"bsize = {bsize}    sdist = {sdist}   btime = {btime}")
        # print(f"self.pvar.m_outputs_done = {self.pvar.m_outputs_done}")
        # print(f"this_time = {this_time}  next_time = {next_time}")

        # Read data and append to software sample buffer
        try:
            ai_read_data, lost_count, corrupt_count = self.pvar.wf_device.AnalogInput.read_available_samples([0])
            self.pvar.ai_data_buffer += ai_read_data[0]
            # print(f"Read {len(ai_sample_data[0])} samples.  lost_count={lost_count}  corrupt_count={corrupt_count}")
            # print(f"Read {len(ai_read_data[0])} samples.  AI buffer contains {len(self.pvar.ai_data_buffer )} samples")
            # print(f"{len(self.pvar.ai_data_buffer )}")

            if len(self.pvar.ai_data_buffer) >= bsize:
                # Full block of data ready, output it
                # print("Outputting buffer...")

                # Build output buffer
                buffer_num_samples = len(ai_read_data)
                buffer_size_seconds = buffer_num_samples * sdist
                buffer_start_time = this_time - buffer_size_seconds

                OutBuff = self.GetOutputBlock(0)
                for i in range(bsize):
                    OutBuff[i] = self.pvar.ai_data_buffer[i]
                OutBuff.StartTime = next_time
                OutBuff.SampleDistance = sdist
                OutBuff.BlockSize = bsize
                OutBuff.Release()

                # Increment block output count and removed output data from sample buffer
                self.pvar.m_outputs_done += 1
                self.pvar.ai_data_buffer = self.pvar.ai_data_buffer[bsize:]

            #     for channel in range(self.NumOutChannel):
            #         OutBuff = self.GetOutputBlock(channel)
            #         for i in range(bsize):
            #             OutBuff[i] = self.ProcessValue((next_time, i, sdist), channel)
            #         OutBuff.StartTime = next_time
            #         OutBuff.SampleDistance = sdist
            #         OutBuff.BlockSize = bsize
            #         OutBuff.Release()
            #     self.pvar.m_outputs_done += 1
        except Exception as e:
            print(e)

        return True

    def selected_device_change_handler(self) -> None:
        # Close any existing device handles and refresh the device list
        self.pvar.wf_manager.close_all_devices()
        self.refresh_device_info()

        # Find the selected device index and open a new device handle
        device_index = self.get_device_index_by_selection_name(self.pvar.selected_device)
        self.pvar.wf_device = self.pvar.wf_manager.open_device(device_index)

        # Update device parameters for user selection validation
        min, max = self.pvar.wf_device.AnalogInput.get_sample_rate_min_max()
        self.pvar.sample_rate_min = min
        self.pvar.sample_rate_max = max

        # Validate user selections
        # self.coerce_sample_rate(dialog)

    def coerce_sample_rate(self, dialog) -> None:
        Logger.debug("coerce_sample_rate()")
        dialog_manager = lys.DialogManager(self, dialog)
        dialog_manager.SelectModulePage()
        selected_sample_rate = dialog_manager.GetProperty(SettingName.SampleRate.value)

        if selected_sample_rate < self.pvar.sample_rate_min:
            dialog_manager.SetProperty(SettingName.SampleRate.value, self.pvar.sample_rate_min)
            print(
                f"Analog input sample rate increased from {selected_sample_rate} to min rate of {self.pvar.sample_rate_min} S/s"
            )

        if selected_sample_rate > self.pvar.sample_rate_max:
            dialog_manager.SetProperty(SettingName.SampleRate.value, self.pvar.sample_rate_max)
            print(
                f"Analog input sample rate reduced from {selected_sample_rate} to max rate of {self.pvar.sample_rate_max} S/s"
            )

    def refresh_device_info(self) -> None:
        self.pvar.devices_info = self.pvar.wf_manager.get_devices_info()

    def get_device_index_by_selection_name(self, selection_name: str) -> int:
        for i in range(len(self.pvar.devices_info)):
            if self.pvar.devices_info[i].serial_number in selection_name:
                return i
        return -1

    # def open_wf_device(self) -> Device:
    #     return self.pvar.wf_manager.open_device()
