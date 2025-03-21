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

#sd.play(y,sr)

# Wait until audio is finished playing
#sd.wait()

#duration of one sample
sample_duration = 1 / sr
print(f"duration of 1 sample is: {sample_duration:.6f} seconds")

#duration og audio signal in seconds
duration = sample_duration * len(y)
print(f"duration of signal is: {duration:.2f} seconds")

#visualize the waveforms
#plt.figure(figsize=(15,17))
#plt.subplot(1,1,1)
#librosa.display.waveshow(y, sr=sr)
#plt.title("Waveplot of audio")
#plt.ylim((-1,1))

#plt.show()


#calculate the aplitude envelope
def amplitude_envelope(signal, frame_size, hop_length):
    amplitude_envelope = []

    #calculate AE for each frame
    for i in range(0, len(signal), hop_length):
        current_frame_amplitude_envelope = max(signal[i:i+frame_size])
        amplitude_envelope.append(current_frame_amplitude_envelope)

    return np.array(amplitude_envelope)

AE_audio = amplitude_envelope(y, FRAME_SIZE, HOP_LENGTH)

print(len(AE_audio)) #it is the number of frames in the audio

#visualize the amplitude envelope for the audio
frames = range(0,AE_audio.size)
t = librosa.frames_to_time(frames, hop_length=HOP_LENGTH)

plt.figure(figsize=(15,17))

#plt.subplot(1,1,1)
librosa.display.waveshow(y, sr=sr)
plt.plot(t,AE_audio,color='r')
plt.title("Waveplot of audio")
#plt.ylim((-1,1))

plt.show()