# The Harmonix Set

Beats, downbeats, and functional structural annotations for 912 Pop tracks.

## Introduction

This repository contains human annotated labels for 912 Western Pop music tracks, gathered by [Harmonix](https://www.harmonixmusic.com/games).

## Data Overview

The full dataset can be found in the [dataset directory](https://github.com/urinieto/harmonixset/tree/master/dataset), which contains the following:

* [beats_and_downbeats](https://github.com/urinieto/harmonixset/tree/master/dataset/beats_and_downbeats): Directory with a tab-separated file for each track in the dataset, with the following three fields per line containing beats and downbeats: 
    - `beat_time_stamp`: The placement of the beat in seconds (and downbeat, if `beat_position_in_bar` = 1).
    - `beat_position_in_bar`: The number of beat within a bar (when 1, the beat also represents a downbeat).
    - `bar_number`: The number of the bar.
* [segments](https://github.com/urinieto/harmonixset/tree/master/dataset/segments): Directory with a tab-separated file for each track in the dataset, with the following two fields per line containing segmentation data:
    - `boundary_time_stamp`: The placement of a functional segmentation boundary in seconds.
    - `label`: The label of the segment that starts on the current boundary.
* [metadata.tsv](https://github.com/urinieto/harmonixset/blob/master/dataset/metadata.csv): Metadata of the Harmonix Set in a comma-separated file containing the following fields:
    - **File**: File name, used to identify each of the tracks in the dataset.
    - **Title**: Title of the track.
    - **Artist**: Name of the artist of the given track.
    - **Release**: Name of the release (e.g., album, compilation, EP) where the track is found.
    - **Duration**: Duration of the track in seconds.
    - **BPM**: Beats per minute.
    - **Ratio Bars in 4**: Percentage of bars that have 4 beats.
    - **Time Signature**: The time signature of the track.
    - **Genre**: The music genre of the track.
    - **MusicBrainz Id**: The [MusicBrainz](https://musicbrainz.org/) identifier of the track.
    - **Acoustid Id**: The [AcoustID](https://acoustid.org/) identifier of the current track (when available).
* [jams](https://github.com/urinieto/harmonixset/tree/master/dataset/jams): Directory containing [JAMS](https://github.com/marl/jams/) files, one per track, with beats, downbeats, segmentation, and metadata (using JAMS version 0.3.3).
* [YouTube URLs](https://github.com/urinieto/harmonixset/blob/master/dataset/youtube_urls.csv): URLs with the associated YouTube video.
* [YouTube Alignment Scores](https://github.com/urinieto/harmonixset/blob/master/dataset/youtube_alignment_scores.csv): Alignment scores based on Dynamic Time Warping when aligning audio from YouTube videos to the original audio used to annotate the dataset.

## Experiment Results

You may find the raw results in the [results](https://github.com/urinieto/harmonixset/tree/master/results/) folder.

### Segmentation Results

These results include song-level segmentation metrics for the entire dataset, using three different types of beat-synchronized Constant-Q Transform features:

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
* [Audio Alignment](https://github.com/urinieto/harmonixset/blob/master/notebooks/Audio%20Alignment.ipynb): Notebook containing the code to align the audio from YouTube to the original audio used for annotating the dataset. It uses DTW to generate the final audio files and get an alignment score to get a sense of how close the audio from YouTube is from the original one.



## Cite

Please, cite the following paper if you're planning to publish results using this dataset:

[1] Nieto, O., McCallum, M., Davies., M., Robertson, A., Stark, A., Egozy, E., The Harmonix Set: Beats, Downbeats, and Functional Segment Annotations of Western Popular Music, Proc. of the 20th International Society for Music Information Retrieval Conference (ISMIR), Delft, The Netherlands, 2019 ([PDF](https://ccrma.stanford.edu/~urinieto/MARL/publications/ISMIR2019-Nieto-Harmonix.pdf)).
