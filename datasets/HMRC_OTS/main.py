# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.9.1
#   kernelspec:
#     display_name: Python 3.8.7 64-bit
#     metadata:
#       interpreter:
#         hash: f2b0bb78cbb17f9579fa5e62801b4f61ba0bc1633b5d43780d3380efce1f0d9c
#     name: python3
# ---

# +
import logging
import json
import pandas as pd

from gssutils import *

# +
# logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)

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
api_chunks = get_odata_api_chunks(distro)
logging.debug(f'The chunks found on api are {api_chunks}')

# Get PMD Chunks
pmd_chunks = get_pmd_chunks(distro)
logging.debug(f'The chunks found on api are {pmd_chunks}')

pd.to_datetime('/id/month/2000-01', format='/id/month/%Y-%m').strftime('%Y%m')

test = ['/id/month/2000-01', '/id/month/2000-02', '/id/month/2000-03', '/id/month/2000-05']

# Get next period to download
if len(pmd_chunks) != 0:
    fetch_chunk = min(api_chunks)
else:
    pmd_chunks = [int(pd.to_datetime(x, format='/id/month/%Y-%m').strftime('%Y%m')) for x in pmd_chunks]
    fetch_chunk = min(set(api_chunks)-set(pmd_chunks))
logging.info(f'Earliest chunk not on PMD but found on API is {fetch_chunk}')

# Fetch the chunk
df = distro.as_pandas(chunks_wanted=fetch_chunk)
df

# Determine date formatting (which helps determin the next period to download)
df['Period'] = pd.to_datetime(df['MonthId'], format="%Y%m").dt.strftime('/id/month/%Y-%m')

# Check if we've only got one chunk
df['Period'].value_counts()

# Add dataframe is in the cube
cubes.add_cube(scraper, df, scraper.title)

# + tags=["outputPrepend"]
# Write cube
cubes.output_all()
# -


