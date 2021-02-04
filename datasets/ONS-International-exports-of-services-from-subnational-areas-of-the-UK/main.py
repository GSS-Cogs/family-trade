# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
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

# ONS-International-exports-of-services-from-subnational-areas-of-the-UK

# +
from gssutils import *
import json
import numpy as np 

cubes = Cubes("info.json")
trace = TransformTrace()
info = json.load(open('info.json'))
scraper = Scraper(seed = 'info.json')
scraper
# -

distribution = scraper.distribution(latest = True)
tabs = {tab.name: tab for tab in distribution.as_databaker()}

data_download = distribution.downloadURL
datasetTitle = distribution.title
columns = ['Period', 'Export Services', 'Service Origin Geography', 'Flow Directions', 'Service Destination', 'Marker', 'Sheet Name']

# +
# tab 1a
tab = tabs['1a'] #set tab as tab 1a
trace.start(datasetTitle, tab, columns, data_download) #start tracer for tab 1a   
cell = tab.excel_ref('A4')

industry = cell.fill(DOWN).is_not_blank().is_not_whitespace()
trace.Export_Services("Defined from cell ref A4 down")

geography = cell.fill(RIGHT).is_not_blank().is_not_whitespace()
trace.Service_Origin_Geography("Defined from cell ref A4 and right")

trace.Service_Destination("Hardcoded as all")

sheet = tab.name

observations = geography.fill(DOWN).is_not_blank().is_not_whitespace()
dimensions = [
    HDim(industry, 'Export Services', DIRECTLY, LEFT),
    HDim(geography, 'Service Origin Geography', DIRECTLY, ABOVE),
    HDimConst('Service Destination', 'all'),
    HDimConst('NUTS','nuts1/'),
    HDimConst("Sheet", tab.name)
]
tidy_sheet = ConversionSegment(tab, dimensions, observations)
savepreviewhtml(tidy_sheet,fname = tab.name+ "Preview.html")
trace.with_preview(tidy_sheet)
#store 1a and appending to combined_dataframe
trace.store("combined_dataframe", tidy_sheet.topandas())


# +
# tab 1b
tab = tabs['1b'] #set tab as tab 1b
trace.start(datasetTitle, tab, columns, data_download) #start tracer for tab 1b
cell = tab.excel_ref('A5')

industry = cell.fill(DOWN).is_not_blank().is_not_whitespace()
trace.Export_Services("Defined from cell ref A5 Down ")

origin = cell.shift(0,-1).fill(RIGHT).is_not_blank().is_not_whitespace() 
trace.Service_Origin_Geography("Defined from cell ref A4 across")

destination = cell.fill(RIGHT).is_not_blank().is_not_whitespace() 
trace.Service_Destination("Defined from cell A5 across")

sheet = tab.name

observations = destination.fill(DOWN).is_not_blank().is_not_whitespace() 
dimensions = [
            HDim(industry,'Export Services',DIRECTLY,LEFT),
            HDim(destination, 'Service Destination',DIRECTLY,ABOVE),
            HDim(origin, 'Service Origin Geography',CLOSEST,LEFT),
            HDimConst('NUTS','nuts1/'),
            HDimConst("Sheet", tab.name)
]  
tidy_sheet = ConversionSegment(tab, dimensions, observations)   
savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
trace.with_preview(tidy_sheet)
#store 1b and appending to combined_dataframe
trace.store("combined_dataframe", tidy_sheet.topandas())

# +
# tab 2a
tab = tabs['2a'] #set tab as tab 2a
trace.start(datasetTitle, tab, columns, data_download) #start tracer for tab 2a
cell = tab.excel_ref('A5')

industry = cell.shift(1,0).fill(RIGHT).is_not_blank().is_not_whitespace()
trace.Export_Services("Defined from cell ref B5 Down ")

geography = cell.fill(DOWN).is_not_blank().is_not_whitespace()  
trace.Service_Origin_Geography("Defined from cell ref A5 down")

trace.Service_Destination("Hardcoded as all")

sheet = tab.name

observations = industry.fill(DOWN).is_not_blank().is_not_whitespace() 
dimensions = [
            HDim(industry,'Export Services',DIRECTLY,ABOVE),
            HDim(geography, 'Service Origin Geography',DIRECTLY,LEFT),
            HDimConst('Service Destination','all'),
            HDimConst('NUTS','nuts2/'),  # geography in this tab represents nuts2, defining constant to append to front of Service Origin Geography column once in df
            HDimConst("Sheet", tab.name)
]  
tidy_sheet = ConversionSegment(tab, dimensions, observations)   
savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
trace.with_preview(tidy_sheet)
#store 2a and appending to combined_dataframe
trace.store("combined_dataframe", tidy_sheet.topandas())

