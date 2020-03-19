# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.2.4
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
import pandas as pd
import requests
from pathlib import Path
from io import BytesIO
from cachecontrol import CacheControl
from cachecontrol.caches.file_cache import FileCache
from cachecontrol.heuristics import LastModified
from zipfile import ZipFile

session = CacheControl(requests.Session(),
                       cache=FileCache('.cache'),
                       heuristic=LastModified())

dataUrl = "https://www.uktradeinfo.com/Statistics/Documents/Data%20Downloads/"

with ZipFile(BytesIO(session.get(dataUrl + "SMKA12_2017archive.zip").content)) as controlZips:
    for monthZipName in controlZips.namelist():
        with ZipFile(BytesIO(controlZips.open(monthZipName).read())) as monthControlZip:
            assert len(monthControlZip.namelist()) == 1
            with monthControlZip.open(monthControlZip.namelist()[0]) as monthControl:
                table = pd.read_csv(monthControl, sep='|', encoding='latin-1')
                display(table)
        break

# +
# Non EU

colspec = [(1,9), (11,15), (17,19), (21,42), (44,52), (54,57), (59.76), ]
names = ["COMCODE", "SITC", "RECORD-TYPE", "FILE-NAME", "MONTH-ALPHA", "YEAR", "SUITE"]
with ZipFile(BytesIO(session.get(dataUrl + "SMKE19_2017archive.zip").content)) as controlZips:
    for monthZipName in controlZips.namelist():
        with ZipFile(BytesIO(controlZips.open(monthZipName).read())) as monthControlZip:
            assert len(monthControlZip.namelist()) == 1
            with monthControlZip.open(monthControlZip.namelist()[0]) as monthControl:
                table = pd.read_csv(monthControl, sep='|', encoding='latin-1')
                display(table)
            
# -


