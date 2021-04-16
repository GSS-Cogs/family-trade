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
# -

logging.basicConfig(level=logging.DEBUG)

# +
infoFileName = 'info.json'

info = json.load(open(infoFileName))
scraper = Scraper(seed=infoFileName)
cubes = Cubes(infoFileName)
distro = scraper.distribution(latest=True)
# -

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
# df = distro.as_pandas(chunks_wanted=fetch_chunk)
# We will get 6 in one go.
df = distro.as_pandas(chunks_wanted=fetch_chunk)

# Clearing all blank strings
df = df.replace(r'^\s*$', np.nan, regex=True)

# For everything which isn't a data column, it's categorical so...
for col in df.columns:
    if col not in ['Value', 'NetMass']:
        df[col] = df[col].astype('category')

# Quarter conversion g(x) = x//3+1, so g(1)=1, g(4)=2, g(7)=3, g(10)=4
df['Period'] = [
    f"id/quarter/{str(x)[:4]}-Q{str(int(str(x)[-2:])//3+1)}" for x in df['MonthId']]

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
    # Formally 'East of England'
    'East': 'http://statistics.data.gov.uk/id/statistical-geography/E12000006',
    'South East': 'http://statistics.data.gov.uk/id/statistical-geography/E12000008',
    'London': 'http://statistics.data.gov.uk/id/statistical-geography/E12000007',
    'Unallocated - Known': 'http://gss-data.org.uk/data/gss_data/trade/HMRC_RTS#concept/uk-region/unallocated-known',
    'Unallocated - Unknown': 'http://gss-data.org.uk/data/gss_data/trade/HMRC_RTS#concept/uk-region/unallocated-unknown',
    'Northern Ireland': 'http://statistics.data.gov.uk/id/statistical-geography/N92000002',
    'Wales': 'http://statistics.data.gov.uk/id/statistical-geography/W92000004',
    'Scotland': 'http://statistics.data.gov.uk/id/statistical-geography/S92000003'
}

region_codes = {
    'North East': 'E12000001',
    'North West': 'E12000002',
    'Yorkshire and The Humber': 'E12000003',
    'East Midlands': 'E12000004',
    'West Midlands': 'E12000005',
    'South West': 'E12000009',
    'East': 'E12000006',  # Formally 'East of England'
    'South East': 'E12000008',
    'London': 'E12000007',
    'Unallocated - Known': 'unallocated-known',
    'Unallocated - Unknown': 'unallocated-unknown',
    'Northern Ireland': 'N92000002',
    'Wales': 'W92000004',
    'Scotland': 'S92000003'
}
df['UK Region'] = df['RegionName'].cat.rename_categories(regions)
df['UK Region Code'] = df['RegionName'].cat.rename_categories(region_codes)

df['Country'] = df['CountryId'].astype(str)

# # SITC Codes
# Need to go via strings

df['SITC Code'] = df['Sitc2Code'].astype(str)
df['SITC Code'] = df['SITC Code'].astype('category')

# Bring Value and NetMass into a single column
new_df = pd.DataFrame()
for measure in ['Value', 'NetMass']:
    temp_df = df[['Period', 'Flow Type', 'UK Region Code',
                  'UK Region', 'Country', 'SITC Code', measure]]
    temp_df.rename({measure: 'Value'}, axis=1, inplace=True)
    temp_df['Measure Type'] = measure
    new_df = pd.concat([new_df, temp_df], axis=0)
df = new_df
del temp_df, new_df

# Final formatting - measure-types
df['Measure Type'] = df['Measure Type'].astype('category')
df['Measure Type'].cat.rename_categories(
    {'Value': 'gbp-million', 'NetMass': 'net-mass'}, inplace=True)

df["Units"] = df["Measure Type"].map(
    lambda x: x.strip().replace("net-mass", "tonnes"))

# -

cubes.add_cube(scraper, df, scraper.title,
               override_containing_graph=f"http://gss-data.org.uk/graph/gss_data/trade/{info['id']}/{fetch_chunk}" if info['load']['accretiveUpload'] else None)

# Write cube
cubes.output_all()

# Change the aboutUrl in the -metadata.json so we don't get URIs within URIs.
metadata_json = open("./out/hmrc-regional-trade-statistics.csv-metadata.json", "r")
metadata = json.load(metadata_json)
metadata_json.close()

metadata["tables"][0]["tableSchema"]["aboutUrl"] = (
    metadata["tables"][0]["tableSchema"]["aboutUrl"].replace("{uk_region}", "{uk_region_code}")
)

metadata_json = open("./out/hmrc-regional-trade-statistics.csv-metadata.json", "w")
json.dump(metadata, metadata_json, indent=4)
metadata_json.close()
