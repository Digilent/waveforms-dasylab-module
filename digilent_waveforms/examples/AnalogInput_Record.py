# Update include path for local import
import sys
import os
import time

sys.path.insert(0, f"{os.getcwd()}")

from digilent_waveforms import Manager, DwfException

ai_channels = [0, 1]
samples_to_acquire = 5000

try:
    # Initialize the Digilent WaveForms Manager
    wf_manager = Manager()

    # Open first WaveForms device
    wf_device = wf_manager.open_first_device()
    print(f"Using {wf_device.name} {wf_device.serial_number}")

    # Start sampling AI channels
    wf_device.ai_record(channels=ai_channels, sample_rate=1000, range=10)

    # Read AI data in chunks until specified number of samples has been acquired (sleep between reads)
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
    with open("output.csv", "w") as csv_file:
        # Iterate over samples
        for sample_index in range(0, len(ai_data[0])):
            # Write row (n-channels)
            num_channels = len(ai_data)
            for chanel_index in range(0, num_channels):
                csv_file.write("%s" % ai_data[chanel_index][sample_index])
                if chanel_index < num_channels - 1:
                    csv_file.write(",")
            csv_file.write("\n")

except DwfException as e:
    print(e.message)
    print(e.error)
