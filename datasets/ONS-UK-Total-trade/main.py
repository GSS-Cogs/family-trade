# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.8
#   kernelspec:
#     display_name: Python 3.9.12 64-bit
#     language: python
#     name: python3
# ---

# UK trade in services: all countries, non-seasonally adjusted

import pandas as pd
from gssutils import *

metadata = Scraper(seed='info.json')

metadata.dataset.family = 'trade'

distribution = metadata.distribution(latest=True)

tabs = {tab.name: tab for tab in metadata.distribution(latest=True).as_databaker()}


# +
def left(s, amount):
    return s[:amount]
def right(s, amount):
    return s[-amount:]

def date_time (date):
    if len(date)  == 4:
        return 'year/' + date
    elif len(date) == 6:
        return 'quarter/' + left(date,4) + '-' + right(date,2)
    else:
        return date


# -

tidied_sheets = []
for name, tab in tabs.items():
    datasetTitle = 'uk-total-trade-all-countries-non-seasonally-adjusted'
    
    if 'Index' in name or '7 Contact Sheet' in name or 'Notes' in name:
        continue
    period = tab.excel_ref("B3").expand(DOWN).filter(contains_string("Country")).fill(RIGHT).is_not_blank().is_not_whitespace()
    flow = tab.excel_ref("A3").expand(DOWN).filter(contains_string("by Country")).is_not_blank().is_not_whitespace()
    country = tab.excel_ref('B4').fill(DOWN).is_not_blank().is_not_whitespace()- tab.excel_ref('B4').fill(DOWN).filter(contains_string("Country"))
    trade_type = tab.excel_ref('A1')
    observations = period.fill(DOWN).is_not_blank().is_not_whitespace()-period
    
    dimensions = [
        HDim(period,'Period',DIRECTLY,ABOVE),
        HDim(country,'Country',DIRECTLY,LEFT),
        HDim(flow, 'Flow',CLOSEST,ABOVE),
        HDim(trade_type, 'Trade Type',CLOSEST,LEFT)
    ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations) 
    tidy_sheet = tidy_sheet.topandas()
    tidied_sheets.append(tidy_sheet)
    # savepreviewhtml(tidy_sheet,fname=tab.name + "Preview.html")

df = pd.concat(tidied_sheets, sort = True).fillna('')

#Post Processing 
df.rename(columns={'OBS' : 'Value','DATAMARKER' : 'Marker'}, inplace=True)
df['Trade Type'] = df['Trade Type'].apply(lambda x: 'total' if 'Total Trade' in x else 
                                    ('goods' if 'Trade in Goods' in x else 
                                    ('services' if 'Trade in Services' in x else x)))
df['Marker'].replace('N/A', 'not-collated', inplace=True)
df['Period'] = df['Period'].astype(str).replace('\.0', '', regex=True)
df['Period'] =  df["Period"].apply(date_time)
df = df[['Period', 'Country', 'Flow', 'Trade Type', 'Marker', 'Value']]

df['Flow'] = df['Flow'].map(lambda x: 'exports'  if 'Exports' in x else 'imports')

add_to_des = """
These tables have been produced to provide an aggregated quarterly goods and services estimate and combines the most recent estimates for goods and services split by country.
Data for goods and services is consistent for annual whole world totals and quarters (from Q1 2016) with the trade data published in the Quarterly National Accounts, Quarterly Sector Accounts and Quarterly Balance of Payments on 31st March 2022.
These data are our best estimate of these bilateral UK trade flows. Users should note that alternative estimates are available, in some cases, via the statistical agencies for bilateral countries or through central databases such as:
UN Comtrade.
Some data for countries have been marked with N/A. This is because Trade in Goods do not collate data from these countries, therefore only Trade in Services is reflected within total trade for these countries or vice versa.
The data within these tables are also consistent with the below releases:
For Trade in Goods the data is consistent with UK Trade: February 2022 publication on 11th April 2022
For Trade in Services the data is consistent with UK Trade in services by partner country: October to December 2021 publication on 28th April 2022
Data is in current price (CP), £m and is non-seasonal adjusted
"""
metadata.dataset.description = metadata.dataset.description + add_to_des

df.to_csv('observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')
