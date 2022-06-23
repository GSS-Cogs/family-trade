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

# UK trade in goods, CPA (08)

import pandas as pandas
from gssutils import *

metadata = Scraper(seed="info.json")

distribution = metadata.distribution(latest = True)

title = distribution.title

tabs = distribution.as_databaker()

tidied_sheets = []
for tab in tabs:
    if tab.name not in ['Table of contents', 'Cover sheet', 'Notes']:

        flow_direction = tab.name.split(' ', 1)[1]
        period = tab.excel_ref("C4").expand(RIGHT).is_not_blank().is_not_whitespace()
        product = tab.excel_ref("A5").expand(DOWN).is_not_blank().is_not_whitespace()
        cdid = tab.excel_ref('B5').expand(DOWN)
        observations = tab.excel_ref('C5').expand(DOWN).expand(RIGHT).is_not_blank().is_not_whitespace() 

        dimensions = [
            HDim(period, 'Period', DIRECTLY, ABOVE),
            HDim(product, 'Product', DIRECTLY, LEFT),
            HDim(cdid, 'CDID', DIRECTLY, LEFT),
            HDimConst('Flow Direction', flow_direction)
            ]
        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        table = tidy_sheet.topandas()
        tidied_sheets.append(table)


# +
def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]


# -

df = pd.concat(tidied_sheets, sort=True)

#Post Processing 
df = df[df['OBS'] != 0]
df.rename(columns={'OBS' : 'Value'}, inplace=True)
df['Value'] = df['Value'].astype(int)
df['Period'] = df['Period'].map(lambda x: 'year/' + left(x,4) if 'Q' not in x else 'quarter/' + left(x,4) + '-' + right(x,2))
df['Product'] = df['Product'].map(lambda x: x.split(' ', 1)[1])
df['Flow Direction'] = df['Flow Direction'].apply(pathify)
df['Flow Direction'] = df['Flow Direction'].str.rstrip("-annual")
df['Flow Direction'] = df['Flow Direction'].str.rstrip("-quarter")
df['CDID'] = df['CDID'].map(lambda x: x if len(x.strip()) > 0 else 'not-applicable')

df = df[['Period', 'Flow Direction', 'Product', 'CDID', 'Value']]

# +
metadata.dataset.title = "UK Trade in goods by Classification of Product by Activity, time series dataset, Quarterly and Annual"

metadata.dataset.comment = "Publication tables, UK trade in goods, CPA (08). Additional information for UK trade in goods by classification of product by activity. Current price, seasonally adjusted."
# -

add_to_des = """
Publication tables, UK trade in goods, CPA (08). 
UK trade in goods by classification of product by activity, time series dataset, quarterly and annual up to and including 2022 Q1
Additional informtion for the value of UK imports and exports of goods grouped by product. Goods are attributed to the activity of which they are the principal products
Unit pounds million, current price, seasonally adjusted.
This publication includes a residual line which is used to account for any residual between the seasonally adjusted aggregate of 'Total Classification of Product by Activity (CPA)' and the seasonally adjusted aggregate of 'Total Standard International Trade Classification (SITC)' that is published in the UK Trade Statistical Bulletin, Gross Domestic Product (GDP), Balance of Payments (BoP) and Pink Book releases. The seasonal adjustment residual will account for differences at the aggregate level that are introduced because of differences in CPA and SITC classifications at the level at which seasonal adjustment is applied.
"""
metadata.dataset.description = metadata.dataset.description + add_to_des

df.to_csv('observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')
