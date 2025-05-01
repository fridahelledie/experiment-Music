import librosa
import numpy as np
import queue
import sys
import os
import sounddevice as sd
import Client
from scipy.spatial.distance import cosine

from dtaidistance import dtw

# Set working directory to files absolute path (this is because unity changes the CWD when launching the script)
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# =============== CONFIG ===============
USE_SIMULATED_INPUT = True  # Flip this to False to use real mic input
SIMULATED_INPUT_NAME = "03PollackBarberSonata.wav"
BUFFER_SIZE = 4096
N_FFT = 2048
HOP_LENGTH = 512
C = 8  # Window size for DTW
# ======================================

# Command-line input
if len(sys.argv) < 2:
    print("Usage: python OLTW-aligner.py <SelectedSong>")
    sys.exit(1)

song_name = sys.argv[1]
ref_audio_path = os.path.join("audio", song_name)
sim_audio_path = os.path.join("audio", SIMULATED_INPUT_NAME)

# Load reference audio and chroma
y_ref, sr = librosa.load(ref_audio_path, sr=None)

# Client connection
if not Client.connect():
    print("Failed to connect to Unity client.")
    sys.exit(1)

# Chroma buffer for live input
audio_queue = queue.Queue()

# DTW tracking
P = [(0, 0)]
t, j = 0, 0
d = {}
c = 16 #Window Size

# Previous direction tracking
previous = None
runCount = 1
maxRunCount = 3

#variables for chroma features
n_fft = 1024  #window length
hop_length = 512

# History buffer for smoother chroma computation
history_buffer = np.zeros(BUFFER_SIZE)

def evaluate_cost(t, j, X, Y, d):
    distance = cosine(X[:, t], Y[:, j])

    neighbors = []
    if t - 1 >= 0 and (t - 1, j) in d.keys():
        neighbors.append(d[(t - 1, j)])
    if j - 1 >= 0 and (t, j - 1) in d.keys():
        neighbors.append(d[(t, j - 1)])
    if t - 1 >= 0 and j - 1 >= 0 and (t - 1, j - 1) in d.keys():
        neighbors.append(d[(t - 1, j - 1)])

    if len(neighbors) > 0:
        distance += min(neighbors)

    return distance

def get_inc(t, j, d):
    global runCount, previous
    # at the very start return both
    if t < c:
        return "Both"
    # if one direction has been repeated to often, switch
    if runCount > maxRunCount:
        if previous == "Row":
            return "Column"
        else:
            return "Row"
    # find the best direction
    best_cost = np.inf
    best_move = "Both"
    # check in all directions from the current cell(t,j)
    # first check that we are not on the first row,checks if the cost of moving up is less than current
    if (t - 1, j) in d.keys() and d[(t - 1, j)] < best_cost:
        best_cost = d[(t - 1, j)]  # update the best cost
        best_move = "Row"  # assign the best move
    # checks if moving left is the best
    if (t, j - 1) in d.keys() and d[(t, j - 1)] < best_cost:
        best_cost = d[(t, j - 1)]  # update the best cost
        best_move = "Column"  # assign the best move
    # checks if moving left and up is the best
    if (t - 1, j - 1) in d.keys() and d[(t - 1, j - 1)] < best_cost:
        best_move = "Both"  # assign the best move

    return best_move

def online_tw():
    global t, j, P, d, previous, runCount, live_features, ref_features, c
    t, j = P[-1]

    # initialize new rows diagonal values (cost values)
    if t == 0 and live_features.shape[1] > 0:
        d[(t, j)] = evaluate_cost(t, j, live_features, ref_features, d)

    while t < live_features.shape[1] - 1 and j < ref_features.shape[1]:
        decision = get_inc(t, j, d)

        if decision != "Column":  # calculate new row if last step was not a column
            t += 1
            for k in range(max(0, j - c + 1), j + 1):
                if t < live_features.shape[1] and k < ref_features.shape[1]:
                    d[(t, k)] = evaluate_cost(t, k, live_features, ref_features, d)

        if decision != "Row":  # Calculate new row
            j += 1
            for k in range(max(0, t - c + 1), t + 1):
                if k < live_features.shape[1] and j < ref_features.shape[1]:
                    d[(k, j)] = evaluate_cost(k, j, live_features, ref_features, d)

        # HOT FIX that makes sure that we never make an unnecessary column followed imidietly by a row or vice versa
        if previous != decision and decision != "Both" and previous != None and previous != "Both":
            # print(f"{previous} {P[-1]} {decision}")
            P.pop(-1)
            previous = "Both"
        # HOT FIX END

        if decision == previous:
            runCount += 1
        else:
            runCount = 1

        # Log only previous decision if it was not both, since it is always alowed to be both
        if decision != "Both":
            previous = decision

        if (t, j) in d.keys():
            P.append((t, j))
            Client.send_data(f"{j}")
    return d, P

