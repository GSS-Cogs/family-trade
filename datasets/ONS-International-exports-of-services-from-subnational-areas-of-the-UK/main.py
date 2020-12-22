# -*- coding: utf-8 -*-
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

# ONS-International-exports-of-services-from-subnational-areas-of-the-UK

# +
from gssutils import *

scraper = Scraper('https://www.ons.gov.uk/businessindustryandtrade/internationaltrade/datasets/internationalexportsofservicesfromsubnationalareasoftheuk')
tabs = { tab.name: tab for tab in scraper.distributions[0].as_databaker() }
scraper.dataset.family = 'trade'
cubes = Cubes("info.json")
trace = TransformTrace()
# -

for name,tab in tabs.items():
    continue

datasetTitle = "Total values of service exports in £ million brokendown by NUTS1, NUTS2, NUTS3, Joint Authority, industry, destination (EU or rest of world)"
columns=['Product', 'Service Origin', 'Service Destination', 'Flow', 'Unit', 'Measure Type', 'Period', 'Value', 'Marker']
trace.start(datasetTitle, tab, columns, scraper.distributions[0].downloadURL)

# +
for name,tab in tabs.items():
    print(name)
    
    if tab.name in ['1a', '4a']:
        cell = tab.excel_ref('A4')
        industry = cell.fill(DOWN).is_not_blank().is_not_whitespace()
        trace.Product("Taken from A5 and down")
        geography = cell.fill(RIGHT).is_not_blank().is_not_whitespace()
#         trace.Service_Origin("Taken from B4 and right")
        observations = geography.fill(DOWN).is_not_blank().is_not_whitespace()

    elif '3' in tab.name:
        footer = tab.excel_ref("A173").expand(RIGHT).expand(DOWN)
        cell = tab.excel_ref('A4')
        origin = cell.fill(DOWN).is_not_blank().is_not_whitespace()-footer
        trace.Service_Origin = ("Taken from A5 to A172 which are not blank")
        destination = cell.shift(1,0).fill(RIGHT).is_not_blank().is_not_whitespace() \
            .filter(lambda x: type(x.value) != 'Percentage' not in x.value)
        trace.Service_Destination("Taken from C4 to E4 which are not blank")
        observations = destination.fill(DOWN).is_not_blank().is_not_whitespace()

    elif '2a' in tab.name:
        footer = tab.excel_ref('A46').expand(RIGHT).expand(DOWN)
        cell = tab.excel_ref('A5')
        industry = cell.shift(1, 0).fill(RIGHT).is_not_blank().is_not_whitespace()
        trace.Product("Taken from C5 and across which are non blank")
        geography = cell.fill(DOWN).is_not_blank().is_not_whitespace()-footer
        trace.Service_Origin("Taken from A6 and down which are not blank")
        observations = industry.fill(DOWN).is_not_blank().is_not_whitespace()
        
    elif '2b' in tab.name:
        cell = tab.excel_ref('A5')
        industry = cell.shift(0,-1).fill(RIGHT).is_not_blank().is_not_whitespace()
        trace.Product("Taken from cell ref CDE4 across which are not blank")
        origin = cell.fill(DOWN).is_not_blank().is_not_whitespace()
        trace.Service_Origin("Taken from cell ref A6 to A45 down which are not blank")
        destination = cell.shift(1, 0).fill(RIGHT).is_not_blank().is_not_whitespace()
        trace.Service_Destination("Taken from cell ref C5 across which are not blank")
        observations = destination.fill(DOWN).is_not_blank().is_not_whitespace()

    elif tab.name in ['1b','4b']:
        footer = tab.excel_ref("A20").expand(RIGHT).expand(DOWN)
        cell = tab.excel_ref('A5')
        industry = cell.fill(DOWN).is_not_blank().is_not_whitespace()
        trace.Product("Taken from cell ref A6 and down, excluding footer and non blank values")
        origin = cell.shift(0,-1).fill(RIGHT).is_not_blank().is_not_whitespace()
