import librosa
import json
import numpy as np

# Audio settings
sr = 22050  # Sampling rate
n_fft = 2048  # FFT window size
hop_length = 1024  # Hop length for STFT
buffer_size = 2048  # Chunk size

# Load the audio file
audio_path = "input_audio.wav"
y, sr = librosa.load(audio_path, sr=sr)

# Initialize feature storage
feature_data = []

# Process audio in chunks
num_chunks = len(y) // buffer_size
for i in range(num_chunks):
    start = i * buffer_size
    end = start + buffer_size
    audio_chunk = y[start:end]

    # Compute onset strength
    onset_env = librosa.onset.onset_strength(y=audio_chunk, sr=sr, hop_length=hop_length)
    max_onset_strength = onset_env.max()

    # Compute chroma features
    chroma = librosa.feature.chroma_stft(y=audio_chunk, sr=sr, n_fft=n_fft, hop_length=hop_length)
    chroma_list = np.round(chroma.mean(axis=1), 3).tolist()

    # Store the feature with a timestamp
    feature_data.append({
        "timestamp": round(start / sr, 3),  # Time in seconds
        "onset": round(max_onset_strength, 3),
        "chroma": chroma_list
    })

# Save features to a JSON file
with open("audio_features.json", "w") as f:
    json.dump(feature_data, f, indent=4, default=lambda x: float(x))


print("Feature extraction complete. Data saved to audio_features.json")
