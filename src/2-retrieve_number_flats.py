import os
import json
import pandas as pd
from impl import fetch_content



API_KEY = os.getenv('API_KEY')


if os.path.exists('data/number_apartments.jsonl'):
    already_processed = []
    with open('data/number_apartments.jsonl', 'r') as f:
        for line in f:
            line = eval(line)
            already_processed.append(line['distrito'])


df = pd.read_csv('data/average_metrics.csv')
items = df[['distrito', 'tipo']].set_index('distrito')['tipo'].to_dict()


for distrito, tipo in items.items():
    if distrito in already_processed:
        continue

    if tipo == 'centro':
        url = f'https://www.idealista.com/maps/madrid/{distrito}/'
    else:
        url = f'https://www.idealista.com/maps/{distrito}-madrid/'

    soup = fetch_content(API_KEY, url)

    if soup is None or soup == -1 or soup == 'END':
        print('ERROR')

    divs = soup.find_all('div', class_='space-y-2')
    for div in divs:
        como_son = div.find_all('h2', class_='h2')
        if len(como_son) and 'Como son' in como_son[0].text:
            viviendas = como_son[0].find_next('p').text


    with open('data/number_apartments.jsonl', 'a') as f:
        result = {
            'distrito': distrito,
            'viviendas': viviendas
        }
        json.dump(result, f)
        f.write('\n')
