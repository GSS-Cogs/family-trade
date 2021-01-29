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

# ## Balance of Payments Current Account: Secondary income B5

# +

import pandas as pd
from gssutils import *
from databaker.framework import *

cubes = Cubes("info.json")

scraper = Scraper(seed='info.json')
scraper

distribution = scraper.distribution(latest=True)
distribution

tabs = distribution.as_databaker()


# +
def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]


# +

trace = TransformTrace()
title = 'Secondary income'
columns = ['Period','Flow Directions', 'Income', 'Income Description', 'Sector', 'Account Type', 'Seasonal Adjustment', 
           'CDID', 'Value', 'Marker', 'Measure Type', 'Unit']

for tab in tabs:
    if (tab.name == 'B5') or (tab.name == 'B5A'):
        
        trace.start(title, tab, columns, distribution.downloadURL)
        
        flow = tab.excel_ref('B').expand(DOWN).by_index([7,24,43]) - tab.excel_ref('B51').expand(DOWN)
        sector = tab.excel_ref('B').expand(DOWN).by_index([8,14,25,34,44,45]) - tab.excel_ref('B51').expand(DOWN)
        income = tab.excel_ref('B10').expand(DOWN).is_not_blank() - tab.excel_ref('B51').expand(DOWN)
        code = tab.excel_ref('C7').expand(DOWN).is_not_blank()
        year =  tab.excel_ref('D4').expand(RIGHT).is_not_blank()
        quarter = tab.excel_ref('D5').expand(RIGHT)
        seasonal_adjustment = tab.excel_ref('B2')
        income_type = tab.excel_ref('B1')
        observations = quarter.fill(DOWN).is_not_blank()
        
        dimensions = [
            HDim(flow, 'Flow Directions', CLOSEST, ABOVE),
            HDim(sector, 'Sector', CLOSEST, ABOVE),
            HDim(income, 'Income Description', DIRECTLY, LEFT),
            HDim(code, 'CDID', DIRECTLY, LEFT),
            HDim(year, 'Period', DIRECTLY, ABOVE),
            HDim(quarter, 'Quarter', DIRECTLY, ABOVE),        
            HDim(seasonal_adjustment, 'Seasonal Adjustment', CLOSEST, LEFT),
            HDim(income_type, 'Income', CLOSEST, LEFT),
            HDimConst('Account Type', 'Current Account'),
            HDimConst('Measure Type', 'GBP Total'),
            HDimConst('Unit', 'gbp-million'),
        ]
        cs = ConversionSegment(tab, dimensions, observations)
        tidy_sheet = cs.topandas() 
        trace.store('combined_dataframe', tidy_sheet)

df = trace.combine_and_trace(title, "combined_dataframe")

df['Period'] = df.Period.str.replace('\.0', '')
df['Quarter'] = df["Quarter"].str.lstrip()
df['Period'] = df['Period'] + df['Quarter']
df['Period'] = df['Period'].map(lambda x: 'year/' + left(x,4) if 'Q' not in x else 'quarter/' + left(x,4) + '-' + right(x,2))
df.drop(['Quarter'], axis=1, inplace=True)

df['Income Description'] = df['Income Description'].str.rstrip('2')
df['Income Description'] = df['Income Description'].str.rstrip('3')
df['Income Description'] = df['Income Description'].str.lstrip()

df['Income'] = df['Income'].str.rstrip('1')
df['Sector'] = df['Sector'].str.lstrip()

df = df.replace({'Seasonal Adjustment' : {' Seasonally adjusted' : 'SA', ' Not Seasonally adjusted': 'NSA' }})

df.rename(columns={'OBS' : 'Value','DATAMARKER' : 'Marker'}, inplace=True)
df['Marker'].replace(' -', 'unknown', inplace=True)

# +

# +
tidy = df[['Period','Flow Directions', 'Income', 'Income Description', 'Sector', 'Account Type', 'Seasonal Adjustment', 
           'CDID', 'Value', 'Marker', 'Measure Type', 'Unit']]
for column in tidy:
    if column in ('Flow Directions', 'Income', 'Income Description', 'Sector', 'Account Type'):
        tidy[column] = tidy[column].str.lstrip()
        tidy[column] = tidy[column].map(lambda x: pathify(x))
        
tidy

# + endofcell="--"

# --
