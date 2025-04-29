import librosa
import json
import numpy as np
import sys
import os
import Client

# Set working directory to files absolute path (this is because unity changes the CWD when launching the script)
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Check if the script received a filename
if len(sys.argv) < 2:
    print("Usage: python songProcessor.py <SelectedSong>")
    sys.exit(1)

# Get the song filename from arguments
selected_song = sys.argv[1]
audio_input_path = os.path.join("audio", selected_song)
json_output_path = os.path.join("jsonVisualizations", os.path.splitext(selected_song)[0] + ".json")

# Audio settings
sr = 22050  # Sampling rate
n_fft = 2048  # FFT window size
hop_length = 1024  # Hop length for STFT
buffer_size = 2048  # Chunk size

# Client connection
if not Client.connect():
    print("Failed to connect to Unity client.")
    sys.exit(1)

# Function to compute amplitude envelope
def amplitude_envelope(signal, frame_size, hop_length):
    amplitude_envelope = []
    for i in range(0, len(signal), hop_length):
        amplitude_envelope.append(max(signal[i:i + frame_size]))
    return np.array(amplitude_envelope)

# Load the audio file
try:
    y, sr = librosa.load(audio_input_path, sr=sr)
except FileNotFoundError:
    print(f"Audio file not found at {audio_input_path}")
    Client.send_data(f"Audio file not found at {audio_input_path}")
    sys.exit(1)
except Exception as e:
    Client.send_data("Error while loading audio file:" + type(e).__name__)
    sys.exit(1)

# Compute amplitude envelope for the entire audio
AE_audio = amplitude_envelope(y, buffer_size, hop_length)

# Compute beats
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
        "beat_times": round(current_beat_times[0], 3) if len(current_beat_times) == 1 else (current_beat_times if len(current_beat_times) > 1 else None),
    })


# Save features to a JSON file
os.makedirs(os.path.dirname(json_output_path), exist_ok=True)
Client.send_data("got through makedir")

with open(json_output_path, "w") as f:
    json.dump(feature_data, f, indent=4, default=lambda x: float(x))

Client.send_data("Should have saved" )
