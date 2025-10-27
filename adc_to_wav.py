# # Khumo Mukhari
# # Pre-processing script 
# # Turning Raw ADC values to stereo Wave file 
# +
import numpy as np
import wave
import struct
import time
from pathlib import Path


def read_adc_data(txt_filename):
    with open(txt_filename, 'r') as file:
        # Read the lines, convert to integers, and store them
        data = [int(line.strip()) for line in file]
    return data

def convert_to_wav(adc_data, wav_filename, vref=1.5, sample_rate=48000):
    # Separate the data into two channels
    channel1 = adc_data[0::2]  # Samples for channel 1
    channel2 = adc_data[1::2]  # Samples for channel 2

    # Interleave the two channels for stereo
    interleaved_data = np.empty((len(channel1) + len(channel2)), dtype=np.int32)
    interleaved_data[0::2] = channel1
    interleaved_data[1::2] = channel2

    # Convert the 24-bit data to bytes (3 bytes per sample)
    wav_data = bytearray()
    for sample in interleaved_data:
        # Ensure sample is in the 24-bit range, convert to 3 bytes
        sample &= 0xFFFFFF  # Mask to 24 bits
        wav_data.extend(struct.pack('<i', sample)[0:3])  # Only take the first 3 bytes

    # Write the WAV file
    with wave.open(wav_filename, 'wb') as wav_file:
        wav_file.setnchannels(2)   # Mono
        wav_file.setsampwidth(3)   # 24-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(wav_data)

    print(f"WAV file has been successfully written to {wav_filename}")

INPUT_ROOTS = [Path(r"cw_trials\driving_tests_1")]
vref = 1.5

for root in INPUT_ROOTS:
    if not root.exists():
        print(f"Folder not found: {root}")
        continue
    for txt_path in sorted(root.glob("*.txt")):
        txt_filename = str(txt_path)
        wav_filename = str(txt_path.with_suffix(".wav"))
        try:
            adc_data = read_adc_data(txt_filename)
        except ValueError:
            nums = []
            with open(txt_filename, "r") as f:
                for line in f:
                    s = line.strip()
                    if not s:
                        continue
                    for t in s.replace(",", " ").split():
                        if t.lstrip("+-").isdigit():
                            nums.append(int(t))
            adc_data = nums
        convert_to_wav(adc_data, wav_filename, vref)
        print(f"Converted {txt_filename} -> {wav_filename}")
        

print(f"Script completed in {time.perf_counter():.2f} seconds")