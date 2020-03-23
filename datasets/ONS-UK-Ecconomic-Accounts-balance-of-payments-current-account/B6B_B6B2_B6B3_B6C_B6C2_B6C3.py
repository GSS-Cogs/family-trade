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

# ## Balance of Payments Current Account: Transactions with non-EU countries B6B, B6B2, B6B3, B6C, B6C2, B6C3

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
    if (tab.name == 'B6B') or (tab.name == 'B6B_2') or (tab.name == 'B6B_3') or (tab.name == 'B6C') or (tab.name == 'B6C_2') or (tab.name == 'B6C_3'):
        
        account_Type = tab.excel_ref('B1')
        seasonal_adjustment = tab.excel_ref('B3')
        transaction_type = tab.excel_ref('B8')
        flow = tab.excel_ref('B').expand(DOWN).by_index([10]) - tab.excel_ref('B72').expand(DOWN)
        services = tab.excel_ref('B').expand(DOWN).by_index([11,21,31,41,51,62]) - tab.excel_ref('B72').expand(DOWN)
        country = tab.excel_ref('B10').expand(DOWN).is_not_blank()
        code = tab.excel_ref('C7').expand(DOWN).is_not_blank()
        year =  tab.excel_ref('D5').expand(RIGHT).is_not_blank()
        quarter = tab.excel_ref('D6').expand(RIGHT)
        #savepreviewhtml(observations)
        
        if (tab.name == 'B6B_2') or (tab.name == 'B6B_3') or (tab.name == 'B6C_2') or (tab.name == 'B6C_3'):
            transaction_type = tab.excel_ref('B9')
            flow = tab.excel_ref('B').expand(DOWN).by_index([11]) - tab.excel_ref('B72').expand(DOWN)
            services = tab.excel_ref('B').expand(DOWN).by_index([12,22,32,42,52,63]) - tab.excel_ref('B73').expand(DOWN)
            year =  tab.excel_ref('D6').expand(RIGHT).is_not_blank()
            quarter = tab.excel_ref('D7').expand(RIGHT)
        if (tab.name == 'B6B_3') or (tab.name == 'B6C_2') or (tab.name == 'B6C_3'):
            services = tab.excel_ref('B').expand(DOWN).by_index([12,22,32,42,52,63]) - tab.excel_ref('B73').expand(DOWN)
        
        observations = quarter.fill(DOWN).is_not_blank()   
        
        dimensions = [
            HDim(account_Type, 'Account Type', CLOSEST, LEFT),
            HDim(seasonal_adjustment, 'Seasonal adjustments', CLOSEST, LEFT),
            HDim(transaction_type, 'Transaction Type', CLOSEST, LEFT),
            HDim(flow, 'Flow Directions', CLOSEST, ABOVE),
            HDim(services, 'Services', CLOSEST, ABOVE),
            HDim(country, 'Country Transaction', DIRECTLY, LEFT),
            HDim(code, 'CIDI', DIRECTLY, LEFT),
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
df['Account Type'] = df['Account Type'].str.rstrip(':')
df['Transaction Type'] = df['Transaction Type'].str.rstrip('1')
df['Country Transaction'] = df['Country Transaction'].str.lstrip()
df.rename(columns={'OBS' : 'Value','DATAMARKER' : 'Marker'}, inplace=True)
df['Marker'].replace(' -', 'unknown', inplace=True)

# +
tidy = df[['Period','Flow Directions', 'Services', 'Account Type', 'Transaction Type', 'Country Transaction', 'Seasonal adjustments', 
           'CIDI', 'Value', 'Marker', 'Measure Type', 'Unit']]
for column in tidy:
    if column in ('Flow Directions', 'Services', 'Account Type', 'Seasonal adjustments', 'Transaction Type', 'Country Transaction'):
        tidy[column] = tidy[column].str.lstrip()
        tidy[column] = tidy[column].map(lambda x: pathify(x))
        
tidy

# +
destinationFolder = Path('out')
destinationFolder.mkdir(exist_ok=True, parents=True)

TITLE = 'Balance of Payments Current Account: Transactions with non-EU countries'
OBS_ID = pathify(TITLE)

tidy.drop_duplicates().to_csv(destinationFolder / f'{OBS_ID}.csv', index = False)

# +
from gssutils.metadata import THEME
from os import environ
scraper.set_dataset_id(f'{pathify(environ.get("JOB_NAME", ""))}/{OBS_ID}')
scraper.dataset.title = f'{TITLE}'
scraper.dataset.family = 'trade'

with open(destinationFolder / f'{OBS_ID}.csv-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())

schema = CSVWMetadata('https://gss-cogs.github.io/family-disability/reference/')
schema.create(destinationFolder / f'{OBS_ID}.csv', destinationFolder / f'{OBS_ID}.csv-schema.json')
# -


