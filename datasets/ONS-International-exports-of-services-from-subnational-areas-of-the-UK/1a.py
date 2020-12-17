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

# Total value of service exports from the UK by NUTS1 area and industry, 2017

# +
from gssutils import *

scraper = Scraper('https://www.ons.gov.uk/businessindustryandtrade/internationaltrade/datasets/internationalexportsofservicesfromsubnationalareasoftheuk')
tabs = { tab.name: tab for tab in scraper.distributions[0].as_databaker() }
scraper.dataset.family = 'trade'
trace = TransformTrace()
# -

list(tabs)

tab = tabs['1a']

datasetTitle = 'Total value of service exports from the UK by NUTS1 area and industry, 2017'
columns=['Product','Service Origin','Service Destination','Flow', 'Unit', 'Measure Type', 'Period', 'Value', 'Marker']
trace.start(datasetTitle, tab, columns, scraper.distributions[0].downloadURL)  

# +
cell = tab.excel_ref('A4')
industry = cell.fill(DOWN).is_not_blank().is_not_whitespace()
trace.Product("Taken from A5 and down")
geography = cell.fill(RIGHT).is_not_blank().is_not_whitespace()
trace.Service_Origin("Taken from B4 and right")
observations = geography.fill(DOWN).is_not_blank().is_not_whitespace()
dimensions = [
            HDim(industry,'Product',DIRECTLY,LEFT),
            HDim(geography, 'Service Origin',DIRECTLY,ABOVE),
            HDimConst('Service Destination','all'),
            HDimConst('Flow','Exports'),
            HDimConst('Unit','gbp-million'),  
            HDimConst('Measure Type','GBP Total'),
            HDimConst('Period','gregorian-interval/2016-03-31T00:00:00/P1Y')
    
]  
c1 = ConversionSegment(tab, dimensions, observations)
trace.with_preview(c1)
trace.store("combined_dataframe", c1.topandas())
# -

new_table = trace.combine_and_trace(datasetTitle, "combined_dataframe")

new_table.rename(columns={'OBS': 'Value','DATAMARKER': 'Marker'}, inplace=True)
trace.multi(["Value", "Marker"], "Rename databaker columns OBS and DATAMARKER columns to value and Marker respectively")
new_table

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
trace.Service_Origin("replacing the values in Service Origin column in the order of\
'United Kingdom':'nuts1/all',\
'North East':'nuts1/UKC',\
'North West':'nuts1/UKD',\
'Yorkshire and The Humber':'nuts1/UKE',\
'East Midlands':'nuts1/UKF',\
'West Midlands':'nuts1/UKG',\
'East of England':'nuts1/UKH',\
'London':'nuts1/UKI',\
'South East':'nuts1/UKJ',\
'South West':'nuts1/UKK',\
'Wales':'nuts1/UKL',\
'Scotland':'nuts1/UKM',\
'Northern Ireland':'nuts1/UKN'")

trace.render("spec_v1.html")
new_table


