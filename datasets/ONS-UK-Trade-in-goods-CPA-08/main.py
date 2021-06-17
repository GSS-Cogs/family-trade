# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.4.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# UK trade in goods, CPA (08)

import json
import pandas as pd
from gssutils import *

cubes = Cubes('info.json')

pd.options.mode.chained_assignment = None 
pd.set_option('display.float_format', lambda x: '%.0f' % x)


# +
def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]


# -

scraper = Scraper(seed="info.json")
scraper

distribution = scraper.distribution(latest=True)
distribution

tabs = distribution.as_databaker()

# +
trace = TransformTrace()
title = distribution.title

scraper.dataset.title = 'UK trade in goods, CPA(08)'
columns = ['Period', 'Flow Direction', 'Product', 'CDID', 'Unit', 'Value']
for tab in tabs:
    if tab.name not in ['Index', 'Contact']:
        print(tab.name)
        trace.start(title, tab, columns, distribution.downloadURL)
        
        flow_direction = tab.name.split(' ', 1)[1]
        
        period = tab.excel_ref("C4").expand(RIGHT).is_not_blank()
        product = tab.excel_ref("A5").expand(DOWN).is_not_blank() 
        cdid = tab.excel_ref('B5').expand(DOWN)
        observations = tab.excel_ref('C5').expand(DOWN).expand(RIGHT).is_not_blank() 

        dimensions = [
            HDim(period, 'Period', DIRECTLY, ABOVE),
            HDim(product, 'Product', DIRECTLY, LEFT),
            HDim(cdid, 'CDID', DIRECTLY, LEFT),
            HDimConst('Flow Direction', flow_direction)
            ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)   
        trace.store("combined_dataframe", tidy_sheet.topandas())
# -

df = trace.combine_and_trace(title, "combined_dataframe")

# +
# df = df[df['CDID'] != ' '] 
# -

df = df[df['OBS'] != 0]

df.rename(columns={'OBS' : 'Value'}, inplace=True)
df['Value'] = df['Value'].astype(int)
df['Period'] = df['Period'].map(lambda x: 'year/' + left(x,4) if 'Q' not in x else 'quarter/' + left(x,4) + '-' + right(x,2))
df['Product'] = df['Product'].map(lambda x: x.split(' ', 1)[0])

df['CDID'] = df['CDID'].map(lambda x: x if len(x.strip()) > 0 else 'not-applicable')

df = df[['Period', 'Flow Direction', 'Product', 'CDID', 'Value']]
df['Flow Direction'] = df['Flow Direction'].apply(pathify)
df

# +
scraper.dataset.title = "UK Trade in goods by Classification of Product by Activity, time series dataset, Quarterly and Annual"

scraper.dataset.comment = "Publication tables, UK trade in goods, CPA (08). Additional information for UK trade in goods by classification of product by activity. Current price, seasonally adjusted."

scraper.dataset.description = """
Publication tables, UK trade in goods, CPA (08). 
Additional information for UK trade in goods by classification of product by activity. 
Current price, seasonally adjusted.
This publication includes a residual line which is used to account for any residual between the seasonally adjusted aggregate of 'Total Classification of Product by Activity (CPA)' and the seasonally adjusted aggregate of 'Total Standard International Trade Classification (SITC)' that is published in the UK Trade Statistical Bulletin, Gross Domestic Product (GDP), Balance of Payments (BoP) and Pink Book releases. The seasonal adjustment residual will account for differences at the aggregate level that are introduced because of differences in CPA and SITC classifications at the level at which seasonal adjustment is applied.
"""
# -

cubes.add_cube(scraper, df, title)
cubes.output_all()

trace.render("spec_v1.html")


