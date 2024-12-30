# Get data for each district

import os
import requests
import pandas as pd
import bs4 as BeautifulSoup

API_KEY = os.getenv('API_KEY')


df = pd.read_csv('data/average_metrics.csv')
distritos = df['distrito'].tolist()


distrito = distritos[0]

url = f'https://www.idealista.com/venta-viviendas/madrid/{distrito}/'

payload = {"api_key": API_KEY, "url": url, "render": True}

response = requests.get("http://api.scraperapi.com", params=payload)
soup = BeautifulSoup(response.text, 'lxml')


print(soup)