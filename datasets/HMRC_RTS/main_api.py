# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.7.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

import json
import requests
import pandas as pd
from cachecontrol import CacheControl
from cachecontrol.caches.file_cache import FileCache
from cachecontrol.heuristics import ExpiresAfter

sess = requests.session()
cached_sess = CacheControl(sess, cache=FileCache('.cache'), heuristic=ExpiresAfter(days=7))


def fetch_api_to_df(url: str) -> pd.DataFrame():
    page = cached_sess.get(url)
    contents = page.json()
    df = pd.DataFrame(contents['value'])
    print('Fetching data from {url}.'.format(url=page.url))
    while '@odata.nextLink' in contents.keys():
        print('Fetching more data from {url}.'.format(url=contents['@odata.nextLink']))
        page = cached_sess.get(contents['@odata.nextLink'])
        contents = page.json()
        df = df.append(pd.DataFrame(contents['value']))
    return df


rts = fetch_api_to_df(url='https://api.uktradeinfo.com/RTS')

# +
# This data is way too big to process through, so I'll limit it to processing only the most recent MonthId
# rts = rts.loc[rts['MonthId'] == rts['MonthId'].max()]

# +
# try:
#     rts = rts_bku.copy(deep=True)
# except NameError:
#     rts_bku = rts.copy(deep=True)
# rts
# -

# MonthId 
# Required Pandas > 1.0
# df['Period'] = pd.to_datetime(df['MonthId'], format='%Y%m').dt.strftime('/id/quarter/%Y-%q')
rts['Period'] = pd.PeriodIndex(pd.to_datetime(rts['MonthId'], format='%Y%m'), freq='Q').astype(str)
rts['Period'] = rts['Period'].apply(lambda x:'/id/quarter/{year}-{quarter}'.format(year=x[:4], quarter=x[-1:]))
rts['Period'] = rts['Period'].astype('category')
rts.head()

# FlowTypeId
# https://api.uktradeinfo.com/FlowType
FlowTypes = fetch_api_to_df(url='https://api.uktradeinfo.com/FlowType')
for column in FlowTypes.columns[1:]:
    FlowTypes[column] = FlowTypes[column].astype('category')
rts = rts.merge(FlowTypes, on='FlowTypeId').drop(labels=['@odata.type'], axis=1)
del FlowTypes
rts.head()


# GovRegionId
# https://api.uktradeinfo.com/Region
GovRegions = fetch_api_to_df(url='https://api.uktradeinfo.com/Region')
for column in GovRegions.columns[1:]:
    GovRegions[column] = GovRegions[column].astype('category')
rts = rts.merge(GovRegions, left_on='GovRegionId', right_on='RegionId').drop(labels=['RegionId'], axis=1)
del GovRegions
rts.head()

# CountryID
# https://api.uktradeinfo.com/Country
Countries = fetch_api_to_df(url='https://api.uktradeinfo.com/Country')
for column in Countries.columns[1:]:
    Countries[column] = Countries[column].astype('category')
rts = rts.merge(Countries, on='CountryId')
del Countries
rts.head()


# CommoditySitc2Id
# https://api.uktradeinfo.com/SITC
SITCs = fetch_api_to_df(url='https://api.uktradeinfo.com/SITC')
for column in SITCs.columns[1:]:
    SITCs[column] = SITCs[column].astype('category')
rts = rts.merge(SITCs, left_on='CommoditySitc2Id', right_on='CommoditySitcId').drop(labels=['CommoditySitcId'], axis=1)
rts.head()

# +
# Value

# +
# NetMass
# -

rts.head()

# +
# rts.to_excel('test_output.xlsx')
# -


