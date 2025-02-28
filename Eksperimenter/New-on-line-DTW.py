import sounddevice as sd
import librosa
import numpy as np
import queue
from dtaidistance import dtw

X = []  # list of incoming feature vectors

P = []  # alignment path

previous = None  # stores the last movement direction
runCount = 1  # prevent excessive movement in the same direction
MaxRunCount = 5  # Limit on how many consecutive movements in the same direction are allowed.
c = 10  # Warping constraint, defining the alignment window. (ADJUST)
i = 1
j = 1

# Load audio file
audio_path = "audio_file.wav"
y, sr = librosa.load(audio_path, sr=None)  # using original sampling rate

# Compute chroma features
Y = librosa.feature.chroma_stft(y=y, sr=sr)  # list of fixed features

# Recording settings
sr = 22050  # Sampling rate
buffer_size = 1024  # Number of samples per chunk
n_fft = 1024 #FFT window size
hop_length = 512  # Hop length for STFT

# Queue for transferring audio data
audio_queue = queue.Queue()


# Audio callback function (runs in a separate thread)
def audio_callback(indata, frames, time, status):
    if status:
        print(status)
        return

    # Convert stereo to mono
    audio_chunk = indata.mean(axis=1) if indata.shape[1] > 1 else indata[:, 0]

    # Put audio chunk into queue
    audio_queue.put(audio_chunk)


# Placeholder function for path cost evaluation
def EvaluatePathCost(i, j, X, Y):
    return dtw.distance(X[:i], Y[:j])  # DTW distance up to current index


def GetInc(i, j, X, Y):  # determines the next movement direction, row, column or both

    if i < c:  # Allows movement in both directions at the start (to find the best alignment).
        return "Both"

    if runCount > MaxRunCount:  # If too many consecutive moves in one direction, force a switch.
        if previous == "Row":
            return "Column"
        else:
            return "Row"

    # Chooses the movement direction based on the minimum path cost.
    path_costs = {}

    # For each m from 1 to c, evaluate path costs in both directions, and add to path_costs
    for m in range(1, c):
        path_costs[(i, j - m)] = EvaluatePathCost(i, j - m, X, Y)  # Column movement
        path_costs[(i - m, j)] = EvaluatePathCost(i - m, j, X, Y)  # Row movement

    (x, y), _ = min(path_costs.items(), key=lambda item: item[1])  # Select minimum cost path

    # Determines whether the lowest-cost movement is in time (Row), column (Column), or both.
    if x < i:
        return "Row"
    elif y < j:
        return "Column"
    else:
        return "Both"


# Start the audio stream
with sd.InputStream(callback=audio_callback, samplerate=sr, channels=1, blocksize=buffer_size):
    print("Recording... Press Ctrl+C to stop.")
    try:
        while True:
            # Whenever an audio chunk is processed, get it and compute the feature for it
            if not audio_queue.empty():
                audio_chunk = audio_queue.get()

                # Compute chroma features (needs to be done on main thread)
                chroma = librosa.feature.chroma_stft(y=audio_chunk, sr=sr, n_fft=n_fft, hop_length=hop_length)

                X.append(chroma)

                # Find appropriate increase direction, and increase the counter variable for that direction (i or j)
                direction = GetInc(i, j, X, Y)

                if direction == "Row":
                    i += 1
                elif direction == "Column":
                    j += 1
                else:
                    i += 1
                    j += 1

                # Store which counter variables match
                P.append((i, j))



    except KeyboardInterrupt:
        print("\nStopped recording.")
        print(P)





