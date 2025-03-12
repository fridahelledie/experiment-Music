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

                # Compute onset strength
                onset_env = librosa.onset.onset_strength(y=audio_chunk, sr=sr, hop_length=hop_length)

                # Get the maximum onset strength in the current chunk
                max_onset_strength = onset_env.max()

                # Check if onset strength exceeds a threshold
                if max_onset_strength > 0.3:  # arbitrarily set threshold, we'll need to test to adjust this
                    onset_message = f"O,{round(max_onset_strength, 3)}"
                    print(f"Onset detected: {onset_message}")
                    Client.send_data(onset_message)

                # Compute chroma features (needs to be done on main thread)
                chroma = librosa.feature.chroma_stft(y=audio_chunk, sr=sr, n_fft=n_fft, hop_length=hop_length)

                chroma_list = np.round(chroma.mean(axis=1), 3)
                chroma_message = "C," + ",".join(map(str, chroma_list))

                # Print chroma feature values
                print("Chroma Features:")
                # print(np.round(chroma.mean(axis=1), 3))  # Print averaged chroma per pitch class
                print(chroma_message)
                Client.send_data(chroma_message)
                print("-" * 50)

    except KeyboardInterrupt:
        print("\nStopped recording.")

Client.disconnect()