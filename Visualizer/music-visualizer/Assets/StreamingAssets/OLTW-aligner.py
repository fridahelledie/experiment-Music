import librosa
import numpy as np
import queue
import sys
import os
import sounddevice as sd
import Client

from dtaidistance import dtw

# Set working directory to files absolute path (this is because unity changes the CWD when launching the script)
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# =============== CONFIG ===============
USE_SIMULATED_INPUT = True  # Flip this to False to use real mic input
SIMULATED_INPUT_NAME = "03PollackBarberSonata.mp3"
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
ref_chroma = librosa.feature.chroma_stft(y=y_ref, sr=sr, n_fft=N_FFT, hop_length=HOP_LENGTH)

# Client connection
if not Client.connect():
    print("Failed to connect to Unity client.")
    sys.exit(1)

# Chroma buffer for live input
live_chroma = np.empty(shape=(ref_chroma.shape[0], 0))
audio_queue = queue.Queue()

# DTW tracking
P = [(0, 0)]
t, j = 0, 0
D = np.full((1, ref_chroma.shape[1]), np.inf)

# Previous direction tracking
previous = None
runCount = 1
maxRunCount = 3

def evaluate_cost(t, j, X, Y, D):
    cost = dtw.distance(X[:, t], Y[:, j])
    neighbors = []
    if t - 1 >= 0: neighbors.append(D[t - 1, j])
    if j - 1 >= 0: neighbors.append(D[t, j - 1])
    if t - 1 >= 0 and j - 1 >= 0: neighbors.append(D[t - 1, j - 1])
    return cost + (min(neighbors) if neighbors else 0)

def get_inc(t, j, D):
    global runCount, previous
    if t < C:
        return "Both"
    if runCount > maxRunCount:
        return "Column" if previous == "Row" else "Row"

    best_cost, best_move = np.inf, "Both"
    if t - 1 >= 0 and D[t - 1, j] < best_cost:
        best_cost, best_move = D[t - 1, j], "Row"
    if j - 1 >= 0 and D[t, j - 1] < best_cost:
        best_cost, best_move = D[t, j - 1], "Column"
    if t - 1 >= 0 and j - 1 >= 0 and D[t - 1, j - 1] < best_cost:
        best_move = "Both"
    return best_move

def online_tw():
    global t, j, P, D, previous, runCount, live_chroma
    t, j = P[-1]

    while t < live_chroma.shape[1] - 1 and j < ref_chroma.shape[1]:
        decision = get_inc(t, j, D)

        if decision != "Column":
            t += 1
            if t >= D.shape[0]:
                D = np.vstack([D, np.full((1, D.shape[1]), np.inf)])
            for k in range(max(0, j - C + 1), j + 1):
                if t < D.shape[0] and k < D.shape[1]:
                    D[t, k] = evaluate_cost(t, k, live_chroma, ref_chroma, D)

        if decision != "Row":
            j += 1
            for k in range(max(0, t - C + 1), t + 1):
                if k < D.shape[0] and j < D.shape[1]:
                    D[k, j] = evaluate_cost(k, j, live_chroma, ref_chroma, D)

        if previous and previous != decision and decision != "Both":
            if len(P) > 0:
                P.pop(-1)
            previous = "Both"
        elif decision != "Both":
            previous = decision

        runCount = runCount + 1 if decision == previous else 1

        if t < D.shape[0] and j < D.shape[1]:
            P.append((t, j))
            Client.send_data(f"{j:.3f}")  # Send alignment progress to Unity

def calculate_chroma_chunk(audio_chunk):
    return librosa.feature.chroma_stft(y=audio_chunk, sr=sr, n_fft=N_FFT, hop_length=HOP_LENGTH)

def simulate_input(audio_path):
    y_live, _ = librosa.load(audio_path, sr=sr)
    for start in range(0, len(y_live), BUFFER_SIZE):
        chunk = y_live[start:start+BUFFER_SIZE]
        if len(chunk) == 0: break
        if chunk.ndim > 1: chunk = chunk.mean(axis=1)
        chroma = calculate_chroma_chunk(chunk)
        append_and_process_chroma(chroma)

def append_and_process_chroma(chroma):
    global live_chroma, D
    live_chroma = np.append(live_chroma, chroma, axis=1)
    D = np.append(D, np.full((chroma.shape[1], D.shape[1]), np.inf), axis=0)
    online_tw()

def mic_callback(indata, frames, time, status):
    if status:
        print(status)
    audio_chunk = indata[:, 0] if indata.ndim > 1 else indata
    chroma = calculate_chroma_chunk(audio_chunk)
    append_and_process_chroma(chroma)

# =============== Main ===============
ref_features = generate_reference_features(y_ref, BUFFER_SIZE)
live_features = np.empty(shape=(ref_features.shape[0], 0))

Client.send_data("READY")

# Wait for Unity to send "START"
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

Client.send_data("READY")

# Wait for Unity to send "START"
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
