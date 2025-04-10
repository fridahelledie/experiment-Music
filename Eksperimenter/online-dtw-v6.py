import librosa
import numpy as np
import queue

import soundfile
from librosa.sequence import dtw
import matplotlib.pyplot as plt
import soundfile as sf
from numpy.ma.core import shape
from dtaidistance import dtw
from scipy.spatial.distance import euclidean

c = 8 #Window Size

#variables for get inc and online tw
previous = None
runCount = 1
maxRunCount = 3

#variables for chroma features
n_fft = 2048  #window length
hop_length = 512

#Reference audio
reference_audio_path = "audio_file.wav"
y, sr = librosa.load(reference_audio_path, sr=None)
Y_chroma = librosa.feature.chroma_stft(y=y, sr=sr, n_fft=n_fft, hop_length=hop_length)

#Input audio
input_audio_path = "audio_file_slowed.wav"
#x, sr = librosa.load(input_audio_path, sr=None)
# X_chroma = np.empty(shape=(Y_chroma.shape[0], 0))
#X_chroma = librosa.feature.chroma_stft(y=x, sr=sr, n_fft=n_fft, hop_length=hop_length)


def show_dtw(D, P, c=c):
    plt.figure(figsize=(8, 6))
    plt.imshow(D, cmap='hot')
    plt.plot(P[:, 1], P[:, 0], marker="o", linestyle="-", markersize=3)
    plt.xlabel("Reference Audio (j)")
    plt.ylabel("Live Audio (t)")
    plt.title(f"Alignment Path (c={c})")
    plt.grid()
    plt.show()
def show_comparison(D, P1, P2):
    plt.figure(figsize=(8, 6))
    plt.imshow(D, cmap='hot')
    plt.plot(P1[:, 1], P1[:, 0], marker="o", linestyle="-", markersize=3)
    plt.plot(P2[:, 1], P2[:, 0], marker="o", linestyle="-", markersize=3)
    plt.xlabel("Reference Audio (j)")
    plt.ylabel("Live Audio (t)")
    plt.title("Alignment Path")
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
def show_colored_path(D, P):
    plt.figure(figsize=(8, 6))
    plt.imshow(D, cmap='hot')
    for idx in range(1, len(P)):
        t1, j1 = P[idx - 1]
        t2, j2 = P[idx]
        if t2 == t1 + 1 and j2 == j1 + 1:
            color = "green"  # diagonal
        elif t2 == t1 + 1:
            color = "red"    # row
        else:
            color = "blue"   # column
        plt.plot([j1, j2], [t1, t2], color=color, marker='o')
    plt.title("Colored Path: Green=Diagonal, Red=Row, Blue=Column")
    plt.show()

def online_tw(live_features, ref_features, _D, _P, _t, _j):
    global previous, runCount
    # D = np.append(_D, np.full(shape=(max(0, live_features.shape[1] - _D.shape[0]) , _D.shape[1]), fill_value=np.inf), axis=0)
    new_rows = live_features.shape[1]
    D = np.vstack([_D, np.full((new_rows, _D.shape[1]), np.inf)])
    # D.resize((live_features.shape[0], _D.shape[1]))
    P = _P
    t = _t
    j = _j

    print(f"Initial D shape: {D.shape}, P length: {len(P)}")

    while t < live_features.shape[1] and j < ref_features.shape[1]:
        #print(f"t: {t}, j: {j}, D.shape: {D.shape}, ")
        decision = GetInc(t, j, D)
        #print(f"Decision: {decision}")


        if decision != "Column":  # calculate new row if last step was not a column
            t += 1
            for k in range(max(0, j - c + 1), j + 1):
                if t < D.shape[0] and t < live_features.shape[1] and k < D.shape[1]:
                    #print(D.shape)
                    #print(f"Updating D[{t}, {k}]")
                    D[t, k] = EvaluatePathCost(t, k, live_features, ref_features, D)

        if decision != "Row":  # Calculate new row
            j += 1
            for k in range(max(0, t - c + 1), t + 1):
                if k < D.shape[0] and k < live_features.shape[1] and j < D.shape[1]:
                    #print(f"Updating D[{t}, {k}]")
                    D[k, j] = EvaluatePathCost(k, j, live_features, ref_features, D)

        # if t < D.shape[0] and j < D.shape[1]:
        #     D[t, j] = EvaluatePathCost(t, j, live, ref, D)
        #print(f"Updated D: \n{D}")
        print (previous, runCount)
        if decision == previous:
            runCount += 1
        else:
            runCount = 1

        if decision != "Both":
            previous = decision

        P.append((t, j))

    return D, P, t, j

def EvaluatePathCost(t, j, X, Y, D):
    distance = dtw.distance(X[:,t], Y[:,j])
    #distance = euclidean(X[:, t], Y[:, j])  # 12-D chroma vectors
    #distance = np.linalg.norm(X[:, t] - Y[:, j])

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

    #if t==0 or j == 0:
        #return "Both"

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
    live_audio, sr = librosa.load(input_audio_path, sr=None)

    #Declare variables
    live_chroma = np.empty(shape=(ref.shape[0], 0)) #Declares an empty array for keeping the chroma features as they are inputted
    audio_queue = queue.Queue()

    #Online tw variables
    P = [(0, 0)]  # list of points in the path cost
    t = 0
    j = 0
    D = np.full((live_chroma.shape[1], ref.shape[1]), np.inf)  # Cost matrix
    #D[0, 0] = 0

    # D[t, j] = EvaluatePathCost(t, j, live_chroma, ref, D) # Calculate cost of first step in cost matrix

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
        # print(live_chroma.shape)
        #run online time warp
        D, P, t, j, = online_tw(live_chroma, ref, D,P,t,j)

    show_dtw(D, np.array(P))


def calculate_chroma_chunk(audio_chunk):
    chroma = librosa.feature.chroma_stft(y=audio_chunk, sr=sr, n_fft=n_fft, hop_length=hop_length)

    return chroma


# show_dtw(D, np.array(P))
# show_colored_path(D, np.array(P))

#Frida
simulate_live_audio_input(audio_path="audio_file.wav", buffer_size=4096, ref=Y_chroma)