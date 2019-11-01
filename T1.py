# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.2.4
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
from gssutils import *

scraper = Scraper("https://www.gov.uk/government/collections/uk-regional-trade-in-goods-statistics-disaggregated-by-smaller-geographical-areas")
scraper
# -

scraper.select_dataset(latest=True)
scraper

tabs = {tab.name: tab for tab in scraper.distribution(title=lambda t: 'Data Tables' in t).as_databaker()}

tab = tabs['T1 NUTS1 (Summary Data)']

tidy = pd.DataFrame()

flow = tab.filter('Flow').fill(DOWN).is_not_blank().is_not_whitespace()
#EuNonEu = tab.filter('EU / Non-EU').fill(DOWN).is_not_blank().is_not_whitespace()
geography = tab.filter('EU / Non-EU').fill(DOWN).is_not_blank().is_not_whitespace() | flow
nut = tab.filter('NUTS1').fill(DOWN).is_not_blank().is_not_whitespace() | flow
observations = tab.filter('Statistical Value (£ million)').fill(DOWN).is_not_blank().is_not_whitespace()
observations = observations.filter(lambda x: type(x.value) != str or 'HMRC' not in x.value)
Dimensions = [
            HDim(flow,'Flow',DIRECTLY,LEFT),            
            HDim(geography,'HMRC Partner Geography',DIRECTLY,LEFT),
            HDim(nut,'NUTS Geography',DIRECTLY,LEFT),
            HDimConst('SITC 4', 'all'),
            HDimConst('Measure Type', 'GBP Total'),
            HDimConst('Unit', 'gbp-million'),
            HDimConst('Year', '2017')
            ]
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
table1 = c1.topandas()
tidy = pd.concat([tidy, table1])

# +
#savepreviewhtml(c1)
#tidy
# -

observations1 = tab.filter('Business Count').fill(DOWN).is_not_blank().is_not_whitespace()
observations1 = observations1.filter(lambda x: type(x.value) != str or 'HMRC' not in x.value)
Dimensions = [
            HDim(flow,'Flow',DIRECTLY,LEFT),           
            HDim(geography,'HMRC Partner Geography',DIRECTLY,LEFT),
            HDim(nut,'NUTS Geography',DIRECTLY,LEFT),
            HDimConst('Measure Type', 'Count of Businesses'),
            HDimConst('SITC 4', 'all'),
            HDimConst('Unit', 'businesses'),
            HDimConst('Year', '2017')
            ]
c2 = ConversionSegment(observations1, Dimensions, processTIMEUNIT=True)
table2 = c2.topandas()
tidy = pd.concat([tidy, table2])

#savepreviewhtml(c2)
tidy

tidy['Marker'] = tidy['DATAMARKER'].map(lambda x:'not-applicable'
                                  if (x == 'N/A')
                                  else (x))

import numpy as np
tidy['OBS'].replace('', np.nan, inplace=True)
# tidy.dropna(subset=['OBS'], inplace=True)
# tidy.drop(columns=['Marker'], inplace=True)
tidy.rename(columns={'OBS': 'Value'}, inplace=True)
# tidy['Value'] = tidy['Value'].astype(int)
tidy['Value'] = tidy['Value'].map(lambda x:''
                                  if (x == ':') | (x == 'xx') | (x == '..') | (x == 'N/A')
                                  else (x))

# +
tidy['NUTS Geography'] = tidy['NUTS Geography'].map(
    lambda x: {
        'East':'East of England', 
        'Exp' : 'nuts1/all',
        'Imp': 'nuts1/all'}.get(x, x))

tidy['HMRC Partner Geography'] = tidy['HMRC Partner Geography'].map(
    lambda x: {
        'Exp' : 'europe',
        'Imp': 'europe'}.get(x, x))
# -

for col in tidy.columns:
    if col not in ['Value', 'Year']:
        tidy[col] = tidy[col].astype('category')
        display(col)
        display(tidy[col].cat.categories)

tidy['NUTS Geography'] = tidy['NUTS Geography'].cat.rename_categories({
    'East Midlands' : 'nuts1/UKF', 
    'East of England': 'nuts1/UKH', 
    'London' : 'nuts1/UKI', 
    'North East' : 'nuts1/UKC',
    'North West' : 'nuts1/UKD', 
    'Scotland' : 'nuts1/UKM', 
    'South East' : 'nuts1/UKJ', 
    'South West' : 'nuts1/UKK',
    'Total for functional category' : 'nuts1/all', 
    'Wales' : 'nuts1/UKL', 
    'West Midlands' : 'nuts1/UKG',
    'Yorkshire and The Humber' : 'nuts1/UKE',
    'Northern Ireland' : 'nuts1/UKN',
    'East of England' : 'nuts1/UKH', 
    'Unallocated - Known' : 'nuts1/unk', 
    'Unallocated - Unknown' : 'nuts1/unu'
})
tidy['HMRC Partner Geography'] = tidy['HMRC Partner Geography'].cat.rename_categories({
        'EU'   : 'C',
        'Non-EU' : 'non-eu'})
tidy['Flow'] = tidy['Flow'].cat.rename_categories({
        'Exp'   : 'exports',
        'Imp' : 'imports'})

# +
#tidy = tidy.rename(columns={'EU / Non EU' : 'EU - Non-EU'})
# -

tidy =tidy[['Year', 'NUTS Geography','HMRC Partner Geography','Flow','SITC 4','Measure Type', 'Value', 'Unit','Marker']]

tidy


