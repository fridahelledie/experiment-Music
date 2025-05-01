import time

import librosa
import numpy as np
import queue
from librosa.sequence import dtw
from scipy.spatial.distance import cosine
import matplotlib.pyplot as plt
import librosa.display
from DLNCO_extraction_realtime import DLNCOProcessor

c = 16 #Window Size

#Debugging
duration = 40

#variables for get inc and online tw
previous = None
runCount = 1
maxRunCount = 3
max_matrix_size = 1024
matrix_offset = 0

#variables for chroma features
n_fft = 1024  #window length
hop_length = 512

N = 8 # number of chroma features per chunk

buffer_size = N * hop_length

#Reference audio
reference_audio_path = "03BarberSonata_1.wav"
reference_audio, sr = librosa.load(reference_audio_path)

#Input audio
input_audio_path = "03BarberSonata_3.wav"
input_audio, sr = librosa.load(input_audio_path, sr=sr) #forces matching sampling rates between reference and input audio

#DLNCO
dlnco = DLNCOProcessor()

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
def construct_matrix(d, live_features, ref_features):
    D = np.full(shape=(live_features.shape[1], ref_features.shape[1]), fill_value=np.inf)
    for k, v in d.items():
        x, y = k
        x_shape, y_shape = D.shape
        if x_shape > x >= 0 and y_shape > y >= 0:
            D[x, y] = v
    return D


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


def online_tw(live_features, ref_features, _d, _P, _t, _j):
    global previous, runCount, max_matrix_size, matrix_offset
    d = _d
    P = _P
    t = _t
    j = _j

    #initialize new rows diagonal values (cost values)
    if t == 0 and live_features.shape[1] > 0:
        d[(t, j)] = EvaluatePathCost(t, j, live_features, ref_features, d)


    while t < live_features.shape[1] - 1 and j < ref_features.shape[1]:
        decision = GetInc(t, j, d)


        if decision != "Column":  # calculate new row if last step was not a column
            t += 1
            for k in range(max(0, j - c + 1), j + 1):
                if t < live_features.shape[1] and k < ref_features.shape[1]:
                    d[(t, k)] = EvaluatePathCost(t, k, live_features, ref_features, d)

        if decision != "Row":  # Calculate new row
            j += 1
            for k in range(max(0, t - c + 1), t + 1):
                if k < live_features.shape[1] and j < ref_features.shape[1]:
                    d[(k, j)] = EvaluatePathCost(k, j, live_features, ref_features, d)


        #HOT FIX that makes sure that we never make an unnecessary column followed imidietly by a row or vice versa
        if previous != decision and decision != "Both" and previous != None and previous != "Both":
            # print(f"{previous} {P[-1]} {decision}")
            P.pop(-1)
            previous = "Both"
        #HOT FIX END

        if decision == previous:
            runCount += 1
        else:
            runCount = 1

        #Log only previous decision if it was not both, since it is always alowed to be both
        if decision != "Both":
            previous = decision


        if (t, j) in d.keys():
            P.append((t, j))

    return d, P

def EvaluatePathCost(t, j, X, Y, d):
    #distance = dtw.distance(X[:,t], Y[:,j])
    distance = cosine(X[:, t], Y[:, j])  # or try
    #distance = np.linalg.norm(X[:,t] - Y[:,j])


    neighbors = []
    if t - 1 >= 0 and (t -1, j) in d.keys():
        neighbors.append(d[(t - 1, j)])
    if j - 1 >= 0 and (t, j - 1) in d.keys():
        neighbors.append(d[(t , j - 1)])
    if t - 1 >= 0 and j - 1 >= 0 and (t - 1, j - 1) in d.keys():
        neighbors.append(d[(t - 1, j - 1)])

    if len(neighbors) > 0:
        distance += min(neighbors)

    return distance

def GetInc(t, j, d):
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
    if (t - 1, j) in d.keys() and d[(t - 1,j)] < bestCost:
        bestCost = d[(t - 1, j)] #update the best cost
        bestMove = "Row" #assign the best move

    #checks if moving left is the best
    if (t, j - 1) in d.keys() and d[(t, j - 1)] < bestCost:
        bestCost = d[(t, j - 1)] #update the best cost
        bestMove = "Column" #assign the best move

    # checks if moving left and up is the best
    if (t - 1, j - 1) in d.keys() and d[(t - 1, j - 1)] < bestCost:
        bestMove = "Both"  # assign the best move

    return bestMove

def simulate_live_audio_input_new(live_audio, buffer_size, ref_features):
    global matrix_offset
    # live_audio, sr_ = librosa.load(audio_path, sr=sr, duration=duration) # Force same sr as reference

    #Declare variables
    live_features = np.empty(shape=(ref_features.shape[0], 0)) #Declares an empty array for keeping the chroma features as they are inputted

    #Online tw variables
    P = [(0, 0)]  # list of points in the path cost
    t = 0
    j = 0
    d = {(0,0) : 0}  # Cost dictionary

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
        live_features = np.append(live_features, feature_chunk, axis=1)

        #run online time warp
        t, j = P[-1]
        print(f"{t}, {j}")
        d, P = online_tw(live_features, ref_features, d, P, t, j)

    #Returns cost dictionary and alignment path
    return d,P, live_features


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

    #New chroma calulation
    chroma = librosa.feature.chroma_stft(
        y=audio_chunk,
        sr=sr,
        n_fft=n_fft,
        hop_length=hop_length,
        center = False
    )

    return chroma

def get_feature_chunk(audio_chunk):
    return calculate_chroma_chunk(audio_chunk)
    # return dlnco.compute_chunk(audio_chunk)


#Generating reference features
reference_features = generate_reference_features(reference_audio, buffer_size)

#Timing the algorithm
start_time = time.time()

d, P, live_features = simulate_live_audio_input_new(live_audio=input_audio, buffer_size=buffer_size, ref_features=reference_features)


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

# compare_dtw_paths(
#     D_new,
#     [P_new],
#     ["Improved Simulation", "Original Simulation"],
#     ["blue", "orange"]
# )

D = construct_matrix(d, live_features, reference_features)
show_dtw(D, np.array(P))





