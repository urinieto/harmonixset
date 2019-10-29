"""Script to download YouTube videos as mp3s.

You should never use this.

But if you do, you need the `youtube-dl` package,
which can be obtained by:

    pip install youtube-dl

But really, you should never use any of this."""

import os
import subprocess
import pandas as pd
from tqdm import tqdm

YOUTUBE_URLS_CSV = "../dataset/youtube_urls.csv"
AUDIO_FORMAT = "mp3"
AUDIO_QUALITY = "128K"
OUTPUT_DIR = "mp3s"


def get_dl_cmd(url, file_id):
    return "youtube-dl {} -x --audio-format {} --audio-quality {} " \
        "-o {}".format(url, AUDIO_FORMAT, AUDIO_QUALITY,
                       os.path.join(OUTPUT_DIR, file_id + ".%(ext)s"))


if __name__ == "__main__":
    # Create output dir if doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Read URLs
    df = pd.read_csv(YOUTUBE_URLS_CSV, sep=",")

    # Download MP3s
    for i, row in tqdm(df.iterrows(), total=len(df)):
        cmd = get_dl_cmd(row["URL"], row["File"])
        subprocess.call(cmd.split(" "))
