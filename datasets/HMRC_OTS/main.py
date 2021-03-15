# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.10.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
import logging
import json
import pandas as pd

from gssutils import *

# +
infoFileName = 'info.json'

info    = json.load(open(infoFileName))
scraper = Scraper(seed=infoFileName)
cubes   = Cubes(infoFileName)

scraper.dataset.family = info['families']

# + tags=[]
distro = scraper.distribution(latest=True)
# -

# Get OData API Chunks
api_chunks = distro.get_odata_api_chunks()
logging.debug(f'The chunks found on api are {api_chunks}')

# Get PMD Chunks
pmd_chunks = distro.get_pmd_chunks()
logging.debug(f'The chunks found on api are {pmd_chunks}')

# Get next period to download
if len(pmd_chunks) == 0:
    fetch_chunk = min(api_chunks)
else:
    pmd_chunks = [int(pd.to_datetime(x, format='/id/month/%Y-%m').strftime('%Y%m')) for x in pmd_chunks]
    fetch_chunk = min(set(api_chunks)-set(pmd_chunks))
logging.info(f'Earliest chunk not on PMD but found on API is {fetch_chunk}')

# Download the chonky dataframe
df = distro.as_pandas(chunks_wanted=fetch_chunk)

# Drop all columns not specified
df.drop([x for x in df.columns if x not in ['MonthId','FlowTypeDescription', 'SuppressionIndex', 'CountryId', 'Cn8Code', 'PortCodeNumeric', 'Period', 'Value', 'NetMass']], axis=1, inplace=True)

# Convert columns to categorical if categorical
for col in df.columns:
    if col not in ['Value', 'NetMass', 'MonthId']:
        df[col] = df[col].astype('category')

# Period column
df['Period'] = pd.to_datetime(df['MonthId'], format="%Y%m").dt.strftime('/id/month/%Y-%m')
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
df['SuppressionIndex'].cat.rename_categories(lambda x: pathify(x), inplace=True)


# FlowTypeDescription
df['FlowTypeDescription'].cat.rename_categories(lambda x: pathify(x), inplace=True)

df.columns

# The melty magic to take two values in the same row and create unique records for these values, the source column name becomes the 'variable' column, the column value stays in ends up in the 'value' column.
df = df.melt(id_vars=['SuppressionIndex', 'CountryId', 'FlowTypeDescription', 'Cn8Code', 'PortCodeNumeric', 'Period'], value_vars=['Value', 'NetMass'])

# Units, Measures, and dictionaries, oh my!
df.loc[df['variable'] == 'Value', 'meausre-type'] = 'monetary-value'
df.loc[df['variable'] == 'Value', 'unit-type'] = 'http://gss-data.org.uk/def/concept/measurement-units/gbp'
df.loc[df['variable'] == 'NetMass', 'meausre-type'] = 'net-mass'
df.loc[df['variable'] == 'NetMass', 'unit-type'] = 'http://qudt.org/vocab/unit/KiloGM'
df.drop('variable', axis=1, inplace=True)
df['unit-type'] = df['unit-type'].astype('category')
df['meausre-type'] = df['meausre-type'].astype('category')

# Rename columns
col_names = {
    'SuppressionIndex': 'marker',
    'CountryId': 'country-id',
    'FlowTypeDescription': 'flow-type',
    'Cn8Code': 'cn8-code',
    'PortCodeNumeric': 'port-code',
    'Period': 'period'
}
df.rename(col_names, axis=1, inplace=True)

# Add dataframe is in the cube
cubes.add_cube(scraper, df, scraper.title)

# + tags=[]
# Write cube
cubes.output_all()
# -


