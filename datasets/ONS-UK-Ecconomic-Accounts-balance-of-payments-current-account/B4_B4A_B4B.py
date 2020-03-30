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

# ## Balance of Payments Current Account: Primary income B4

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
    if (tab.name == 'B4') or (tab.name == 'B4A') or (tab.name == 'B4B'):
    
        income = tab.excel_ref('B10').expand(DOWN).is_not_blank()  
        code = tab.excel_ref('C7').expand(DOWN).is_not_blank()
        year =  tab.excel_ref('D4').expand(RIGHT).is_not_blank()
        quarter = tab.excel_ref('D5').expand(RIGHT)
        seasonal_adjustment = tab.excel_ref('B2')
        income_type = tab.excel_ref('B1')
        observations = quarter.fill(DOWN).is_not_blank()
        
        if (tab.name == 'B4B'):
            flow = tab.excel_ref('B').expand(DOWN).by_index([7,18,29]) - tab.excel_ref('B72').expand(DOWN)
            earning_type = tab.excel_ref('B').expand(DOWN).by_index([9,20,31]) - tab.excel_ref('B72').expand(DOWN)
        if tab.name == 'B4':
            earning_type = tab.excel_ref('B').expand(DOWN).by_index([9,31,52]) - tab.excel_ref('B72').expand(DOWN)
            flow = tab.excel_ref('B').expand(DOWN).by_index([7,29,50]) - tab.excel_ref('B72').expand(DOWN)
        if tab.name == 'B4A':
            earning_type = tab.excel_ref('B').expand(DOWN).by_index([9,31,51]) - tab.excel_ref('B72').expand(DOWN)
            flow = tab.excel_ref('B').expand(DOWN).by_index([7,29,50]) - tab.excel_ref('B72').expand(DOWN)
                
        dimensions = [
            HDim(year, 'Period', DIRECTLY, ABOVE),
            HDim(quarter, 'Quarter', DIRECTLY, ABOVE),
            HDim(code, 'CDID', DIRECTLY, LEFT),
            HDim(flow, 'Flow Directions', CLOSEST, ABOVE),
            HDim(income, 'Income Description', DIRECTLY, LEFT),
            HDim(seasonal_adjustment, 'Seasonal Adjustment', CLOSEST, LEFT),
            HDim(earning_type, 'Earnings', CLOSEST, ABOVE),
            HDim(income_type, 'Income', CLOSEST, LEFT),
            HDimConst('Account Type', 'Current Account'),
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
df.rename(columns={'OBS' : 'Value','DATAMARKER' : 'Marker'}, inplace=True)
df['Income Description'] = df['Income Description'].str.lstrip()
df['Income Description'] = df['Income Description'].str.rstrip('1')
df['Marker'].replace(' -', 'unknown', inplace=True)
df = df.replace({'Seasonal Adjustment' : {' Seasonally adjusted' : 'SA', ' Not seasonally adjusted': 'NSA', ' Sector analysis': 'sector-analysis' }})
df = df.replace({'Earnings' : { '' : 'Net earnings', 
                                   ' (Net earnings)' : 'Net earnings',
                                   ' (Earnings of UK residents on investment abroad)' : 'Earnings of UK residents on investment abroad',
                                   ' (Foreign earnings on investment in UK)' : 'Foreign earnings on investment in the UK',
                                   ' (Foreign earnings on investment in the UK)' : 'Foreign earnings on investment in the UK'}})
# +
tidy = df[['Period','Flow Directions', 'Income', 'Income Description', 'Earnings', 'Account Type', 'Seasonal Adjustment', 
           'CDID', 'Value', 'Marker', 'Measure Type', 'Unit']]
for column in tidy:
    if column in ('Flow Directions', 'Income', 'Income Description', 'Earnings', 'Account Type'):
        tidy[column] = tidy[column].str.lstrip()
        tidy[column] = tidy[column].str.rstrip()
        tidy[column] = tidy[column].map(lambda x: pathify(x))
        
tidy

# +
destinationFolder = Path('out')
destinationFolder.mkdir(exist_ok=True, parents=True)

TITLE = 'Balance of Payments: Primary income'
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
# -


