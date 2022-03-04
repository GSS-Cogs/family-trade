# %%
import json
import pandas as pandas
from gssutils import *
from csvcubed.models.cube.qb.catalog import CatalogMetadata # make sure you're in the test container until it's sorted

# to ignore potential chained_assignment warning 
pd.options.mode.chained_assignment = None 

# round float values to 1 decimal
pd.set_option('display.float_format', lambda x: '%.0f' % x)

info_json_file = 'info.json'

# %%

# get first landing page details
metadata = Scraper(seed = info_json_file)

# load data
distribution = metadata.distribution(latest = True)
# %%

tabs = distribution.as_databaker()
tidied_sheets = [] 
# %%

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


# %%
# functions to trim x number of characters from a string
def left(s: str, amount: int) -> str:
    return s[:amount]

def right(s: str, amount: int) -> str:
    return s[-amount:]
# %%

#create dataframe from tab data and convert NaN to blanks
df = pd.concat(tidied_sheets, sort=True).fillna('')
# %%

# remove rows with 0 values in observations. there are blank obs as well but these are dealt with later
df = df[df['OBS'] != 0]
# %%

# reformat columns
df['OBS'] = df['OBS'].astype(int)
df['Period'] = df['Period'].map(lambda x: 'year/' + left(x,4) if 'Q' not in x else 'quarter/' + left(x,4) + '-' + right(x,2)) # column includes yearly and quartely periods
df['Product'] = df['Product'].map(lambda x: x.split(' ', 1)[0])
df['CDID'] = df['CDID'].map(lambda x: x if len(x.strip()) > 0 else 'not-applicable')
# %%

# rename
df.rename(columns={'OBS' : 'Value'}, inplace=True)

# reorder
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


#%%
df.to_csv('observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json') 

# %%
