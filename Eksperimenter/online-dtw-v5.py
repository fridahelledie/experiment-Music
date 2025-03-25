from logging import exception

import sounddevice as sd
import librosa
import numpy as np
import queue
from librosa.sequence import dtw
import matplotlib.pyplot as plt
import soundfile as sf

P = [(0, 0)] #Warping path

c = 10

#Reference audio
reference_audio_path = "audio_file.wav"
y, sr = librosa.load(reference_audio_path, sr=None)
Y_chroma = librosa.feature.chroma_stft(y=y, sr=sr)

#Input audio
input_audio_path = "audio_file_slowed.wav"
audio_queue = queue.Queue()
X_chroma = np.empty(shape=(Y_chroma.shape[0], 0))

def show_dtw(D, P):
    plt.figure(figsize=(8, 6))
    plt.imshow(D, cmap='hot')
    plt.plot(P[:, 1], P[:, 0], marker="o", linestyle="-", markersize=3)
    plt.xlabel("Reference Audio (j)")
    plt.ylabel("Live Audio (i)")
    plt.title("Alignment Path")
    plt.grid()
    plt.show()

def show_path(P):
    plt.figure(figsize=(8, 6))
    plt.plot(P[:, 1], P[:, 0], marker="o", linestyle="-", markersize=3)
    plt.xlabel("Reference Audio (j)")
    plt.ylabel("Live Audio (i)")
    plt.title("Alignment Path and cost matrix")
    plt.grid()
    plt.show()

def show_matrix(D):
    plt.figure(figsize=(8, 6))
    plt.imshow(D, cmap='hot')
    plt.xlabel("Reference Audio (j)")
    plt.ylabel("Live Audio (i)")
    plt.title("Cost matrix")
    plt.grid()
    plt.show()

def EvaluatePathCost(i, j, X, Y):
    pass

def GetInc(i, j, X, Y):
    pass

def simulated_input(audio_path, buffer_size, X_chroma, Y_chroma, i_start=0, j_start=0):
    input_file = sf.SoundFile(audio_path)
    x_chroma = X_chroma

    for frame in range(0, len(input_file), buffer_size):
        #reads buffer_sizer amount of frames
        audio_chunk = input_file.read(frames=buffer_size, dtype=np.float32)

        #Stop when file ends
        if len(audio_chunk) == 0:
            break

        # If stereo, convert to mono
        if audio_chunk.ndim > 1:
            audio_chunk = audio_chunk.mean(axis=1)

        # Enqueue audio chunk
        audio_queue.put(audio_chunk)

        #Handle audio data
        i, j = P[-1] #current warping path point
        print(f"i:{i}, j:{j}")
        x_chroma, D = process_audio_queue(sr=input_file.samplerate, x_chroma=x_chroma, i=i, j=j)

        #Calculate path
        path_segment = calculate_path_segment(D, i, j)
        for point in path_segment:
            P.append((i + point[0], j + point[1]))

        if len(np.array(path_segment).shape) == 2: #This if statement is to catch a bug that happens
            show_dtw(D, np.array(path_segment))


        # print(f"P : {P}")
        # show_dtw(D=D, P=np.array(P))

    #calculate and show final cost matrix
    D, wp = dtw(x_chroma, Y_chroma, metric='euclidean')
    show_dtw(D, np.array(P))


def process_audio_queue(sr, x_chroma, i, j):
    if not audio_queue.empty():
        audio_chunk = audio_queue.get()

        #Compute chroma feature for audio chunk
        chroma = librosa.feature.chroma_stft(y=audio_chunk, sr=sr)
        new_x_chroma = np.append(x_chroma, chroma, axis=1)
        # print(new_x_chroma.shape)

        #calculate dtw matrix from current position (i, j) to current max
        D, wp = dtw(new_x_chroma[:,i:], Y_chroma[:,j:min(j+c, Y_chroma.shape[1])], metric='euclidean')
        # show_matrix(D)

        return new_x_chroma, D

#Calculates dtw path from current i, j position to
def calculate_path_segment(D, i, j):
    i_current = 0
    j_current = 0
    path_points = []
    # print(D.shape)
    while i_current < D.shape[0] - 1 and j_current < D.shape[1] - 1:
        #add all possible steps to dictionary
        possible_steps = {(i_current, j_current + 1): D[i_current, j_current + 1],
                          (i_current + 1, j_current): D[i_current + 1, j_current],
                          (i_current + 1, j_current + 1): D[i_current + 1, j_current + 1]}

        #choose the cheapest step
        # print(possible_steps.items())
        step, _ = min(possible_steps.items(), key=lambda item: item[1])
        # print(step)
        #Add step to path
        path_points.append((step[0], step[1]))

        #update current path possition
        i_current = step[0]
        j_current = step[1]

    # print (path_points)
    return path_points

simulated_input(input_audio_path, buffer_size=4096, X_chroma=X_chroma, Y_chroma=Y_chroma)