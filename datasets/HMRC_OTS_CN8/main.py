#!/usr/bin/env python
# coding: utf-8
# %%
from gssutils import *
from databaker.framework import *
import pandas as pd
from gssutils.metadata import THEME
from gssutils.metadata import *
import datetime
from gssutils.metadata import Distribution, GOV
pd.options.mode.chained_assignment = None

def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

def mid(s, offset, amount):
    return s[offset:offset+amount]

scraper = Scraper('https://www.gov.uk/government/statistical-data-sets/live-tables-on-social-housing-sales')
dist = scraper.distribution(title=lambda x: x.startswith('Table 678'))
scraper.dataset.title = dist.title
#scraper.dataset.description = 'The table provides statistics on the sales of social housing stock – whether owned by local authorities or private registered providers.'    
dist


# %%


tabs = (t for t in dist.as_databaker())

tidied_sheets = []

for tab in tabs:
    
    cell = tab.filter(contains_string('Table 678'))

    remove = cell.expand(DOWN).filter(contains_string('Notes')).shift(0,-2).expand(DOWN).expand(RIGHT)

    period = cell.shift(0,4).expand(DOWN).is_not_blank() - remove

    area = 'E92000001'
        
    scheme = cell.shift(0,2).expand(RIGHT).is_not_blank()
        
    scheme_type = cell.shift(0,3).expand(RIGHT).is_not_blank()

    observations = period.fill(RIGHT).is_not_blank()

    dimensions = [
        HDim(period, 'Period', DIRECTLY, LEFT),
        HDim(scheme, 'scheme', CLOSEST, LEFT),
        HDim(scheme_type, 'Scheme Type', DIRECTLY, ABOVE),
        HDimConst('Area', area),
        HDimConst('Measure Type', 'Count'),
        HDimConst('Unit', 'Dwellings')
        ]

    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    savepreviewhtml(tidy_sheet, fname="Preview.html")

    tidied_sheets.append(tidy_sheet.topandas())
        


# %%
df = pd.concat(tidied_sheets, ignore_index = True, sort = False).fillna('')

df = df.replace({'Period' : {
    '2018-195' : '2018-19',}})

df['Period'] = df['Period'].map(lambda x: 'government-year/' + left(x, 4) + '-19' + right(x,2) if '19' in left(x,2) else 'government-year/' + left(x, 4) + '-20' + right(x,2))

df = df.replace({'scheme' : {
    'Private Registered Provider (PRP) Social Housing Sales6' : 'Private Registered Provider (PRP) Social Housing Sales',},
                'DATAMARKER' : {
    '..' : 'not available'
                },
                'Scheme Type' : {
    '(LA, Preserved and Voluntary 2) Right to Buy Sales' : 'Right to Buy Sales',
    '(Preserved and Voluntary 2,3) Right to Buy Sales' : 'Right to Buy Sales', 
    'Other Sales to tenants' : 'Other Sales', 
    'Sales to Private Sector 3,4' : 'Sales to Private Sector', 
    'Total1' : 'Total'
                }})

df.rename(columns={'OBS' : 'Value',
                   'DATAMARKER' : 'Marker',
                   'scheme' : 'MCHLG Scheme',
                   'Scheme Type' : 'MCHLG Scheme Type'}, inplace=True)

df.head(50)


# %%
from IPython.core.display import HTML
for col in df:
    if col not in ['Value']:
        df[col] = df[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(df[col].cat.categories)    


# %%
tidy = df[['Area','Period', 'MCHLG Scheme', 'MCHLG Scheme Type', 'Value', 'Marker', 'Measure Type', 'Unit']]

for column in tidy:
    if column in ('Marker', 'MCHLG Scheme', 'MCHLG Scheme Type'):
        tidy[column] = tidy[column].map(lambda x: pathify(x))

tidy.head(50)

from IPython.core.display import HTML
for col in tidy:
    if col not in ['Value']:
        tidy[col] = tidy[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(tidy[col].cat.categories)    


# %%
destinationFolder = Path('out')
destinationFolder.mkdir(exist_ok=True, parents=True)

TAB_NAME = 'observations'

tidy.drop_duplicates().to_csv(destinationFolder / f'{TAB_NAME}.csv', index = False)

scraper.dataset.family = 'affordable-housing'
scraper.dataset.comment = """
        The total local authority social housing sales reported in this table differs slightly from the total sales by local authority reported in live table 682. The local authority data is this table is sourced from LAHS and DELTA, whereas the data in live table 682 is sourced entirely from LAHS.
        Does not include sales from one PRP to another PRP.
        Further information on other types of social housing sales (such as more detail at a local authority level and on Right to Buy), are available here-
        https://www.gov.uk/government/collections/social-housing-sales-including-right-to-buy-and-transfersections/social-housing-sales-including-right-to-buy-and-transfers
        """

with open(destinationFolder / f'{TAB_NAME}.csv-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())

csvw = CSVWMetadata('https://gss-cogs.github.io/family-affordable-housing/reference/')
csvw.create(destinationFolder / f'{TAB_NAME}.csv', destinationFolder / f'{TAB_NAME}.csv-schema.json')
tidy


# %%




