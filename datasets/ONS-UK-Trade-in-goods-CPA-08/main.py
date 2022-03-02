# %%
import json
import pandas as pandas
from gssutils import *
from csvcubed.models.cube.qb.catalog import CatalogMetadata # make sure you're in the test container until it's sorted

info_json_file = 'info.json'

# %%

# get first landing page details
metadata = Scraper(seed = info_json_file)

# load data
distribution1 = metadata.distribution(latest = True)

cubes = Cubes('info.json')
info = json.load(open('info.json'))
landingPage = info['landingPage']
metadata = Scraper(seed="info.json")
distribution = metadata.distribution(latest = True)
title = distribution.title
distribution
# -

tabs = distribution.as_databaker()
tidied_sheets = []

for tab in tabs:
    if tab.name not in ['Index', 'Contact']:

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
        table = tidy_sheet.topandas()
        tidied_sheets.append(table)


# +
def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]


# -

df = pd.concat(tidied_sheets, sort=True)
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
metadata.dataset.title = "UK Trade in goods by Classification of Product by Activity, time series dataset, Quarterly and Annual"

metadata.dataset.comment = "Publication tables, UK trade in goods, CPA (08). Additional information for UK trade in goods by classification of product by activity. Current price, seasonally adjusted."

metadata.dataset.description = """
Publication tables, UK trade in goods, CPA (08). 
Additional information for UK trade in goods by classification of product by activity. 
Current price, seasonally adjusted.
This publication includes a residual line which is used to account for any residual between the seasonally adjusted aggregate of 'Total Classification of Product by Activity (CPA)' and the seasonally adjusted aggregate of 'Total Standard International Trade Classification (SITC)' that is published in the UK Trade Statistical Bulletin, Gross Domestic Product (GDP), Balance of Payments (BoP) and Pink Book releases. The seasonal adjustment residual will account for differences at the aggregate level that are introduced because of differences in CPA and SITC classifications at the level at which seasonal adjustment is applied.
"""
# -

cubes.add_cube(metadata, df, metadata.dataset.title)
cubes.output_all()
