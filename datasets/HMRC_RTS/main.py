# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.9.1
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

# Quarter conversion g(x) = x//3+1, so g(1)=1, g(4)=2, g(7)=3, g(10)=4
df['Period'] = [f"/id/quarter/{str(x)[:4]}-{str(int(str(x)[-2])//3+1)}" for x in df['MonthId']]

cubes.add_cube(scraper, df, scraper.title)

# Write cube
cubes.output_all()


