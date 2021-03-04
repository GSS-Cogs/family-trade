# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.10.2
#   kernelspec:
#     display_name: Python 3.8.8 64-bit
#     metadata:
#       interpreter:
#         hash: 4cd7ab41f5fca4b9b44701077e38c5ffd31fe66a6cab21e0214b68d958d0e462
#     name: python3
# ---

# +
import logging
import json
import pandas as pd
import numpy as np

from gssutils import *

# +
infoFileName = 'info.json'

info    = json.load(open(infoFileName))
scraper = Scraper(seed=infoFileName)
cubes   = Cubes(infoFileName)
distro  = scraper.distribution(latest=True)
# -

scraper.dataset.family = info['families']

# Get API Chunks
api_chunks = distro.get_odata_api_chunks()
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
        year = y[-6:-2]
        qrtr = ('0'+str(3*(int(y[-1])-1)+1))[-2:]
        tmp.append(year+qrtr)
    pmd_chunks = tmp
    fetch_chunk = min(set(api_chunks)-set(pmd_chunks))
logging.info(f'Earliest chunk not on PMD but found on API is {fetch_chunk}')

df = distro.as_pandas(chunks_wanted=fetch_chunk)

# Clearing all blank strings
df = df.replace(r'^\s*$', np.nan, regex=True)

# For everything which isn't a data column, it's categorical so...
for col in df.columns:
    if col not in ['Value', 'NetMass']:
        df[col] = df[col].astype('category')

# Quarter conversion g(x) = x//3+1, so g(1)=1, g(4)=2, g(7)=3, g(10)=4
df['Period'] = [f"/id/quarter/{str(x)[:4]}-{str(int(str(x)[-2])//3+1)}" for x in df['MonthId']]

df.head()

df.columns

# Flows
df.rename({"FlowTypeDescription": "Flow Type"}, inplace=True, axis=1)
df['Flow Type'].cat.rename_categories(lambda x: utils.pathify(x), inplace=True)

# Region Name
regions = {
    'North East': 'http://statistics.data.gov.uk/id/statistical-geography/E12000001',
    'North West': 'http://statistics.data.gov.uk/id/statistical-geography/E12000002',
    'Yorkshire and The Humber': 'http://statistics.data.gov.uk/id/statistical-geography/E12000003',
    'East Midlands': 'http://statistics.data.gov.uk/id/statistical-geography/E12000004',
    'West Midlands': 'http://statistics.data.gov.uk/id/statistical-geography/E12000005',
    'South West': 'http://statistics.data.gov.uk/id/statistical-geography/E12000009',
    'East': 'http://statistics.data.gov.uk/id/statistical-geography/E12000006', # Formally 'East of England'
    'South East': 'http://statistics.data.gov.uk/id/statistical-geography/E12000008',
    'London': 'http://statistics.data.gov.uk/id/statistical-geography/E12000007',
    'Unallocated - Known': 'http://gss-data.org.uk/data/gss_data/trade/HMRC_RTS#concept/uk-region/unallocated-known',
    'Unallocated - Unknown': 'http://gss-data.org.uk/data/gss_data/trade/HMRC_RTS#concept/uk-region/unallocated-unknown',
    'Northern Ireland': 'http://statistics.data.gov.uk/id/statistical-geography/N92000002',
    'Wales': 'http://statistics.data.gov.uk/id/statistical-geography/W92000004',
    'Scotland': 'http://statistics.data.gov.uk/id/statistical-geography/S92000003'
}
df['UK Region'] = df['RegionName'].cat.rename_categories(regions)

# # Country Codes
# Our goal here is to use the ISO-3166 Alpha-2 codes http://gss-data.org.uk/def/trade/concept/international-country-codes/{CountryCodeAlpha} but if there isn't a country code, then use
# http://gss-data.org.uk/data/gss_data/trade/HMRC_RTS#concept/country/{CountryName} (patified)
#
# The destination column will be `Country`.
#
# And since we're working with categorical variables (which makes for things like mapping faster), we need to format these two columns seperately, combine the categories as strings, and then reconvert to categories.

# CountryCodes
df['CountryCodeAlpha'].cat.rename_categories(lambda x: f"http://gss-data.org.uk/def/trade/concept/international-country-codes/{x}", inplace=True)

# CountryNames 
df['CountryName'].cat.rename_categories(lambda x: f"http://gss-data.org.uk/data/gss_data/trade/HMRC_RTS#concept/country/{pathify(x)}", inplace=True)

# Combine the two columns as strings, preferring CountryCodes over CountryNames
df['Country'] = df['CountryCodeAlpha'].astype(str)
df.loc[df['Country'] == 'nan', 'Country'] = df.loc[df['Country'] == 'nan', 'CountryName'].astype(str)

# Return Country to categories
df['Country'] = df['Country'].astype('category')

# # SITC Codes
# Need to go via strings again like Country Codes

df['SITC Code'] = df['Sitc1Code'].astype(str) + df['Sitc2Code'].astype(str)
df['SITC Code'] = df['SITC Code'].astype('category')

# Bring Value and NetMass into a single column
new_df = pd.DataFrame()
for measure in ['Value', 'NetMass']:
    temp_df = df[['Period', 'Flow Type', 'UK Region', 'Country', 'SITC Code', measure]]
    temp_df.rename({measure: 'Value'}, axis=1, inplace=True)
    temp_df['measure type'] = measure
    new_df = pd.concat([new_df, temp_df], axis=0)
df = new_df
del temp_df, new_df


# +
# Final formatting - Columns
df.columns = [pathify(x) for x in df.columns]

# Final formatting - measure-types
df['measure-type'] = df['measure-type'].astype('category')
df['measure-type'].cat.rename_categories({'Value': 'value', 'NetMass': 'net-mass'}, inplace=True)

# -

cubes.add_cube(scraper, df, scraper.title)

# Write cube
cubes.output_all()


