import os
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample

def read_wav(file_path):
    # Read the file
    sample_rate, data = wavfile.read(file_path)
    
    # If stereo, convert to mono by averaging the two channels
    if len(data.shape) == 2:
        data = np.mean(data, axis=1)
    
    return sample_rate, data

def write_wav(file_path, sample_rate, data):
    # Ensure data is in int16 format
    wavfile.write(file_path, sample_rate, data.astype(np.int16))

def add_noise(original, noise, noise_factor=0.5):
    # Ensure the two signals are of the same length
    min_length = min(len(original), len(noise))
    original = original[:min_length]
    noise = noise[:min_length]

    # Normalize both signals
    original = original / np.max(np.abs(original))
    noise = noise / np.max(np.abs(noise))
    
    # Add noise to the original signal
    noisy_signal = original + noise_factor * noise

    # Normalize the noisy signal to 16-bit range and prevent clipping
    noisy_signal = noisy_signal / np.max(np.abs(noisy_signal)) * 32767
    noisy_signal = np.clip(noisy_signal, -32767, 32767)
    
    return noisy_signal

def resample_audio(data, original_rate, target_rate):
    # Resample the audio data to the target sample rate
    num_samples = int(len(data) * target_rate / original_rate)
    resampled_data = resample(data, num_samples)
    return resampled_data

def process_folder(input_folder, output_folder, noise_file, noise_factor=0.5):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Read the noise file once
    sample_rate_noise, noise_data = read_wav(noise_file)

    # Iterate over each class (subfolder)
    for class_name in os.listdir(input_folder):
        class_path = os.path.join(input_folder, class_name)
        
        # Skip if it's not a folder
        if not os.path.isdir(class_path):
            continue
        
        # Create the same class folder in the output directory
        output_class_path = os.path.join(output_folder, class_name)
        os.makedirs(output_class_path, exist_ok=True)
        
        # Iterate over each wav file in the class folder
        for filename in os.listdir(class_path):
            if filename.endswith(".wav"):
                file_path = os.path.join(class_path, filename)

                # Read the original file
                sample_rate_original, original_data = read_wav(file_path)

                # Resample noise if the sample rates don't match
                if sample_rate_original != sample_rate_noise:
                    print(f"Resampling noise from {sample_rate_noise} Hz to {sample_rate_original} Hz for file {filename}")
                    noise_data_resampled = resample_audio(noise_data, sample_rate_noise, sample_rate_original)
                else:
                    noise_data_resampled = noise_data

                # Add noise to the original signal
                noisy_data = add_noise(original_data, noise_data_resampled, noise_factor=noise_factor)

                # Write the noisy file with the same name to the output class folder
                output_file_path = os.path.join(output_class_path, filename)
                write_wav(output_file_path, sample_rate_original, noisy_data)
                print(f"Noisy file saved at: {output_file_path}")

# Folder paths
input_folder = 'sound classes'  # Folder containing subfolders with .wav files (each subfolder is a class)
output_folder = 'final classes'  # Folder where noisy .wav files will be saved
noise_wav_path = 'noise1.wav'  # Path to the noise file

# Process the folder
process_folder(input_folder, output_folder, noise_wav_path, noise_factor=0.5)