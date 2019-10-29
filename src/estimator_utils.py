"""
Created 10-13-19 by Matt C. McCallum
"""


# Local imports
from audio_utils import mp3_to_wav

# Third party imports
# None.

# Python standard library imports
from multiprocessing import Pool
import os
import tempfile
import traceback
from functools import wraps
import logging


def estimator(func):
    """
    Simple wrapper function around a function that analyizes a file. 
    The wrapper logs the function that is analyzing the file and the
    file that is being analyzed.

    Args:
        func: function - A file analysis function that takes the filename as the first
        argument.

    Return:
        function - The wrapped function (with logging).
    """
    @wraps(func)
    def est_func(fname, *args, **kwargs):
        logging.info('Analyzing  "{}" estimator for track: {}'.format(func.__name__, fname))
        try:
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.wav', prefix='tmp') as temp_audio_file:
                with open(fname, 'rb') as mp3_file:
                    temp_audio_file.write(mp3_to_wav(mp3_file).read())
                result = func(temp_audio_file.name, *args, **kwargs)
            return result[0], fname
        except Exception:
            logging.error('Failed to analyze "{}" for track: {}'.format(func.__name__, fname), exc_info=True)
            return [[], fname]
    return est_func


def process_estimator(args, estimator, output_dir, num_threads):
    """
    Process all files provided by a given algorithm and places the results
    as new-line separated values in a text file.

    Args:
        args: list(tuple(str, *)) - A list of sets of arguments to pass to the estimator function,
        iteratively. The first in each argument tuple should be the filename of the mp3 audio to
        be analyzed. The remaining arguments may be additional metadata used in estimation.

        estimator: function - A function that takes in an audio filename and produces
        estimates of beat positions as list of float values (in seconds).

        output_dir: str - The path to a directory within which to save the beat position
        estimates as individual text files - one per file specified in `filenames`.

        num_threads: int - The number of threads to use to analyze the set of files.
        each file for analysis is assigned to a single one of these threads, while the
        files themselves are split between threads.
    """
    # Analyze beats
    if num_threads > 1:
        the_pool = Pool(num_threads, maxtasksperchild=1)
        estimates = the_pool.starmap(estimator, args)
        the_pool.close()
        the_pool.join()
    else:
        estimates = [estimator(*arg) for arg in args]

    logging.info('Saving results for estimator: "{}"'.format(estimator.__name__))

    # Save beats
    for est in estimates:
        output_fname = os.path.join(output_dir,  os.path.splitext(os.path.basename(est[1]))[0] + '.txt')
        with open(output_fname, 'w') as f:
            f.write('\n'.join([str(time_marker) for time_marker in est[0]]))
