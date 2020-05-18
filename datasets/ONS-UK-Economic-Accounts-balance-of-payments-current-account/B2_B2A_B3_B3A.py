# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.4.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# ## Balance of Payments Current Account: Trade in goods and services B2, B3 

# +
from gssutils import *
import json

scraper = Scraper(json.load(open('info.json'))['landingPage'])
scraper

# +
dist = scraper.distributions[0]
tabs = (t for t in dist.as_databaker())
tidied_sheets = []

def left(s, amount):
    return s[:amount]
def right(s, amount):
    return s[-amount:]

import re
YEAR_RE = re.compile(r'[0-9]{4}')
YEAR_MONTH_RE = re.compile(r'([0-9]{4})\s+(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)')
YEAR_QUARTER_RE = re.compile(r'([0-9]{4})(Q[1-4])')

class Re(object):
    def __init__(self):
        self.last_match = None
    def fullmatch(self,pattern,text):
        self.last_match = re.fullmatch(pattern,text)
        return self.last_match

def time2period(t):
    gre = Re()
    if gre.fullmatch(YEAR_RE, t):
        return f"year/{t}"
    elif gre.fullmatch(YEAR_MONTH_RE, t):
        year, month = gre.last_match.groups()
        month_num = {'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04', 'MAY': '05', 'JUN': '06',
                     'JUL': '07', 'AUG': '08', 'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'}.get(month)
        return f"month/{year}-{month_num}"
    elif gre.fullmatch(YEAR_QUARTER_RE, t):
        year, quarter = gre.last_match.groups()
        return f"quarter/{year}-{quarter}"
    else:
        print(f"no match for {t}")


# -

for tab in tabs:
    if 'B2' in tab.name: #Tabs B2 and B2A
        flow = tab.excel_ref('B').expand(DOWN).by_index([7,21,35]) - tab.excel_ref('B46').expand(DOWN)
        product = tab.excel_ref('B').expand(DOWN).is_not_blank().is_not_whitespace() - flow  - tab.excel_ref('B3').expand(UP)
        code = tab.excel_ref('C7').expand(DOWN).is_not_blank()
        year =  tab.excel_ref('D4').expand(RIGHT).is_not_blank()
        quarter = tab.excel_ref('D5').expand(RIGHT)
        seasonal_adjustment = tab.excel_ref('B2')
        trade = tab.excel_ref('B1')
        observations = quarter.fill(DOWN).is_not_blank()
        #savepreviewhtml(observations)
        
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

        tidy_sheet = ConversionSegment(tab, dimensions, observations)        
        #savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
        tidied_sheets.append(tidy_sheet.topandas())
        
    if 'B3' in tab.name: #Tabs B3 and B3A
        
        flow = tab.excel_ref('B').expand(DOWN).by_index([7,22,37]) - tab.excel_ref('B51').expand(DOWN)
        product = tab.excel_ref('B').expand(DOWN).is_not_blank().is_not_whitespace() - flow  - tab.excel_ref('B3').expand(UP)
        code = tab.excel_ref('C7').expand(DOWN).is_not_blank()
        year =  tab.excel_ref('D4').expand(RIGHT).is_not_blank()
        quarter = tab.excel_ref('D5').expand(RIGHT)
        seasonal_adjustment = tab.excel_ref('B2')
        trade = tab.excel_ref('B1')
        observations = quarter.fill(DOWN).is_not_blank()
        #savepreviewhtml(flow)
        
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

        tidy_sheet = ConversionSegment(tab, dimensions, observations)        
       # savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
        tidied_sheets.append(tidy_sheet.topandas())


df = pd.concat(tidied_sheets, ignore_index = True, sort = False)
df['Period'] = df.Period.str.replace('\.0', '')
df['Quarter'] = df['Quarter'].str.lstrip()
df['Period'] = df['Period'] + df['Quarter']
df.drop(['Quarter'], axis=1, inplace=True)
df['Period'] = df['Period'].apply(time2period)

df['Flow Directions'] = df['Flow Directions'].map(lambda x: x.split()[0])
df = df.replace({'Seasonal Adjustment' : {' Seasonally adjusted' : 'SA', ' Not seasonally adjusted' : 'NSA' }})
df['Product'] = df['Product'].str.lstrip()
df.rename(columns={'OBS' : 'Value','DATAMARKER' : 'Marker'}, inplace=True)
df['Marker'].replace(' -', 'unknown', inplace=True)


# +
tidy = df[['Period','Flow Directions','Product','Seasonal Adjustment', 'CDID', 'Services', 'Account Type', 'Value', 'Marker', 'Measure Type', 'Unit']]
for column in tidy:
    if column in ('Flow Directions', 'Product', 'Services', 'Account Type'):
        tidy[column] = tidy[column].str.lstrip()
        tidy[column] = tidy[column].map(lambda x: pathify(x))
        
tidy

# + endofcell="--"
destinationFolder = Path('out')
destinationFolder.mkdir(exist_ok=True, parents=True)

TITLE = 'Balance of Payments: Trade in goods and services'
OBS_ID = pathify(TITLE)
import os
GROUP_ID = pathify(os.environ.get('JOB_NAME', 'gss_data/trade/' + Path(os.getcwd()).name))

tidy.drop_duplicates().to_csv(destinationFolder / f'{OBS_ID}.csv', index = False)
# # +
from gssutils.metadata import THEME
scraper.set_base_uri('http://gss-data.org.uk')
scraper.set_dataset_id(f'{GROUP_ID}/{OBS_ID}')
scraper.dataset.title = TITLE

scraper.dataset.family = 'trade'
with open(destinationFolder / f'{OBS_ID}.csv-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())
# -

schema = CSVWMetadata('https://gss-cogs.github.io/family-trade/reference/')
schema.create(destinationFolder / f'{OBS_ID}.csv', destinationFolder / f'{OBS_ID}.csv-schema.json')

tidy

# --
