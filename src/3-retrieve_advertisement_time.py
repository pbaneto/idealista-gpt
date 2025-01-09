import os
import json
import threading
import pandas as pd
from impl import fetch_content
from concurrent.futures import ThreadPoolExecutor
from functools import partial


def process_href(href, api_key, lock):
    """
    Worker function to process a single HREF.
    Fetches the page, finds the date, and writes to file immediately
    if the date is found.
    """
    url = f'https://www.idealista.com{href}'
    soup = fetch_content(api_key, url)

    date = None
    if soup == -1:
        # Could not fetch or status != 200
        date = "Vendido"
    elif soup == 'END':
        os._exist(1)
    elif soup is not None:
        date_found = soup.find_all('p', class_='date-update-text')
        if date_found:
            date = date_found[0].text

    # Write immediately if we got a date
    if date is not None:
        item = {'href': href, 'date': date}

        # Acquire the lock before writing
        with lock:
            with open('data/advertisement_time.jsonl', 'a') as f:
                json.dump(item, f)
                f.write('\n')


if __name__ == '__main__':

    API_KEY = os.getenv('API_KEY')


    # Get href from all the apartments
    hrefs = []
    for file in os.listdir('data/idealista'):
        with open(f'data/idealista/{file}', 'r') as f:
            for line in f:
                line = line.replace('null', 'None')
                line = eval(line)
                hrefs.append(line['href'])

    if os.path.exists('data/advertisement_time.jsonl'):
        already_processed = set()
        try:
            with open('data/advertisement_time.jsonl', 'r') as f:
                for line in f:
                    line_dict = eval(line)
                    already_processed.add(line_dict['href'])
        except FileNotFoundError:
            pass

    hrefs_to_process = [h for h in hrefs if h not in already_processed]

    # Create a lock for writing to the file
    lock = threading.Lock()

    worker = partial(process_href, api_key=API_KEY, lock=lock)
    with ThreadPoolExecutor(max_workers=3) as executor:
        executor.map(worker, hrefs_to_process)
