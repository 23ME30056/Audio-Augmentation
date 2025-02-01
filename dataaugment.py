import numpy as np
from scipy.io import wavfile
from scipy.signal import resample

def read_wav(file_path):
    
    sample_rate, data = wavfile.read(file_path)
    
    # If stereo, converted to mono
    if len(data.shape) == 2:
        data = np.mean(data, axis=1)
    
    return sample_rate, data

def write_wav(file_path, sample_rate, data):
    
    wavfile.write(file_path, sample_rate, data.astype(np.int16))

def add_noise(original, noise, noise_factor=0.5):

    min_length = min(len(original), len(noise))
    original = original[:min_length]
    noise = noise[:min_length]

 
    original = original / np.max(np.abs(original))
    noise = noise / np.max(np.abs(noise))
    
    noisy_signal = original + noise_factor * noise

   
    noisy_signal = noisy_signal / np.max(np.abs(noisy_signal)) * 32767
    noisy_signal = np.clip(noisy_signal, -32767, 32767)
    
    return noisy_signal

def resample_audio(data, original_rate, target_rate):
  
    num_samples = int(len(data) * target_rate / original_rate)
    resampled_data = resample(data, num_samples)
    return resampled_data

# File paths
original_wav_path = 'DOORBELL.wav'
noise_wav_path = 'noise1.wav'
output_wav_path = 'final_noisy.wav'


sample_rate_original, original_data = read_wav(original_wav_path)
sample_rate_noise, noise_data = read_wav(noise_wav_path)

if sample_rate_original != sample_rate_noise:
    print(f"Resampling noise from {sample_rate_noise} Hz to {sample_rate_original} Hz")
    noise_data = resample_audio(noise_data, sample_rate_noise, sample_rate_original)


noisy_data = add_noise(original_data, noise_data, noise_factor=0.5)


write_wav(output_wav_path, sample_rate_original, noisy_data)

print(f"Noisy file saved at: {output_wav_path}")
