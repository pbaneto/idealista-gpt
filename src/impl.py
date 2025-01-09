import os
import time
import requests
from bs4 import BeautifulSoup

API_KEY = os.getenv('API_KEY')

def fetch_content(api_key, url, max_retries=2, delay=2):
    payload = {
        "api_key": api_key,
        "url": url,
        "render": True,
    }

    for attempt in range(max_retries):
        try:
            response = requests.get("http://api.scraperapi.com", params=payload)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')
                return soup
            elif response.status_code == 404:
                return -1
            elif response.status_code == 403:
                return 'END'
            else:
                print(f"Attempt {attempt + 1} failed with status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Attempt {attempt + 1} encountered an error: {e} {url}")

        time.sleep(delay)

    print("Max retries reached. Continuing without successful response.")
    return None
