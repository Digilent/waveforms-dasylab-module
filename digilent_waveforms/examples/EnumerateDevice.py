# Update include path for local import
import sys
import os

sys.path.insert(0, f"{os.getcwd()}")

from digilent_waveforms import Manager, DwfException

try:
    # Initialize the Digilent WaveForms Manager
    wf_manager = Manager()

    # Print WaveForms python module and WaveForms SDK version information
    print(f"Digilent WaveForms Python Module version {wf_manager.module_version}")
    print(f"Digilent WaveForms SDK version {wf_manager.get_waveforms_version()}")

    # Open first WaveForms device
    wf_device = wf_manager.open_first_device()

    # Print device information
    print(wf_device.get_device_info_str())
except DwfException as e:
    print(e.message)
    print(e.error)
