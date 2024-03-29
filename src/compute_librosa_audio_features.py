"""Script to compute audio features from the
original Harmonix audio files.

Created by Oriol Nieto.
"""

import argparse
import glob
import json
import os
import time
import numpy as np

from pqdm.processes import pqdm

import librosa


INPUT_DIR = "mp3s"
OUTPUT_DIR = "audio_features"
OUT_JSON = "info.json"
N_JOBS = 12

# Features params
SR = 24000
N_FFT = 2048
HOP_LENGTH = 1024
WINDOW = "hann"
CENTER = True
PAD_MODE = "constant"
POWER = 2.0
N_MELS = 256
MEL_FMIN = 30
MEL_FMAX = 12000


def compute_melspecs(audio):
    """Computes a mel-spectrogram from the given audio data."""
    return librosa.feature.melspectrogram(
        y=audio,
        sr=SR,
        n_fft=N_FFT,
        hop_length=HOP_LENGTH,
        window=WINDOW,
        center=CENTER,
        pad_mode=PAD_MODE,
        power=POWER,
        n_mels=N_MELS,
        fmin=MEL_FMIN,
        fmax=MEL_FMAX,
    )


def compute_all_features(mp3_file, output_dir):
    """Computes all the audio features."""
    # Decode and read mp3
    audio, _ = librosa.load(mp3_file, sr=SR)

    # Compute mels
    mel = compute_melspecs(audio)

    # Save
    out_file = os.path.join(
        output_dir, os.path.basename(mp3_file).replace(".mp3", "-mel.npy")
    )
    np.save(out_file, mel)


def save_params(output_dir):
    """Saves the parameters to a JSON file."""
    out_json = os.path.join(output_dir, OUT_JSON)
    out_dict = {
        "librosa_version": librosa.__version__,
        "numpy_version": np.__version__,
        "SR": SR,
        "N_FFT": N_FFT,
        "HOP_LENGTH": HOP_LENGTH,
        "WINDOW": WINDOW,
        "CENTER": CENTER,
        "PAD_MODE": PAD_MODE,
        "POWER": POWER,
        "N_MELS": N_MELS,
        "MEL_FMIN": MEL_FMIN,
        "MEL_FMAX": MEL_FMAX,
    }
    with open(out_json, "w") as fp:
        json.dump(out_dict, fp, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Computes audio features for the Harmonix set.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-i",
        "--input_dir",
        default=INPUT_DIR,
        action="store",
        help="Path to the Harmonix set audio.",
    )
    parser.add_argument(
        "-o",
        "--output_dir",
        default=OUTPUT_DIR,
        action="store",
        help="Output directory.",
    )
    parser.add_argument(
        "-j",
        "--n_jobs",
        default=N_JOBS,
        action="store",
        type=int,
        help="Number of jobs to run in parallel.",
    )

    args = parser.parse_args()
    start_time = time.time()

    # Create output dir if doesn't exist
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    # Read mp3s
    mp3s = glob.glob(os.path.join(args.input_dir, "*.mp3"))

    # Compute features for each mp3 in parallel
    pqdm_args = [[mp3_file, args.output_dir] for mp3_file in mp3s]

    pqdm(
        pqdm_args,
        compute_all_features,
        n_jobs=args.n_jobs,
        argument_type="args",
    )

    # Save parameters
    save_params(args.output_dir)

    # Done!
    print("Done! Took %.2f seconds." % (time.time() - start_time))
