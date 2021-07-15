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

from joblib import Parallel, delayed

import madmom
from madmom.processors import ParallelProcessor, SequentialProcessor
from madmom.audio.signal import SignalProcessor, FramedSignalProcessor
from madmom.audio.stft import ShortTimeFourierTransformProcessor
from madmom.audio.spectrogram import (
    FilteredSpectrogramProcessor, LogarithmicSpectrogramProcessor,
    SpectrogramDifferenceProcessor)


INPUT_DIR = "mp3s"
OUTPUT_DIR = "madmom_features"
OUT_JSON = "info.json"
N_JOBS = 12

# Features params
SR = 44100
FRAME_SIZES = [1024, 2048, 4096]
NUM_BANDS = [3, 6, 12]
FPS = 100
FMIN = 30
FMAX = 17000
DIFF_RATIO = 0.5


def compute_all_features(mp3_file, output_dir):
    """Computes all the audio features."""
    sig = SignalProcessor(num_channels=1, sample_rate=SR)

    # process the multi-resolution spec & diff in parallel
    multi = ParallelProcessor([])
    for frame_size, num_band in zip(FRAME_SIZES, NUM_BANDS):
        frames = FramedSignalProcessor(frame_size=frame_size, fps=FPS)
        stft = ShortTimeFourierTransformProcessor()  # caching FFT window
        filt = FilteredSpectrogramProcessor(
            num_bands=num_band, fmin=FMIN, fmax=FMAX, norm_filters=True)
        spec = LogarithmicSpectrogramProcessor(mul=1, add=1)
        diff = SpectrogramDifferenceProcessor(
            diff_ratio=DIFF_RATIO, positive_diffs=True, stack_diffs=np.hstack)

        # process each frame size with spec and diff sequentially
        multi.append(SequentialProcessor((frames, stft, filt, spec, diff)))

    # stack the features and processes everything sequentially
    pre_processor = SequentialProcessor((sig, multi, np.hstack))

    # Compute mels
    feat = pre_processor(mp3_file)

    # Save
    out_file = os.path.join(
        output_dir, os.path.basename(mp3_file).replace(".mp3", "-seq.npy"))
    np.save(out_file, feat)


def save_params(output_dir):
    """Saves the parameters to a JSON file."""
    out_json = os.path.join(output_dir, OUT_JSON)
    out_dict = {
        "madmom_version": madmom.__version__,
        "numpy_version": np.__version__,
        "SR": SR,
        "FRAME_SIZES": FRAME_SIZES,
        "NUM_BANDS": NUM_BANDS,
        "FPS": FPS,
        "FMIN": FMIN,
        "FMAX": FMAX,
        "DIFF_RATIO": DIFF_RATIO
    }
    with open(out_json, 'w') as fp:
        json.dump(out_dict, fp, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                description="Computes audio features for the Harmonix set.",
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-i",
                        "--input_dir",
                        default=INPUT_DIR,
                        action="store",
                        help="Path to the Harmonix set audio.")
    parser.add_argument("-o",
                        "--output_dir",
                        default=OUTPUT_DIR,
                        action="store",
                        help="Output directory.")
    parser.add_argument("-j",
                        "--n_jobs",
                        default=N_JOBS,
                        action="store",
                        type=int,
                        help="Number of jobs to run in parallel.")

    args = parser.parse_args()
    start_time = time.time()

    # Create output dir if doesn't exist
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    # Read mp3s
    mp3s = glob.glob(os.path.join(args.input_dir, "*.mp3"))

    # Compute features for each mp3 in parallel
    Parallel(n_jobs=args.n_jobs)(
        delayed(compute_all_features)(mp3_file, args.output_dir)
        for mp3_file in mp3s)

    # Save parameters
    save_params(args.output_dir)

    # Done!
    print("Done! Took %.2f seconds." % (time.time() - start_time))
