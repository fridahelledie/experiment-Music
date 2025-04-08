import numpy as np
import sounddevice as sd
import librosa
import matplotlib.pyplot as plt
import threading
import queue
import librosa.display


# DLNCO processor with decay state
class DLNCOProcessor:
    def __init__(self, sr=22050, hop_length=512, decay_factor=0.84, local_win=9):
        self.sr = sr
        self.hop_length = hop_length
        self.decay_factor = decay_factor
        self.local_win = local_win
        self.prev_dlnco = None  # decay state

    def compute_chunk(self, y_chunk):
        chroma = librosa.feature.chroma_stft(y=y_chunk, sr=self.sr, hop_length=self.hop_length, n_fft=1024)

        chroma_diff = np.diff(chroma, axis=1)
        chroma_diff = np.maximum(0, chroma_diff)
        chroma_diff = np.pad(chroma_diff, ((0, 0), (1, 0)), mode='constant')

        norm_chroma = np.zeros_like(chroma_diff)
        half_win = self.local_win // 2

        for i in range(chroma_diff.shape[1]):
            start = max(0, i - half_win)
            end = min(chroma_diff.shape[1], i + half_win + 1)
            local_norm = np.linalg.norm(chroma_diff[:, start:end], axis=0)
            max_norm = np.max(local_norm) if np.max(local_norm) != 0 else 1
            norm_chroma[:, i] = chroma_diff[:, i] / max_norm

        dlnco = np.copy(norm_chroma)
        if self.prev_dlnco is not None:
            dlnco[:, 0] += self.decay_factor * self.prev_dlnco

        for i in range(1, dlnco.shape[1]):
            dlnco[:, i] += self.decay_factor * dlnco[:, i - 1]

        self.prev_dlnco = dlnco[:, -1]
        return dlnco


# Settings
samplerate = 22050
blocksize = 2048
hop_length = 1024

# Shared state
audio_q = queue.Queue()
dlnco_proc = DLNCOProcessor(sr=samplerate, hop_length=hop_length)
final_dlnco = []


# Audio callback
def audio_callback(indata, frames, time, status):
    if status:
        print("Stream status:", status)
    audio_q.put(indata.copy().flatten())


# Processing thread
def processing_thread():
    buffer = np.zeros(0)

    while True:
        try:
            new_audio = audio_q.get(timeout=1.0)
        except queue.Empty:
            continue

        buffer = np.concatenate((buffer, new_audio))

        while len(buffer) >= blocksize:
            y_chunk = buffer[:blocksize]
            buffer = buffer[blocksize:]

            dlnco_chunk = dlnco_proc.compute_chunk(y_chunk)
            final_dlnco.append(dlnco_chunk)


# Start background thread
thread = threading.Thread(target=processing_thread, daemon=True)
thread.start()

# Start input stream
print("Streaming... Press Ctrl+C to stop and view the DLNCO feature plot.")
try:
    with sd.InputStream(channels=1, samplerate=samplerate, blocksize=blocksize, callback=audio_callback):
        while True:
            sd.sleep(1000)
except KeyboardInterrupt:
    print("\nStopped. Generating DLNCO plot...")

# After stopping, assemble and plot
if final_dlnco:
    full_dlnco = np.concatenate(final_dlnco, axis=1)
    plt.figure(figsize=(12, 4))
    librosa.display.specshow(full_dlnco, y_axis='chroma', x_axis='time',
                             sr=samplerate, hop_length=hop_length, cmap='coolwarm')
    plt.title("Final DLNCO Feature Plot")
    plt.colorbar()
    plt.tight_layout()
    plt.show()
else:
    print("No DLNCO features were captured.")
