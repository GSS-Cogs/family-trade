# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.1
#   kernelspec:
#     display_name: Python 3.8.9 64-bit
#     name: python3
# ---

# +
import logging
import json
import pandas as pd
import sqlite3

from gssutils import *

# +
file = 'info.json'

info = json.load(open(file))
cube = Cubes(file)
scraper_cn8 = Scraper(seed=file)
scraper_sitc = Scraper(seed=file)

scraper_cn8.dataset.family = info['families']
scraper_sitc.dataset.family = info['families']


# + tags=[]
distro = scraper_cn8.distribution(latest=True)
# -

# Get API Chunks
api_chunks = distro.get_odata_api_chunks()
logging.debug(f'The chunks found on api are {pmd_chunks}')
# Replace line below with line above once gss-utils issue get_odata_api_chunks() query is malformatted #216 is fixed
# api_chunks = [x["MonthId"] for x in distro._session.get(
#     distro.uri, params={'$apply': 'groupby((MonthId))'}).json()["value"]]

# Get PMD Chunks
pmd_chunks = distro.get_pmd_chunks()
logging.debug(f'The chunks found on pmd are {pmd_chunks}')

# Get next period to download
if len(pmd_chunks) == 0:
    fetch_chunk = min(api_chunks)
else:
    pmd_chunks = [int(pd.to_datetime(
        x, format='/id/month/%Y-%m').strftime('%Y%m')) for x in pmd_chunks]
    fetch_chunk = max(set(api_chunks)-set(pmd_chunks))
logging.info(f'Earliest chunk not on PMD but found on API is {fetch_chunk}')

# Download the chonky dataframe
df = distro.as_pandas(chunks_wanted=fetch_chunk)

# Sampling to downsize work
# df = df.sample(n=5000)

# Drop all columns not specified
df.drop([x for x in df.columns if x not in ['MonthId', 'FlowTypeDescription', 'SuppressionIndex',
        'CountryId', 'Cn8Code', 'SitcCode', 'PortCodeNumeric', 'Period', 'Value', 'NetMass']], axis=1, inplace=True)

# Convert columns to categorical if categorical
for col in df.columns:
    if col not in ['Value', 'NetMass', 'MonthId']:
        df[col] = df[col].astype('category')

# Period column
df['Period'] = pd.to_datetime(
    df['MonthId'], format="%Y%m").dt.strftime('/id/month/%Y-%m')
df.drop('MonthId', inplace=True, axis=1)
df['Period'] = df['Period'].astype('category')

# SuppressionIndex is a datamaker
# We use an empty string for suppression index of 0 because a np.nan value isn't acceptable in categorical data
suppression = {
    0: '',
    1: 'Complete suppression, where no information is published.',
    2: 'Suppression of countries and ports, where only the overall total value (£ sterling) and quantity (kg) are published.',
    3: 'Suppression of countries, ports and total trade quantity, where only the overall total value is published.',
    4: 'Suppression of quantity for countries and ports, where the overall total value and quantity are published, but where a country and port breakdown is only available for value.',
    5: 'Suppression of quantity for countries, ports and total trade, where no information on quantity is published, but a full breakdown of value is available.'
}
df['SuppressionIndex'].cat.rename_categories(suppression, inplace=True)
df['SuppressionIndex'].cat.rename_categories(
    lambda x: pathify(x), inplace=True)


# FlowTypeDescription
df['FlowTypeDescription'].cat.rename_categories(
    lambda x: pathify(x), inplace=True)

# SitcCode changes
df['SitcCode'].cat.rename_categories(
    lambda x: x.replace('-', '+'), inplace=True)
# CN8 changes
df['Cn8Code'].cat.rename_categories(
    lambda x: x.replace('-', '+'), inplace=True)


