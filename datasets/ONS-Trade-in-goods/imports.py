# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.6.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

import pandas as pd
from gssutils import *
import json
from gssutils.metadata import *

# +
import datetime

cubes = Cubes("info.json")
title = "Trade in goods: country-by-commodity imports"
# -

with open ('info.json') as file:
    info = json.load(file)

landingPage = info['landingPage'][1]
landingPage

scraper = Scraper(landingPage)
scraper.dataset.family = info['families']
scraper

from zipfile import ZipFile
from io import BytesIO

distribution = scraper.distribution(mediaType=lambda x: 'zip' in x, latest=True)
distribution

with ZipFile(BytesIO(scraper.session.get(distribution.downloadURL).content)) as zip:
    assert(len(zip.namelist()) == 1)
    with zip.open(zip.namelist()[0]) as excelFile:
        buffered_fobj = BytesIO(excelFile.read())
        data = pd.read_excel(buffered_fobj,
                             sheet_name=1, dtype={
                                 'COMMODITY': 'category',
                                 'COUNTRY': 'category',
                                 'DIRECTION': 'category'
                             }, na_values=['','N/A'], keep_default_na=False)
data

pd.set_option('display.float_format', lambda x: '%.0f' % x)

# +
table = data.drop(columns='DIRECTION')
table.rename(columns={
    'COMMODITY': 'CORD SITC',
    'COUNTRY': 'ONS Partner Geography'}, inplace=True)
table = pd.melt(table, id_vars=['CORD SITC','ONS Partner Geography'], var_name='Period', value_name='Value')

table['Period'] = table['Period'].astype(str)
table.dropna(subset=['Value'], inplace=True)
table['Value'] = table['Value'].astype(int)
table
# -

table['CORD SITC'].cat.categories = table['CORD SITC'].cat.categories.map(lambda x: x.split(' ')[0])
table['ONS Partner Geography'].cat.categories = table['ONS Partner Geography'].cat.categories.map(lambda x: x[:2])

table["Period"] = pd.to_datetime(table['Period'], format='%Y%b')

table["Period"] = 'quarter/' + pd.PeriodIndex(table['Period'], freq='Q').astype(str).str.replace('Q', '-Q')

table['Seasonal Adjustment'] = pd.Series('NSA', index=table.index, dtype='category')
table['Measure Type'] = pd.Series('gbp million', index=table.index, dtype='category')
table['Unit'] = pd.Series('gbp', index=table.index, dtype='category')
table['Flow'] = pd.Series('imports', index=table.index, dtype='category')

table = table[['ONS Partner Geography', 'Period','Flow','CORD SITC', 'Seasonal Adjustment', 'Measure Type','Value','Unit' ]]
table

table.rename(columns={'Flow':'Flow Directions'}, inplace=True)

# flow has been changed to Flow Direction to differentiate from Migration Flow dimension
