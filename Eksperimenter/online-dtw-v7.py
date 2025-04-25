import time

import librosa
import numpy as np
import queue
from librosa.sequence import dtw
import soundfile as sf
from numba.core.cgutils import false_bit
from numpy.ma.core import shape
from dtaidistance import dtw
from scipy.spatial.distance import euclidean
from scipy.spatial.distance import cosine
from librosa.sequence import dtw as librosa_dtw
import matplotlib.pyplot as plt
import librosa.display

c = 16 #Window Size

#Debugging
duration = 100

#variables for get inc and online tw
previous = None
runCount = 1
maxRunCount = 3

#variables for chroma features
n_fft = 1024  #window length
hop_length = 512

N = 8 # number of chroma features per chunk

buffer_size = N * hop_length

#Reference audio
reference_audio_path = "03BarberSonata_1.wav"
y, sr = librosa.load(reference_audio_path, sr=None)
Y_chroma = librosa.feature.chroma_stft(y=y,
    sr=sr,
    n_fft=n_fft,
    hop_length=hop_length,
    center = False
)

#Input audio
input_audio_path = "03BarberSonata_1.wav"
x, sr = librosa.load(input_audio_path, sr=None)
X_chroma = librosa.feature.chroma_stft(y=x, sr=sr, n_fft=n_fft, hop_length=hop_length)


def show_dtw(D, P, c=c):
    plt.figure(figsize=(8, 6))
    plt.imshow(D, cmap='hot', origin='lower')
    plt.plot(P[:, 1], P[:, 0], marker="o", linestyle="-", markersize=3)
    plt.xlabel("Reference Audio (j)")
    plt.ylabel("Live Audio (t)")
    plt.title(f"Alignment Path (c={c})")
    plt.grid()
    plt.show()
def show_path(P):
    plt.figure(figsize=(8, 6))
    plt.plot(P[:, 1], P[:, 0], marker="o", linestyle="-", markersize=3)
    plt.xlabel("Reference Audio (j)")
    plt.ylabel("Live Audio (t)")
    plt.title("Alignment Path and cost matrix")
    plt.grid()
    plt.show()
def show_matrix(D):
    plt.figure(figsize=(8, 6))
    plt.imshow(D, cmap='hot')
    plt.xlabel("Reference Audio (j)")
    plt.ylabel("Live Audio (t)")
    plt.title("Cost matrix")
    plt.grid()
    plt.show()
def compare_dtw_paths(D, paths, labels, colors):
    plt.figure(figsize=(10, 8))
    plt.imshow(D, cmap='hot', origin='lower')
    for P, label, color in zip(paths, labels, colors):
        P = np.array(P)
        plt.plot(P[:, 1], P[:, 0], label=label, color=color, linewidth=2)
    plt.xlabel("Reference Audio (j)")
    plt.ylabel("Live Audio (t)")
    plt.title("Comparison of DTW Alignment Paths")
    plt.legend()
    plt.grid()
    plt.show()

def generate_reference_chromas(audio_path, buffer_size):
    audio, sr_ = librosa.load(audio_path, sr=sr, duration=duration)

    # Declare variables
    chroma = np.empty(shape=(12, 0))  # Declares an empty array for keeping the chroma features as they are inputted
    audio_queue = queue.Queue()

    for frame in range(0, len(audio), buffer_size):
        audio_chunk = audio[frame:frame + buffer_size]

        # Stop when file ends (Safety)
        if len(audio_chunk) == 0:
            break

        # If stereo, convert to mono
        if audio_chunk.ndim > 1:
            audio_chunk = audio_chunk.mean(axis=1)

        # Enqueue audio chunk
        audio_queue.put(audio_chunk)

        chroma_chunk = calculate_chroma_chunk(audio_queue.get())
        chroma = np.append(chroma, chroma_chunk, axis=1)
        # print(chroma.shape)

    return chroma