# +
# tab 2b
tab = tabs['2b'] #set tab as 2b
trace.start(datasetTitle, tab, columns, data_download) #start tracer for tab 2b
cell = tab.excel_ref("A5")

industry = cell.shift(0,-1).fill(RIGHT).is_not_blank().is_not_whitespace()
trace.Export_Services("Defined from cell ref C4 across")

destination = cell.shift(1,0).fill(RIGHT).is_not_blank().is_not_whitespace()
trace.Service_Destination("Defined from cell ref B5 across")
origin = cell.fill(DOWN).is_not_blank().is_not_whitespace()
trace.Service_Origin_Geography("Defined from cell ref B5 down")

sheet = tab.name

observations = destination.fill(DOWN).is_not_blank().is_not_whitespace()
dimensions = [
    HDim(industry, "Export Services", CLOSEST, LEFT),
    HDim(destination, "Service Destination", DIRECTLY, ABOVE),
    HDim(origin, "Service Origin Geography", DIRECTLY, LEFT),
    HDimConst('NUTS','nuts2/'),
    HDimConst("Sheet", tab.name)
]
tidy_sheet = ConversionSegment(tab, dimensions, observations)
savepreviewhtml(tidy_sheet, fname = tab.name + "Preview.html")
trace.with_preview(tidy_sheet)
#store 2b and appending to combined_dataframe
trace.store("combined_dataframe", tidy_sheet.topandas())
# # +
#tab 3
tab = tabs['3'] #start tracer for tab 3
trace.start(datasetTitle, tab, columns, data_download)
cell = tab.excel_ref("A4")

trace.Export_Services("Hard coded as all services")

origin = cell.fill(DOWN).is_not_blank().is_not_whitespace()
trace.Service_Origin_Geography("Defined from cell ref A4 down")

destination = cell.shift(1,0).fill(RIGHT).is_not_blank().is_not_whitespace() \
            .filter(lambda x: type(x.value) != 'Percentage' not in x.value)
trace.Service_Destination("Defined from cell ref B4 across excluding percentage values")

sheet = tab.name

observations = destination.fill(DOWN).is_not_blank().is_not_whitespace()
dimensions = [
    HDimConst('Export Services', 'all services'),
    HDim(origin, 'Service Origin Geography', DIRECTLY, LEFT),
    HDim(destination, 'Service Destination', DIRECTLY, ABOVE),
    HDimConst('NUTS', 'nuts3/'), #geography in this tab represents nuts3, definig constant to append to front of Service Origin Geography column once in df
    HDimConst("Sheet", tab.name)
]
tidy_sheet = ConversionSegment(tab, dimensions, observations)
savepreviewhtml(tidy_sheet, fname = tab.name + "Preview.html")
trace.with_preview(tidy_sheet)
#stor 3 and appending to combined_dataframe
trace.store("combined_dataframe", tidy_sheet.topandas())
# # +
# tab 4a
tab = tabs['4a'] #set tab as tab 4a
trace.start(datasetTitle, tab, columns, data_download) #start traer for tab 4a
cell = tab.excel_ref("A4")

industry = cell.fill(DOWN).is_not_blank().is_not_whitespace()
trace.Export_Services("Defined from cell ref A4 down")

geography = cell.fill(RIGHT).is_not_blank().is_not_whitespace()
trace.Service_Origin_Geography("Defined from cell ref across")
trace.Service_Destination("Hardcoded as all")

sheet = tab.name

observations = geography.fill(DOWN).is_not_blank().is_not_whitespace() 
dimensions = [
    HDim(industry, 'Export Services', DIRECTLY, LEFT ),
    HDim(geography, 'Service Origin Geography', DIRECTLY, ABOVE),
    HDimConst('Service Destination', 'all'),
    HDimConst("Sheet", tab.name)
]
tidy_sheet = ConversionSegment(tab, dimensions,observations)
savepreviewhtml(tidy_sheet, fname = tab.name + 'Preview.html')
trace.with_preview(tidy_sheet)
# store 4a and appending to combined_dataframe
trace.store("combined_dataframe", tidy_sheet.topandas())
# # +
# tab 4b
tab = tabs['4b'] #set tab as tab 4b
trace.start(datasetTitle, tab, columns, data_download) #start tracer for tab 4b
cell = tab.excel_ref('A5')

