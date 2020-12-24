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
import pandas as pd
from gssutils import *

# # Motion due to no current API-based scraper

import requests
from cachecontrol import CacheControl
from cachecontrol.caches.file_cache import FileCache
from cachecontrol.heuristics import ExpiresAfter

# Object manages the session
sess = requests.session()
cached_sess = CacheControl(sess, cache=FileCache('.cache'), heuristic=ExpiresAfter(days=7))


# Define child of Scraper which rips from API end point and spits out an dataframe with as_pandas()
class ApiScraper(Scraper):
    """
    Inherits the Scraper class and replace the as_pandas() to get the data from the api endpoint, heavy caching requried
    """

    def as_pandas(self):
        url = self.distributions[0].downloadURL
        page = cached_sess.get(url)
        contents = page.json()
        df = pd.DataFrame(contents['value'])
        # print('Fetching data from {url}.'.format(url=page.url))
        while '@odata.nextLink' in contents.keys():
            # print('Fetching more data from {url}.'.format(url=contents['@odata.nextLink']))
            page = cached_sess.get(contents['@odata.nextLink'])
            contents = page.json()
            df = df.append(pd.DataFrame(contents['value']))
        return df


# For the remainder of the augmentation process, another method
def fetch_api_to_df(url: str) -> pd.DataFrame():
    page = cached_sess.get(url)
    contents = page.json()
    df = pd.DataFrame(contents['value'])
    # print('Fetching data from {url}.'.format(url=page.url))
    while '@odata.nextLink' in contents.keys():
        # print('Fetching more data from {url}.'.format(url=contents['@odata.nextLink']))
        page = cached_sess.get(contents['@odata.nextLink'])
        contents = page.json()
        df = df.append(pd.DataFrame(contents['value']))
    return df



# # And we begin

# +
infoFileName = 'info.json'

info    = json.load(open(infoFileName))
scraper = ApiScraper(seed=infoFileName)
cubes   = Cubes(infoFileName)

scraper.dataset.family = info['families']
# -

rts = scraper.as_pandas()

# MonthId 
# Required Pandas > 1.0
# df['Period'] = pd.to_datetime(df['MonthId'], format='%Y%m').dt.to_period('Q').dt.strftime('/id/quarter/%Y-%q')
rts['Period'] = pd.PeriodIndex(pd.to_datetime(rts['MonthId'], format='%Y%m'), freq='Q').astype(str)
rts['Period'] = rts['Period'].apply(lambda x:'/id/quarter/{year}-{quarter}'.format(year=x[:4], quarter=x[-1:]))
rts['Period'] = rts['Period'].astype('category')

# FlowTypeId
# https://api.uktradeinfo.com/FlowType (Strip all strings)
FlowTypes = fetch_api_to_df(url=info['apiEndpoints']['FlowTypeId']).applymap(lambda x: x.strip() if isinstance(x, str) else x)
for column in FlowTypes.columns[1:]:
    FlowTypes[column] = FlowTypes[column].astype('category')
rts = rts.merge(FlowTypes, on='FlowTypeId').drop(labels=['@odata.type'], axis=1)
del FlowTypes


# GovRegionId
# https://api.uktradeinfo.com/Region
GovRegions = fetch_api_to_df(url=info['apiEndpoints']['GovRegionId'])
for column in GovRegions.columns[1:]:
    GovRegions[column] = GovRegions[column].astype('category').str.strip()
rts = rts.merge(GovRegions, left_on='GovRegionId', right_on='RegionId').drop(labels=['RegionId'], axis=1)
del GovRegions

# CountryID
# https://api.uktradeinfo.com/Country
Countries = fetch_api_to_df(url=info['apiEndpoints']['CountryId'])
for column in Countries.columns[1:]:
    Countries[column] = Countries[column].astype('category')
rts = rts.merge(Countries, on='CountryId')
del Countries


# CommoditySitc2Id
# https://api.uktradeinfo.com/SITC
SITCs = fetch_api_to_df(url=info['apiEndpoints']['CommoditySitc2Id'])
for column in SITCs.columns[1:]:
    SITCs[column] = SITCs[column].astype('category')
rts = rts.merge(SITCs, left_on='CommoditySitc2Id', right_on='CommoditySitcId').drop(labels=['CommoditySitcId'], axis=1)


# Add dataframe is in the cube
cubes.add_cube(scraper, rts, info['title'])

# Write cube
cubes.output_all()