def online_tw(live_features, ref_features, _D, _P, _t, _j):
    global previous, runCount
    D = np.append(_D, np.full(shape=(max(0, live_features.shape[1] - _D.shape[0]) , _D.shape[1]), fill_value=np.inf), axis=0)

    P = _P
    t = _t
    j = _j


    #initialize new rows diagonal values (cost values)
    if t == 0 and live_features.shape[1] > 0 and D.shape[0] > 0:
        D[t, j] = EvaluatePathCost(t, j, live_features, ref_features, D)


    while t < live_features.shape[1] - 1 and j < ref_features.shape[1]:
        decision = GetInc(t, j, D)


        if decision != "Column":  # calculate new row if last step was not a column
            t += 1
            for k in range(max(0, j - c + 1), j + 1):
                if t < D.shape[0] and t < live_features.shape[1] and k < D.shape[1]:
                    D[t, k] = EvaluatePathCost(t, k, live_features, ref_features, D)

        if decision != "Row":  # Calculate new row
            j += 1
            for k in range(max(0, t - c + 1), t + 1):
                if k < D.shape[0] and k < live_features.shape[1] and j < D.shape[1]:
                    D[k, j] = EvaluatePathCost(k, j, live_features, ref_features, D)


        #HOT FIX that makes sure that we never make an unnecessary column followed imidietly by a row or vice versa
        if previous != decision and decision != "Both" and previous != None and previous != "Both":
            print(f"{previous} {P[-1]} {decision}")
            P.pop(-1)
            previous = "Both"
        #HOT FIX END

        if decision == previous:
            runCount += 1
        else:
            runCount = 1

        if decision != "Both":
            previous = decision


        if t < D.shape[0] and j < D.shape[1]:
            P.append((t, j))

    return D, P

def EvaluatePathCost(t, j, X, Y, D):
    #distance = dtw.distance(X[:,t], Y[:,j])
    distance = cosine(X[:, t], Y[:, j])  # or try
    #distance = np.linalg.norm(X[:,t] - Y[:,j])


    neighbors = []
    if t - 1 >= 0:
        neighbors.append(D[t - 1, j])
    if j - 1 >= 0:
        neighbors.append(D[t , j - 1])
    if t - 1 >= 0 and j - 1 >= 0:
        neighbors.append(D[t - 1, j - 1])

    if len(neighbors) > 0:
        distance += min(neighbors)

    return distance

def GetInc(t, j, D):
    #at the very start return both
    if t < c:
        return "Both"


    #if one direction has been repeated to often, switch
    if runCount > maxRunCount:
        if previous == "Row":
            return "Column"
        else:
            return "Row"

    #find the best direction
    bestCost = np.inf
    bestMove = "Both"

    #check in all directions from the current cell(t,j)
    #first check that we are not on the first row,checks if the cost of moving up is less than current
    if t - 1 < D.shape[0] and D[t - 1,j] < bestCost:
        bestCost = D[t - 1, j] #update the best cost
        bestMove = "Row" #assign the best move

    #checks if moving left is the best
    if j - 1 < D.shape[1] and D[t, j - 1] < bestCost:
        bestCost = D[t, j - 1] #update the best cost
        bestMove = "Column" #assign the best move

    # checks if moving left and up is the best
    if t - 1 < D.shape[0] and j - 1 < D.shape[1] and D[t - 1, j - 1] < bestCost:
        bestCost = D[t - 1, j - 1]  # update the best cost
        bestMove = "Both"  # assign the best move

    return bestMove

def simulate_live_audio_input(audio_path, buffer_size, ref):
    live_audio, sr_ = librosa.load(audio_path, sr=sr, duration=duration)

    #Declare variables
    live_chroma = np.empty(shape=(ref.shape[0], 0)) #Declares an empty array for keeping the chroma features as they are inputted
    audio_queue = queue.Queue()

    #Online tw variables
    P = [(0, 0)]  # list of points in the path cost
    t = 0
    j = 0
    D = np.full((live_chroma.shape[1], ref.shape[1]), np.inf)  # Cost matrix

    #For loop that cuts the file into buffersize chunks
    for frame in range(0, len(live_audio), buffer_size):
        #reads buffer_sizer amount of frames
        audio_chunk = live_audio[frame:frame+buffer_size]

        # Stop when file ends (Safety)
        if len(audio_chunk) == 0:
            break

        # If stereo, convert to mono
        if audio_chunk.ndim > 1:
            audio_chunk = audio_chunk.mean(axis=1)

        # Enqueue audio chunk
        audio_queue.put(audio_chunk)

        # Calculate chroma for latest audio chunk
        chroma = calculate_chroma_chunk(audio_queue.get())
        live_chroma = np.append(live_chroma, chroma, axis=1)
        #run online time warp
        t, j = P[-1]
        D, P = online_tw(live_chroma, ref, D,P,t,j)

    #show_dtw(D, np.array(P))
    return D,P

