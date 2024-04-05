# Update include path for local import
import sys
import os

sys.path.insert(0, f"{os.getcwd()}")

from digilent_waveforms import Manager, DwfException

try:
    # Initialize the Digilent WaveForms Manager
    wf_manager = Manager()

    # Close all devices
    wf_manager.close_all_devices()
except DwfException as e:
    print(e.message)
    print(e.error)
