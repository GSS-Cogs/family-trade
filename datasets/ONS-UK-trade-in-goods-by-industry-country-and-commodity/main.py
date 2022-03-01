# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.1.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# UK trade in goods by industry, country and commodity, exports and imports

import pandas as pd
import json
from gssutils import *

pd.options.mode.chained_assignment = None 

cubes = Cubes("info.json")

# +
info = json.load(open('info.json'))

landingPage = info['landingPage']
landingPage

# +
scraper1 = Scraper(landingPage[0])
scraper2 = Scraper(landingPage[1])

scraper1.dataset.family = info['families']
scraper1
# -

scraper2

distribution1 = scraper1.distribution(latest=True)
distribution2 = scraper2.distribution(latest=True)
distribution1

distribution2

tabs1 = distribution1.as_databaker()
tabs2 = distribution2.as_databaker()
tabs = tabs1 + tabs2

title1 = distribution1.title
title2 = distribution2.title

# +
trace = TransformTrace()
title = distribution1.title + ' and imports' 
columns = ['ONS Partner Geography', 'Period','Flow','CORD SITC', 'SIC 2007', 'Measure Type','Value','Unit', 'Marker']

for tab in tabs:
    if tab.name not in ['tig_ind_ex', 'tig_ind_im']:
        continue
    
    trace.start(title1, tab, columns, distribution1.downloadURL)
#     trace.start(title2, tab, columns, distribution2.downloadURL)
    
    if tab.name == 'tig_ind_ex':
        flow = 'exports'
    elif tab.name == 'tig_ind_im':
        flow = 'imports' 
 
    country = tab.filter('Country').fill(DOWN).is_not_blank()
    industry = tab.filter('Industry').fill(DOWN).is_not_blank()
    commodity = tab.filter('Commodity').fill(DOWN).is_not_blank()
    year = tab.excel_ref('E1').expand(RIGHT).is_not_blank()

    observations = year.fill(DOWN).is_not_blank()

    dimensions = [
                HDimConst('Measure Type', 'GBP Total'),
                HDimConst('Unit', 'gbp-million'),
                HDimConst('Flow', flow),

                HDim(year,'Period', DIRECTLY,ABOVE),
                HDim(country,'ONS Partner Geography', DIRECTLY,LEFT),
                HDim(commodity,'CORD SITC', DIRECTLY,LEFT),
                HDim(industry,'SIC 2007', DIRECTLY,LEFT)       
                ]
    cs = ConversionSegment(tab, dimensions, observations)
    tidy_sheet = cs.topandas()
    trace.store("combined_dataframe", tidy_sheet) 
# -

pd.set_option('display.float_format', lambda x: '%.1f' % x) 

table = trace.combine_and_trace(title, "combined_dataframe").fillna('')

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
#reformat columns
df['Period'] = 'year/' + df['Period'].str[0:4]
df['Commodity'] = df['Commodity'].str[:2] # codelist has 3 char long codes included but in this datset there are only categories with 1 to 2 char long in their code
df['Commodity'] = df['Commodity'].str.strip() # codes included in this datset are only 1 to 2 characters long
df['ONS Partner Geography'] = df['ONS Partner Geography'].str[:2]
df['Industry'] = df['Industry'].str[2:] # remove numbers as we're creating a new codelist. just first 2 characters in case 'U unknown industry' is used
df['Industry'] = df['Industry'].str.strip()
#%%
#rename columns
df.rename(columns={'OBS': 'Value', 'DATAMARKER' : 'Marker'}, inplace=True)


# %%
#reorder columns
df = df[['Period','ONS Partner Geography','Industry','Flow','Commodity', 'Value', 'Marker']]



#%%
df.to_csv('observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json') 

# %%
