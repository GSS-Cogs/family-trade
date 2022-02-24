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

# UK trade in goods by industry, country and commodity, imports

import pandas as pd
import json
from gssutils import *

pd.options.mode.chained_assignment = None 

cubes = Cubes("info.json")

# +
with open ('info.json') as file:
    info = json.load(file)

landingPage = info['landingPage'][1]
landingPage
# -

scraper = Scraper(landingPage)
scraper.dataset.family = info['families']
scraper

distribution = scraper.distribution(latest=True)
distribution

tabs = distribution.as_databaker()
tab = tabs[1]  
print(tab.name)

trace = TransformTrace()
title = distribution.title
columns = ['ONS Partner Geography', 'Period','Flow','CORD SITC', 'SIC 2007', 'Measure Type','Value','Unit', 'Marker']
trace.start(title, tab, columns, distribution.downloadURL)

# +
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

table = trace.combine_and_trace(title, "combined_dataframe").fillna('')
# -

pd.set_option('display.float_format', lambda x: '%.1f' % x) 

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

table = table[['ONS Partner Geography', 'Period','Flow','CORD SITC', 'SIC 2007', 'Measure Type','Value','Unit', 'Marker']]

trace.render("spec_v1.html")