industry = cell.fill(DOWN).is_not_blank().is_not_whitespace()
trace.Export_Services("Defined from cell ref A5 down")

origin = cell.shift(0,-1).fill(RIGHT).is_not_blank().is_not_whitespace()  
trace.Service_Origin_Geography("Defined from cell ref A6 across")

destination = cell.fill(RIGHT).is_not_blank().is_not_whitespace() 
trace.Service_Destination("Defined from cell ref A5 across")

sheet = tab.name

observations = destination.fill(DOWN).is_not_blank().is_not_whitespace() 
dimensions = [
            HDim(industry,'Export Services',DIRECTLY,LEFT),
            HDim(destination, 'Service Destination',DIRECTLY,ABOVE),
            HDim(origin, 'Service Origin Geography',CLOSEST,LEFT), 
            HDimConst("Sheet", tab.name)
]  
tidy_sheet = ConversionSegment(tab, dimensions, observations)   
savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
trace.with_preview(tidy_sheet)
#store 4b and appending to combined_dataframe
trace.store("combined_dataframe", tidy_sheet.topandas())
# -

#post processing
df = trace.combine_and_trace(datasetTitle, "combined_dataframe")

df.rename(columns={'OBS' : 'Value','DATAMARKER' : 'Marker'}, inplace=True)

df.rename(columns={'OBS' : 'Value','DATAMARKER' : 'Marker'}, inplace=True)

df['Period'] = "year/2017"
trace.Period("Hard coded as year/2017")

df['Export Services'] = df['Export Services'].apply(pathify)

df["Service Destination"] = df["Service Destination"].apply(pathify)

df['Service Destination'] = df['Service Destination'].map(
    lambda x: { 'total' : 'all', 'row' :'rest-of-world'}.get(x, x))

df['Marker'] = df['Marker'].map(lambda x: { '..' : 'suppressed' }.get(x, x))

df['Flow Directions'] = 'exports'
trace.Flow_Directions("Adding Flow directions column to dataframe with value exports")

#Changing notation for nuts 1 values one. (Tabs 1a and 1b)
f1=((df['NUTS'] =='nuts1/'))
df.loc[f1,'Service Origin Geography'] = df.loc[f1,'Service Origin Geography'].map(
    lambda x: {  
        'United Kingdom':'all',
        'North East ':'UKC',
        'North West':'UKD',
        'Yorkshire and The Humber':'UKE',
        'East Midlands':'UKF',
        'West Midlands':'UKG',
        'East of England':'UKH',
        'London':'UKI',
        'South East':'UKJ',
        'South West':'UKK',
        'Wales':'UKL',
        'Scotland':'UKM',
        'Northern Ireland':'UKN'      
         }.get(x, x))

# +
#df['Service Origin Geography'].unique()
# -

#adding in the nuts?/ notation to each value in Service Origin Geography
df['NUTS'].replace(np.nan, '', inplace=True)

df['Service Origin Geography'] = df['NUTS'] + df['Service Origin Geography']

# +
#df['Service Origin Geography'] = df['Service Origin Geography'].apply(pathify)

# +
#df['Service Origin Geography'].unique()

# +
df = df.replace({'Service Origin Geography' : {
    'nuts1/all': 'http://data.europa.eu/nuts/code/UK',
    'nuts1/' : 'http://data.europa.eu/nuts/code/', 
    'nuts2/' : 'http://data.europa.eu/nuts/code/', 
    'nuts3/' : 'http://data.europa.eu/nuts/code/',}},regex=True)

df = df.replace({'Service Origin Geography' : {
    'Cambridgeshire and Peterborough' : 'http://statistics.data.gov.uk/id/statistical-geography/E47000008',
    'Aberdeen and Aberdeenshire' : 'http://statistics.data.gov.uk/id/statistical-geography/S11000001', #Using strategic development plan code as this includes Aberdeen and the Shire
    'Cardiff Capital Region' : 'http://statistics.data.gov.uk/id/statistical-geography/W42000001',
    'Edinburgh and South East Scotland' : 'http://statistics.data.gov.uk/id/statistical-geography/S11000003', #NOTE DOWN
    'Glasgow City Region' : 'http://statistics.data.gov.uk/id/statistical-geography/S12000049', #No code on geog site for city region just Glasgow City
    'Greater Manchester' : 'http://statistics.data.gov.uk/id/statistical-geography/E47000001',
    'Inner London' : 'http://statistics.data.gov.uk/id/statistical-geography/E13000001',
    'Liverpool City Region' : 'http://statistics.data.gov.uk/id/statistical-geography/E47000004',
    'North of Tyne' : 'http://statistics.data.gov.uk/id/statistical-geography/E47000011',
    'Outer London' : 'http://statistics.data.gov.uk/id/statistical-geography/E13000002',
    'Sheffield City Region' : 'http://statistics.data.gov.uk/id/statistical-geography/E47000002',
    'Swansea Bay' : 'http://statistics.data.gov.uk/id/statistical-geography/W42000004',
    'Tees Valley' : 'http://statistics.data.gov.uk/id/statistical-geography/E47000006',
    'West Midlands' : 'http://statistics.data.gov.uk/id/statistical-geography/E47000007',
    'West of England' : 'http://statistics.data.gov.uk/id/statistical-geography/E47000009' }})

