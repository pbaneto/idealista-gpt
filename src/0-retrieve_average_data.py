import os
import requests
import pandas as pd
import unicodedata
from bs4 import BeautifulSoup

API_KEY = os.getenv("API_KEY")


def transform_word(word):
    # Remove accents
    word = ''.join(
        char for char in unicodedata.normalize('NFD', word)
        if unicodedata.category(char) != 'Mn'
    )
    word = word.lower()
    word = word.replace(' ', '-')
    return word


def get_historic(x):
    tipo = x['tipo']
    distrito = x['distrito']

    if tipo == 'centro':
        urls = {
            'venta': f'https://www.idealista.com/sala-de-prensa/informes-precio-vivienda/venta/madrid-comunidad/madrid-provincia/madrid/{distrito}/historico/',
            'alquiler': f'https://www.idealista.com/sala-de-prensa/informes-precio-vivienda/alquiler/madrid-comunidad/madrid-provincia/madrid/{distrito}/historico/'
        }
    else:
        urls = {
            'venta': f'https://www.idealista.com/sala-de-prensa/informes-precio-vivienda/venta/madrid-comunidad/madrid-provincia/{distrito}/historico/',
            'alquiler': f'https://www.idealista.com/sala-de-prensa/informes-precio-vivienda/alquiler/madrid-comunidad/madrid-provincia/{distrito}/historico/',
        }

    result_evolution = {}
    for k, url in urls.items():
        payload = {"api_key": API_KEY, "url": url, "render": True}

        response = requests.get("http://api.scraperapi.com", params=payload)
        soup = BeautifulSoup(response.text, 'lxml')

        table = soup.find_all('div', class_='price-indicator-table-block')[0]
        body = table.find('tbody').find_all('tr')

        evolution = []
        for line in body:
            tds = line.find_all('td')
            time = tds[0].get_text()
            value = tds[1].get_text()
            evolution.append((time, value))

        result_evolution[k] = evolution
    x['evolution'] = result_evolution
    return x


def fetch_actual_price():
    urls = {
        'venta-centro':"https://www.idealista.com/sala-de-prensa/informes-precio-vivienda/venta/madrid-comunidad/madrid-provincia/madrid/",
        'alquiler-centro': "https://www.idealista.com/sala-de-prensa/informes-precio-vivienda/alquiler/madrid-comunidad/madrid-provincia/madrid/",
        'venta-provincia': 'https://www.idealista.com/sala-de-prensa/informes-precio-vivienda/venta/madrid-comunidad/madrid-provincia/',
        'alquiler-provincia': 'https://www.idealista.com/sala-de-prensa/informes-precio-vivienda/alquiler/madrid-comunidad/madrid-provincia/'
    }
    results = []
    for k, url in urls.items():
        payload = {"api_key": API_KEY, "url": url, "render": True}

        response = requests.get("http://api.scraperapi.com", params=payload)
        soup = BeautifulSoup(response.text, 'lxml')

        table = soup.find_all("div", class_="price-indicator-table-block")[0]
        rows = table.find_all('tr')

        for row in rows[1:]: # Remove table header
            tds = row.find_all('td')
            district = tds[0].get_text()
            price = tds[1].get_text().split(' ')[0]

            results.append(
                {
                    'distrito': district,
                    'precio': price,
                    'zona': k,
                }
            )
    df = pd.DataFrame.from_dict(results)
    return df



def main(output_file):

    # Fetch current €/m2 per district
    df = fetch_actual_price()
    results = df.to_dict(orient='records')

    # Calculate PER and Rentabilidad Bruta
    metrics = {}
    for row in results:
        aux = row['zona'].split('-')
        tipo = aux[0]
        province_center = aux[1]

        distrito = row['distrito']

        if distrito in ['Madrid', 'Madrid provincia']:
            continue

        if distrito not in metrics:
            metrics[distrito] = {}

        metrics[distrito]['tipo'] = province_center

        if tipo == 'alquiler':
            metrics[distrito]['alquiler/m2'] = row['precio']
        else:
            metrics[distrito]['venta/m2'] = row['precio']


    metrics = pd.DataFrame.from_dict(metrics, orient='index').reset_index()
    metrics = metrics.rename(columns={'index': 'distrito'})
    metrics = metrics.dropna()

    metrics.loc[:, 'venta/m2'] = metrics['venta/m2'].apply(lambda x: x.replace('.', ''))
    metrics.loc[:, 'venta/m2'] = metrics['venta/m2'].apply(float)

    metrics.loc[:, 'alquiler/m2'] = metrics['alquiler/m2'].apply(lambda x: x.replace(',', '.'))
    metrics.loc[:, 'alquiler/m2'] = metrics['alquiler/m2'].apply(float)

    metrics.loc[:, 'PER'] = metrics['venta/m2'] / (metrics['alquiler/m2'] * 12)
    metrics.loc[:, 'RB'] = ((metrics['alquiler/m2'] * 12) / metrics['venta/m2']) * 100
    metrics.loc[:, 'difference'] = metrics['PER'] - metrics['RB']


    # Get historic from all district and calculate evolution

    metrics.loc[:, 'distrito'] = metrics['distrito'].map(transform_word)
    metrics = metrics.apply(get_historic, axis=1)
    metrics.to_csv(output_file)


if __name__ == '__main__':

    output_file = 'data/average_metrics.csv'

    if not os.path.exists(output_file):
        main(output_file)
    else:
        print('Data already extracted')
