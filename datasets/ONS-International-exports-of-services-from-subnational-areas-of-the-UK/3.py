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
trace = TransformTrace()
# -

list(tabs)

tab = tabs['3']

datasetTitle = 'Total value of service exports from Great Britain by NUTS3 area and destination, 2017'
columns=['Product', 'Service Destination', 'Service Origin', 'Flow', 'Unit', 'Measure Type', 'Period', 'Value', 'Marker']
trace.start(datasetTitle, tab, columns, scraper.distributions[0].downloadURL)

# +
footer = tab.excel_ref("A173").expand(RIGHT).expand(DOWN)
cell = tab.excel_ref('A4')
origin = cell.fill(DOWN).is_not_blank().is_not_whitespace()-footer
trace.Service_Origin = ("Taken from A5 to A172 which are not blank")
destination = cell.shift(1,0).fill(RIGHT).is_not_blank().is_not_whitespace() \
            .filter(lambda x: type(x.value) != 'Percentage' not in x.value) 
trace.Service_Destination("Taken from C4 to E4 which are not blank")
observations = destination.fill(DOWN).is_not_blank().is_not_whitespace()
dimensions = [
            HDimConst('Product','all services'),
            HDim(destination, 'Service Destination',DIRECTLY,ABOVE),
            HDim(origin, 'Service Origin',DIRECTLY,LEFT),
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

new_table['Service Origin'] = 'nuts3/' + new_table['Service Origin']
trace.Service_Origin = ("Adding nuts3/ to values in Service Origin column")

trace.render("spec_v1.html")
new_table
