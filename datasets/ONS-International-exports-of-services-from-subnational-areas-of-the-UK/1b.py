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

# Total value of service exports from the UK by NUTS1 area, industry and destination, 2017

# +
from gssutils import *

scraper = Scraper('https://www.ons.gov.uk/businessindustryandtrade/internationaltrade/datasets/internationalexportsofservicesfromsubnationalareasoftheuk')
tabs = { tab.name: tab for tab in scraper.distributions[0].as_databaker() }
scraper.dataset.family = 'trade'
trace = TransformTrace()
# -

list(tabs)

tab = tabs['1b']

datasetTitle = 'Total value of service exports from the UK by NUTS1 area, industry and destination, 2017'
columns=['Product', 'Service Destination', 'Service Origin','Flow', 'Unit', 'Measure Type', 'Period', 'Value', 'Marker']
trace.start(datasetTitle, tab, columns, scraper.distributions[0].downloadURL)

# +
footer = tab.excel_ref("A20").expand(RIGHT).expand(DOWN)
cell = tab.excel_ref('A5')
industry = cell.fill(DOWN).is_not_blank().is_not_whitespace()-footer
trace.Product("Taken from cell ref A6 and down, excluding footer and non blank values")
origin = cell.shift(0,-1).fill(RIGHT).is_not_blank().is_not_whitespace()
trace.Service_Origin("Taken from cell ref BC4 and right and non blank values")
destination = cell.fill(RIGHT).is_not_blank().is_not_whitespace()
trace.Service_Destination("Taken from cell ref B5 and right and not blank values")
observations = destination.fill(DOWN).is_not_blank().is_not_whitespace()
dimensions = [
            HDim(industry,'Product',DIRECTLY,LEFT),
            HDim(destination, 'Service Destination',DIRECTLY,ABOVE),
            HDim(origin, 'Service Origin',CLOSEST,LEFT),
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
# new_table["Service Origin"] == "Northern Ireland"

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
'North East ':'nuts1/UKC',\
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


