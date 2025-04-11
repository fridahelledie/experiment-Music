import librosa
import numpy as np
import queue
from librosa.sequence import dtw
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist


#variables for chroma features
n_fft = 2048  #window length
hop_length = 512
buffer_size = 4096 #sice of audio chunk to simulate live input


#Load reference audio and extract chroma features
reference_audio_path = "audio_file.wav"
y, sr = librosa.load(reference_audio_path, sr=None)
Y_chroma = librosa.feature.chroma_stft(y=y, sr=sr, n_fft=n_fft, hop_length=hop_length)
ref_len = Y_chroma.shape[1]


#Load input audio to simulate live input
input_audio_path = "audio_file_slowed.wav"
x, sr = librosa.load(input_audio_path, sr=None)

#D is a cost matrix
D = np.empty((0, ref_len)) # Rows = live input, columns = reference

def simulate_live_input(audio, ref_chroma, buffer_size, sr):
    global D

    for start in range(0, len(audio), buffer_size):
        end = start + buffer_size
        chunk = audio[start:end]

        if len(chunk) == 0:
            break

        #if stereo, convert to mono
        if chunk.ndim > 1:
            chunk = chunk.mean(axis=1)

        #compute chroma for the chunk
        chunk_chroma = librosa.feature.chroma_stft(y=chunk, sr=sr, hop_length=hop_length)

        # Compute pairwise distances (new rows of the cost matrix)
        distances = cdist(chunk_chroma.T, ref_chroma.T, metric='cosine')  # shape: (new_chunk_len, ref_len)

        # Append new rows to full cost matrix
        D = np.vstack([D, distances])


        print(f"Updated cost matrix shape: {D.shape}")


simulate_live_input(x, Y_chroma, buffer_size, sr)

# Parameters for the cutout
num_rows_to_show = 10   # Show last 10 live frames
num_cols_to_show = 20   # Optional: show only first 20 reference frames

# Get the cutout
cutout = D[-num_rows_to_show:, :num_cols_to_show]

print("\nCutout of the final cost matrix:")
print(np.round(cutout, 3))  # Rounded for easier reading