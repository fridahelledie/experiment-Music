import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt


# Load audio file
audio_path = "120_Am_Piano_2_481.wav"
y, sr = librosa.load(audio_path, sr=None)  # using original sampling rate

# Compute chroma features
chroma = librosa.feature.chroma_stft(y=y, sr=sr)

# Get time vector for chroma frames
times = librosa.frames_to_time(np.arange(chroma.shape[1]), sr=sr)


# Function to get chroma at a specific time
def get_chroma_at_time(target_time):
    # Find the closest frame index to the given time
    frame_idx = np.argmin(np.abs(times - target_time))
    chroma_vector = chroma[:, frame_idx]  # Extract chroma vector at that frame
    return chroma_vector

# Onset strength envelope is a function that tracks changes in energy over time
onset_envelope = librosa.onset.onset_strength(y=y, sr=sr)

    # converts onset frame indices to actual timestamps in seconds
times = librosa.times_like(onset_envelope, sr=sr)

    # detects the points in time where new notes or percussive events start, uses onset_envelope to find peaks
onset_frames = librosa.onset.onset_detect(onset_envelope=onset_envelope, sr=sr)


target_time = 5.0
chroma_at_time = get_chroma_at_time(target_time)

# Print the chroma vector
print(f"Chroma vector at {target_time} seconds:")
print(chroma_at_time)

# Plot the chroma features
plt.figure(figsize=(10, 4))
librosa.display.specshow(chroma, x_axis='time', y_axis='chroma', cmap='Greys')
plt.colorbar(label="Intensity")
plt.title("Chroma Features")

#plot detected onsets as vertical red dashed lines
for onset in onset_frames:
    plt.axvline(onset, color='r', linestyle='--',label='Onset' if onset== onset_frames[0] else "")

plt.xlabel("Time (s)")
plt.ylabel("Pitch Class")
plt.legend()
plt.show()


