import sounddevice as sd
import librosa
import numpy as np
import queue
from librosa.sequence import dtw
import matplotlib.pyplot as plt
import soundfile as sf


X = []  # list of incoming feature vectors

P = []  # alignment path

previous = None  # stores the last movement direction
runCount = 1  # prevent excessive movement in the same direction
MaxRunCount = 100  # Limit on how many consecutive movements in the same direction are allowed.
c = 20  # Warping constraint, defining the alignment window.
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


def EvaluatePathCost(i, j, X, Y):
    if len(X) == 0 or i <= 0 or j <= 0:
        return float('inf')

    X_np = np.hstack(X)
    # Limit the alignment window to c elements
    seq1 = X_np[:, max(0, i - (c // 2)):i]  # Half window for each sequence
    seq2 = Y[:, max(0, j - (c // 2)):j]

    D, wp = dtw(seq1, seq2, metric='euclidean')
    # print(D)
    return D[-1, -1]

def GetInc(i, j, X, Y):  # determines the next movement direction, row, column, or both
    if i < c:  # Forces movement in both directions at the start
        return "Both"

    if runCount > MaxRunCount:  # If too many consecutive moves in one direction, force a switch.
        if previous == "Row":
            return "Column"
        else:
            return "Row"

    # Chooses the movement direction based on the minimum path cost.
    path_costs = {}

    for m in range(1, min(c, i, j)):  # Ensure within bounds
        path_costs[(i, j - m)] = EvaluatePathCost(i, j - m, X, Y)  # Column step
        path_costs[(i - m, j)] = EvaluatePathCost(i - m, j, X, Y)  # Row step
        path_costs[(i - m, j - m)] = EvaluatePathCost(i - m, j - m, X, Y)  # Diagonal step

    (x, y), _ = min(path_costs.items(), key=lambda item: item[1])  # Select minimum cost path

    # New comparison logic to allow for both to move
    row_move = x < i
    col_move = y < j

    if row_move and col_move:
        return "Both"
    elif row_move:
        return "Row"
    elif col_move:
        return "Column"


''' Actual microphone recording - replaced with distorted test audio for the time being
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
        
                if direction == previous:
                    runCount += 1
                else:
                    runCount = 1
                    previous = direction

                print(f"i: {i}, j: {j}, direction: {direction}, runCount: {runCount}")

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
        P = np.array(P)  # Convert to NumPy array so it can be made into a figure

        plt.figure(figsize=(8, 6))
        plt.plot(P[:, 1], P[:, 0], marker="o", linestyle="-", markersize=3)  # j vs i
        plt.xlabel("Reference Audio (j)")
        plt.ylabel("Live Audio (i)")
        plt.title("Alignment Path")
        plt.grid()
        plt.show()
'''

test_audio_path = "audio_file.wav"
test_audio_file = sf.SoundFile(test_audio_path)

# Simulated live input loop
for frame_start in range(0, len(test_audio_file), buffer_size):
    # Read buffer-sized chunk
    audio_chunk = test_audio_file.read(buffer_size, dtype="float32")

    if len(audio_chunk) == 0:
        break  # Stop when the file ends

    # If stereo, convert to mono
    if audio_chunk.ndim > 1:
        audio_chunk = audio_chunk.mean(axis=1)

    # Put into queue (simulating microphone input)
    audio_queue.put(audio_chunk)

    # Process queue as usual
    if not audio_queue.empty():
        audio_chunk = audio_queue.get()

        # Compute chroma features (needs to be done on main thread)
        chroma = librosa.feature.chroma_stft(y=audio_chunk, sr=sr, n_fft=n_fft, hop_length=hop_length)

        X.append(chroma)

        # Find appropriate increase direction, and increase the counter variable for that direction (i or j)
        direction = GetInc(i, j, X, Y)

        if direction == previous:
            runCount += 1
        else:
            runCount = 1
            previous = direction

        print(f"i: {i}, j: {j}, direction: {direction}, runCount: {runCount}")

        if direction == "Row":
            i += 1
        elif direction == "Column":
            j += 1
        else:
            i += 1
            j += 1

        # Store which counter variables match
        P.append((i, j))

P = np.array(P)  # Convert to NumPy array so it can be made into a figure

# Compute chroma features for x
X_chroma = librosa.feature.chroma_stft(y=y, sr=sr)  # list of fixed features

D, wp = dtw(X_chroma, Y, metric='euclidean')
print(D.shape)

print(P.shape)
print(P)

plt.figure(figsize=(8, 6))
plt.imshow(D, cmap='hot')
plt.plot(P[:, 1], P[:, 0], marker="o", linestyle="-", markersize=3)  # j vs i
plt.xlabel("Reference Audio (j)")
plt.ylabel("Live Audio (i)")
plt.title("Alignment Path")
plt.grid()
plt.show()