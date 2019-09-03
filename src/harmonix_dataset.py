"""
Created 04-06-19 by Matt C. McCallum
"""


# Local imports
# None.

# Third party imports
import pandas as pd
import numpy as np

# Python standard library imports
import os


DEFAULT_DATASET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../dataset')


class HarmonixDataset(object):
    """
    An object for interfacing with the Harmonix dataset data.
    """

    def __init__(self, dataset_dir=DEFAULT_DATASET_DIR):
        """
        Constructor.

        Args:
            dataset_dir: str - An absolute path to the directory in which the dataset
            dat files exist. They are expected to be organized into subfolders therein,
            "beats_and_downbeats" and "segments".
        """
        # Define dataset info
        self._DATA_DIR = os.path.abspath(dataset_dir)
        self._BEAT_DIR = os.path.join(self._DATA_DIR, 'beats_and_downbeats')
        self._BEAT_MARKER_COLUMN = 'BeatMarker'
        self._BEAT_NUMBER_COLUMN = 'BeatNumber'
        self._BAR_NUMBER_COLUMN = 'BarNumber'
        self._BEATS_COLUMNS = [self._BEAT_MARKER_COLUMN, self._BEAT_NUMBER_COLUMN, self._BAR_NUMBER_COLUMN]
        self._SEGMENT_DIR = os.path.join(self._DATA_DIR, 'segments')
        self._SEG_BOUNDARY_COLUMN = 'SegmentStart'
        self._SEG_LABEL_COLUMN = 'SegmentLabel'
        self._SEGMENTS_COLUMNS = [self._SEG_BOUNDARY_COLUMN, self._SEG_LABEL_COLUMN]

        # Load entire dataset into memory
        self._beat_files = [os.path.join(self._BEAT_DIR, fname) for fname in os.listdir(self._BEAT_DIR)]
        self._seg_files = [os.path.join(self._SEGMENT_DIR, fname) for fname in os.listdir(self._SEGMENT_DIR)]
        self._beat_data = {os.path.splitext(os.path.basename(fname))[0]:pd.read_csv(fname, names=self._BEATS_COLUMNS, delimiter='\t') for fname in self._beat_files}
        self._seg_data = {os.path.splitext(os.path.basename(fname))[0]:pd.read_csv(fname, names=self._SEGMENTS_COLUMNS, delimiter=' ') for fname in self._seg_files}

    @property
    def beat_dataframe(self):
        """
        Get the beat data in the form of a dictionary of pandas dataframes. One for each track.

        Return:
            dict(str, pd.DataFrame) - The beat and downbeat times for every track in the dataset.
            The dataframes are composed of three columns. The first, beat times in seconds. The second,
            beat counts within each bar, e.g., 1, 2, 3, 4, 1, 2.... The third, bar counts, the bar number
            that each beat-row corresponds to.
        """
        return self._beat_data

    @property
    def segment_dataframe(self):
        """
        Get the segment data in the form of a dictionary of pandas dataframes. One for each track.

        Return:
            dict(str, pd.DataFrame) - The beat times in seconds for every track in the dataset. Each dataframe
            has two columns, the first specifying the start location of a segment in seconds, and the second
            column specifying the name / label of that segment. There is an additional 'end' label to specify
            the end of a track.
        """
        return self._seg_data

    @property
    def beat_time_lists(self):
        """
        Returns the annotated positions of beats in seconds for every track.

        Return:
            dict(str, list(float)) - A dictionary containing lists of beat times in second
            for each dictionary key, in turn specifying a track.
        """
        return {fname: data[self._BEAT_MARKER_COLUMN].values for fname, data in self._beat_data.items()}

    def downbeat_time_lists(self, offset):
        """
        Returns the annotated positions of downbeats in seconds for every track.

        Args:
            offset: int - The number of beats to offset the downbeat position by, for example
            0 = the downbeat, 1 = the second beat, etc..

        Return:
            dict(str, list(float)) - A dictionary containing lists of downbeat + beat offset times 
            in seconds for each dictionary key, in turn specifying a track.
        """
        downbeats_each_track = {}
        for fname, df in self._beat_data.items():
            bar_numbers = np.array(df[self._BAR_NUMBER_COLUMN])
            bar_start_idxs = np.argwhere((bar_numbers[1:]-bar_numbers[:-1])>0) + offset # <= We ignore the last bar as it is usually incomplete - e.g., the final beat
            if bar_numbers[0] == 1:
                bar_start_idxs = np.concatenate((np.array([0]), bar_start_idxs.flatten()))
            downbeats_each_track[os.path.splitext(fname)[0]] = df[self._BEAT_MARKER_COLUMN].values[bar_start_idxs].flatten()
        return downbeats_each_track
