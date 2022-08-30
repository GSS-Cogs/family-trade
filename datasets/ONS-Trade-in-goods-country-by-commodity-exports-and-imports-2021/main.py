# %%
import pandas as pd
import json
from gssutils import *

from zipfile import ZipFile
from io import BytesIO

import numpy as np

class MyDict(dict):
    def __missing__(self, key):
        return key

info = json.load(open('info.json'))
landingPage = info['landingPage']

#exports
scraper1 = Scraper(landingPage[0])
distribution1 = scraper1.distribution(mediaType=lambda x: 'zip' in x, latest=True)

#imports
scraper2 = Scraper(landingPage[1])
distribution2 = scraper2.distribution(mediaType=lambda x: 'zip' in x, latest=True)


def transform(dataframe):
    '''transforms the dataframe to a datacube
    '''
    df = dataframe
    df.rename(columns={
        'COMMODITY': 'Commodity',
        'COUNTRY': 'ONS Partner Geography',
        'DIRECTION': 'Flow'
        }, inplace=True)
    tidy = pd.melt(df, id_vars=['Commodity','ONS Partner Geography', 'Flow'], var_name='Period', value_name='Value')
    tidy_sheet = tidy.sort_values(['Commodity','ONS Partner Geography', 'Flow'])
    return tidy_sheet

# %%

tab_names = ['1. Annual Exports', '2. Quarterly Exports', '3. Monthly Exports']
tidy_tabs = []

'''Country by Commodity Export data'''
with ZipFile(BytesIO(scraper1.session.get(distribution1.downloadURL).content)) as zip:
    assert(len(zip.namelist()) == 1)
    with zip.open(zip.namelist()[0]) as excelFile:
        buffered_fobj = BytesIO(excelFile.read())
        for i in tab_names:
            data1 = pd.read_excel(buffered_fobj,
                                sheet_name=i, skiprows=3, dtype={
                                    'COMMODITY': 'category',
                                    'COUNTRY': 'category',
                                    'DIRECTION': 'category'
                                }, na_values=['','N/A'], keep_default_na=False)
            tidy_tabs.append(data1)
export_sheets = []

for i in tidy_tabs:
    export_sheets.append(transform(i))

table1 = pd.concat(export_sheets)

# %%
tab_names = ['1. Annual Imports', '2. Quarterly Imports', '3. Monthly Imports']
tidy_tabs = []

'''Country by Commodity Import data'''
with ZipFile(BytesIO(scraper2.session.get(distribution2.downloadURL).content)) as zip:
    assert(len(zip.namelist()) == 1)
    with zip.open(zip.namelist()[0]) as excelFile:
        buffered_fobj = BytesIO(excelFile.read())
        for i in tab_names:
            data2 = pd.read_excel(buffered_fobj,
                                sheet_name=i, skiprows=3, dtype={
                                    'COMMODITY': 'category',
                                    'COUNTRY': 'category',
                                    'DIRECTION': 'category'
                                }, na_values=['','N/A'], keep_default_na=False)
            tidy_tabs.append(data2)
import_sheets = []

for i in tidy_tabs:
    import_sheets.append(transform(i))

table2 = pd.concat(import_sheets)

# %%
table = pd.concat([table1, table2])

# Post ptocessing 
# %%
table.loc[table['Period'].str.len() == 7, 'Period'] = pd.to_datetime(table.loc[table['Period'].str.len() == 7, 'Period'], format='%Y%b').astype(str).map(lambda x: 'month/' + x[:7])# + left(x,7))
table['Period'] = table['Period'].apply(lambda x: 'year/' + x if len(x) == 4  else (
    'quarter/' + x[:4] + '-' + x[4:] if len(x) == 6  else x ))
table['Flow'] = table['Flow'].map(lambda x: x.split(' ')[1])
table['Flow'] = table['Flow'].map(lambda x: pathify(x))
table['ONS Partner Geography'].cat.categories = table['ONS Partner Geography'].cat.categories.map(lambda x: x[:2])
table['Commodity'].cat.categories = table['Commodity'].cat.categories.map(lambda x: x.split(' ')[0])
table['Seasonal Adjustment'] = pd.Series('NSA', index=table.index, dtype='category')

# %%
table['Marker'] = ''
table['Marker'] = np.where(table['Value'].str.isnumeric() == False, table['Value'], table['Marker'])

markerRep = MyDict({'X' : 'data-not-collated'})
valRep = MyDict({'X' : ''})

table['Marker'] = table['Marker'].map(markerRep)
table['Value'] = table['Value'].map(valRep)
# %%
table = table[['Period','ONS Partner Geography','Flow','Commodity','Seasonal Adjustment','Value', 'Marker']]
table


descr = """
Monthly import country-by-commodity data on the UK's trade in goods, including trade by all countries and selected commodities, non-seasonally adjusted.

Users should note the following:
Industry data has been produced using Standard Industrial Classification 2007 (SIC07).
Commodity data has been produced using Standard International Trade Classification (SITC).

Due to risks around disclosing data related to individual firms we are only able to provide data for certain combinations of the dimensions included, i.e. country, commodity and industry. This dataset therefore provides the following two combinations:
    Industry (SIC07 2 digit), by Commodity (SITC 2 digit), by geographic region (worldwide, EU and non-EU)
    Industry (SIC07 2 digit), by Commodity total, by individual country

Methodology improvements
Within this latest experimental release improvements have been made to the methodology that has resulted in some revisions when compared to our previous release in April 2019.
These changes include; improvements to the data linking methodology and a targeted allocation of some of the Balance of Payments (BoP) adjustments to industry.
The data linking improvements were required due to subtleties in both the HMRC data and IDBR not previously recognised within Trade.

While we are happy with the quality of the data in this experimental release we have noticed some data movements, specifically in 2018.
We will continue to review the movements seen in both the HMRC microdata and the linking methodology and, where appropriate, will further develop the methodology for Trade in Goods by Industry for future releases.

"""

title = "Trade in goods: country by commodity, exports and imports 2021"
scraper1.dataset.title = title
scraper1.dataset.description = descr


# %%
table.to_csv('observations.csv', index=False)
catalog_metadata = scraper1.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')

# %%
