# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.8
#   kernelspec:
#     display_name: Python 3.9.12 64-bit
#     language: python
#     name: python3
# ---

# ###  Individual country data (goods) on a monthly basis to Tidy Data

# + vscode={"languageId": "python"}

import pandas as pd
import numpy as np
from gssutils import *
from databaker.framework import *



metadata = Scraper(seed='info.json')
metadata

distribution = metadata.distribution(latest=True)
distribution

tabs = distribution.as_databaker()


# + vscode={"languageId": "python"}
def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]


# + vscode={"languageId": "python"}
tidied_sheets = []
title = distribution.title

for tab in tabs:
    if tab.name == 'Notes':
        continue
    print(tab.name)
    
    period = tab.excel_ref('A4').expand(DOWN).is_not_blank()
    country = tab.excel_ref('B3').expand(RIGHT).is_not_blank()

    flow_direction = tab.name[-len('exports'):]

    observations = tab.excel_ref('B4').expand(DOWN).expand(RIGHT).is_not_blank()

    dimensions = [
        HDimConst('Flow', flow_direction),
        HDim(period, 'Period', DIRECTLY, LEFT),
        HDim(country, 'ONS Partner Geography', DIRECTLY, ABOVE)       
    ]

    cs = ConversionSegment(tab, dimensions, observations)
    tidy_sheet = cs.topandas()
    tidied_sheets.append(tidy_sheet)

# + vscode={"languageId": "python"}
df = pd.concat(tidied_sheets, sort = True).fillna('')

# + vscode={"languageId": "python"}
df = df[df['OBS'] != 0]

# + vscode={"languageId": "python"}
df.loc[df['Period'].str.len() == 7, 'Period'] = pd.to_datetime(df.loc[df['Period'].str.len() == 7, 'Period'], format='%Y%b').astype(str).map(lambda x: 'month/' + left(x,7))

# + vscode={"languageId": "python"}
df.loc[df['Period'].str.len() == 4, 'Period'] = 'year/' + df.loc[df['Period'].str.len() == 4, 'Period']

# + vscode={"languageId": "python"}
df.rename(columns= {'OBS':'Value'}, inplace=True)
df.rename(columns= {'ONS Partner Geography': 'Geography'}, inplace=True)

# + vscode={"languageId": "python"}
df.loc[df['Geography'].str.len() > 2, 'Geography'] = df['Geography'].str[:2]

# + vscode={"languageId": "python"}
df["Flow"] = df["Flow"].apply(pathify)

# + vscode={"languageId": "python"}
df = df[['Geography','Period','Flow','Value']]

# + vscode={"languageId": "python"}
df.to_csv("observations.csv", index = False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')
