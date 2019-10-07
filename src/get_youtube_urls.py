"""Script to get the set of YouTube URLs
for the Harmonix dataset.
"""

import pandas as pd
import re
import urllib.request
import urllib.parse
import time

from tqdm import tqdm
from urllib.error import HTTPError

METADATA_CSV = "../dataset/metadata.csv"
OUT_CSV = "youtube_urls.csv"
SLEEP = 4000


def process():
    # Read metadata
    df = pd.read_csv(METADATA_CSV, sep=",")

    # Search URLs
    urls = []
    for i, row in tqdm(df.iterrows(), total=len(df)):
        query = row["Title"] + ' ' + row["Artist"]
        query_string = urllib.parse.urlencode({"search_query": query})
        try:
            html_content = urllib.request.urlopen(
                "http://www.youtube.com/results?" + query_string)
        except HTTPError:
            time.sleep(SLEEP)
            html_content = urllib.request.urlopen(
                "http://www.youtube.com/results?" + query_string)
        search_results = re.findall(
            r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
        try:
            urls.append({
                "URL": "http://www.youtube.com/watch?v=" + search_results[0],
                "File": row["File"]
            })
            print(query, "http://www.youtube.com/watch?v=" + search_results[0])
        except IndexError:
            print("Warning: Can't get the URL for {}".format(query))

    # Save results
    urls_df = pd.DataFrame(urls)
    urls_df = urls_df[["File", "URL"]]
    urls_df.to_csv(OUT_CSV, index=None)

    print("Saved {} URLs in {}".format(len(urls_df), OUT_CSV))


if __name__ == "__main__":
    process()
