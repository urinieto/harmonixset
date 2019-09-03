"""
Created 09-01-19 by Matt C. McCallum
"""


# Local imports
from harmonix_dataset import HarmonixDataset 

# Third party imports
import mir_eval
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Python standard library imports
import argparse
import os
import copy


ALGORITHM_DIR_MAP = {
    'Ellis': 'Ellis',
    'Krebs': 'Krebs',
    'Korzeniowski': 'Korzeniowski',
    'Bock 1': 'Bock_1',
    'Bock 2': 'Bock_2'
}


def main(results_dir=None):
    """
    A simple script to evaluate the results of various algorithms on the
    Harmonix Dataset. Each of these algorithms must first be run on the
    Harmonix Dataset audio which at this stage is difficult to get hold of
    due to copyright restrictions. The code here is provided for completeness
    so that a reader may understand exactly how the published results were obtained.

    This code is provided as a single script for the convenience of quick readibility
    to a reader. Further structuring of this code into classes that may be more modular
    and reusable could be beneficial. For example, classes that maintain reading / writing
    directory hierarchies on disk for various result types. However, our primary concern 
    at this stage is to provide a precise demonstration of how the results were evaluated.

    Args:
        results_dir: str - The directory within which to organize results as easily
        readable .txt or .csv files.
    """
    #
    # Read in harmonix dataset
    #
    dataset = HarmonixDataset()
    reference_data = dataset.beat_time_lists
    reference_data = {os.path.splitext(os.path.basename(fname))[0]: value for fname, value in reference_data.items()}

    #
    # Prepare results structures
    #
    results_struct = dict.fromkeys(ALGORITHM_DIR_MAP)
    result_types = {
        'F-Measure': [],
        'Max F-Measure': [],
        'Track ID': []
    }
    for alg in results_struct.keys():
        results_struct[alg] = copy.deepcopy(result_types)

    #
    # Calculate results
    #
    for alg, alg_dir in ALGORITHM_DIR_MAP.items():
        alg_results_dir = os.path.join(results_dir, alg_dir)
        results_files = [os.path.join(alg_results_dir, x) for x in os.listdir(alg_results_dir)]
        for result_file in results_files:
            trk_id = os.path.splitext(os.path.basename(result_file))[0]
            with open(result_file, 'r') as f:
                estimated_beats = [float(x) for x in f.read().split('\n')[:-1]]

            # Compute all variations on the reference beat to compute 'Max F-Measure'
            all_vars = mir_eval.beat._get_reference_beat_variations(reference_data[trk_id])
            all_vars = [all_vars[0], all_vars[2], all_vars[3], all_vars[4]]

            scores = [mir_eval.beat.f_measure(np.array(variation), np.array(estimated_beats)) for variation in all_vars]
            results_struct[alg]['Max F-Measure'] += [max(scores)]
            results_struct[alg]['F-Measure'] += [scores[0]]
            results_struct[alg]['Track ID'] += [trk_id]

    #
    # Save results struct to file
    #
    for alg_name, alg_results in results_struct.items():
        data = pd.DataFrame(alg_results)
        data.to_csv(os.path.join(results_dir, alg_name + '.csv'))

    #
    # Plot results
    #
    plotting_results = {
        'F-Measure': {},
        'Max F-Measure': {}
    }

    # A bit of reorginization of the results dict to group things for plotting
    # together.
    for alg, results in results_struct.items():
        for res_type, res_values in results.items():
            if res_type != 'Track ID':
                plotting_results[res_type][alg] = res_values

    plots = [[],[]]
    poss = [[1, 3, 5, 7, 9],
            [0, 2, 4, 6, 8]]
    colors = ['purple', 'turquoise']
    idx = 0
    fig, ax = plt.subplots()
    for result_type, result_algs in plotting_results.items():
        c1 = colors[idx]
        plots[idx] = ax.boxplot(list(result_algs.values()), labels=list(result_algs.keys()),
                    positions=poss[idx],
                notch=True, patch_artist=True,
                boxprops=dict(facecolor=c1, color="purple"),
                capprops=dict(color=c1),
                whiskerprops=dict(color=c1),
                flierprops=dict(color=c1, markeredgecolor=c1),
                medianprops=dict(color=c1))
        idx += 1

    #
    # Format plot and save to disk
    #
    plt.xticks([0.5, 2.5, 4.5, 6.5, 8.5], list(ALGORITHM_DIR_MAP.keys()))
    plt.xlim(-0.5, 9.5)
    plt.ylabel('F-Measure')
    plt.tight_layout()
    save_fname = os.path.join(results_dir, 'beats.pdf')
    ax.legend([plots[1]["boxes"][0], plots[0]["boxes"][0]], 
              ['F-Measure', 'Max F-Measure'], loc='lower right')
    plt.ylim(-0.05, 1)
    plt.savefig(save_fname)


if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Evaluates the performance of beat tracking algorithms and plots these results.')
    parser.add_argument('--results-dir', default='../results/beats/', type=str)
    kwargs = vars(parser.parse_args())
    main(**kwargs)
