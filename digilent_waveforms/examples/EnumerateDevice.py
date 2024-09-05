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

    # Print device AI information
    ai_min_sample_rate, ai_max_sample_rate = wf_device.AnalogInput.get_sample_rate_min_max()
    print(f"Analog Input Sample Rate: {ai_min_sample_rate} to {ai_max_sample_rate} S/s")

    ai_ranges = wf_device.AnalogInput.get_range_steps()
    print(f"Analog Input Ranges: {ai_ranges}")
except DwfException as e:
    print(e.message)
    print(e.error)
