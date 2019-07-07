# The Harmonix Set

Beats, downbeats, and functional structural annotations for 912 Pop tracks.

## Introduction

This repository contains human annotated labels for 912 Western Pop music tracks, gathered by [Harmonix](https://www.harmonixmusic.com/games).

## Data Overview

The full dataset can be found in the [dataset folder](https://github.com/urinieto/harmonixset/tree/master/dataset), which contains the following:

* [beats_and_downbeats](https://github.com/urinieto/harmonixset/tree/master/dataset/beats_and_downbeats): Folder with a tab-separatted txt file for each file in the dataset, with the following three fields per line: 
    - `beat_time_stamp`: The placement of the beat (and downbeat, if `beat_position_in_bar` = 1).
    - `beat_position_in_bar`: The number of beat within a bar (when 1, the beat also represents a downbeat).
    - `bar_number`: The number of the bar.

## Experiment Results

You may find the raw results in the [results](https://github.com/urinieto/harmonixset/tree/master/results/) folder.

### Segmentation Results

These results include song-level segmentation metrics for the entire dataset, using three different types of beat-syncrhonized Constant-Q Transform features:

* [annot_beats.csv](https://github.com/urinieto/harmonixset/blob/master/results/segmentation/annot_beats.csv): Annotated beats from the Harmonix set.
* [korz_beats.csv](https://github.com/urinieto/harmonixset/blob/master/results/segmentation/korz_beats.csv): Korzeniowski beats from [madmom](https://github.com/CPJKU/madmom).
* [librosa_beats.csv](https://github.com/urinieto/harmonixset/blob/master/results/segmentation/librosa_beats.csv): Beats computed using the default [librosa](https://github.com/librosa/librosa) beat tracker.

These results were computed using the following libraries with their default parameters:

* librosa 0.6.3 (on a macOS 10.13.6 with its default CoreAudio MP3 decoder)
* madmom 0.16.1
* mir\_eval 0.5
* msaf 0.1.8-dev

## Additional Content

A couple of Jupyter notebooks are also included:

* [Dataset Analysis](https://github.com/urinieto/harmonixset/blob/master/notebooks/Dataset%20Analysis.ipynb): The plots of the original publication [1] were produced using this notebook, which employs the results discussed above.
* [JAMS Creation](https://github.com/urinieto/harmonixset/blob/master/notebooks/JAMS%20Creation.ipynb): This notebook was used to generate the JAMS files of the Harmonix Set.



## Cite

Please, cite the following paper if you're planning to publish results using this dataset:

[1] Nieto, O., McCallum, M., Davies., M., Robertson, A., Stark, A., Egozy, E., The Harmonix Set: Beats, Downbeats, and Functional Segment Annotations of Western Popular Music, Proc. of the 20th International Society for Music Information Retrieval Conference (ISMIR), Delft, The Netherlands, 2019 ([PDF](https://ccrma.stanford.edu/~urinieto/MARL/publications/ISMIR2019-Nieto-Harmonix.pdf)).
