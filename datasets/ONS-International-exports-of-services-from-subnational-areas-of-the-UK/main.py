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
import json

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
    HDimConst("Sheet", tab.name)
]
tidy_sheet = ConversionSegment(tab, dimensions, observations)
savepreviewhtml(tidy_sheet, fname = tab.name + "Preview.html")
trace.with_preview(tidy_sheet)
#store 2b and appending to combined_dataframe
trace.store("combined_dataframe", tidy_sheet.topandas())
# +
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
# +
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

# +
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
df

unprefixed_values = df.loc[(df['Sheet'] == '4b'), 'Service Origin Geography']
print(unprefixed_values)

# +
# print(df.loc[df['B'].isin(['one','three'])])
required_values = df.loc[df['Sheet'].isin(['1a', '1b', '2a', '2b', '3', '4a']), 'Service Origin Geography']
print(type(required_values))
required_values = required_values.map(
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
print(required_values)

with pd.option_context('display.max_rows()', None):
    print(required_values)

# +
# with pd.option_context("display.max_rows", None):
#     print(df['Sheet'])
#     print(df['Service Origin Geography'])
# with pd.option_context("display.max_rows", None):
# df[["Service Origin Geography", "Sheet"]]

# +
# with pd.option_context("display.max_rows", None):
#     print(df)

# +
# df.loc[df['foo'].isnull(),'foo'] = df['bar']

# df.Service Origin Geography.fillna(df.City_Region, inplace = True)
# del df['City_Region']
# df

# +
# df['Sheet Name'].unique()
# required_sheet = df[df['Sheet'] == "1a", "1b", "2a", "2b", "3", "4a"]
# value = required_sheet.Sheet.item()
# print(value)

# for tab ,name in tabs.items():
# #     print(tab)
#     if tab in df["Sheet"]:
# -

df.rename(columns={'OBS' : 'Value','DATAMARKER' : 'Marker'}, inplace=True)

#mapping Service Origin Geography outputs to nuts1 codes 
trace.Service_Origin_Geography("mapping Service Origin Geography outputs to nuts1 nuts2 and nuts3 codes ")
df['Service Origin Geography'] = df['Service Origin Geography'].map(
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

f1=(df['NUTS'] =='nuts2/')
df.loc[f1,'Service Origin Geography'] = 'nuts2/' + df.loc[f1,'Service Origin Geography']

f1=(df['NUTS'] =='nuts3/')
df.loc[f1,'Service Origin Geography'] = 'nuts3/' + df.loc[f1,'Service Origin Geography']


df['Period'] = "year/2017"
trace.Period("Hard coded as year/2017")

df['Export Services'] = df['Export Services'].apply(pathify)
df

for x in df["Service Origin Geography"]:
    print(x)

df["Service Origin Geography"] = df["Service Origin Geography"].apply(pathify)

df["Service Destination"] = df["Service Destination"].apply(pathify)

df['Service Destination'] = df['Service Destination'].map(
    lambda x: { 'total' : 'all', 'row' :'rest-of-world'}.get(x, x))

df['Marker'] = df['Marker'].map(lambda x: { '..' : 'suppressed' }.get(x, x))

df['Flow Directions'] = 'exports'
trace.Flow_Directions("Adding Flow directions column to dataframe with value exports")

#define the column order output into dataframe called tidy
tidy = df[['Period','Export Services','Service Origin Geography','Service Destination', 'Flow Directions', 'Value','Marker']]
tidy

#output cube and spec
cubes.add_cube(scraper, tidy.drop_duplicates(), distribution.title)
cubes.output_all()
trace.render("spec_v1.html")

# +
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
