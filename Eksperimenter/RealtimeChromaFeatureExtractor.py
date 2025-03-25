import sounddevice as sd
import librosa
import numpy as np
import queue
import Client

# Audio settings
sr = 22050  # Sampling rate
buffer_size = 2048  # Number of samples per chunk
n_fft = 4096  # FFT window size
hop_length = 1024  # Hop length for STFT

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

#Connect to Unity
if not Client.connect():
    print("Could not connect to unity!")

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

                chroma_list = np.round(chroma.mean(axis=1), 3)
                data = ""
                for i in range(len(chroma_list)):
                    if i > 0:
                        data += ","
                    data += str(chroma_list[i])

                # Print chroma feature values
                print("Chroma Features:")
                # print(np.round(chroma.mean(axis=1), 3))  # Print averaged chroma per pitch class
                print(data)
                Client.send_data(data)
                print("-" * 50)

    except KeyboardInterrupt:
        print("\nStopped recording.")

Client.disconnect()