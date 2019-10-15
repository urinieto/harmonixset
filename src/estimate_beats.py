"""
Created 04-06-19 by Matt C. McCallum

Code for estimating the beat positions from the mp3 audio of the Harmonix dataset 
using the range of algorithms evaluated in the paper.
"""


# Local imports
from harmonix_dataset import HarmonixDataset
from estimator_utils import estimator
from estimator_utils import process_estimator

# Third party imports
import librosa
import madmom

# Python standard library imports
import argparse
import os
import logging
import tempfile


logging.basicConfig(level=logging.INFO)


@estimator
def madmom_1(audio_filename):
    """
    Produces beat time estimates according to the paper:
    
        Florian Krebs, Sebastian Böck and Gerhard Widmer, “An Efficient State Space Model for Joint 
        Tempo and Meter Tracking”, Proceedings of the 16th International Society for Music Information 
        Retrieval Conference (ISMIR), 2015.

    Args:
        filname: str - The filename (with path) to the mp3 audio file to be analyzed by this algorithm.

    Return:
        list(float) - The estimates of the beat positions in the audio as a list of positions in seconds.
    """
    proc = madmom.features.beats.DBNBeatTrackingProcessor(fps=100)
    act = madmom.features.beats.RNNBeatProcessor()(audio_filename)
    return proc(act), audio_filename


@estimator
def madmom_2(audio_filename):
    """
    Produces beat time estimates according to the paper:
    
        Filip Korzeniowski, Sebastian Böck and Gerhard Widmer, “Probabilistic Extraction of Beat Positions 
        from a Beat Activation Function”, Proceedings of the 15th International Society for Music Information 
        Retrieval Conference (ISMIR), 2014.

    Args:
        filname: str - The filename (with path) to the mp3 audio file to be analyzed by this algorithm.

    Return:
        list(float) - The estimates of the beat positions in the audio as a list of positions in seconds.
    """
    proc = madmom.features.beats.CRFBeatDetectionProcessor(fps=100)
    act = madmom.features.beats.RNNBeatProcessor()(audio_filename)
    return proc(act), audio_filename


@estimator
def madmom_3(audio_filename):
    """
    Produces beat time estimates according to the paper:
    
        Sebastian Böck and Markus Schedl, “Enhanced Beat Tracking with Context-Aware Neural Networks”, 
        Proceedings of the 14th International Conference on Digital Audio Effects (DAFx), 2011.

    Args:
        filname: str - The filename (with path) to the mp3 audio file to be analyzed by this algorithm.

    Return:
        list(float) - The estimates of the beat positions in the audio as a list of positions in seconds.
    """
    proc = madmom.features.beats.BeatDetectionProcessor(fps=100)
    act = madmom.features.beats.RNNBeatProcessor()(audio_filename)
    return proc(act), audio_filename


@estimator
def madmom_4(audio_filename):
    """
    Produces beat time estimates according to the paper:
    
        Sebastian Böck and Markus Schedl, “Enhanced Beat Tracking with Context-Aware Neural Networks”, 
        Proceedings of the 14th International Conference on Digital Audio Effects (DAFx), 2011.

    Args:
        filname: str - The filename (with path) to the mp3 audio file to be analyzed by this algorithm.

    Return:
        list(float) - The estimates of the beat positions in the audio as a list of positions in seconds.
    """
    proc = madmom.features.beats.BeatTrackingProcessor(fps=100)
    act = madmom.features.beats.RNNBeatProcessor()(audio_filename)
    return proc(act), audio_filename


@estimator
def ellis(audio_filename):
    """
    Produces beat time estimates according to the paper:
    
        Ellis, Daniel PW. “Beat tracking by dynamic programming.” Journal of New Music Research, 2007.

    Using the implementation contained in the librosa python module.

    Args:
        filname: str - The filename (with path) to the mp3 audio file to be analyzed by this algorithm.

    Return:
        list(float) - The estimates of the beat positions in the audio as a list of positions in seconds.
    """
    signal, _ = librosa.load(audio_filename)
    _, result = librosa.beat.beat_track(signal, units='time')
    return result, audio_filename


def main(audio_dir, results_dir):
    """
    Estimates beat positions for all files in the Harmonix Set, using the estimators published in the paper.

    Args:
        audio_dir: str - The complete path to the directory containing mp3 files for all tracks in the Harmonix Set.

        results_dir: str - The complete path to the directory to save the estimated beat positions to.
    """
    #
    # Get the filenames from the dataset, these should correspond to the filenames of the audio files.
    #
    dataset = HarmonixDataset()
    filenames_and_beats = dataset.beat_time_lists
    filenames = [os.path.join(audio_dir, os.path.splitext(os.path.basename(fname))[0] + '.mp3') for fname in filenames_and_beats.keys()]

    #
    # Compile arguments and run estimators
    #
    # NOTE [matt.c.mccallum 10.13.19]: Librosa is done on a single thread due to a locking issue
    #                                  when using the `librosa.load` function and the multiprocessing module.
    #                                  This causes the `librosa.load` function to hang indefinitely.
    #                                  This may be due to the specific decoder that Librosa uses and so this
    #                                  may be platform dependent as is the decoder selection.
    args = [(fname,) for fname in filenames]
    estimator_args = [
        (args, madmom_1, os.path.join(results_dir, 'Krebs'), 12),
        (args, madmom_2, os.path.join(results_dir, 'Korzeniowski'), 12),
        (args, madmom_3, os.path.join(results_dir, 'Bock_1'), 12),
        (args, madmom_4, os.path.join(results_dir, 'Bock_2'), 12),
        (args, ellis, os.path.join(results_dir, 'Ellis'), 1)
    ]
    for args in estimator_args:
        process_estimator(*args)


if __name__=='__main__':
    THIS_PATH = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser(description='Estimates beat positions for mp3 audio of tracks in the harmonix dataset')
    parser.add_argument('--audio-dir', default=os.path.join(THIS_PATH, '../dataset/audio'), type=str)
    parser.add_argument('--results-dir', default=os.path.join(THIS_PATH, '../results/beats'), type=str)
    kwargs = vars(parser.parse_args())
    main(**kwargs)