# The melty magic to take two values in the same row and create unique records for these values, the source column name becomes the 'variable' column, the column value stays in ends up in the 'value' column.
df = df.melt(id_vars=['SuppressionIndex', 'CountryId', 'FlowTypeDescription',
             'SitcCode', 'Cn8Code', 'PortCodeNumeric', 'Period'], value_vars=['Value', 'NetMass'])

# Units, Measures, and dictionaries, oh my!
df.loc[df['variable'] == 'Value', 'measure_type'] = 'monetary-value'
df.loc[df['variable'] == 'Value',
       'unit_type'] = 'http://gss-data.org.uk/def/concept/measurement-units/gbp'
df.loc[df['variable'] == 'NetMass', 'measure_type'] = 'net-mass'
df.loc[df['variable'] == 'NetMass',
       'unit_type'] = 'http://qudt.org/vocab/unit/KiloGM'
df.drop('variable', axis=1, inplace=True)
df['unit_type'] = df['unit_type'].astype('category')
df['measure_type'] = df['measure_type'].astype('category')

# Rename columns
col_names = {
    'SuppressionIndex': 'marker',
    'CountryId': 'country_id',
    'FlowTypeDescription': 'flow_type',
    'Cn8Code': 'cn8_id',
    'SitcCode': 'sitc_id',
    'PortCodeNumeric': 'port',
    'Period': 'period'
}
df.rename(col_names, axis=1, inplace=True)

# +
# Defaults, get your categorical value series defaults
def default(series=pd.Series, value=str) -> pd.DataFrame():
    if value in series.cat.categories:
        return series.fillna(value)
    else:
        return series.cat.add_categories(value).fillna(value)


df['country_id'] = default(series=df['country_id'], value='unknown')
df['port'] = default(series=df['port'], value='499')
df['sitc_id'] = default(series=df['sitc_id'], value='unknown')
df['cn8_id'] = default(series=df['cn8_id'], value='unknown')
df['marker'] = default(series=df['marker'], value='')
# -

# Null values are inadmissable in the the qb spec, so we'll drop them
df = df.dropna(subset=['value'])

# Create a SQLite3 database to be able to do the aggregation.
con = sqlite3.connect('tempdb.db')
df.to_sql('data', con, if_exists='replace')
del df

# cn8 cube work - aggregate on cn8 and discard sitc values, pass the resulting dataframe straight into the cube creation
qry = """
SELECT marker, country_id, flow_type, cn8_id, port, period, measure_type, unit_type, sum(value) as value
from data
group by marker, country_id, flow_type, cn8_id, port, period, measure_type, unit_type
"""
scraper_cn8.dataset.title = "HMRC Overseas Trade Statistics - Combined Nomenclature 8"
scraper_cn8.set_dataset_id(f"{info['id']}-cn8")

cube.add_cube(scraper_cn8, pd.read_sql_query(qry, con), f"{info['id']}-cn8",
              override_containing_graph=f"http://gss-data.org.uk/graph/gss_data/trade/{info['id']}-cn8/{fetch_chunk}"
              if info['load']['accretiveUpload'] else None)

# Need to output CN8 dataset with appropriate title before the SITC dataset tries to overwrite the dataset's
# label/title.

# sitc cube work - aggregate on sitc and discard sn8 values
qry = """
SELECT marker, country_id, flow_type, sitc_id, port, period, measure_type, unit_type, sum(value) as value
from data
group by marker, country_id, flow_type, sitc_id, port, period, measure_type, unit_type
"""
scraper_sitc.dataset.title = "HMRC Overseas Trade Statistics - SITCv4"
scraper_sitc.set_dataset_id(f"{info['id']}-sitc")
cube.add_cube(scraper_sitc, pd.read_sql_query(qry, con), f"{info['id']}-sitc",
              override_containing_graph=f"http://gss-data.org.uk/graph/gss_data/trade/{info['id']}-sitc/{fetch_chunk}"
              if info['load']['accretiveUpload'] else None)

# Output it!
cube.output_all()
