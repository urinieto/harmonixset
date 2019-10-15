"""
Created 10-13-19 by Matt C. McCallum
"""


# Local imports
# None.

# Third party imports
from mutagen import mp3
import numpy as np

# Python standard library imports
import struct
import io
import wave
from subprocess import Popen, PIPE


# Set some wav parameters to convert to when reading from mp3.
WAV_BIT_DEPTH = 16
WAV_SAMP_RATE = 44100
WAV_FFMPEG_FMT = 'pcm_s' + str(WAV_BIT_DEPTH) + 'le'


def wav_packing_string(num_frames, num_channels, bit_depth):
    """
    Get the string for packing or unpacking a given number of frames using the struct module.

    Args:
        num_frames: int - The number of frames to cover in the packing string

        num_channels: int - The number of channels in the audio, e.g., 2 for stereo.

        bit_depth: int - The number of bits per sample.

    Return:
        str - The string to be used with the struct module for unpacking, packing the given number of frames for the
        current audio format described in this object.
    """
    unpack_fmt = '<%i' % ( num_frames * num_channels )
    if bit_depth == 16:
        unpack_fmt += 'h'
    elif bit_depth == 32:
        unpack_fmt += 'i'
    else:
        raise Exception('Unsupporeted bit depth format for packing data.')
    return unpack_fmt


def mp3_to_wav(mp3_source_file):
    """
    Converts an mp3 file to a wav file in memory.

    Args:
        mp3_source_file: file-like - A file-like object containing mp3 data.

    Return:
        file-like - A file-like object containing wav data.
    """
    n_channels = mp3.MP3(mp3_source_file).info.channels
    mp3_source_file.seek(0)

    # Decode
    p = Popen(["ffmpeg", "-loglevel", "panic", "-f", "mp3", "-i", "pipe:0", "-map_metadata", "-1", "-vn", "-acodec", WAV_FFMPEG_FMT, "-ac",
            str(n_channels), "-ar", str(WAV_SAMP_RATE), "-f", "wav", 'pipe:1'], stdout=PIPE, stderr=PIPE, stdin=PIPE)
    in_mem_file = io.BytesIO(p.communicate(input=mp3_source_file.read())[0])

    # Fix file size as ffmpeg output via std stream doesn't include a file size.
    in_mem_file.seek(0)
    file_length = in_mem_file.seek(0, 2)
    in_mem_file.seek(4)
    in_mem_file.write(struct.pack('i', file_length - 8))
    in_mem_file.seek(0)
    test_data = in_mem_file.read(10000)
    data_start = test_data.find(b'data')
    in_mem_file.seek(data_start + 4)
    in_mem_file.write(struct.pack('i', file_length - data_start - 8))
    in_mem_file.seek(0)

    return in_mem_file


def mp3_get_samples(mp3_source_file):
    """
    Reads samples from an mp3 file as a numpy array of floats, with channels along the first
    axis and samples along the second axis.

    Args:
        mp3_source_file: file-like - A file-like object containing mp3 data.

    Return:
        np.ndarray - An array of shape (channels, samples) containing the audio sample data as
        floats in the range [-1.0, 1.0]
    """
    # First get the number of channels for later
    n_channels = mp3.MP3(mp3_source_file).info.channels

    # Get an in memory wav object
    in_mem_file = mp3_to_wav(mp3_source_file)

    # Read in wav data
    audio = wave.open(in_mem_file, 'rb')
    num_frames = audio.getnframes()
    data = audio.readframes( num_frames )
    audio.close()
    data = struct.unpack( wav_packing_string( num_frames, n_channels, WAV_BIT_DEPTH ), data )

    return_array = np.zeros( ( n_channels, num_frames ) )
    for channel in range( n_channels ):
        return_array[channel,:] = np.array( data[channel::n_channels] )/( 2.0**WAV_BIT_DEPTH )

    return return_array
