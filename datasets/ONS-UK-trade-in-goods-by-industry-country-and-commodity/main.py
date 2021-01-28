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

# +
table = table[table['OBS'] != 0]
table.loc[table['DATAMARKER'].astype(str) == '..', 'DATAMARKER'] = 'suppressed'
table.rename(columns={'OBS': 'Value', 'DATAMARKER' : 'Marker'}, inplace=True)

table['CORD SITC'] = table['CORD SITC'].str[:1]
table['ONS Partner Geography'] = table['ONS Partner Geography'].str[:2]
table['SIC 2007'] = table['SIC 2007'].str[:2]
table
# -

table['Period'] = 'year/' + table['Period'].str[0:4]

table = table[['ONS Partner Geography', 'Period','Flow','CORD SITC', 'SIC 2007', 'Measure Type', 'Value', 'Unit', 'Marker']]

cubes.add_cube(scraper1, table, title)
cubes.output_all()

trace.render("spec_v1.html")
