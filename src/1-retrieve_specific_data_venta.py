import os
import json
import pandas as pd
from impl import fetch_content


def get_article_info(article, tipo):
    article_info = {}
    info = article.find_all('div', class_='item-info-container')
    item_link = info[0].find_all('a', class_='item-link')

    if len(item_link):
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
    for div in divs:
        if 'price-row' in div.get('class'):
            try:
                price = div.find_all('span', class_='item-price')[0].text
            except Exception as e:
                price = None
            try:
                parking = div.find_all('span', class_='item-parking')[0].text
            except Exception as e:
                parking = None

        elif 'item-detail-char' in div.get('class'):
            spans = div.find_all('span')
            details = []
            for span in spans:
                details.append(span.text)

    try:
        description = info[0].find_all('div', class_='item-description')[0].text
    except Exception as e:
        description = None

    article_info['price'] = price
    article_info['parking'] = parking
    article_info['details'] = details
    article_info['description'] = description

    with open(f'data/{distrito}_{tipo}.jsonl', 'a') as f:
        json.dump(article_info, f)
        f.write('\n')

    return article



def get_articles(distrito, tipo, zona):
    if zona == 'centro':
        url = f'https://www.idealista.com/{tipo}-viviendas/madrid/{distrito}/con-pisos'
    else:
        url = f'https://www.idealista.com/{tipo}-viviendas/{distrito}-madrid/'

    while True:
        soup = fetch_content(API_KEY, url)
        if soup is None:
            break

        articles = soup.find_all('article', class_='item')

        # Get everything from each article
        for article in articles:
            try:
                get_article_info(article, tipo)
            except Exception as e:
                print('ERROR')

        # Get link to next page in idealista
        try:
            next_uri = soup.find_all('div', class_='pagination')[0].find_all('a', class_='icon-arrow-right-after')
            next_uri = next_uri[0]['href']
            url = f'https://idealista.com{next_uri}'
        except Exception as e:
            return



if __name__ == '__main__':

    API_KEY = os.getenv('API_KEY')

    df = pd.read_csv('data/average_metrics.csv')
    distritos = df[['distrito', 'tipo']].set_index('distrito')['tipo'].to_dict()

    for distrito, zona in distritos.items():
        if not os.path.exists(f'data/{distrito}_venta.jsonl'):
            get_articles(distrito, 'venta', zona)
        else:
            print(distrito, 'venta already exists')

        if not os.path.exists(f'data/{distrito}_alquiler.jsonl'):
            get_articles(distrito, 'alquiler', zona)
        else:
            print(distrito, 'alquiler already exists')