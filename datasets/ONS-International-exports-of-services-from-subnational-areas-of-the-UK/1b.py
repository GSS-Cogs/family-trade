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

# Total value of service exports from the UK by NUTS1 area, industry and destination, 2017

# +
from gssutils import *

scraper = Scraper('https://www.ons.gov.uk/businessindustryandtrade/internationaltrade/datasets/internationalexportsofservicesfromsubnationalareasoftheuk')
tabs = { tab.name: tab for tab in scraper.distributions[0].as_databaker() }
# -

list(tabs)

tab = tabs['1b']

# +
cell = tab.excel_ref('A5')
industry = cell.fill(DOWN).is_not_blank().is_not_whitespace()
origin = cell.shift(0,-1).fill(RIGHT).is_not_blank().is_not_whitespace()  
destination = cell.fill(RIGHT).is_not_blank().is_not_whitespace() 
observations = destination.fill(DOWN).is_not_blank().is_not_whitespace() 
Dimensions = [
            HDim(industry,'Product',DIRECTLY,LEFT),
            HDim(destination, 'Service Destination',DIRECTLY,ABOVE),
            HDim(origin, 'Service Origin',CLOSEST,LEFT),
            HDimConst('Flow','Exports'),
            HDimConst('Unit','gbp-million'),  
            HDimConst('Measure Type','GBP Total'),
            HDimConst('Period','gregorian-interval/2016-03-31T00:00:00/P1Y')
    
]  
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
new_table = c1.topandas()
import numpy as np
new_table.rename(columns={'OBS': 'Value','DATAMARKER': 'Marker'}, inplace=True)
