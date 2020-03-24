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

# ## Balance of Payments Current Account: Transactions with the EU and EMU B6, B6A

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


# +
for tab in tabs:
    if (tab.name == 'B6') or (tab.name == 'B6A1'):
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
            HDimConst('Unit', '£ Million'),
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)        
        #savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
        tidied_sheets.append(tidy_sheet.topandas())
        



# -

df = pd.concat(tidied_sheets, ignore_index = True, sort = False)
df['Quarter'] = df['Quarter'].astype(str)
df['Quarter'] = df['Quarter'].map(lambda x: '-Q1' if 'Q1' in x else('-Q2' if 'Q2' in x else ('-Q3' if 'Q3' in x else ('-Q4' if 'Q4' in x else ''))))
df['Year'] = df['Quarter'].map(lambda x: 'government-quarter/' if '-Q1' in x else('government-quarter/' if '-Q2' in x else('government-quarter/' if '-Q3' in x else('government-quarter/' if '-Q4' in x else 'government-year/'))))
df['Period'] = df['Year'] + df['Period'].map(lambda x: left(x,4)) + df['Quarter']
df.drop(['Quarter', 'Year'], axis=1, inplace=True)
df['Account Type'] = df['Account Type'].map(lambda x: x.split()[0]) + ' ' +  df['Account Type'].map(lambda x: x.split()[1])
df['Account Type'] = df['Account Type'].str.rstrip(':')
df['Services'] = df['Services'].str.rstrip('4')
df['Members'] = df['Members'].map(lambda x: 'of which EMU members' if '     of which EMU members4' in x else 'European Union (EU)')
df = df.replace({'Seasonal Adjustment' : {' Seasonally adjusted' : 'SA', ' Not seasonally adjusted': 'NSA' }})
df.rename(columns={'OBS' : 'Value','DATAMARKER' : 'Marker'}, inplace=True)


# +
tidy = df[['Period','Flow Directions', 'Account Type', 'Transaction Type', 'Services','Members', 'Seasonal Adjustment', 
           'CDID', 'Value', 'Measure Type', 'Unit']]
for column in tidy:
    if column in ('Flow Directions', 'Account Type', 'Transaction Type', 'Services', 'Members'):
        tidy[column] = tidy[column].str.lstrip()
        tidy[column] = tidy[column].map(lambda x: pathify(x))
        
tidy

# +
destinationFolder = Path('out')
destinationFolder.mkdir(exist_ok=True, parents=True)

TITLE = 'Balance of Payments Current Account: Transactions with the EU and EMU'
OBS_ID = pathify(TITLE)
GROUP_ID = 'ONS-UK-Ecconomic-Accounts-balance-of-payments-current-account'

tidy.drop_duplicates().to_csv(destinationFolder / f'{OBS_ID}.csv', index = False)
# -

print(OBS_ID)

# +
from gssutils.metadata import THEME
scraper.set_base_uri('http://gss-data.org.uk')
scraper.set_dataset_id(f'gss_data/trade/{GROUP_ID}/{OBS_ID}')
scraper.dataset.title = TITLE

scraper.dataset.family = 'trade'
with open(destinationFolder / f'{OBS_ID}.csv-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())

schema = CSVWMetadata('https://gss-cogs.github.io/family-trade/reference/')
schema.create(destinationFolder / f'{OBS_ID}.csv', destinationFolder / f'{OBS_ID}.csv-schema.json')
# -


