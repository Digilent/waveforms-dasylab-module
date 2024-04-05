# Update include path for local import
import sys
import os
import time
import csv

sys.path.insert(0, f"{os.getcwd()}")

from digilent_waveforms import Manager, DwfException

ai_channels = [0, 1]
samples_to_acquire = 5000

try:
    # Initialize the Digilent WaveForms Manager
    wf_manager = Manager()

    # Open first WaveForms device
    wf_device = wf_manager.open_first_device()

    wf_device.ai_record(ai_channels, 1000)

    sample_count = 0
    ai_data = wf_device.ai_get_data_container(ai_channels)
    while sample_count < samples_to_acquire:
        data, lost_count, corrupt_count = wf_device.ai_read_samples(ai_channels)

        for channel_index in range(0, len(ai_channels)):
            ai_data[channel_index] += data[channel_index]

        sample_count += len(data[0])
        print(f"{sample_count} samples acquired")
        time.sleep(0.5)

    wf_manager.close_all_devices()

    # Save to .csv

    with open("record.csv", "w") as csv_file:
        for channel in ai_data:
            for sample in channel:
                csv_file.write("%s\n" % sample)

except DwfException as e:
    print(e.message)
    print(e.error)
