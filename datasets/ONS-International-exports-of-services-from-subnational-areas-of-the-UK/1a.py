# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# Total value of service exports from the UK by NUTS1 area and industry, 2017

# +
from gssutils import *

scraper = Scraper('https://www.ons.gov.uk/businessindustryandtrade/internationaltrade/datasets/internationalexportsofservicesfromsubnationalareasoftheuk')
tabs = { tab.name: tab for tab in scraper.distributions[0].as_databaker() }
# -

list(tabs)

tab = tabs['1a']

# +
cell = tab.excel_ref('A4')
industry = cell.fill(DOWN).is_not_blank().is_not_whitespace()
geography = cell.fill(RIGHT).is_not_blank().is_not_whitespace()            
observations = geography.fill(DOWN).is_not_blank().is_not_whitespace() 
Dimensions = [
            HDim(industry,'Product',DIRECTLY,LEFT),
            HDim(geography, 'Service Origin',DIRECTLY,ABOVE),
            HDimConst('Service Destination','all'),
            HDimConst('Flow','Exports'),
            HDimConst('Unit','gbp-million'),  
            HDimConst('Measure Type','GBP Total'),
            HDimConst('Period','gregorian-interval/2016-03-31T00:00:00/P1Y')
    
]  
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
new_table = c1.topandas()
import numpy as np
new_table.rename(columns={'OBS': 'Value','DATAMARKER': 'Marker'}, inplace=True)
# -

new_table['Service Origin'] = new_table['Service Origin'].map(
    lambda x: {  
'United Kingdom':'nuts1/all',
'North East ':'nuts1/UKC',
'North West':'nuts1/UKD',
'Yorkshire and The Humber':'nuts1/UKE',
'East Midlands':'nuts1/UKF',
'West Midlands':'nuts1/UKG',
'East of England':'nuts1/UKH',
'London':'nuts1/UKI',
'South East':'nuts1/UKJ',
'South West':'nuts1/UKK',
'Wales':'nuts1/UKL',
'Scotland':'nuts1/UKM',
'Northern Ireland':'nuts1/UKN'      
        }.get(x, x))
