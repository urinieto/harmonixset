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
    'Bock 1': 'Bock_1',
    'Bock 2': 'Bock_2',
    'Durand': 'Durand'
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
    reference_data = dataset.downbeat_time_lists(0)
    reference_data = {os.path.splitext(os.path.basename(fname))[0]: value for fname, value in reference_data.items()}
    # NOTE [matt.c.mccallum 09.02.19]: The results provided by Durand estimated the position of the end of the first
    #                                  beat in the bar. This is equivalent to downbeat estimation and is easily converted
    #                                  to conventional downbeats by subtracting a beat. As such we evaluate Durand's algorithm
    #                                  with respect to the end of the first beat position.
    reference_data_durand = dataset.downbeat_time_lists(1)
    reference_data_durand = {os.path.splitext(os.path.basename(fname))[0]: value for fname, value in reference_data_durand.items()}

    #
    # Prepare results structures
    #
    results_struct = dict.fromkeys(ALGORITHM_DIR_MAP)
    result_types = {
        'F-Measure': [],
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
            # NOTE [matt.c.mccallum 09.02.19]: The results provided by Durand estimated the position of the end of the first
            #                                  beat in the bar. This is equivalent to downbeat estimation and is easily converted
            #                                  to conventional downbeats by subtracting a beat. As such we evaluate Durand's algorithm
            #                                  with respect to the end of the first beat position.
            if alg=='Durand':
                ref = reference_data_durand[trk_id]
            else:
                ref = reference_data[trk_id]
            mir_eval.beat.validate(ref, np.array(estimated_beats))
            results_struct[alg]['F-Measure'] += [mir_eval.beat.f_measure(ref, np.array(estimated_beats))]
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
        'F-Measure': {}
    }

    # A bit of reorginization of the results dict to group things for plotting
    # together.
    for alg, results in results_struct.items():
        for res_type, res_values in results.items():
            if res_type != 'Track ID':
                plotting_results[res_type][alg] = res_values

    c1 = 'turquoise'
    for result_type, result_algs in plotting_results.items():
        plt.figure()
        box2 = plt.boxplot(list(result_algs.values()), labels=list(result_algs.keys()),
            notch=True, patch_artist=True,
            boxprops=dict(facecolor=c1, color="purple"),
            capprops=dict(color=c1),
            whiskerprops=dict(color=c1),
            flierprops=dict(color=c1, markeredgecolor=c1),
            medianprops=dict(color=c1))

        #
        # Format plot and save to disk
        #
        plt.ylabel(result_type)
        plt.tight_layout()
        plt.savefig(os.path.join(results_dir, 'downbeats.pdf'))


if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Evaluates the performance of beat tracking algorithms and plots these results.')
    parser.add_argument('--results-dir', default='../results/downbeats/', type=str)
    kwargs = vars(parser.parse_args())
    main(**kwargs)
