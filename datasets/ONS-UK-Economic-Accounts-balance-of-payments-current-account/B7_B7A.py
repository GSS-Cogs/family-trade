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

# ## Balance of Payments Capital Account B7

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


# -

title = 'Balance of Payments: Capital Account'

# +

trace = TransformTrace()
title = 'Capital Account'
columns = ['Period','Flow Directions','Services','Sector','Seasonal Adjustment', 'CDID', 'Account Type', 'Value', 
           'Marker','Measure Type', 'Unit']

for tab in tabs:
    if 'B7' in tab.name: #Tabs B7 and B7A
        
        trace.start(title, tab, columns, distribution.downloadURL)
        
        sector_index = [9,14,16,22,32,37,46,54,59,64]
        flow = tab.excel_ref('B').expand(DOWN).by_index([7,30,52]) - tab.excel_ref('B70').expand(DOWN)
        sector_only = tab.excel_ref('B').expand(DOWN).by_index(sector_index) - tab.excel_ref('B70').expand(DOWN)
        services = tab.excel_ref('B8').expand(DOWN).is_not_blank() - sector_only - flow - tab.excel_ref('B70').expand(DOWN)
        code = tab.excel_ref('C7').expand(DOWN).is_not_blank()
        year =  tab.excel_ref('D4').expand(RIGHT).is_not_blank()
        quarter = tab.excel_ref('D5').expand(RIGHT)
        seasonal_adjustment = tab.excel_ref('B2')
        account_Type = tab.excel_ref('B1')
        observations = quarter.fill(DOWN).is_not_blank()
        
        dimensions = [
            HDim(account_Type, 'Account Type', CLOSEST, LEFT),
            HDim(seasonal_adjustment, 'Seasonal Adjustment', CLOSEST, LEFT),
            HDim(flow, 'Flow Directions', CLOSEST, ABOVE),
            HDim(services, 'Services', DIRECTLY, LEFT),
            HDim(sector_only, 'Sector', CLOSEST, ABOVE),
            HDim(code, 'CDID', DIRECTLY, LEFT),
            HDim(year, 'Period', DIRECTLY, ABOVE),
            HDim(quarter, 'Quarter', DIRECTLY, ABOVE),
            HDimConst('Measure Type', 'GBP Total'),
            HDimConst('Unit', 'gbp-million'),
        ]
        cs = ConversionSegment(tab, dimensions, observations)
        tidy_sheet = cs.topandas() 
        trace.store('combined_dataframe', tidy_sheet)

df = trace.combine_and_trace(title, "combined_dataframe")

df['Period'] = df.Period.str.replace('\.0', '')
df['Quarter'] = df["Quarter"].map(lambda x: x.lstrip() if isinstance(x, str) else x)
df['Period'] = df['Period'] + df['Quarter']
df['Period'] = df['Period'].map(lambda x: 'year/' + left(x,4) if 'Q' not in x else 'quarter/' + left(x,4) + '-' + right(x,2))
df.drop(['Quarter'], axis=1, inplace=True)

df['Account Type'] = df['Account Type'].map(lambda x: x.split()[0]) + ' ' +  df['Account Type'].map(lambda x: x.split()[1])
df['Account Type'] = df['Account Type'].str.rstrip('1')
df['Services'] = df['Services'].str.rstrip('2')
df['Services'] = df['Services'].str.lstrip()
df = df.replace({'Sector' : {' ' : 'total'}})

df.rename(columns={'OBS' : 'Value','DATAMARKER' : 'Marker'}, inplace=True)
df['Marker'].replace(' -', 'unknown', inplace=True)

df = df.replace({'Seasonal Adjustment' : {' Seasonally adjusted' : 'SA', ' Not seasonally adjusted': 'NSA' }})

# +

# +
tidy = df[['Period','Flow Directions','Services','Sector','Seasonal Adjustment', 'CDID', 'Account Type', 'Value', 
           'Marker','Measure Type', 'Unit']]
for column in tidy:
    if column in ('Flow Directions', 'Services', 'Account Type', 'Sector'):
        tidy[column] = tidy[column].str.lstrip()
        tidy[column] = tidy[column].map(lambda x: pathify(x))
        
tidy

# + endofcell="--"

# --
