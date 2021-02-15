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
    print(tab.name)
    
    trace.start(title1, tab, columns, distribution1.downloadURL)
#     trace.start(title2, tab, columns, distribution2.downloadURL)
    
    if tab.name == 'tig_ind_ex':
        flow = 'exports'
    elif tab.name == 'tig_ind_im':
        flow = 'imports'
    print(flow)   
 
    country = tab.filter('country').fill(DOWN).is_not_blank()
    industry = tab.filter('industry').fill(DOWN).is_not_blank()
    commodity = tab.filter('commodity').fill(DOWN).is_not_blank()
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

scraper1.dataset.title = 'UK trade in goods by industry, country and commodity - Imports & Exports'
scraper2.dataset.title = 'UK trade in goods by industry, country and commodity - Imports & Exports'
scraper1.dataset.description = descr
scraper2.dataset.description = descr

# +
table = table[table['OBS'] != 0]
table.loc[table['DATAMARKER'].astype(str) == '..', 'DATAMARKER'] = 'suppressed'
table.rename(columns={'OBS': 'Value', 'DATAMARKER' : 'Marker'}, inplace=True)
# LPerryman - changed indice to 2 rather than 1
table['CORD SITC'] = table['CORD SITC'].str[:2]
table['ONS Partner Geography'] = table['ONS Partner Geography'].str[:2]
table['SIC 2007'] = table['SIC 2007'].str[:2]

# LPerryman - changing names back to what is in the spreadsheet, can't remember why they were changed
# Some values have a space on the end and deleting Measure type and Unit coluns as these can be defined in the info.json
# Converting Value to integer
table = table.rename(columns={"CORD SITC": "Commodity", 'SIC 2007': 'Industry'})
table['Industry'] = table['Industry'].str.strip()
table['Commodity'] = table['Commodity'].str.strip()
del table['Measure Type']
del table['Unit']
table['Value'].loc[(table['Value'] == '')] = 0
table['Value'] = table['Value'].astype(int)
table.head(10)
# -

table['Period'] = 'year/' + table['Period'].str[0:4]

#table = table[['ONS Partner Geography', 'Period','Flow','CORD SITC', 'SIC 2007', 'Measure Type', 'Value', 'Unit', 'Marker']]
table = table[['ONS Partner Geography', 'Period','Flow','Commodity', 'Industry', 'Value', 'Marker']]


cubes.add_cube(scraper1, table, title)
cubes.output_all()

trace.render("spec_v1.html")

# +
#table['Industry'].unique()

# +
#table['Commodity'].unique()

# +
#print(scraper1.dataset.title)
#print(scraper2.dataset.comment)
# -


