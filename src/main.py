import os
import re
import math
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


# Load advertised time per flat

published = {}
with open('data/advertisement_time.jsonl', 'r') as f:
    for line in f:
        line = eval(line)
        published[line['href']] = line['date']

temp = {
    'minuto': 1,
    'minutos': 1,
    'hora': 60,
    'horas': 60,
    'día': 60*24,
    'días': 60*24,
    'mes': 60*24*30,
    'meses': 60*24*30,
    'año': 60*24*30*12
}
for k, string in published.items():
    if string == 'Vendido':
        published[k] = 1
        continue

    integers = re.findall(r'\d+', string)
    integers = [int(num) for num in integers]
    integer = integers[0] if len(integers) else None
    if integer is None:
        for i in ['un', 'una']:
            if i in string:
                integer = 1

    metric = [t for t in temp if t in string][0]
    minutes = temp[metric] * integer
    published[k] = (minutes + 60*24*30) / (60*24*30) # Transform everything to months


# Add number of flats per distrit

apartments = []
with open('data/number_apartments.jsonl', 'r') as f:
    for line in f:
        line = eval(line)
        numbers = re.findall(r"-?\d+(?:\.\d+)?", line['viviendas'])
        line['number_apartments'] = numbers[0].replace('.', '')
        _idx = numbers.index('2')
        line['year'] = numbers[_idx+1:]
        line.pop('viviendas')
        apartments.append(line)
apartments = pd.DataFrame(apartments)
apartments = apartments[['distrito', 'number_apartments']].set_index('distrito')['number_apartments'].to_dict()



# Create Dataframe with all the information

distritos = [i.split('_')[0] for i in os.listdir('data/idealista/') if i.endswith('jsonl')]
distritos = list(set(distritos))

info = []
for distrito in distritos:
    for k in ['venta', 'alquiler']:
        with open(f'data/idealista/{distrito}_{k}.jsonl', 'r') as f:
            for line in f:
                line = line.replace('null', 'None')
                line = eval(line)

                # Split details into hab, meters, floor and publish date
                detail = line['details']
                hab = next((i for i in detail if 'hab.' in i), None)
                meters = next((i for i in detail if 'm²' in i), None)
                floor = next((i for i in detail if any(keyword in i for keyword in ['interior', 'exterior', 'ascensor'])), None)

                info.append({
                    'distrito': distrito,
                    'href': line['href'],
                    'price': line['price'],
                    'meters': meters,
                    'hab': hab,
                    'floor': floor,
                    'parking': line['parking'],
                    'state': k,
                    'description': line['description']
                })

df = pd.DataFrame(info)


# Add advertisement time
df['advertised_time'] = df['href'].apply(lambda x: published[x])

# Transform data to float
df['price'] = df['price'].str.replace('.', '').str.replace('€', '').str.replace('/mes', '').astype(float)
df['meters'] = df['meters'].str.replace('m²', '').str.replace('.', '').astype(float)


range_meters = {
    30: [0, 40],
    50: [40, 60],
    80: [60, 90],
    100: [90, 120],
    120: [120, 1000]
}
def get_range_meters(meters):
    for r, _range in range_meters.items():
        if _range[0] <= meters < _range[1]:
            return r

df['mean_meters'] = df['meters'].apply(get_range_meters)
df['€/meter'] = df['price'] / df['meters']

# Save df with information for each apartment
df.to_csv('data/info_per_apartment.csv', index=False)



# Group apartments in range meters

df_grouped = df.groupby(['distrito', 'mean_meters', 'state']).agg({'€/meter': ['mean', 'size'], 'advertised_time': ['mean']}).reset_index()
df_grouped.columns = ['distrito', 'mean_meters', 'state', '€/meter', 'size', 'advertised_time']

data = df_grouped.pivot_table(
    index=['distrito', 'mean_meters'],
    columns='state',
    values=['€/meter', 'size', 'advertised_time']
).reset_index()

data.columns = ['distrito', 'mean_meters', 'advertised_rent_time', 'advertised_sell_time', 'size_rent', 'size_sell', '€/meter_rent', '€/meter_sell']
data.fillna(0, inplace=True)

data['apartments'] = data['distrito'].apply(lambda x: int(apartments[x]))


# Calculate metrics on average across each group of meters in each district
data['RB'] = data.apply(lambda x: ((x['€/meter_rent'] * 12) / x['€/meter_sell']) * 100 if x['€/meter_sell'] > 0 else 0, axis=1)
data['PER'] = data.apply(lambda x: x['€/meter_sell'] / (x['€/meter_rent'] * 12) if x['€/meter_rent'] > 0 else 0, axis=1)


evolution = pd.read_csv('data/evolution.csv')
data = pd.merge(data, evolution, on='distrito', how='inner')

data['sell'] = data['mean_meters'] * data['€/meter_sell']
data['rent'] = data['mean_meters'] * data['€/meter_rent']

data['change_2014_2024_sell'] = data['change_2014_2024_sell'].apply(lambda x: x/100)
data['change_2014_2024_rent'] = data['change_2014_2024_rent'].apply(lambda x: x/100)

data['change_2021_2024_sell'] = data['change_2021_2024_sell'].apply(lambda x: x/100)
data['change_2021_2024_rent'] = data['change_2021_2024_rent'].apply(lambda x: x/100)

# Revalorization: How much does the flats cost when I finish paying for it? Just took into account the inflation
data['revaluation'] = data['sell'] * (data['change_2021_2024_sell'] + 1 )**data['PER']

# Calculate PER adjusted to the rent price evolution
def calculate_per_adjusted(x):
    venta = x['sell']
    PER = x['PER']
    a0 = x['rent'] * 12
    g = x['change_2021_2024_sell']
    n = math.log(1 + (g * venta / a0)) / math.log(1 + g) - 1 if a0 > 0 else 0
    x['PER_adjusted'] = n
    return x

data = data.apply(calculate_per_adjusted, axis=1)

# Normalize the columns using Min-Max scaling
scaler = MinMaxScaler()
#data['log_revaluation'] = np.log1p(data['revaluation'])  # Log transformation
data['norm_revaluation'] = scaler.fit_transform(data[['revaluation']])

data['norm_RB'] = scaler.fit_transform(data[['RB']])

data['inverse_PER'] = data['PER'].apply(lambda x: 1 / x if x > 0 else 0)
data['norm_PER'] = scaler.fit_transform(data[['inverse_PER']])


# Save data df with information for each group of apartments per district
data.to_csv('data/info_per_district_and_meters.csv', index=False)