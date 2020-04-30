#!/usr/bin/env python
# coding: utf-8
# %%
from gssutils import *

def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

def mid(s, offset, amount):
    return s[offset:offset+amount]

import json

scraper = Scraper(json.load(open('info.json'))['landingPage'])
scraper


# %%
distribution = scraper.distribution(latest=True)
tabs = distribution.as_databaker()
distribution

# %%
tidied_sheets = []

for i in tabs:
    if not i.name in ['NUTS1 by category 2011','NUTS1 by category 2012','NUTS1 by category 2013','NUTS1 by category 2014','NUTS1 by category 2015','NUTS1 by category 2016']:
        continue
    tab = distribution.as_pandas(sheet_name = i.name)
    
    observations = tab.iloc[2:17]
    observations.rename(columns = observations.iloc[0], inplace = True)
    observations.drop(observations.index[0], inplace = True)
    
    table = pd.melt(observations, id_vars = ['Functional category'], var_name = 'Area', value_name = 'Value')
    table.Value.dropna(inplace = True)
    table['Unit'] = 'gbp-million'
    table['Measure Type'] = 'GBP Total'
    table['Year']  = right(i.name,4)
    table['Flow'] = 'exports'    
    
    tidied_sheets.append(table)    
    
tabNI = tab = distribution.as_pandas(sheet_name = 'Northern Ireland')  
observations = tabNI.iloc[3:18, :6]
observations.rename(columns= observations.iloc[0], inplace=True)
observations.drop(observations.index[0], inplace = True)
observations.columns.values[0] = 1
table = pd.melt(observations, id_vars=[1], var_name='Year', value_name='Value')
table.Value.dropna(inplace =True)
table.columns = ['Functional category' if x== 1 else x for x in table.columns]
table['Unit'] = 'gbp-million'
table['Measure Type'] = 'GBP Total'
table['Area'] = 'Northern Ireland'
table['Flow'] = 'exports'
table['Year'] = table['Year'].apply(lambda x: pd.to_numeric(x, downcast='integer'))
table['Year'] = table['Year'].astype(int)
table['Functional category'] = table['Functional category'].map(lambda x: { 
                    'Total in all categories':'Total in all categories for NUTS1 area' }.get(x, x))
tidied_sheets.append(table)

tidy = pd.concat(tidied_sheets, ignore_index = True, sort = False).fillna('')
tidy


# %%
tidy['Area'] = tidy['Area'].map(lambda x: { 'Yorkshire and the Humber':'Yorkshire and The Humber' }.get(x, x))


# %%
for col in tidy.columns:
    if col not in ['Value', 'Year']:
        tidy[col] = tidy[col].astype('category')
        display(col)
        display(tidy[col].cat.categories)


# %%
tidy['NUTS Geography'] = tidy['Area'].cat.rename_categories({
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
    'Northern Ireland' : 'nuts1/UKN'
})
tidy['ONS Functional Category'] = tidy['Functional category'].cat.rename_categories({
    'Administrative and support services' : 'administrative-support' , 
    'Construction' :'construction', 
    'Financial' : 'financial',
    'Information and communication' : 'information-communication', 
    'Insurance and pension services' : 'insurance-pension',
    'Manufacturing' : 'manufacturing', 
    'Other services' : 'other', 
    'Primary and utilities' :'primary-utilities',
    'Real estate, professional, scientific and technical' : 'real-estate',
    'Retail (excluding motor trades)' : 'retail',
    'Total in all categories for NUTS1 area' : 'all',
    'Transport' : 'transport', 
    'Travel' : 'travel',
    'Wholesale and motor trades' : 'wholesale-motor'            
})


# %%
tidy['Value'] = tidy['Value'].map(lambda x:'' 
                            if (x == ':') | (x == 'xx') | (x == '..') 
                            else int(x))
tidy = tidy[tidy['Value'] != '']


# %%
tidy = tidy[['NUTS Geography','Year','ONS Functional Category','Flow','Measure Type','Value','Unit']]


# %%
tidy.rename(columns={'Flow':'Flow Directions'}, inplace=True)

#Flow has been changed to Flow Direction to differentiate from Migration Flow dimension

# %%
from pathlib import Path
out = Path('out')
out.mkdir(exist_ok=True)
tidy.drop_duplicates().to_csv(out / 'observations.csv', index = False)


# %%


from gssutils.metadata import THEME

scraper.dataset.family = 'trade'
scraper.dataset.theme = THEME['business-industry-trade-energy']
with open(out / 'observations.csv-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())


# %%
csvw = CSVWMetadata('https://gss-cogs.github.io/family-trade/reference/')
csvw.create(out / 'observations.csv', out / 'observations.csv-schema.json')

