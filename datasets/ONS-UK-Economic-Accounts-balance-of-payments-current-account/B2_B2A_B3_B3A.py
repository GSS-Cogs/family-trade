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

# ## Balance of Payments Current Account: Trade in goods and services B2, B3 

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

# +
trace = TransformTrace()
title = 'Trade in goods and services'
columns = ['Period','Flow Directions','Product','Seasonal Adjustment', 'CDID', 'Services', 'Account Type', 'Value', 'Marker', 'Measure Type', 'Unit']

for tab in tabs:
    if 'B2' in tab.name: #Tabs B2 and B2A
        print(tab.name)
        
        trace.start(title, tab, columns, distribution.downloadURL)
        
        trace.Flow_Directions("Selected as Exports, Imports and Balances")
        flow = tab.excel_ref('B').expand(DOWN).by_index([7,21,35]) - tab.excel_ref('B46').expand(DOWN)
        
        trace.Product("Selected as products from cell B and removing flow directions, trade and seasonal adjustment")
        product = tab.excel_ref('B').expand(DOWN).is_not_blank().is_not_whitespace() - flow  - tab.excel_ref('B3').expand(UP)
        
        code = tab.excel_ref('C7').expand(DOWN).is_not_blank()
        year =  tab.excel_ref('D4').expand(RIGHT).is_not_blank()
        quarter = tab.excel_ref('D5').expand(RIGHT)
        seasonal_adjustment = tab.excel_ref('B2')
        trade = tab.excel_ref('B1')
        observations = quarter.fill(DOWN).is_not_blank()
        
        dimensions = [
            HDim(year, 'Period', DIRECTLY, ABOVE),
            HDim(quarter, 'Quarter', DIRECTLY, ABOVE),
            HDim(code, 'CDID', DIRECTLY, LEFT),
            HDim(flow, 'Flow Directions', CLOSEST, ABOVE),
            HDim(product, 'Product', DIRECTLY, LEFT),
            HDim(seasonal_adjustment, 'Seasonal Adjustment', CLOSEST, LEFT),
            HDim(trade, 'Services', CLOSEST, LEFT),
            HDimConst('Account Type', 'Current Account'),
            HDimConst('Measure Type', 'GBP Total'),
            HDimConst('Unit', 'gbp-million')   
        ]
        
        cs = ConversionSegment(tab, dimensions, observations) 
        tidy_sheet = cs.topandas() 
        trace.store('combined_dataframe', tidy_sheet)
        
    elif 'B3' in tab.name: #Tabs B3 and B3A
        print(tab.name)
        
        trace.start(title, tab, columns, distribution.downloadURL)
        
        flow = tab.excel_ref('B').expand(DOWN).by_index([7,22,37]) - tab.excel_ref('B51').expand(DOWN)
        product = tab.excel_ref('B').expand(DOWN).is_not_blank().is_not_whitespace() - flow  - tab.excel_ref('B3').expand(UP)
        code = tab.excel_ref('C7').expand(DOWN).is_not_blank()
        year =  tab.excel_ref('D4').expand(RIGHT).is_not_blank()
        quarter = tab.excel_ref('D5').expand(RIGHT)
        seasonal_adjustment = tab.excel_ref('B2')
        trade = tab.excel_ref('B1')
        observations = quarter.fill(DOWN).is_not_blank()
        
        dimensions = [
            HDim(year, 'Period', DIRECTLY, ABOVE),
            HDim(quarter, 'Quarter', DIRECTLY, ABOVE),
            HDim(code, 'CDID', DIRECTLY, LEFT),
            HDim(flow, 'Flow Directions', CLOSEST, ABOVE),
            HDim(product, 'Product', DIRECTLY, LEFT),
            HDim(seasonal_adjustment, 'Seasonal Adjustment', CLOSEST, LEFT),
            HDim(trade, 'Services', CLOSEST, LEFT),
            HDimConst('Account Type', 'Current Account'),
            HDimConst('Measure Type', 'GBP Total'),
            HDimConst('Unit', 'gbp-million'),
         ]
        
        cs = ConversionSegment(tab, dimensions, observations)
        tidy_sheet = cs.topandas() 
        trace.store('combined_dataframe', tidy_sheet)
# -

df = trace.combine_and_trace(title, "combined_dataframe")    

df['Period'] = df.Period.str.replace('\.0', '')
df['Quarter'] = df['Quarter'].str.lstrip()
df['Period'] = df['Period'] + df['Quarter']
df['Period'] = df['Period'].map(lambda x: 'year/' + left(x,4) if 'Q' not in x else 'quarter/' + left(x,4) + '-' + right(x,2))
df.drop(['Quarter'], axis=1, inplace=True)

df['Flow Directions'] = df['Flow Directions'].map(lambda x: x.split()[0])
df = df.replace({'Seasonal Adjustment' : {' Seasonally adjusted' : 'SA', ' Not seasonally adjusted' : 'NSA' }})
df['Product'] = df['Product'].str.lstrip()
df.rename(columns={'OBS' : 'Value','DATAMARKER' : 'Marker'}, inplace=True)
df['Marker'].replace(' -', 'unknown', inplace=True)

# +

# +
tidy = df[['Period','Flow Directions','Product','Seasonal Adjustment', 'CDID', 'Services', 'Account Type', 'Value', 'Marker', 'Measure Type', 'Unit']]
for column in tidy:
    if column in ('Flow Directions', 'Product', 'Services', 'Account Type'):
        tidy[column] = tidy[column].str.lstrip()
        tidy[column] = tidy[column].map(lambda x: pathify(x))
        
tidy

# + endofcell="--"

# --
