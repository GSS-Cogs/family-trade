#!/usr/bin/env python
# coding: utf-8

# In[34]:


import logging
import json
import pandas as pd
import numpy as np

from gssutils import *


# In[35]:


logging.basicConfig(level=logging.DEBUG)


# In[36]:


infoFileName = 'info.json'

info = json.load(open(infoFileName))
scraper = Scraper(seed=infoFileName)
distro = scraper.distribution(latest=True)


# In[37]:


scraper.dataset.family = info['families']

# Get API Chunks
# api_chunks = distro.get_odata_api_chunks()
# Replace line below with line above once gss-utils issue get_odata_api_chunks() query is malformatted #216 is fixed
api_chunks = [x["MonthId"] for x in distro._session.get(
    distro.uri, params={'$apply': 'groupby((MonthId))'}).json()["value"]]
logging.debug(f'The chunks found on api are {api_chunks}')

# Get PMD Chunks
pmd_chunks = distro.get_pmd_chunks()
logging.debug(f'The chunks found on api are {pmd_chunks}')

# Get next period to download
if len(pmd_chunks) == 0:
    fetch_chunk = min(api_chunks)
else:
    # Quarter conversion f(x)=3(x-1)=1, so f(1)=1, f(2)=4, f(3)=7, f(4)-10
    # Year is y[-6:-2], Quarter is y[-1]
    tmp = list()
    for y in pmd_chunks:
        y = str(y)
        year = y[-7:-3]
        qrtr = ('0'+str(3*(int(y[-1])-1)+1))[-2:]
        tmp.append(int(year+qrtr))
    pmd_chunks = tmp
    fetch_chunk = max(set(api_chunks)-set(pmd_chunks))
logging.info(f'Earliest chunk not on PMD but found on API is {fetch_chunk}')

# For a temporary accretive data replacement, instead of fetching a single chunk as the line below
df = distro.as_pandas(chunks_wanted=fetch_chunk)

# Drop all columns not specified
drop_columns = [x for x in df.columns if x not in ['FlowTypeDescription', 'Value', 'NetMass',
                                                   'MonthId', 'RegionName', 'CountryId', 'Sitc2Code']]
df = df.drop(drop_columns, axis=1)

# Clearing all blank strings
df = df.replace(r'^\s*$', np.nan, regex=True)

# For everything which isn't a data column, it's categorical so...
for col in df.columns:
    if col not in ['Value', 'NetMass', 'MonthId']:
        df[col] = df[col].astype('category')

# Period column
# Quarter conversion g(x) = x//3+1, so g(1)=1, g(4)=2, g(7)=3, g(10)=4
df['Period'] = [
    f"{str(x)[:4]}-Q{str(int(str(x)[-2:])//3+1)}" for x in df['MonthId']]

# Flows - Rename and pathify
df.rename({"FlowTypeDescription": "Flow Type"}, inplace=True, axis=1)
df['Flow Type'].cat.rename_categories(lambda x: pathify(x), inplace=True)

# Locations
region_codes = {
    'North East': 'http://statistics.data.gov.uk/id/statistical-geography/E12000001',
    'North West': 'http://statistics.data.gov.uk/id/statistical-geography/E12000002',
    'Yorkshire and The Humber': 'http://statistics.data.gov.uk/id/statistical-geography/E12000003',
    'East Midlands': 'http://statistics.data.gov.uk/id/statistical-geography/E12000004',
    'West Midlands': 'http://statistics.data.gov.uk/id/statistical-geography/E12000005',
    'South West': 'http://statistics.data.gov.uk/id/statistical-geography/E12000009',
    # Formally 'East of England'
    'East': 'http://statistics.data.gov.uk/id/statistical-geography/E12000006',
    'South East': 'http://statistics.data.gov.uk/id/statistical-geography/E12000008',
    'London': 'http://statistics.data.gov.uk/id/statistical-geography/E12000007',
    'Northern Ireland': 'http://statistics.data.gov.uk/id/statistical-geography/N92000002',
    'Wales': 'http://statistics.data.gov.uk/id/statistical-geography/W92000004',
    'Scotland': 'http://statistics.data.gov.uk/id/statistical-geography/S92000003',
    'Unallocated - Known': 'http://gss-data.org.uk/data/gss_data/trade/hmrc-regional-trade-statistics#concept/uk-region/unallocated-known',
    'Unallocated - Unknown': 'http://gss-data.org.uk/data/gss_data/trade/hmrc-regional-trade-statistics#concept/uk-region/unallocated-unknown'
}
df['Region'] = pd.Categorical(df['RegionName'].replace(
    region_codes), categories=region_codes.values(), ordered=False)

df['Country'] = df['CountryId'].astype(str)

# # SITC Codes
# Need to go via strings
df['SITC Code'] = df['Sitc2Code'].astype(str).astype('category')

# The melty magic to take two values in the same row and create unique records for these values, the source column name becomes the 'variable' column, the column value stays in ends up in the 'value' column.
df = df.melt(id_vars=['Period', 'Flow Type', 'Region',
             'Country', 'SITC Code'], value_vars=['Value', 'NetMass'])

# Measures & Units
df.loc[df['variable'] == 'Value', 'Measure Type'] = 'monetary-value'
df.loc[df['variable'] == 'Value',
       'Unit'] = 'http://gss-data.org.uk/def/concept/measurement-units/gbp'
df.loc[df['variable'] == 'NetMass', 'Measure Type'] = 'net-mass'
df.loc[df['variable'] == 'NetMass',
       'Unit'] = 'http://qudt.org/vocab/unit/KiloGM'
df.drop('variable', axis=1, inplace=True)
df['Unit'] = df['Unit'].astype('category')
df['Measure Type'] = df['Measure Type'].astype('category')
df


# In[38]:


df = df.rename(columns={'value' : 'Value'})

scraper.dataset.comment = """

International trade in goods data at summary product and country level, by UK regions and devolved administrations.
"""

scraper.dataset.description = scraper.dataset.comment + """

HM Revenue & Customs (HMRC) collects the UK's international trade in goods data, which are published as two National Statistics series - the 'Overseas Trade in Goods Statistics (OTS)' and the 'Regional Trade in Goods Statistics (RTS)'. The RTS are published quarterly showing trade at summary product and country level, split by UK regions and devolved administrations.

RTS data is categorised by partner country and Standard International Trade Classification, Rev.4 (SITC) at division level (2-digit). In this release RTS data is analysed mainly at partner country and SITC section (1-digit) level, with references to specific SITC divisions where appropriate. The collection and publication methodology for the RTS is available on www.gov.uk.

"""
df


# In[39]:


df.to_csv('observations.csv', index=False)

catalog_metadata = scraper.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')