def simulate_live_audio_input_new(audio_path, buffer_size, ref):
    live_audio, sr_ = librosa.load(audio_path, sr=sr, duration=duration) # Force same sr as reference

    #Declare variables
    live_chroma = np.empty(shape=(ref.shape[0], 0)) #Declares an empty array for keeping the chroma features as they are inputted

    #Online tw variables
    P = [(0, 0)]  # list of points in the path cost
    t = 0
    j = 0
    D = np.full((live_chroma.shape[1], ref.shape[1]), np.inf)  # Cost matrix

    #History buffer for smoother chroma computation
    history_buffer = np.zeros(buffer_size)


    #For loop that cuts the file into buffersize chunks
    for frame_start in range(0, len(live_audio), buffer_size):
        #reads buffer_sizer amount of frames
        audio_chunk = live_audio[frame_start : frame_start + buffer_size]

        # Stop when file ends (Safety)
        if len(audio_chunk) == 0:
            break

        # If stereo, convert to mono
        if audio_chunk.ndim > 1:
            audio_chunk = audio_chunk.mean(axis=1)


        # Concatenate with previous buffer to maintain continuity
        padded_chunk = np.concatenate((history_buffer[-buffer_size:], audio_chunk))

        if len(padded_chunk) < n_fft:
            continue  # skip until we have enough audio

        # Compute chroma for this chunk
        chroma = calculate_chroma_chunk(padded_chunk)
        # chroma = librosa.feature.chroma_stft(
        #     y=padded_chunk,
        #     sr=sr,
        #     n_fft=n_fft,
        #     hop_length=hop_length,
        #     center = False
        # )
        #


        # Keep only chroma frames that came from the *new* audio (excluding overlap frames)
        new_frames = (len(audio_chunk) // hop_length)
        chroma = chroma[:, -new_frames:] if chroma.shape[1] >= new_frames else chroma

        # Update history
        history_buffer = np.concatenate((history_buffer, audio_chunk))[-n_fft:]

        # Append to total live chroma
        live_chroma = np.append(live_chroma, chroma, axis=1)

        #run online time warp
        t, j = P[-1]
        D, P = online_tw(live_chroma, ref, D,P,t,j)

    #show_dtw(D, np.array(P))
    return D,P

def simulate_live_chroma_input(precomputed_chroma, ref, chunk_size_frames):
    live_chroma = np.empty(shape=(ref.shape[0], 0))

    # Online TW variables
    P = [(0, 0)]
    t, j = 0, 0
    D = np.full((0, ref.shape[1]), np.inf)

    # Simulate feeding chroma features chunk-by-chunk
    for frame_start in range(0, precomputed_chroma.shape[1], chunk_size_frames):
        frame_end = frame_start + chunk_size_frames
        chroma_chunk = precomputed_chroma[:, frame_start:frame_end]

        live_chroma = np.append(live_chroma, chroma_chunk, axis=1)

        # Run online TW
        t, j = P[-1]
        D, P = online_tw(live_chroma, ref, D, P, t, j)

    #show_dtw(D, np.array(P))
    return D,P

def full_offline_dtw(reference_chroma, live_chroma):
    # Compute cost matrix using cosine distance
    cost_matrix = np.zeros((live_chroma.shape[1], reference_chroma.shape[1]))

    for t in range(live_chroma.shape[1]):
        for j in range(reference_chroma.shape[1]):
            cost_matrix[t, j] = cosine(live_chroma[:, t], reference_chroma[:, j])

    # Use librosa's DTW function
    D, wp = librosa.sequence.dtw(C=cost_matrix)

    # wp gives you the path in reverse (from end to start), so flip it
    wp = np.array(wp)[::-1]

    return D, wp


def calculate_chroma_chunk(audio_chunk):
    #Old chroma calculation
    # chroma = librosa.feature.chroma_stft(y=audio_chunk, sr=sr, n_fft=n_fft, hop_length=hop_length)

    #
    chroma = librosa.feature.chroma_stft(
        y=audio_chunk,
        sr=sr,
        n_fft=n_fft,
        hop_length=hop_length,
        center = False
    )

    return chroma




ref_chroma = generate_reference_chromas(reference_audio_path, buffer_size)


#Timing the algorithm
start_time = time.time()

D_new, P_new = simulate_live_audio_input_new(audio_path= input_audio_path, buffer_size= buffer_size, ref=ref_chroma)

# D, P = simulate_live_audio_input(audio_path=input_audio_path, buffer_size= buffer_size, ref=ref_chroma)

#D_chroma, P_chroma = simulate_live_chroma_input(precomputed_chroma=X_chroma, ref=Y_chroma, chunk_size_frames=10)

#D_offline, P_offline = full_offline_dtw(Y_chroma, X_chroma)

#Print time since start
print(f"Finished in {time.time() - start_time} seconds")

'''
compare_dtw_paths(
    D,
    [P_offline, P, P_new,],
    ["offline","precomputed chroma DTW", "Original Simulation", "Improved Simulation"],
    ["red", "green", "blue", "orange"]
)'''

compare_dtw_paths(
    D_new,
    [P_new,],
    ["Original Simulation", "Improved Simulation"],
    ["blue", "orange"]
)





