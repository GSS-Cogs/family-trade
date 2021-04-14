# -*- coding: utf-8 -*-
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

# ###  Individual country data (goods) on a monthly basis to Tidy Data

# +

import pandas as pd
import numpy as np
from gssutils import *
from databaker.framework import *

cubes = Cubes("info.json")

scraper = Scraper(seed='info.json')
scraper

distribution = scraper.distribution(latest=True)
distribution

tabs = distribution.as_databaker()


# +

# +
def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]


# +
trace = TransformTrace()
title = distribution.title
columns = ['Geography','Period','Flow','Measure Type','Value','Unit']

for tab in tabs:
    if tab.name == 'Notes':
        continue
    print(tab.name)
    
    trace.start(title, tab, columns, distribution.downloadURL)
    period = tab.excel_ref('A4').expand(DOWN).is_not_blank()
    country = tab.excel_ref('B3').expand(RIGHT).is_not_blank()

    flow_direction = tab.name[-len('exports'):]

    observations = tab.excel_ref('B4').expand(DOWN).expand(RIGHT).is_not_blank()

    dimensions = [
        HDimConst('Measure Type', 'GBP Total'),
        HDimConst('Unit', '£ Million'),
        HDimConst('Flow', flow_direction),
        HDim(period, 'Period', DIRECTLY, LEFT),
        HDim(country, 'ONS Partner Geography', DIRECTLY, ABOVE)       
    ]

    cs = ConversionSegment(tab, dimensions, observations)
    tidy_sheet = cs.topandas()
    trace.store('combined_dataframe', tidy_sheet)
# -

df = trace.combine_and_trace(title, "combined_dataframe")

df = df[df['OBS'] != 0]

df.loc[df['Period'].str.len() == 7, 'Period'] = pd.to_datetime(df.loc[df['Period'].str.len() == 7, 'Period'], format='%Y%b').astype(str).map(lambda x: 'month/' + left(x,7))

df.loc[df['Period'].str.len() == 4, 'Period'] = 'year/' + df.loc[df['Period'].str.len() == 4, 'Period']

df.rename(columns= {'OBS':'Value'}, inplace=True)
df.rename(columns= {'ONS Partner Geography': 'Geography'}, inplace=True)

df.loc[df['Geography'].str.len() > 2, 'Geography'] = df['Geography'].str[:2]

df = df[['Geography','Period','Flow','Value']]
df['Flow'] = df['Flow'].map(lambda x: pathify(x))

cubes.add_cube(scraper, df, title)
cubes.output_all()

trace.render("spec_v1.html")

# +

# --
