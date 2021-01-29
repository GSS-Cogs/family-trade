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

# ## Balance of Payments Current Account: Summary B1

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

# +
def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]


# -

# -

trace = TransformTrace()
title = 'Balance of Payments: Summary' # Distribution.title
columns = ['Period','Flow Directions','Services','Seasonal Adjustment', 'CDID', 'Account Type', 'Value', 
           'Measure Type', 'Unit']

for tab in tabs:
    if 'B1' in tab.name: #Tab B1
        
        trace.start(title, tab, columns, distribution.downloadURL)
        
        ## "Removing records of 'Balances as a % of GDP' & 'Current balance as a % of GDP' information")
        remove_percentage = tab.excel_ref('A30').expand(RIGHT).expand(DOWN) - tab.excel_ref('A41').expand(RIGHT).expand(DOWN)
        
        trace.Account_Type("Selects current account and financial account")
        account_type = tab.excel_ref('B').expand(DOWN).by_index([9,44,66]) - tab.excel_ref('B76').expand(DOWN)
        
        trace.Seasonal_Adjustment("Selects Seasonally Adjusted or Non-seasonally Adjusted")
        seasonal_adjustment = tab.excel_ref('B').expand(DOWN).by_index([7,42]) - tab.excel_ref('B76').expand(DOWN)
        
        flow = tab.excel_ref('B2')
        
        trace.Services("Selects trade activities as cell 'B' and removes percentage, \
            account type and seasonal ajuestment")
        services = tab.excel_ref('B10').expand(DOWN).is_not_blank() - remove_percentage - account_type - seasonal_adjustment 
        
        code = tab.excel_ref('C7').expand(DOWN).is_not_blank()
        year =  tab.excel_ref('D4').expand(RIGHT).is_not_blank()
        quarter = tab.excel_ref('D5').expand(RIGHT)
        observations = quarter.fill(DOWN).is_not_blank() - remove_percentage
        
        dimensions = [
            HDim(account_type, 'Account Type', CLOSEST, ABOVE),
            HDim(seasonal_adjustment, 'Seasonal Adjustment', CLOSEST, ABOVE),
            HDim(flow, 'Flow Directions', CLOSEST, ABOVE),
            HDim(services, 'Services', DIRECTLY, LEFT),
            HDim(code, 'CDID', DIRECTLY, LEFT),
            HDim(year, 'Period', DIRECTLY, ABOVE),
            HDim(quarter, 'Quarter', DIRECTLY, ABOVE),
            HDimConst('Measure Type', 'GBP Total'),
            HDimConst('Unit', 'gbp-million')
        ]
        
        cs = ConversionSegment(tab, dimensions, observations)        
        tidy_sheet = cs.topandas() 
        trace.store('dataframe', tidy_sheet)
        df = trace.combine_and_trace(title, 'dataframe')

df['Period'] = df.Period.str.replace('\.0', '')
df['Quarter'] = df['Quarter'].str.lstrip()
df['Period'] = df['Period'] + df['Quarter']
df['Period'] = df['Period'].map(lambda x: 'year/' + left(x,4) if 'Q' not in x else 'quarter/' + left(x,4) + '-' + right(x,2))
df.drop(['Quarter'], axis=1, inplace=True)

df['Account Type'] = df['Account Type'].map(lambda x: x.split()[0]) + ' ' +  df['Account Type'].map(lambda x: x.split()[1])
df['Account Type'] = df['Account Type'].str.rstrip('1')
df['Account Type'] = df['Account Type'].str.rstrip('2')
df['Services'] = df['Services'].str.rstrip('3')
df['Services'] = df['Services'].str.lstrip()
df = df.replace({'Seasonal Adjustment' : {' Seasonally adjusted' : 'SA', ' Not seasonally adjusted': 'NSA' }})
df['Flow Directions'] = df['Flow Directions'].map(lambda x: x.split()[0])
df.rename(columns={'OBS' : 'Value','DATAMARKER' : 'Marker'}, inplace=True)

# +

tidy = df[['Period','Flow Directions','Services','Seasonal Adjustment', 'CDID', 'Account Type', 'Value', 
           'Measure Type', 'Unit']]
for column in tidy:
    if column in ('Flow Directions', 'Services', 'Account Type'):
        tidy[column] = tidy[column].str.lstrip()
        tidy[column] = tidy[column].map(lambda x: pathify(x))
tidy

# + endofcell="--"

# --