def get_feature_chunk(audio_chunk):
    return librosa.feature.chroma_stft(
        y=audio_chunk,
        sr=sr,
        n_fft=n_fft,
        hop_length=hop_length,
        center=False
    )


def simulate_input(audio_path):
    global history_buffer

    y_live, _ = librosa.load(audio_path, sr=sr)
    for start in range(0, len(y_live), BUFFER_SIZE):
        chunk = y_live[start:start+BUFFER_SIZE]
        if len(chunk) == 0: break
        if chunk.ndim > 1: chunk = chunk.mean(axis=1)

        # Concatenate with previous buffer to maintain continuity
        padded_audio_chunk = np.concatenate((history_buffer[-BUFFER_SIZE:], chunk))

        if len(padded_audio_chunk) < n_fft:
            continue  # skip until we have enough audio

        feature_chunk = get_feature_chunk(padded_audio_chunk)
        new_frames = (len(chunk) // hop_length)
        feature_chunk = feature_chunk[:, -new_frames:] if feature_chunk.shape[1] >= new_frames else feature_chunk
        history_buffer = np.concatenate((history_buffer, chunk))[-n_fft:]

        append_and_process_chroma(feature_chunk)

def append_and_process_chroma(chroma):
    global live_features
    live_features = np.append(live_features, chroma, axis=1)
    online_tw()

def mic_callback(indata, frames, time, status):
    global history_buffer
    if status:
        print(status)
    chunk = indata[:, 0] if indata.ndim > 1 else indata

    # Concatenate with previous buffer to maintain continuity
    padded_audio_chunk = np.concatenate((history_buffer[-BUFFER_SIZE:], chunk))

    feature_chunk = get_feature_chunk(padded_audio_chunk)
    new_frames = (len(chunk) // hop_length)
    feature_chunk = feature_chunk[:, -new_frames:] if feature_chunk.shape[1] >= new_frames else feature_chunk
    history_buffer = np.concatenate((history_buffer, chunk))[-n_fft:]

    append_and_process_chroma(feature_chunk)

def generate_reference_features(audio, buffer_size):
    # Declare variables
    features = np.empty(shape=(12, 0))  # Declares an empty array for keeping the features as they are generated

    # History buffer for smoother chroma computation
    history_buffer = np.zeros(buffer_size)

    for frame_start in range(0, len(audio), buffer_size):
        # reads buffer_sizer amount of frames
        audio_chunk = audio[frame_start: frame_start + buffer_size]

        # Stop when file ends (Safety)
        if len(audio_chunk) == 0:
            break

        # If stereo, convert to mono
        if audio_chunk.ndim > 1:
            audio_chunk = audio_chunk.mean(axis=1)

        # Concatenate with previous buffer to maintain continuity
        padded_audio_chunk = np.concatenate((history_buffer[-buffer_size:], audio_chunk))

        if len(padded_audio_chunk) < n_fft:
            continue  # skip until we have enough audio

        # Compute chroma for this chunk
        feature_chunk = get_feature_chunk(padded_audio_chunk)

        # Keep only chroma frames that came from the *new* audio (excluding overlap frames)
        new_frames = (len(audio_chunk) // hop_length)
        feature_chunk = feature_chunk[:, -new_frames:] if feature_chunk.shape[1] >= new_frames else feature_chunk

        # Update history
        history_buffer = np.concatenate((history_buffer, audio_chunk))[-n_fft:]

        # Append to total live chroma
        features = np.append(features, feature_chunk, axis=1)

    return features

# =============== Main ===============
ref_features = generate_reference_features(y_ref, BUFFER_SIZE)
live_features = np.empty(shape=(ref_features.shape[0], 0))

Client.send_data("READY")

def wait_for_start():
    while True:
        try:
            data = Client.sock.recv(1024).decode("utf-8").strip()
            if data == "START":
                print("Received START from Unity.")
                break
        except Exception as e:
            print("Error while waiting for START:", e)
            break

wait_for_start()

try:
    if USE_SIMULATED_INPUT:
        simulate_input(sim_audio_path)  # Just using the same track as dummy live input
    else:
        with sd.InputStream(callback=mic_callback, channels=1, samplerate=sr, blocksize=BUFFER_SIZE):
            print("Listening to mic... Press Ctrl+C to stop.")
            while True:
                pass
except KeyboardInterrupt:
    print("Stopped by user.")
except Exception as e:
    print(f"Error: {e}")
finally:
    Client.disconnect()