#         trace.Service_Origin("Taken from cell ref BC4 and right and non blank values")
        destination = cell.fill(RIGHT).is_not_blank().is_not_whitespace()
        trace.Service_Destination("Taken from cell ref B5 and right and not blank values")
        observations = destination.fill(DOWN).is_not_blank().is_not_whitespace()
        
    if tab.name in ['1a', '4a']:
        
        dimensions = [
            HDim(industry,'Product',DIRECTLY,LEFT),
            HDim(geography, 'Service Origin',DIRECTLY,ABOVE),
            HDimConst('Service Destination','all'),
            HDimConst('Flow','Exports'),
            HDimConst('Unit','gbp-million'),  
            HDimConst('Measure Type','GBP Total'),
            HDimConst('Period','gregorian-interval/2016-03-31T00:00:00/P1Y')
        ]
            
    elif tab.name in ['3']:
        
        dimensions = [
            HDimConst('Product','all services'),
            HDim(destination, 'Service Destination',DIRECTLY,ABOVE),
            HDim(origin, 'Service Origin',DIRECTLY,LEFT),
            HDimConst('Flow','Exports'),
            HDimConst('Unit','gbp-million'),  
            HDimConst('Measure Type','GBP Total'),
            HDimConst('Period','gregorian-interval/2016-03-31T00:00:00/P1Y')
    
]
    elif tab.name in ['2a']:
        
        dimensions = [
            HDim(industry,'Product',DIRECTLY,ABOVE),
            HDim(geography, 'Service Origin',DIRECTLY,LEFT),
            HDimConst('Service Destination','all'),
            HDimConst('Flow','Exports'),
            HDimConst('Unit','gbp-million'),  
            HDimConst('Measure Type','GBP Total'),
            HDimConst('Period','gregorian-interval/2016-03-31T00:00:00/P1Y')
    
]
        
    elif tab.name in ['2b']:
        
        dimensions = [
            HDim(industry,'Product',CLOSEST,LEFT),
            HDim(destination, 'Service Destination',DIRECTLY,ABOVE),
            HDim(origin, 'Service Origin',DIRECTLY,LEFT),
            HDimConst('Flow','Exports'),
            HDimConst('Unit','gbp-million'),  
            HDimConst('Measure Type','GBP Total'),
            HDimConst('Period','gregorian-interval/2016-03-31T00:00:00/P1Y')
    
]  
   
    elif tab.name in ['1b', '4b']:
            
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
# new_table = c1.topandas()
# new_table
# -

new_table = trace.combine_and_trace(datasetTitle, "combined_dataframe")

if tab.name in ['1a', '2a', '3', '2a', '2b', '1b', '4b']:
    new_table.rename(columns={'OBS': 'Value','DATAMARKER': 'Marker'}, inplace=True)
    trace.multi(["Value", "Marker"], "Rename databaker columns OBS and DATAMARKER columns to value and Marker respectively")
    new_table
elif tab.name in '4a':
    new_table.rename(columns={'OBS': 'Value'}, inplace=True)
# trace.multi(["Value", "Marker"], "Rename databaker columns OBS and DATAMARKER columns to value and Marker respectively")
    trace.Value("Renamed column OBS into Value")

# +
if tab.name in '1a':
    
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
    
elif tab.name in '1b':
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
# -

if tab.name in '3':
    new_table['Service Origin'] = 'nuts3/' + new_table['Service Origin']
    trace.Service_Origin = ("Adding nuts3/ to values in Service Origin column")
elif tab.name in ['2a', '2b']:
    new_table['Service Origin'] = 'nuts2/' + new_table['Service Origin']
    trace.Service_Origin = ("Adding nuts2/ to values in Service Origin column")

new_table

cubes.add_cube(scraper, new_table, "ONS-International-exports-of-services-from-subnational-areas-of-the-UK" )

cubes.output_all()
trace.render("spec_v1.html")
