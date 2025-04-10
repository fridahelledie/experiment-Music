import librosa
import json
import numpy as np

# Audio settings
sr = 22050  # Sampling rate
n_fft = 2048  # FFT window size
hop_length = 1024  # Hop length for STFT
buffer_size = 2048  # Chunk size

# Function to compute amplitude envelope
def amplitude_envelope(signal, frame_size, hop_length):
    amplitude_envelope = []
    for i in range(0, len(signal), hop_length):
        amplitude_envelope.append(max(signal[i:i + frame_size]))
    return np.array(amplitude_envelope)

# Load the audio file
audio_path = "input_audio.wav"
y, sr = librosa.load(audio_path, sr=sr)

# Compute amplitude envelope for the entire audio
AE_audio = amplitude_envelope(y, buffer_size, hop_length)

#Compute beats
tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, hop_length=hop_length)
beat_times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=hop_length)

# Initialize feature storage
feature_data = []
num_chunks = len(y) // buffer_size

# Process audio in chunks
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

    # Retrieve amplitude envelope value for this chunk
    amplitude_value = float(AE_audio[i]) if i < len(AE_audio) else 0.0

    current_beat_times = [bt for bt in beat_times if start / sr <= bt < end / sr]

    # Store the feature with a timestamp
    feature_data.append({
        "timestamp": round(start / sr, 3),
        "onset": round(max_onset_strength, 3),
        "amplitude": amplitude_value,
        "chroma": chroma_list,
        #"tempo": round(tempo.item(), 3),
        "beat_times": [round(bt, 3) for bt in current_beat_times],
    })



# Save features to a JSON file
with open("audio_features.json", "w") as f:
    json.dump(feature_data, f, indent=4, default=lambda x: float(x))

print("Feature extraction complete. Data saved to audio_features.json")