import sounddevice as sd
import librosa
import matplotlib.pyplot as plt
import numpy as np

# Load audio file
audio_path = "1685 Purcell , Trumpet Tune and Air.mp3"

# Load the audio file using librosa
y, sr = librosa.load(audio_path, sr=None)  # y is the audio time series, sr is the sampling rate

# Compute the Short-Time Fourier Transform (STFT)
stft = np.abs(librosa.stft(y))

# Compute Spectral Flux
flux = np.sqrt(np.sum(np.diff(stft, axis=1) ** 2, axis=0))

# Normalize for better visualization
flux = flux / np.max(flux)

# Plot Spectral Flux
plt.figure(figsize=(10, 4))
plt.plot(flux, label="Spectral Flux", color="blue")
plt.xlabel("Frames")
plt.ylabel("Flux Value")
plt.title("Spectral Flux Over Time")
plt.legend()
plt.show()

# Play the audio using sounddevice
sd.play(y, sr)

# Wait until audio is finished playing
sd.wait()