#df['Service Origin Geography'].unique()
# -

df['Value'].loc[(df['Value'] == '')] = '0'
df['Value'] = df['Value'].astype(int)

#define the column order output into dataframe called tidy
tidy = df[['Period','Export Services','Service Origin Geography','Service Destination', 'Flow Directions', 'Value','Marker']]
tidy.head(5)

#scraper.dataset.title
#scraper.dataset.comment
scraper.dataset.description = scraper.dataset.description + """

Sources: UK Balance of Payments - The Pink Book; International Trade in Services; UK Trade in services by industry, country and service type: 2016 to 2017

Background:
The estimates shown in this workbook are experimental. While we have made some important changes (please refer to the article),
the basic concepts and methodology underpinning this analysis is still largely similar to the methods used in our original article
"Estimating the value of service exports abroad from different parts of the UK: 2011 to 2014" published on 8 July 2016 at:
www.ons.gov.uk/businessindustryandtrade/internationaltrade/articles/estimatingthevalueofserviceexportsabroadfromdifferentpartsoftheuk/2011to2014

Contents of this workbook:
Coverage: United Kingdom
Lowest geography: NUTS3 or Joint Authority
Variable(s): Values of service exports in £ million
Breakdown(s): NUTS1, NUTS2, NUTS3, Joint Authority, industry, destination (EU or rest of world)
Age group(s): n/a
Sex: n/a

Link to related publications:
www.ons.gov.uk/businessindustryandtrade/internationaltrade/articles/estimatingthevalueofserviceexportsabroadfromdifferentpartsoftheuk/previousReleases
www.gov.uk/government/statistics/regional-trade-in-goods-statistics-dis-aggregated-by-smaller-geographical-areas-2017
www.ons.gov.uk/economy/nationalaccounts/balanceofpayments/articles/uktradeinservicesbyindustrycountryandservicetype/2016to2017

The Nomenclature of Territorial Units for Statistics (NUTS) is a hierarchical classification of administrative areas, used across the European Union (EU) for statistical purposes.
NUTS1 are major socio-economic regions, while NUTS2 and NUTS3 are progressively smaller regions. In the context of the UK, the NUTS1 areas are Wales, Scotland, Northern Ireland and the nine regions of England.
Smaller geographic breakdowns may not sum exactly to aggregated totals due to rounding.
The European Union consists of 28 member countries including the United Kingdom. For trade purposes, this includes all 27 countries other than the UK as well as the European Central Bank and European Institutions.
The industrial groups presented in this analysis are based on the UK Standard Industrial Classification 2007, although some changes have been made.
Primary and utilities represents SIC07 section A, B, D and E; section G has been split into two parts (Wholesale and motor trades, and Retail); Other services comprises of O, P, Q, R, S and unknown/unallocated industries
For further information about the industrial classification, please see:
www.ons.gov.uk/methodology/classificationsandstandards/ukstandardindustrialclassificationofeconomicactivities/uksic2007
"""

#output cube and spec
cubes.add_cube(scraper, tidy.drop_duplicates(), distribution.title)
cubes.output_all()
trace.render("spec_v1.html")

#  Keeping for reference
#  Unit = gbp-million
#  , Measure Type = GBP Total
#
# Note the following do not have a NUTS code 
# cambridgeshire-and-peterborough',
# 'greater-manchester', 'liverpool-city-region', 'inner-london',
# 'outer-london', 'north-of-tyne', 'sheffield-city-region',
# 'tees-valley', 'west-of-england', 'cardiff-capital-region',
# 'swansea-bay', 'aberdeen-and-aberdeenshire',
# 'edinburgh-and-south-east-scotland', 'glasgow-city-region'

