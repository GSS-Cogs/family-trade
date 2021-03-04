# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.6.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
# #!/usr/bin/env python
# coding: utf-8
# %%
# -

import pandas as pd
import numpy as np
from gssutils import *
from databaker.framework import *
from IPython.core.display import display

cubes = Cubes("info.json")


# +
def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

def mid(s, offset, amount):
    return s[offset:offset+amount]


# -

scraper = Scraper(seed='info.json')
scraper

# %%
distribution = scraper.distribution(latest=True)
distribution

tabs = distribution.as_databaker()

# +
trace = TransformTrace()
title = distribution.title
columns = ['Functional category', 'Area', 'Value', 'Unit', 'Measure Type', 'Flow', 'Year']

tidied_sheets = []

for tab in tabs:
    if 'NUTS1 by category' in tab.name:
        print (tab.name)
        
        trace.start(title, tab, columns, scraper.distributions[0].downloadURL)
        tab_df = distribution.as_pandas(sheet_name = tab.name)
        
        observations = tab_df.iloc[2:17]
        observations.rename(columns = observations.iloc[0], inplace = True)
        observations.drop(observations.index[0], inplace = True)

        table = pd.melt(observations, id_vars = ['Functional category'], var_name = 'Area', value_name = 'Value')
        table.Value.dropna(inplace = True)
        table['Unit'] = 'gbp-million'
        table['Measure Type'] = 'GBP Total'
        table['Year']  = right(tab.name,4)
        table['Flow'] = 'exports'    

        trace.store("combined_dataframe", table)
        
    elif tab.name == "Northern Ireland":
        print(tab.name)
        
        trace.start(title, tab, columns, scraper.distributions[0].downloadURL)
        tabNI = distribution.as_pandas(sheet_name = 'Northern Ireland')
        
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

        trace.store("combined_dataframe", table)
# -

tidy = trace.combine_and_trace(title, "combined_dataframe")
tidy

tidy['Area'] = tidy['Area'].map(lambda x: { 'Yorkshire and the Humber':'Yorkshire and The Humber' }.get(x, x))

for col in tidy.columns:
    if col not in ['Value', 'Year']:
        tidy[col] = tidy[col].astype('category')
        display(col)
        display(tidy[col].cat.categories)

tidy['NUTS Geography'] = tidy['Area'].cat.rename_categories({
    'East Midlands' : 'UKF', 
    'East of England': 'UKH', 
    'London' : 'UKI', 
    'North East' : 'UKC',
    'North West' : 'UKD', 
    'Scotland' : 'UKM', 
    'South East' : 'UKJ', 
    'South West' : 'UKK',
    'Total for functional category' : 'UK', 
    'Wales' : 'UKL', 
    'West Midlands' : 'UKG',
    'Yorkshire and The Humber' : 'UKE',
    'Northern Ireland' : 'UKN'
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

tidy['Value'] = tidy['Value'].map(lambda x:'' 
                            if (x == ':') | (x == 'xx') | (x == '..') 
                            else int(x))
tidy = tidy[tidy['Value'] != '']

tidy = tidy[['NUTS Geography','Year','ONS Functional Category','Flow','Value']]

tidy.rename(columns={'Flow':'Flow Directions'}, inplace=True)
tidy

# flow has been changed to Flow Direction to differentiate from Migration Flow dimension

cubes.add_cube(scraper, tidy, title)
cubes.output_all()

trace.render("spec_v1.html")

