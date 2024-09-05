# Update include path for local import
import sys
import os
import time

# Update path to enable relative import (for easier development)
sys.path.insert(0, f"{os.getcwd()}")
from digilent_waveforms import Manager, DwfException
from digilent_waveforms.src.constants import DeviceCloseBehavior, OutputFunction

# Example configuration
ai_channels = [0, 1]
ao_channels = [0, 1]
ao_voltages = [1.8, 3.3]
samples_to_acquire = 5000

try:
    # Initialize the Digilent WaveForms Manager
    wf_manager = Manager()

    # Set sto pbahavior to stop outputs when program execution stops
    wf_manager.set_device_close_behavior(DeviceCloseBehavior.StopRunning)

    # Open first WaveForms device
    wf_device = wf_manager.open_first_device()

    # Set Analog Outputs to constant DC value
    wf_device.AnalogOutput.enable_all_channels()
    wf_device.AnalogOutput.set_output_function_all_channels(OutputFunction.DC)
    wf_device.AnalogOutput.set_offets(ao_channels, ao_voltages)
    wf_device.AnalogOutput.start_all_channels()
    time.sleep(1)  # Give AO channels time to settle

    # Start Analog inputs
    wf_device.AnalogInput.record(channels=ai_channels, sample_rate=1000, range=10)

    # Read AI data until specified number of samples has been acquired or timeout occurres (blocking)
    ai_sample_data, lost_count, corrupt_count = wf_device.AnalogInput.read_samples_blocking(
        ai_channels, samples_to_acquire, 7500
    )

    # Close the device handle
    wf_manager.close_all_devices()

    # Save to .csv
    with open("output.csv", "w") as csv_file:
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
