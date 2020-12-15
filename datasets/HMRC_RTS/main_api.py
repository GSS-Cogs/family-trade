# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import json
import requests
import pandas as pd
from cachecontrol import CacheControl
from cachecontrol.caches.file_cache import FileCache
from cachecontrol.heuristics import ExpiresAfter


# %%
sess = requests.session()
cached_sess = CacheControl(sess, cache=FileCache('.cache'), heuristic=ExpiresAfter(days=7))


# %%
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


# %%
rts = fetch_api_to_df(url='https://api.uktradeinfo.com/RTS')


# %%
# This data is way too big to process through, so I'll limit it to processing only the most recent MonthId
rts = rts.loc[rts['MonthId'] == rts['MonthId'].max()]


# %%
rts


# %%
# try:
#     rts = rts_bku.copy(deep=True)
# except NameError:
#     rts_bku = rts.copy(deep=True)
# rts


# %%
# MonthId 
# Required Pandas > 1.0
# df['Period'] = pd.to_datetime(df['MonthId'], format='%Y%m').dt.strftime('/id/quarter/%Y-%q')
rts['Period'] = pd.PeriodIndex(pd.to_datetime(rts['MonthId'], format='%Y%m'), freq='Q').astype(str)
rts['Period'] = rts['Period'].apply(lambda x:'/id/quarter/{year}-{quarter}'.format(year=x[:4], quarter=x[-1:]))
rts.head()


# %%
# FlowTypeId
# https://api.uktradeinfo.com/FlowType
FlowTypes = fetch_api_to_df(url='https://api.uktradeinfo.com/FlowType')
rts = rts.merge(FlowTypes, on='FlowTypeId').drop(labels=['@odata.type'], axis=1)
del FlowTypes
rts.head()


# %%
# GovRegionId
# https://api.uktradeinfo.com/Region
GovRegions = fetch_api_to_df(url='https://api.uktradeinfo.com/Region')
rts = rts.merge(GovRegions, left_on='GovRegionId', right_on='RegionId').drop(labels=['RegionId'], axis=1)
del GovRegions
rts.head()


# %%
# CountryID
# https://api.uktradeinfo.com/Country
Countries = fetch_api_to_df(url='https://api.uktradeinfo.com/Country')
rts = rts.merge(Countries, on='CountryId')
del Countries
rts.head()


# %%
# CommoditySitc2Id
# https://api.uktradeinfo.com/SITC
SITCs = fetch_api_to_df(url='https://api.uktradeinfo.com/SITC')
rts = rts.merge(SITCs, left_on='CommoditySitc2Id', right_on='CommoditySitcId').drop(labels=['CommoditySitcId'], axis=1)
rts.head()


# %%
# Value


# %%
# NetMass


