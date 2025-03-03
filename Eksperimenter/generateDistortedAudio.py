import librosa
import soundfile as sf
import numpy as np

# Load original audio
y, sr = librosa.load("audio_file.wav", sr=None)

# Create a tempo-varying version
y_stretched = np.concatenate([
    librosa.effects.time_stretch(y[:sr * 5], rate=0.8),  # Slow down first 5 sec
    librosa.effects.time_stretch(y[sr * 5:sr * 10], rate=1.2),  # Speed up next 5 sec
    librosa.effects.time_stretch(y[sr * 10:], rate=1.0)  # Normal speed after
])

# Save the modified file
sf.write("warped_audio.wav", y_stretched, sr)
