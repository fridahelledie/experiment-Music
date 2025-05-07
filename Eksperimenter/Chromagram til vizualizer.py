import librosa.display
import librosa
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter

# Global audio path and parameters
audio_path = '03BarberSonata2_2.20.wav'
n_fft = 2048
hop_length = 512

# Load audio
y, sr = librosa.load(audio_path)

def plot_spectrogram(S_db, title, sr, hop_length):
    plt.figure(figsize=(12, 4))
    librosa.display.specshow(S_db, sr=sr, hop_length=hop_length, x_axis='time', y_axis='log')
    plt.colorbar(format='%+2.0f dB')
    plt.title(title)
    plt.tight_layout()
    plt.show()

#Standard Spectrogram
def show_standard_spectrogram(y, sr):
    S = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop_length))
    S_db = librosa.amplitude_to_db(S, ref=np.max)
    plot_spectrogram(S_db, "Standard Spectrogram", sr, hop_length)

#Bandpass Filtered Spectrogram
def show_bandpass_spectrogram(y, sr, lowcut=100.0, highcut=5000.0, order=4):
    def bandpass_filter(lowcut, highcut, sr, order=4):
        nyq = 0.5 * sr
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        return b, a

    b, a = bandpass_filter(lowcut, highcut, sr, order)
    y_filtered = lfilter(b, a, y)
    S = np.abs(librosa.stft(y_filtered, n_fft=n_fft, hop_length=hop_length))
    S_db = librosa.amplitude_to_db(S, ref=np.max)
    plot_spectrogram(S_db, "Bandpass Filtered Spectrogram", sr, hop_length)

#Masked Spectrogram (Thresholded)
def show_masked_spectrogram(y, sr, threshold_db=-40):
    S = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop_length))
    S_db = librosa.amplitude_to_db(S, ref=np.max)
    S_masked = np.where(S_db > threshold_db, S_db, -80)
    plot_spectrogram(S_masked, "Masked Spectrogram (Threshold > {} dB)".format(threshold_db), sr, hop_length)

#Harmonic Spectrogram (HPSS)
def show_harmonic_spectrogram(y, sr):
    harmonic, _ = librosa.effects.hpss(y)
    S = np.abs(librosa.stft(harmonic, n_fft=n_fft, hop_length=hop_length))
    S_db = librosa.amplitude_to_db(S, ref=np.max)
    plot_spectrogram(S_db, "Harmonic Spectrogram (Pure Tones Emphasis)", sr, hop_length)

#show_standard_spectrogram(y, sr)
#show_bandpass_spectrogram(y, sr)
show_masked_spectrogram(y, sr)
#show_harmonic_spectrogram(y, sr)