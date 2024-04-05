import Ly  # type: ignore
from digilent_waveforms import DwfException
import lys  # type: ignore
import sys

from digilent_waveforms_dasylab._version import __version__
from ctypes import *  # type: ignore
from digilent_waveforms import Manager, Device


class info(object):
    def __init__(self):
        # (oo)
        # Variables for settings
        # Click on the help button to get more information.
        # Example variables
        self.m_a = 1.0
        self.c_b = [
            0.1,
            1.1,
            2.1,
            3.1,
            4.1,
            5.1,
            6.1,
            7.1,
            8.1,
            9.1,
            10.1,
            11.1,
            12.1,
            13.1,
            14.1,
            15.1,
        ]
        self.c_c = [0.0 for n in range(16)]


class pvar(object):
    def __init__(self):
        # (oo)
        # Working variables
        # Click on the help button to get more information.
        # Example variables
        self.m_outputs_done = 0
        self.m_m = 0.0
        self.c_n = [1.0 for n in range(16)]

        self.wf_manager: Manager
        self.wf_device: Device

        import math

        self.math = math


class pscript(lys.mclass):
    def __init__(self, magic):
        self.info = info()
        self.pvar = pvar()

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
        # (oo)
        # Initialization of settings dialog
        # Click on the help button to get more information.

        # Set dialog title
        dlg.title = "Script (Input Data)"
        # Determine the number of channels, current channel and
        # maximum number of channels
        # (Covers moduls which have only outputs and at least one of them.
        # You need to adjust this section if you have chosen another relation
        # setting. You can find more information how to do this in the help)
        self.DlgNumChannels = self.NumOutChannel
        self.DlgMaxChannels = Ly.MAX_CHANNELS
        # Setup dialog parameters
        dm = lys.DialogManager(self, dlg)
        dm.SelectModulePage()
        # dm.AppendFloat(
        #     "Param a", self.info.m_a, "Example: variable m_a in module scope"
        # )
        # dm.SelectChannelPage()
        # dm.AppendFloat(
        #     "Param b", self.info.c_b, "Example: variable c_b in channel scope"
        # )
        # dm.AppendFloat(
        #     "Param c", self.info.c_c, "Example: variable c_c in channel scope"
        # )

    def DlgOk(self, dlg):
        # (oo)
        # Get values of dialog parameters
        # Click on the help button to get more information.
        dom = lys.DialogOkManager(dlg)
        dom.SelectModulePage()
        # self.info.m_a = dom.GetValue("Param a")
        dom.SelectChannelPage()
        # self.info.c_b = dom.GetValue("Param b")
        # self.info.c_c = dom.GetValue("Param c")

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

    def Save(self):
        # (oo)
        # Prepare data before worksheet will be saved (if needed)
        # Click on the help button to get more information.
        pass

    def Load(self):
        # (oo)
        # Prepare data after worksheet has been loaded (if needed)
        # Click on the help button to get more information.
        pass

    def Start(self):
        """
        One time setup on start of measurement
        """

        print(sys.path)
        try:
            # Print this package's version number
            print(f"Digilent WaveForms DASYLab Module version {__version__}")

            # Initialize the Digilent WaveForms Manager
            self.pvar.wf_manager = Manager()

            # Print WaveForms python module and WaveForms SDK version information
            print(f"Digilent WaveForms Python Module version {self.pvar.wf_manager.module_version}")
            print(f"Digilent WaveForms SDK version {self.pvar.wf_manager.get_waveforms_version()}")

            # Open first WaveForms device
            self.pvar.wf_device = self.pvar.wf_manager.open_first_device()

            # Print device information
            print(self.pvar.wf_device.get_device_info_str())
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

        # print(f"sdist = {sdist}")
        print(f"self.pvar.m_outputs_done = {self.pvar.m_outputs_done}")
        # print(f"this_time = {this_time}  next_time = {next_time}")

        if this_time >= next_time:
            for channel in range(self.NumOutChannel):
                OutBuff = self.GetOutputBlock(channel)
                for i in range(bsize):
                    OutBuff[i] = self.ProcessValue((next_time, i, sdist), channel)
                OutBuff.StartTime = next_time
                OutBuff.SampleDistance = sdist
                OutBuff.BlockSize = bsize
                OutBuff.Release()
            self.pvar.m_outputs_done += 1

        return True
