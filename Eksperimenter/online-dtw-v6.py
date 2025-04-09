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

c = 8

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
audio_queue = queue.Queue()
# X_chroma = np.empty(shape=(Y_chroma.shape[0], 0))
x, sr = librosa.load(input_audio_path, sr=None)
X_chroma = librosa.feature.chroma_stft(y=x, sr=sr, n_fft=n_fft, hop_length=hop_length)


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

def EvaluatePathCost(t, j, X, Y, D):
    #distance = dtw.distance(X[:,t], Y[:,j])
    distance = euclidean(X[:, t], Y[:, j])  # 12-D chroma vectors
    print(distance)


    neighbors = []
    if t - 1 >= 0:
        neighbors.append(D[t - 1, j])
    if j - 1 >= 0:
        neighbors.append(D[t , j - 1])
    if t - 1 >= 0 and j - 1 >= 0:
        neighbors.append(D[t - 1, j - 1])

    # print(neighbors)
    if len(neighbors) > 0:
        distance += min(neighbors)

    print(f"d: {distance}, t: {t}, j: {j}")
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

def simulate_live_audio_input(audio_path, buffer_size):
    live_audio = soundfile.read(audio_path) ##Read whole audio file

    #Declare variables
    live_chroma = np.empty(shape=(Y_chroma.shape[0], 0)) #Declares an empty array for keeping the chroma features as they are inputted
    pass

def calculate_chroma_chunk():
    pass

def online_tw():
    pass

live = X_chroma
ref = Y_chroma

D = np.full((live.shape[1], ref.shape[1]), np.inf) # Cost matrix
P = [(0, 0)] #list of points in the path cost
t = 0
j = 0
#D[t, j] = EvaluatePathCost(t, j, live, ref, D)
D[t,j] = euclidean(live[:, t], ref[:,j])

while t < live.shape[1] and j < ref.shape[1]:
    decision = GetInc(t, j, D)

    if decision != "Column": # calculate new row if last step was not a column
        t += 1
        for k in range (max(0, j - c + 1), j + 1):
            if t < D.shape[0] and k < D.shape[1]:
                D[t,k] = EvaluatePathCost(t, k, live, ref, D)

    if decision != "Row": #Calculate new row
        j += 1
        for k in range (max(0, t - c + 1), t + 1):
            if k < D.shape[0] and j < D.shape[1]:
                D[k, j] = EvaluatePathCost(k, j, live, ref, D)

    # if t < D.shape[0] and j < D.shape[1]:
    #     D[t, j] = EvaluatePathCost(t, j, live, ref, D)

    if decision == previous:
        runCount += 1
    else:
        runCount = 1

    if decision != "Both":
        previous = decision


    P.append((t, j))

show_dtw(D, np.array(P))
# show_colored_path(D, np.array(P))


