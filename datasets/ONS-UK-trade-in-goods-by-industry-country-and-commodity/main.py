# %%

# UK trade in goods by industry, country and commodity, exports and imports


import pandas as pd
import json
from gssutils import *
from csvcubed.models.cube.qb.catalog import CatalogMetadata # make sure you're in the test container

info_json_file = 'info.json'

# %% 
# get first landing page details
metadata = Scraper(seed = info_json_file)
# display(metadata) #  to see exactly the data we are loading 
# %%
# load export data
distribution1 = metadata.distribution(latest = True)
# display(distribution1)
# %%
# there are two separate landing pages as we're combining two datasets so need to overwrite the landing page in the info.json (exports) with the other (imports) landing page.
with open(info_json_file, "r") as jsonFile:
    data = json.load(jsonFile)
# change landing page 
data["landingPage"] = "https://www.ons.gov.uk/economy/nationalaccounts/balanceofpayments/datasets/uktradeingoodsbyindustrycountryandcommodityimports"
with open(info_json_file, "w") as jsonFile:
    json.dump(data, jsonFile, indent=2) # put it back in the info json file
del data
# %%
#get the second landing page details
metadata = Scraper(seed = info_json_file)
# display(metadata)
# %%
# load import data
distribution2 = metadata.distribution(latest = True)
# display(distribution2)

# %%
# load tabs from two different distributions/excel workbooks and combine
tabs1 = distribution1.as_databaker()
tabs2 = distribution2.as_databaker()
tabs = tabs1 + tabs2

# %%
# keep tabs we're interested in
tabs = [x for x in tabs if x.name in ('tig_ind_ex final', 'tig_ind_im') ]

# %%
tidied_sheets = []

for tab in tabs:

    # [Dimensions]
    
    if tab.name == 'tig_ind_ex final':
        flow = 'exports'
    elif tab.name == 'tig_ind_im':
        flow = 'imports' 
 
    country = tab.filter('Country').fill(DOWN).is_not_blank()
    industry = tab.filter('Industry').fill(DOWN).is_not_blank()
    commodity = tab.filter('Commodity').fill(DOWN).is_not_blank()
    year = tab.excel_ref('E1').expand(RIGHT).is_not_blank()
    

    # [Observations]

    observations = year.fill(DOWN).is_not_blank() 

    # [Mapping obs to dimensions]

    dimensions = [
                HDimConst('Flow', flow),
                HDim(year,'Period', DIRECTLY,ABOVE),
                HDim(country,'ONS Partner Geography', DIRECTLY,LEFT),
                HDim(commodity,'Commodity', DIRECTLY,LEFT),
                HDim(industry,'Industry', DIRECTLY,LEFT)       
                ]
    cs = ConversionSegment(tab, dimensions, observations)
    tidy_sheet = cs.topandas()
    tidied_sheets.append(tidy_sheet)
# %%

# set float values to 1 sf
pd.set_option('display.float_format', lambda x: '%.1f' % x) 

#craete dataframe from tab data and convert NaN to blanks
df = pd.concat(tidied_sheets, sort = True).fillna('') 

descr = """
Experimental dataset providing a breakdown of UK trade in goods by industry, country and commodity on a balance of payments basis. Data are subject to disclosure control, which means some data have been suppressed to protect confidentiality of individual traders.

Users should note the following:
Industry data has been produced using Standard Industrial Classification 2007 (SIC07).

Commodity data has been produced using Standard International Trade Classification (SITC).

Due to risks around disclosing data related to individual firms we are only able to provide data for certain combinations of the dimensions included, i.e. country, commodity and industry. This dataset therefore provides the following two combinations:
    Industry (SIC07 2 digit), by Commodity (SITC 2 digit), by geographic region (worldwide, EU and non-EU)
    Industry (SIC07 2 digit), by Commodity total, by individual country

Some data has been suppressed to protect confidentiality so that individual traders cannot be identified.

Methodology improvements
Within this latest experimental release improvements have been made to the methodology that has resulted in some revisions when compared to our previous release in April 2019.
These changes include; improvements to the data linking methodology and a targeted allocation of some of the Balance of Payments (BoP) adjustments to industry.
The data linking improvements were required due to subtleties in both the HMRC data and IDBR not previously recognised within Trade.

While we are happy with the quality of the data in this experimental release we have noticed some data movements, specifically in 2018.
We will continue to review the movements seen in both the HMRC microdata and the linking methodology and, where appropriate, will further develop the methodology for Trade in Goods by Industry for future releases. 

Data
All data is in £ million, current prices.

Rounding
Some of the totals within this release (e.g. EU, Non EU and worldwide) may not exactly match data published via other trade releases due to small rounding differences.

Trade Asymmetries
These data are our best estimate of these bilateral UK trade flows. Users should note that alternative estimates are available, in some cases, via the statistical agencies for bilateral countries or through central databases such as UN Comtrade.
UN Comtrade.
"""
# %%
# update metadata's title as now we've combined the datasets
metadata.dataset.title = 'UK trade in goods by industry, country and commodity - Imports & Exports'
metadata.dataset.description = descr

# [Clean up]
# %%

# remove rows with 0 values in observations. there are blank obs as well but these are dealt with later
# i do get a warning somewhere in this section saying "trying to be set on a copy of a slice from a DataFrame"
df = df[df['OBS'] != 0] 
# replace DATAMARKER values
df.loc[df['DATAMARKER'].astype(str) == '..', 'DATAMARKER'] = 'suppressed' 
# this will replace the blank observations from supressed rows with 0
df['OBS'].loc[(df['OBS'] == '')] = 0 
df['OBS'] = df['OBS'].astype(int) 

# %%
#reformat period column
df['Period'] = 'year/' + df['Period'].str[0:4]
df['Commodity'] = df['Commodity'].str[:2] # codelist has 3 char long codes included but in this datset there are only categories with 1 to 2 char long in their code
df['Commodity'] = df['Commodity'].str.strip() # codes included in this datset are only 1 to 2 characters long
df['ONS Partner Geography'] = df['ONS Partner Geography'].str[:2]
df['Industry'] = df['Industry'].str[:2] 
df['Industry'] = df['Industry'].str.strip() # strip incase 'U unknown industry' appears

#%%
#rename columns
df.rename(columns={'OBS': 'Value', 'DATAMARKER' : 'Marker'}, inplace=True)

# add constant values since they're defined in info.json
df["Unit"] = "GBP Million"
df['Measure Type'] = 'Current Prices'

# %%
#reorder columns
df = df.replace({'ONS Partner Geography' : {'NA' : 'NAM',}})
df = df[['Period','ONS Partner Geography','Industry','Flow','Commodity', 'Value','Measure Type', 'Unit', 'Marker']]



#%%
df.to_csv('observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json') 

# %%