# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# ## Balance of Payments Capital Account B7

from gssutils import *
from gssutils.metadata import THEME
scraper = Scraper('https://www.ons.gov.uk/economy/nationalaccounts/uksectoraccounts/datasets/unitedkingdomeconomicaccountsbalanceofpaymentscurrentaccount')
scraper

# +
dist = scraper.distributions[0]
tabs = (t for t in dist.as_databaker())
tidied_sheets = []

def left(s, amount):
    return s[:amount]
def right(s, amount):
    return s[-amount:]


# -

for tab in tabs:
    if 'B7' in tab.name: #Tabs B7 and B7A
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
            HDimConst('Unit', '£ Million'),
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)        
       # savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
        tidied_sheets.append(tidy_sheet.topandas()) 


df = pd.concat(tidied_sheets, ignore_index = True, sort = False)
df['Quarter'] = df['Quarter'].astype(str)
df['Quarter'] = df['Quarter'].map(lambda x: '-Q1' if 'Q1' in x else('-Q2' if 'Q2' in x else ('-Q3' if 'Q3' in x else ('-Q4' if 'Q4' in x else ''))))
df['Year'] = df['Quarter'].map(lambda x: 'government-quarter/' if '-Q1' in x else('government-quarter/' if '-Q2' in x else('government-quarter/' if '-Q3' in x else('government-quarter/' if '-Q4' in x else 'government-year/'))))
df['Period'] = df['Year'] + df['Period'].map(lambda x: left(x,4)) + df['Quarter']
df.drop(['Quarter', 'Year'], axis=1, inplace=True)
df['Account Type'] = df['Account Type'].map(lambda x: x.split()[0]) + ' ' +  df['Account Type'].map(lambda x: x.split()[1])
df['Account Type'] = df['Account Type'].str.rstrip('1')
df['Services'] = df['Services'].str.rstrip('2')
df['Services'] = df['Services'].str.lstrip()
df = df.replace({'Sector' : {' ' : 'total'}})
df.rename(columns={'OBS' : 'Value','DATAMARKER' : 'Marker'}, inplace=True)
df['Marker'].replace(' -', 'unknown', inplace=True)
df = df.replace({'Seasonal Adjustment' : {' Seasonally adjusted' : 'SA', ' Not seasonally adjusted': 'NSA' }})

# +
tidy = df[['Period','Flow Directions','Services','Sector','Seasonal Adjustment', 'CDID', 'Account Type', 'Value', 
           'Marker','Measure Type', 'Unit']]
for column in tidy:
    if column in ('Flow Directions', 'Services', 'Account Type', 'Sector'):
        tidy[column] = tidy[column].str.lstrip()
        tidy[column] = tidy[column].map(lambda x: pathify(x))
        
tidy

# +
destinationFolder = Path('out')
destinationFolder.mkdir(exist_ok=True, parents=True)

TITLE = 'Balance of Payments: Capital Account'
OBS_ID = pathify(TITLE)

tidy.drop_duplicates().to_csv(destinationFolder / f'{OBS_ID}.csv', index = False)
# -

GROUP_ID = 'ons-uk-ecconomic-accounts-balance-of-payments-current-account'

# +
from gssutils.metadata import THEME
scraper.set_base_uri('http://gss-data.org.uk')
scraper.set_dataset_id(f'gss_data/trade/{GROUP_ID}/{OBS_ID}')
scraper.dataset.title = f'{TITLE}'

scraper.dataset.family = 'trade'
with open(destinationFolder / f'{OBS_ID}.csv-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())

schema = CSVWMetadata('https://gss-cogs.github.io/family-trade/reference/')
schema.create(destinationFolder / f'{OBS_ID}.csv', destinationFolder / f'{OBS_ID}.csv-schema.json')
