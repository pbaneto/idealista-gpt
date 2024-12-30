# Get data for each district

import os
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup


def get_article_info_venta(article):
    article_info = {}
    info = article.find_all('div', class_='item-info-container')

    try:
        item_link = info[0].find_all('a', class_='item-link')
    except Exception as e:
        continue

    try:
        href = item_link[0]['href']
    except Exception as e:
        href = None

    try:
        title = item_link[0]['title']
    except Exception as e:
        title = None

    article_info['href'] = href
    article_info['title'] = title


    divs = info[0].find_all('div')
    if len(divs):
        try:
            price = divs[0].find_all('span', class_='item-price')[0].text
        except Exception as e:
            price = None

        try:
            parking = divs[0].find_all('span', class_='item-parking')[0].text
        except Exception as e:
            parking = None

        try:
            hab = divs[1].find_all('span', class_='item-detail')[0].text
        except Exception as e:
            hab = None

        try:
            meters = divs[1].find_all('span', class_='item-detail')[1].text
        except Exception as e:
            meters = None

        try:
            floor = divs[1].find_all('span', class_='item-detail')[2].text
        except Exception as e:
            floor = None

        try:
            description = info[0].find_all('div', class_='item-description')[0].text
        except Exception as e:
            description = None

        article_info['price'] = price
        article_info['parking'] = parking
        article_info['hab'] = hab
        article_info['meters'] = meters
        article_info['floor'] = floor
        article_info['description'] = description

    with open(f'data/{distrito}_venta.jsonl', 'a') as f:
        json.dump(article_info, f)
        f.write('\n')


def get_article_info_alquiler(article):
    #TODO: write code
    return article


def get_articles(distrito, tipo):

    url = f'https://www.idealista.com/{tipo}-viviendas/madrid/{distrito}/con-pisos'

    while True:
        payload = {"api_key": API_KEY, "url": url, "render": True}
        response = requests.get("http://api.scraperapi.com", params=payload)
        soup = BeautifulSoup(response.text, 'lxml')


        articles = soup.find_all('article')


        # Get everything from each article
        for article in articles:
            if tipo == 'venta':
                try:
                    get_article_info_venta(article)
                except Exception as e:
                    print('ERROR')

            elif tipo == 'alquiler':
                try:
                    get_article_info_alquiler(article)
                except Exception as e:
                    print('ERROR')


        # Get link to next page in idealista
        next_uri = soup.find_all('div', class_='pagination')[0].find_all('a', class_='icon-arrow-right-after')
        if len(next_uri) > 0:
            next_uri = next_uri[0]['href']
            url = f'https://idealista.com/{next_uri}'
        else:
            return



API_KEY = os.getenv('API_KEY')


df = pd.read_csv('data/average_metrics.csv')
distritos = df['distrito'].tolist()

for distrito in distritos:
    get_articles(distrito, 'venta')
    get_articles(distrito, 'alquiler')