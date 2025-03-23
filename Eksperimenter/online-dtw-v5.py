import sounddevice as sd
import librosa
import numpy as np
import queue
from librosa.sequence import dtw
import matplotlib.pyplot as plt
import soundfile as sf

P = [] #Warping path

#current warping path end point
i = 0 # input
j = 0 # reference

#Reference audio
reference_audio_path = "audio_file.wav"
y, sr = librosa.load(reference_audio_path, sr=None)
Y_chroma = librosa.feature.chroma_stft(y=y, sr=sr)

#Input audio
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
    plt.title("Alignment Path")
    plt.grid()
    plt.show()

def show_matrix(D):
    plt.figure(figsize=(8, 6))
    plt.imshow(D, cmap='hot')
    plt.xlabel("Reference Audio (j)")
    plt.ylabel("Live Audio (i)")
    plt.title("Alignment Path")
    plt.grid()
    plt.show()

def EvaluatePathCost(i, j, X, Y):
    pass

def GetInc(i, j, X, Y):
    pass

def simulated_input(audio_path, buffer_size, X_chroma):
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
        x_chroma = process_audio_queue(sr=input_file.samplerate, x_chroma=x_chroma)

    D, wp = dtw(x_chroma, Y_chroma, metric='euclidean')
    show_matrix(D)


def process_audio_queue(sr, x_chroma):
    if not audio_queue.empty():
        audio_chunk = audio_queue.get()

        #Compute chroma feature for audio chunk
        chroma = librosa.feature.chroma_stft(y=audio_chunk, sr=sr)
        new_x_chroma = np.append(x_chroma, chroma, axis=1)

        #calculate dtw matrix from current position (i, j) to current max
        # print(x_chroma.shape)
        # print(Y_chroma.shape)
        # D, wp = dtw(new_x_chroma, Y_chroma, metric='euclidean')
        # show_matrix(D)
        return new_x_chroma

#Calculates dtw path from current i, j position to
def calculate_path_segment(D, i, j, I, J):
    i_current = i
    j_current = j
    path_points = ()
    while i_current != I and j_current != J:
        possible_paths = {(i_current, j_current + 1): D[i_current, j_current + 1],
                          (i_current, j_current): D[i_current + 1, j_current],
                          (i_current + 1, j_current + 1): D[i_current + 1, j_current + 1]}



    pass

simulated_input(reference_audio_path, buffer_size=1048, X_chroma=X_chroma)