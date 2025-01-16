# Madrid Real Estate Market Analysis

This repository provides insights into the real estate market in Madrid using data from [Idealista](https://www.idealista.com/) from December 2024.

The goal is to measure which districts are the best for investment according to renting and the selling price. Two metrics where used to performed this evaluation:


### PER (Price-to-Earnings Ratio)

The **PER** is number of years to recover the investment:

> PER = Purchase Price  / Annual Rental Income

A lower PER value generally indicates a more attractive investment.

---

### Annual Rental Yield

The **Annual Rental Yield** is calculated as:

> Annual Rental Yield = (Annual Rental Income / Purchase Price) * 100

This value is expressed as a percentage and represents the annual return from renting the property compared to its purchase price.


## How to Use

1. **Clone the repository**

2. **Install requirements**
   ```bash
   python install -r requirements.txt
3. **Investment calculator**

    Open the `where_to_invest.ipynb` notebook in the `notebooks/` folder and input your details to calculate potential investments.


## Interactive Notebook

In Binder, you can visualize and interact with the plots and maps.

Click the badge below to launch the interactives notebooks:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/pbaneto/idealista-gpt/HEAD)



Use this environment to explore data and check the values of the visualizations.