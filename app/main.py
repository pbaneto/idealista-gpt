import streamlit as st
import pandas as pd
from sklearn.preprocessing import MinMaxScaler



def calculate_investment_score(data, input_money, weight_revaluation, weight_rent_anual, weight_per):
    try:
        data['loan'] = data['sell'].apply(lambda x: x - float(input_money)) # keep just the ones with 0 or positive loan
        filtered = data[data['loan'] > 0].copy()
        scaler = MinMaxScaler()
        filtered['normalized_loan'] = scaler.fit_transform(1 / filtered[['loan']])
        filtered['score'] = (
                            float(weight_rent_anual)/10 * filtered['norm_RB']
                             + float(weight_revaluation)/10 * filtered['norm_revaluation']
                             + float(weight_per)/10 * filtered['norm_PER']
                            )
        cols = ['distrito', 'size_rent', 'size_sell', 'mean_meters', 'rent', 'sell', 'RB', 'PER', 'score', 'revaluation', 'loan', 'advertised_rent_time', 'advertised_sell_time']
        filtered = filtered[cols]
        filtered = filtered.sort_values(by=['loan'])
    except Exception as e:
        print('Please enter valid numbers', e)
    return filtered


data = pd.read_csv('../data/info_per_district_and_meters.csv')


# Start app

st.title('Madrid Idealista')

input_money = st.text_input("How much do you want to invest?", 100000)



st.markdown("#### Allocate a total of 10 points across the following criteria based on their importance to you:")

weight_revaluation = st.selectbox('How many points do you give to revaluation?', range(11))
weight_rent_anual = st.selectbox('How many points do you give to RB (Gross annual yield)?', range(11))
weight_per = st.selectbox('How many points do you give to PER?', range(11))


result = calculate_investment_score(data, input_money, weight_revaluation, weight_rent_anual, weight_per)

# Add a button to run the calculation
if st.button('Calculate Investment Score'):
    total_weight = weight_revaluation + weight_rent_anual + weight_per
    if total_weight == 10:
        result = calculate_investment_score(data, input_money, weight_revaluation, weight_rent_anual, weight_per)
        st.write(result.head(20))  # Display the table with results

    else:
        st.error('The sum of the weights must be equal to 10. Please adjust your selections.')
