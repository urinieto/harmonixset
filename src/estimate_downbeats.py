"""
Created 10-13-19 by Matt C. McCallum
"""


# Local imports
from harmonix_dataset import HarmonixDataset
from estimator_utils import estimator
from estimator_utils import process_estimator

# Third party imports
import madmom
import numpy as np

# Python standard library imports
import argparse
import os
import logging


logging.basicConfig(level=logging.INFO)


@estimator
def madmom_1(filename, reference_beats_filename):
    """
    Estimates beats using reference beats and the `DBNBarTrackingProcessor` provided
    with madmom:
        
        S. Bock, F. Korzeniowski, J. Schlüter, F. Krebs, and G. Widmer, “Madmom: A new Python Audio and Music 
        Signal Processing Library,” in Proceedings of the 24th ACM International Conference on Multimedia 
        (ACMMM), Amsterdam, Netherlands, Oct. 2016.

    This estimator uses reference beat positions to estimate downbeat positions.

    Args:
        filname: str - The filename (with path) to the mp3 audio file to be analyzed by this algorithm.

        reference_beats_filename: str - The filename (with path) to a csv file containing the beat positions
        as the first column.

    Return:
        list(float) - The estimates of the downbeat positions in the audio as a list of positions in seconds.
    """
    proc = madmom.features.downbeats.DBNBarTrackingProcessor(beats_per_bar=[3, 4])
    beats = np.loadtxt(reference_beats_filename)[:,0]
    act = madmom.features.downbeats.RNNBarProcessor()((filename, beats))
    downbeat_data = proc(act)
    estimated_beats = downbeat_data[:, 0]
    estimated_downbeats = downbeat_data[:, 1]
    downbeat_inds = np.argwhere((estimated_downbeats[1:]-estimated_downbeats[:-1]) < 0)
    return estimated_beats[downbeat_inds].flatten(), filename


@estimator
def madmom_2(filename, reference_beats_filename):
    """
    Produces downbeat time estimates according to the algorithm described in:

        Sebastian Böck, Florian Krebs and Gerhard Widmer, “Joint Beat and Downbeat Tracking with Recurrent Neural 
        Networks” Proceedings of the 17th International Society for Music Information Retrieval Conference 
        (ISMIR), 2016.

    Args:
        filname: str - The filename (with path) to the mp3 audio file to be analyzed by this algorithm.

        reference_beats_filename: str - Not used, only provided here for consistence of interface with other
        downbeat estimator functions.

    Return:
        list(float) - The estimates of the downbeat positions in the audio as a list of positions in seconds.
    """
    proc = madmom.features.downbeats.DBNDownBeatTrackingProcessor(beats_per_bar=[3, 4], fps=100)
    act = madmom.features.downbeats.RNNDownBeatProcessor()(filename)
    downbeat_data = proc(act)
    estimated_beats = downbeat_data[:, 0]
    estimated_downbeats = downbeat_data[:, 1]
    downbeat_inds = np.argwhere((estimated_downbeats[1:]-estimated_downbeats[:-1]) < 0)
    return estimated_beats[downbeat_inds].flatten(), filename


def main(audio_dir, results_dir, beats_dir):
    """
    Estimates beat positions for all files in the Harmonix Set, using the estimators published in the paper.

    Args:
        audio_dir: str - The complete path to the directory containing mp3 files for all tracks in the Harmonix Set.

        results_dir: str - The complete path to the directory to save the estimated beat positions to.

        beats_dir: str - The complete path to a directory containing reference beat markers for each track. The
        beat markers are to be stored in an individual file for each track, with the first column of that csv file
        pertaining to the beat marker values in seconds.
    """
    #
    # Get the filenames from the dataset, these should correspond to the filenames of the audio files.
    #
    dataset = HarmonixDataset()
    filenames_and_beats = dataset.beat_time_lists
    filenames = [os.path.join(audio_dir, os.path.splitext(os.path.basename(fname))[0] + '.mp3') for fname in filenames_and_beats.keys()]
    beat_fnames = [os.path.join(beats_dir, os.path.splitext(os.path.basename(fname))[0] + '.txt') for fname in filenames]

    #
    # Compile arguments and run estimators
    #
    # NOTE [matt.c.mccallum 10.13.19]: Unfortunately the Durand algorithm provided in the published results is not
    # available as it is not open source. Only madmom algorithms are included below.
    args = list(zip(filenames, beat_fnames))
    estimator_args = [
        (args, madmom_1, os.path.join(results_dir, 'Bock_1'), 12),
        (args, madmom_2, os.path.join(results_dir, 'Bock_2'), 12)
    ]
    for args in estimator_args:
        process_estimator(*args)


if __name__=='__main__':
    THIS_PATH = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser(description='Estimates beat positions for mp3 audio of tracks in the harmonix dataset')
    parser.add_argument('--audio-dir', default=os.path.join(THIS_PATH, '../dataset/audio'), type=str)
    parser.add_argument('--results-dir', default=os.path.join(THIS_PATH, '../results/downbeats'), type=str)
    parser.add_argument('--beats-dir', default=os.path.join(THIS_PATH, '../dataset/beats_and_downbeats'), type=str)
    kwargs = vars(parser.parse_args())
    main(**kwargs)
