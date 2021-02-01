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

# ## Balance of Payments Current Account: Transactions with the EU and EMU B6, B6A

# +

import pandas as pd
from gssutils import *
from databaker.framework import *

pd.options.mode.chained_assignment = None 

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
title = 'Transactions with the EU and EMU'
columns = ['Period','Flow Directions', 'Account Type', 'Transaction Type', 'Services', 'Members', 'Seasonal Adjustment', 
           'CDID', 'Value', 'Measure Type', 'Unit']

for tab in tabs:
    if (tab.name == 'B6') or (tab.name == 'B6A'):
        trace.start(title, tab, columns, distribution.downloadURL)
        
        emu_index = [12,14,17,19,21,25,29,31,34,36,38,42,46,48,51,53,55,59]
        flow = tab.excel_ref('B').expand(DOWN).by_index([10,27,44]) - tab.excel_ref('B60').expand(DOWN)
        emu_only = tab.excel_ref('B').expand(DOWN).by_index(emu_index) - tab.excel_ref('B60').expand(DOWN)
        services = tab.excel_ref('B11').expand(DOWN).is_not_blank() - emu_only - flow - tab.excel_ref('B60').expand(DOWN)
        emu_and_services = tab.excel_ref('B11').expand(DOWN).is_not_blank() - flow  - tab.excel_ref('B60').expand(DOWN)
        
        account_Type = tab.excel_ref('B1')
        seasonal_adjustment = tab.excel_ref('B3')
        transaction_type = tab.excel_ref('B8')
        code = tab.excel_ref('C7').expand(DOWN).is_not_blank()
        year =  tab.excel_ref('D5').expand(RIGHT).is_not_blank()
        quarter = tab.excel_ref('D6').expand(RIGHT)
        observations = quarter.fill(DOWN).is_not_blank()
        
        dimensions = [
            HDim(account_Type, 'Account Type', CLOSEST, LEFT),
            HDim(seasonal_adjustment, 'Seasonal Adjustment', CLOSEST, LEFT),
            HDim(transaction_type, 'Transaction Type', CLOSEST, LEFT),
            HDim(flow, 'Flow Directions', CLOSEST, ABOVE),
            HDim(code, 'CDID', DIRECTLY, LEFT),
            HDim(year, 'Period', DIRECTLY, ABOVE),
            HDim(quarter, 'Quarter', DIRECTLY, ABOVE),
            HDim(services, 'Services', CLOSEST, ABOVE),
            HDim(emu_and_services, 'Members', DIRECTLY, LEFT),
            HDimConst('Measure Type', 'GBP Total'),
            HDimConst('Unit', 'gbp-million'),
        ]
        
        cs = ConversionSegment(tab, dimensions, observations)
        tidy_sheet = cs.topandas() 
        trace.store('combined_dataframe', tidy_sheet)

df = trace.combine_and_trace(title, "combined_dataframe")

df['Period'] = df.Period.str.replace('\.0', '')
df['Quarter'] = df['Quarter'].map(lambda x: x.lstrip() if isinstance(x, str) else x)
df['Period'] = df['Period'] + df['Quarter']
df['Period'] = df['Period'].map(lambda x: 'year/' + left(x,4) if 'Q' not in x else 'quarter/' + left(x,4) + '-' + right(x,2))
df.drop(['Quarter'], axis=1, inplace=True)

df['Account Type'] = df['Account Type'].map(lambda x: x.split()[0]) + ' ' +  df['Account Type'].map(lambda x: x.split()[1])
df['Account Type'] = df['Account Type'].str.rstrip(':')
df['Services'] = df['Services'].str.rstrip('4')
df['Members'] = df['Members'].map(lambda x: 'of which EMU members' if '     of which EMU members4' in x else 'European Union (EU)')
df = df.replace({'Seasonal Adjustment' : {' Seasonally adjusted' : 'SA', ' Not seasonally adjusted': 'NSA' }})

df.rename(columns={'OBS' : 'Value','DATAMARKER' : 'Marker'}, inplace=True)
df['Marker'].replace(' -', 'unknown', inplace=True)

# +

tidy = df[['Period','Flow Directions', 'Account Type', 'Transaction Type', 'Services', 'Members', 'Seasonal Adjustment', 
           'CDID', 'Value', 'Marker', 'Measure Type', 'Unit']]

for column in tidy:
    if column in ['Flow Directions', 'Account Type', 'Transaction Type', 'Services', 'Members']:
        tidy[column] = tidy[column].str.lstrip()
        tidy[column] = tidy[column].map(lambda x: pathify(x))       
tidy

# + endofcell="--"

# --
