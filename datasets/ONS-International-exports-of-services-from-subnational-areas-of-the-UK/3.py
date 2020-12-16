# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.7.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# Total value of service exports from Great Britain by NUTS3 area and destination, 2017 

# +
from gssutils import *

scraper = Scraper('https://www.ons.gov.uk/businessindustryandtrade/internationaltrade/datasets/internationalexportsofservicesfromsubnationalareasoftheuk')
tabs = { tab.name: tab for tab in scraper.distributions[0].as_databaker() }
scraper.dataset.family = 'trade'
# -

list(tabs)

tab = tabs['3']

# +
cell = tab.excel_ref('A4')
origin = cell.fill(DOWN).is_not_blank().is_not_whitespace()  
destination = cell.shift(1,0).fill(RIGHT).is_not_blank().is_not_whitespace() \
            .filter(lambda x: type(x.value) != 'Percentage' not in x.value) 
observations = destination.fill(DOWN).is_not_blank().is_not_whitespace() 
Dimensions = [
            HDimConst('Product','all services'),
            HDim(destination, 'Service Destination',DIRECTLY,ABOVE),
            HDim(origin, 'Service Origin',DIRECTLY,LEFT),
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

new_table['Service Origin'] = 'nuts3/' + new_table['Service Origin']
