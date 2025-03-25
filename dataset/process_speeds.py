import pandas as pd
import re
import requests
from urllib.parse import urlparse
import multiprocessing as mp
from tqdm import tqdm
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'dataset/link_validation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

def clean_url(url):
    return url.split('(')[0].strip()

def check_link_validity(url):
    try:
        clean_url_str = clean_url(url)
        response = requests.head(clean_url_str, allow_redirects=True)
        is_valid = response.status_code == 200
        logging.info(f"URL: {clean_url_str} - Status: {'Valid' if is_valid else 'Invalid'}")
        return is_valid
    except Exception as e:
        logging.error(f"Error checking URL {url}: {str(e)}")
        return False

def process_urls_chunk(urls):
    return [check_link_validity(url) for url in urls]

def extract_speed(url):
    # regex pattern for speed information was generated using AI
    speed_match = re.search(r'\((needs to be )?([-+]?\d+\.?\d*)% (sped-up|slowed)\)', url)
    if speed_match:
        speed = float(speed_match.group(2))
        if speed_match.group(3) == "slowed":
            speed = -speed
        return speed
    
    if "(backwards)" in url:
        return -100  
    
    return 0  

def main():
    logging.info("Reading CSV file...")
    df = pd.read_csv('dataset/youtube_urls.csv')
    
    logging.info("Cleaning URLs...")
    df['clean_url'] = df['URL'].apply(clean_url)
    
    logging.info("Extracting speed information...")
    df['speed'] = df['URL'].apply(extract_speed)
    
    logging.info("Starting link validation with multiprocessing...")
    num_processes = mp.cpu_count()
    chunk_size = len(df) // num_processes
    urls_chunks = [df['clean_url'].iloc[i:i + chunk_size].tolist() for i in range(0, len(df), chunk_size)]
    
    with mp.Pool(processes=num_processes) as pool:
        results = []
        for chunk_result in tqdm(pool.imap(process_urls_chunk, urls_chunks), 
                               total=len(urls_chunks),
                               desc="Validating links"):
            results.extend(chunk_result)
    
    df['link_valid'] = results
    
    df['URL'] = df['clean_url']
    df = df.drop('clean_url', axis=1)
    
    logging.info("Saving results to CSV...")
    df.to_csv('dataset/youtube_urls_with_speed.csv', index=False)
    
    valid_count = df['link_valid'].sum()
    total_count = len(df)
    logging.info(f"Processing complete. Valid links: {valid_count}/{total_count} ({valid_count/total_count*100:.2f}%)")
    logging.info("Results saved to youtube_urls_with_speed.csv")

if __name__ == '__main__':
    main() 