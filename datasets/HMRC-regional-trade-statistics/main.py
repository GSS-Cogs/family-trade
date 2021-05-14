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
    'North East': 'E12000001',
    'North West': 'E12000002',
    'Yorkshire and The Humber': 'E12000003',
    'East Midlands': 'E12000004',
    'West Midlands': 'E12000005',
    'South West': 'E12000009',
    'East': 'E12000006',  # Formally 'East of England'
    'South East': 'E12000008',
    'London': 'E12000007',
    'Northern Ireland': 'N92000002',
    'Wales': 'W92000004',
    'Scotland': 'S92000003'
}
df['Location GSS'] = pd.Categorical(df['RegionName'].replace(
    region_codes), categories=region_codes.values(), ordered=False)

region_other = {
    'Unallocated - Known': 'unallocated-known',
    'Unallocated - Unknown': 'unallocated-unknown'
}
df['Location Dataset Local'] = pd.Categorical(df['RegionName'].replace(
    region_other), categories=region_other.values(), ordered=False)

df['Country'] = df['CountryId'].astype(str)

# # SITC Codes
# Need to go via strings
df['SITC Code'] = df['Sitc2Code'].astype(str).astype('category')

# The melty magic to take two values in the same row and create unique records for these values, the source column name becomes the 'variable' column, the column value stays in ends up in the 'value' column.
df = df.melt(id_vars=['Period', 'Flow Type', 'Location GSS', 'Location Dataset Local',
             'Country', 'SITC Code'], value_vars=['Value', 'NetMass'])

# Measures & Units
df.loc[df['variable'] == 'Value', 'measure_type'] = 'monetary-value'
df.loc[df['variable'] == 'Value',
       'unit_type'] = 'gbp-thousands'
df.loc[df['variable'] == 'NetMass', 'measure_type'] = 'net-mass'
df.loc[df['variable'] == 'NetMass',
       'unit_type'] = 'tonnes'
df.drop('variable', axis=1, inplace=True)
df['unit_type'] = df['unit_type'].astype('category')
df['measure_type'] = df['measure_type'].astype('category')


cubes.add_cube(scraper, df, info['id'],
               override_containing_graph=f"http://gss-data.org.uk/graph/gss_data/trade/{info['id']}/{fetch_chunk}" if info['load']['accretiveUpload'] else None)

# Write cube
cubes.output_all()

# Change the aboutUrl in the -metadata.json so we don't get URIs within URIs.
metadata_json = open(
    "./out/hmrc-regional-trade-statistics.csv-metadata.json", "r")
metadata = json.load(metadata_json)
metadata_json.close()

# metadata["tables"][0]["tableSchema"]["aboutUrl"] = (
#     metadata["tables"][0]["tableSchema"]["aboutUrl"].replace(
#         "{uk_region}", "{uk_region_code}")
# )

metadata_json = open(
    "./out/hmrc-regional-trade-statistics.csv-metadata.json", "w")
json.dump(metadata, metadata_json, indent=4)
metadata_json.close()
