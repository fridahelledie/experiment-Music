import librosa
import json
import numpy as np
import sys
import os
import Client
import subprocess
import time

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
n_fft = 1024  # FFT window size
hop_length = 512  # Hop length for STFT
buffer_size = 4096 # Chunk size

# Client connection
if not Client.connect():
    print("Failed to connect to Unity client.")
    sys.exit(1)

# Load the audio file
try:
    y, sr = librosa.load(audio_input_path)
except FileNotFoundError:
    print(f"Audio file not found at {audio_input_path}")
    Client.send_data(f"Audio file not found at {audio_input_path}")
    sys.exit(1)
except Exception as e:
    Client.send_data("Error while loading audio file:" + type(e).__name__)
    sys.exit(1)

# Compute full onset envelope and chroma with consistent frame steps
onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)
chroma = librosa.feature.chroma_stft(y=y, sr=sr, n_fft=n_fft, hop_length=hop_length)

# Compute amplitude envelope per hop step (using RMS)
rms = librosa.feature.rms(y=y, frame_length=n_fft, hop_length=hop_length)[0]

# Compute beats
tempo, beat_frames = librosa.beat.beat_track(onset_envelope=onset_env,y=y, sr=sr, hop_length=hop_length)
beat_times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=hop_length)
#unused_beats = [round(bt, 3) for bt in beat_times]
#unused_beats.sort()


# Compute spectral centroid and bandwidth
spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr, n_fft=n_fft, hop_length=hop_length)[0]
spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr, n_fft=n_fft, hop_length=hop_length)[0]


# Compute spectral centroid and bandwidth
spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr, n_fft=n_fft, hop_length=hop_length)[0]
spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr, n_fft=n_fft, hop_length=hop_length)[0]


# Initialize feature storage
feature_data = []
num_frames = chroma.shape[1]  # number of frames (steps)

for i in range(num_frames):
    timestamp = librosa.frames_to_time(i, sr=sr, hop_length=hop_length)

    # Onset
    onset_strength = float(onset_env[i]) if i < len(onset_env) else 0.0

    # Chroma vector for frame i
    chroma_vector = np.round(chroma[:, i], 3).tolist()

    # Amplitude (RMS energy)
    amplitude = float(rms[i]) if i < len(rms) else 0.0

    # Check for beat occurrence at this frame
    beat_at_frame = None
   # if unused_beats:
    #    beaty = abs(unused_beats[0] - timestamp)
     #   if beaty <= (hop_length / sr): # beat is only assigned if within 1 hop
      #      beat_at_frame = unused_beats.pop(0)
    # Check for beat occurrence at this frame
    frame_time = timestamp
    for bt in beat_times:
        if abs(bt - frame_time) < (hop_length / sr):  # ~512 samples tolerance
            beat_at_frame = round(bt, 3)
            break

    # Spectral centroid and bandwidth
    centroid = float(spectral_centroid[i]) if i < len(spectral_centroid) else 0.0
    bandwidth = float(spectral_bandwidth[i]) if i < len(spectral_bandwidth) else 0.0

    # Store feature entry
    feature_data.append({
        "timestamp": round(timestamp, 3),
        "onset": round(onset_strength, 3),
        "amplitude": round(amplitude, 3),
        "chroma": chroma_vector,
        "beat_times": beat_at_frame,
        "spectral_centroid": round(centroid, 3),
        "spectral_bandwidth": round(bandwidth, 3)
    })

print("Number of used beats:", sum(1 for f in feature_data if f["beat_times"] is not None))

# Save features to a JSON file
os.makedirs(os.path.dirname(json_output_path), exist_ok=True)
Client.send_data("got through makedir")

with open(json_output_path, "w") as f:
    json.dump(feature_data, f, indent=4, default=lambda x: float(x))


Client.send_data("Should have saved" )
Client.disconnect()




