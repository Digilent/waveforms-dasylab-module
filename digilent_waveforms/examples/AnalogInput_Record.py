# Update include path for local import
import sys
import os
from datetime import datetime

# Update path to enable relative import (for easier development)
sys.path.insert(0, f"{os.getcwd()}")
from digilent_waveforms import Manager, DwfException

# Example configuration
ai_channels = [0, 1]
sample_rate = 1000
samples_to_acquire = 5000
timeout = (samples_to_acquire / sample_rate) * 1.25 * 1000  # in ms

try:
    # Initialize the Digilent WaveForms Manager
    wf_manager = Manager()

    # Open first WaveForms device
    wf_device = wf_manager.open_first_device()
    print(f"Using {wf_device.name} {wf_device.serial_number}")

    # Start sampling AI channels
    wf_device.AnalogInput.record(channels=ai_channels, sample_rate=1000, range=10)

    # Read AI data until specified number of samples has been acquired or timeout occurres (blocking)
    ai_sample_data, lost_count, corrupt_count = wf_device.AnalogInput.read_samples_blocking(
        ai_channels,
        samples_to_acquire,
        timeout,
    )

    now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    filename = f"Sample Date {now}.csv"
    print(f"Sampling complete, writing to {filename}")

    # Close the device handle
    wf_manager.close_all_devices()

    # Save to .csv
    with open(filename, "w") as csv_file:
        # Iterate over samples
        for sample_index in range(0, len(ai_sample_data[0])):
            # Write row (n-channels)
            num_channels = len(ai_sample_data)
            for chanel_index in range(0, num_channels):
                csv_file.write("%s" % ai_sample_data[chanel_index][sample_index])
                if chanel_index < num_channels - 1:
                    csv_file.write(",")
            csv_file.write("\n")

except DwfException as e:
    print(e.message)
    print(e.error)
