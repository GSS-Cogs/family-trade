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
import numpy as np
from gssutils import *
import json
from gssutils.metadata import THEME
from gssutils.metadata import *
from databaker.framework import *

cubes = Cubes("info.json")

with open ('info.json') as file:
    info = json.load(file)

landingPage = info['landingPage']
landingPage

title = 'Balance of Payments: Summary'

scraper = Scraper(landingPage)
scraper.dataset.family = info['families']
scraper

# +

# +
# dist = scraper.distributions[0]
# dist
# -

tabs = scraper.distributions[0].as_databaker()


def left(s, amount):
    return s[:amount]


def right(s, amount):
    return s[-amount:]


# -

# +
tidied_sheets = []

for tab in tabs:
    if 'B1' in tab.name: #Tabsz B1
        remove_percentage = tab.excel_ref('A30').expand(RIGHT).expand(DOWN) - tab.excel_ref('A41').expand(RIGHT).expand(DOWN)
        account_Type = tab.excel_ref('B').expand(DOWN).by_index([9,44,66]) - tab.excel_ref('B76').expand(DOWN)
        seasonal_adjustment = tab.excel_ref('B').expand(DOWN).by_index([7,42]) - tab.excel_ref('B76').expand(DOWN)
        flow = tab.excel_ref('B2')
        services = tab.excel_ref('B10').expand(DOWN).is_not_blank() - account_Type - seasonal_adjustment - remove_percentage
        code = tab.excel_ref('C7').expand(DOWN).is_not_blank()
        year =  tab.excel_ref('D4').expand(RIGHT).is_not_blank()
        quarter = tab.excel_ref('D5').expand(RIGHT)
        observations = quarter.fill(DOWN).is_not_blank() - remove_percentage
        
        dimensions = [
            HDim(account_Type, 'Account Type', CLOSEST, ABOVE),
            HDim(seasonal_adjustment, 'Seasonal Adjustment', CLOSEST, ABOVE),
            HDim(flow, 'Flow Directions', CLOSEST, ABOVE),
            HDim(services, 'Services', DIRECTLY, LEFT),
            HDim(code, 'CDID', DIRECTLY, LEFT),
            HDim(year, 'Period', DIRECTLY, ABOVE),
            HDim(quarter, 'Quarter', DIRECTLY, ABOVE),
            HDimConst('Measure Type', 'GBP Total'),
            HDimConst('Unit', 'gbp-million')
        ]
        
        tidy_sheet = ConversionSegment(tab, dimensions, observations)        
        #savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
        tidied_sheets.append(tidy_sheet.topandas())  
# -

df = pd.concat(tidied_sheets, ignore_index = True, sort = False)

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
    if column in ['Flow Directions', 'Services', 'Account Type']:
        tidy[column] = tidy[column].str.lstrip()
        tidy[column] = tidy[column].map(lambda x: pathify(x))
tidy

cubes.add_cube(scraper, tidy, title)
cubes.output_all()

# + endofcell="--"

# --
