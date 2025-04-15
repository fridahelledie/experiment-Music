import librosa
import numpy as np

def calculation(ref_audio, live_audio):

    #Load audio files
    ref_audio, sr_ref = librosa.load(ref_audio, sr=None)
    live_audio, sr_live = librosa.load(live_audio, sr=None)
