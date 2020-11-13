import os
import glob
import librosa
import numpy as np
import json
from joblib import Parallel, delayed

INPUT_DIR = "harmonix_mp3s"
OUTPUT_DIR = "audio_features"
OUT_JSON = "info.json"
N_JOBS = 12

# Features params
SR = 22050
N_MELS = 80
N_FFT = 2048
HOP_LENGTH = 1024
MEL_FMIN = 0
MEL_FMAX = None


def compute_melspecs(audio):
    """Computes a mel-spectrogram from the given audio data."""
    return librosa.feature.melspectrogram(y=audio,
                                          sr=SR,
                                          n_mels=N_MELS,
                                          n_fft=N_FFT,
                                          hop_length=HOP_LENGTH,
                                          fmin=MEL_FMIN,
                                          fmax=MEL_FMAX)


def compute_all_features(mp3_file):
    """Computes all the audio features"""
    # Decode and read mp3
    audio, _ = librosa.load(mp3_file, sr=SR)

    # Compute mels
    mel = compute_melspecs(audio)

    # Save
    out_file = os.path.join(
        OUTPUT_DIR, os.path.basename(mp3_file).replace(".mp3", "-mel.npy"))
    np.save(out_file, mel)


def save_params():
    """Saves the parameters to a JSON file."""
    out_json = os.path.join(OUTPUT_DIR, OUT_JSON)
    out_dict = {
        "librosa_version": librosa.__version__,
        "numpy_version": np.__version__,
        "SR": SR,
        "N_MELS": N_MELS,
        "N_FFT": N_FFT,
        "HOP_LENGTH": HOP_LENGTH,
        "MEL_FMIN": MEL_FMIN,
        "MEL_FMAX": MEL_FMAX
    }
    with open(out_json, 'w') as f:
        json.dump(out_dict, f, indent=4)


if __name__ == "__main__":
    # Create output dir if doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Read mp3s
    mp3s = glob.glob(os.path.join(INPUT_DIR, "*.mp3"))

    # Compute features for each mp3 in parallel
    Parallel(n_jobs=N_JOBS)(
        delayed(compute_all_features)(mp3_file) for mp3_file in mp3s)

    # Save parameters
    save_params()
