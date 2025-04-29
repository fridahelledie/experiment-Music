import librosa
import numpy as np
from scipy.spatial.distance import cdist


def calculation():
    #Audio files load
    ref_audio, sr = librosa.load("piano-logo-145236.mp3", sr=None)
    live_audio, sr = librosa.load("piano_50_procent_slowed.wav", sr=sr)

    hop_length = 1024  #bruges til chroma features og time difference

    #Exctract chroma features
    chroma_ref = librosa.feature.chroma_cqt(y=ref_audio, sr=sr, hop_length=hop_length)
    chroma_live = librosa.feature.chroma_cqt(y=live_audio, sr=sr, hop_length=hop_length)

    #cos distance between chroma
    cosD = cdist(chroma_ref.T, chroma_live.T, metric='cosine')

    #Apply DTW to the distance matrix
    _, wp = librosa.sequence.dtw(C=cosD)
    wp = np.array(wp)[::-1]  # warping path

    #Time diff between frames, dette er det vi skal bruge til at finde delay
    time_per_frame = hop_length / sr
    time_diff = [(j - i) * time_per_frame for i, j in wp]
    delay = np.median(time_diff)

    print(f"Delay: {delay * 1000:.2f} ms")

# Run it
calculation()
