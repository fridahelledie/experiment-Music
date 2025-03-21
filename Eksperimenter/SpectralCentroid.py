import librosa
import librosa.display
import sounddevice as sd
from librosa import samples_like
import matplotlib.pyplot as plt
import numpy as np

#load audio files
audio_path = "1685 Purcell , Trumpet Tune and Air.mp3"
FRAME_SIZE = 1024
HOP_LENGTH = 512

# Load the audio file using librosa
y, sr = librosa.load(audio_path) #sr=None)  # y is the audio time series, sr is the sampling rate. EVT SLET SR=none

sc_audio = librosa.feature.spectral_centroid(y=y, sr=sr, n_fft=FRAME_SIZE, hop_length=HOP_LENGTH)[0]

print(sc_audio.shape) #the number of frames we get

#vizualize the spectral centroid
frames = range(len(sc_audio))
t = librosa.frames_to_time(frames)
plt.figure(figsize=(25,10))

plt.plot(t,sc_audio, color='blue')
plt.title("x axis = time and y is the value of spectral centroid ")
plt.show()

#calculate spectral bandwith
sb_audio = librosa.feature.spectral_bandwidth(y=y, sr=sr, n_fft=FRAME_SIZE, hop_length=HOP_LENGTH)[0]

print(sb_audio.shape) #the number of frames we get

#vizualize the spectral centroid
frames = range(len(sb_audio))
t = librosa.frames_to_time(frames)
plt.figure(figsize=(25,10))

plt.plot(t,sb_audio, color='red')
plt.title("x axis = time and y is the value of spectral bandwidth ")
plt.show()