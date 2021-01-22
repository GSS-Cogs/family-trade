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

from gssutils import *
import json
import math
cubes = Cubes("info.json")
info = json.load(open('info.json'))


scraper = Scraper(seed="info.json")
scraper


# %%
tidied_sheets = []
trace = TransformTrace()
df = pd.DataFrame()

all_tabs = { tab.name: tab for tab in scraper.distributions[0].as_databaker() }


# %%
def cell_to_string(cell):
    s = str(cell)
    start = s.find("'") + len("'")
    end = s.find(">")
    substring = s[start:end].strip("'")
    return substring


# %%
tab = all_tabs["8. Travel"]

tab_title = "8_travel"
tab_columns = ["Year", "NUTS1 Area", "Travel Type", "Country or Origin of Trade", "Measure Type", "Unit"]
trace.start(tab_title, tab, tab_columns, scraper.distributions[0].downloadURL)


year = "2018"
trace.Year("Hardcoded but could have been taken from tab title (cell A1)")

nuts1_area = tab.excel_ref("A5:A17").is_not_blank()
trace.NUTS1_Area("Selected as all non-blank values between cell refs A5 and A17")

travel_type = tab.excel_ref("B3").expand(RIGHT).is_not_blank()
trace.Travel_Type("Selected as all non-blank values from cell ref B3 going right/across.")

origin = tab.excel_ref("B4").expand(RIGHT).is_not_blank()
trace.Country_or_Origin_of_Trade("Selected as all non-blank values from cell ref B4 going right/across.")

measure_type = "Travel-Related Service Imports Value"
trace.Measure_Type("Hardcoded but could have been taken from cell A1")

unit = "£ millions"
trace.Unit("Hardcoded but could have been taken from cell A2")


observations = tab.excel_ref("B5").expand(RIGHT).expand(DOWN).is_not_blank()

dimensions = [
    HDimConst("Year", year),
    HDim(nuts1_area, "NUTS1 Area", CLOSEST, ABOVE),
    HDim(travel_type, "Travel Type", CLOSEST, LEFT),
    HDim(origin, "Country or Origin of Trade", DIRECTLY, ABOVE),
    HDimConst("Measure Type", measure_type),
    HDimConst("Unit", unit)
]

tidy_sheet = ConversionSegment(tab, dimensions, observations)
trace.with_preview(tidy_sheet)
#savepreviewhtml(tidy_sheet)
trace.store("combined_" + tab_title, tidy_sheet.topandas())

df = trace.combine_and_trace(tab_title, "combined_" + tab_title)
df.rename(columns={'OBS' : 'Value'}, inplace=True)
trace.render()

# +
df = df[["Year", "NUTS1 Area", "Travel Type", "Country or Origin of Trade", "Value"]]
"""
df = df.replace({'NUTS1 Area' : {'North East' : 'http://statistics.data.gov.uk/id/statistical-geography/UKC',
                                'NorthWest' : 'http://statistics.data.gov.uk/id/statistical-geography/UKD',
                                'Yorkshire and The Humber' : 'http://statistics.data.gov.uk/id/statistical-geography/UKE',
                                'East Midlands' : 'http://statistics.data.gov.uk/id/statistical-geography/UKF',
                                'West Midlands' : 'http://statistics.data.gov.uk/id/statistical-geography/UKG',
                                'East of England' : 'http://statistics.data.gov.uk/id/statistical-geography/UKH',
                                'London' : 'http://statistics.data.gov.uk/id/statistical-geography/UKI',
                                'South East' : 'http://statistics.data.gov.uk/id/statistical-geography/UKJ',
                                'South West ' : 'http://statistics.data.gov.uk/id/statistical-geography/UKK',
                                'Wales' : 'http://statistics.data.gov.uk/id/statistical-geography/UKL',
                                'Scotland' : 'http://statistics.data.gov.uk/id/statistical-geography/UKM',
                                'Northern Ireland' : 'http://statistics.data.gov.uk/id/statistical-geography/UKN',
                                'UK' : 'http://statistics.data.gov.uk/id/statistical-geography/UK'},
                 'Travel Type' : {'Business travel-related' : 'Business',
                                  'Personal travel-related' : 'Personal',
                                  'Total travel-related' : 'Total'}})
"""

df = df.replace({'NUTS1 Area' : {'North East' : 'http://data.europa.eu/nuts/code/UKC',
                                'NorthWest' : 'http://data.europa.eu/nuts/code/UKD',
                                'Yorkshire and The Humber' : 'http://data.europa.eu/nuts/code/UKE',
                                'East Midlands' : 'http://data.europa.eu/nuts/code/UKF',
                                'West Midlands' : 'http://data.europa.eu/nuts/code/UKG',
                                'East of England' : 'http://data.europa.eu/nuts/code/UKH',
                                'London' : 'http://data.europa.eu/nuts/code/UKI',
                                'South East' : 'http://data.europa.eu/nuts/code/UKJ',
                                'South West ' : 'http://data.europa.eu/nuts/code/UKK',
                                'Wales' : 'http://data.europa.eu/nuts/code/UKL',
                                'Scotland' : 'http://data.europa.eu/nuts/code/UKM',
                                'Northern Ireland' : 'http://data.europa.eu/nuts/code/UKN',
                                'UK' : 'http://data.europa.eu/nuts/code/UK'},
                 'Travel Type' : {'Business travel-related' : 'Business',
                                  'Personal travel-related' : 'Personal',
                                  'Total travel-related' : 'Total'}})

# -

"""
df = df.replace({'NUTS1 Area' : {'North East' : 'UKC',
                                'NorthWest' : 'UKD',
                                'Yorkshire and The Humber' : 'UKE',
                                'East Midlands' : 'UKF',
                                'West Midlands' : 'UKG',
                                'East of England' : 'UKH',
                                'London' : 'UKI',
                                'South East' : 'UKJ',
                                'South West ' : 'UKK',
                                'Wales' : 'UKL',
                                'Scotland' : 'UKM',
                                'Northern Ireland' : 'UKN'},
                 'Travel Type' : {'Business travel-related' : 'Business',
                                  'Personal travel-related' : 'Personal',
                                  'Total travel-related' : 'Total'}})
"""


df = df.rename(columns={'NUTS1 Area' : 'Location', 'Year' : 'Period'})

df['Period'] = df.apply(lambda x: 'year/' + x['Period'], axis = 1)

df['Includes Travel'] = 'Includes Travel'

df['Industry Grouping'] = 'Travel Related Trade'

df['Flow'] = 'Imports'

df['Marker'] = ''

COLUMNS_TO_NOT_PATHIFY = ['Value', 'Location']

for col in df.columns.values.tolist():
    if col in COLUMNS_TO_NOT_PATHIFY:
        continue
    try:
        df[col] = df[col].apply(pathify)
    except Exception as err:
        raise Exception('Failed to pathify column "{}".'.format(col)) from err

dfTravel = df[['Period', 'Location', 'Industry Grouping', 'Country or Origin of Trade', 'Flow', 'Travel Type', 'Includes Travel', 'Value', 'Marker']]
#dfTravel


tab = all_tabs["9. Tidy format"]

tidy_sheet_list = []
cs_list = []

tab_title = "8_tidy_format"
tab_columns = ["Year", "NUTS Level", "NUTS Code", "NUTS Area Name", "Industry Grouping", "Country or Origin of Trade", "Direction of Trade", "Measure Type", "Unit"]
trace.start(tab_title, tab, tab_columns, scraper.distributions[0].downloadURL)

tab_length = len(tab.excel_ref('B')) # number of rows of data
batch_number = 10 # iterates over this many rows at a time
number_of_iterations = math.ceil(tab_length/batch_number) # databaking will iterate this many times

for i in range(0, number_of_iterations):
    Min = str(5 + batch_number * i)
    Max = str(int(Min) + batch_number - 1)

    year = "2018"

    nuts_level = tab.excel_ref("A"+Min+":A"+Max).is_not_blank()

    nuts_code = tab.excel_ref("B"+Min+":B"+Max).is_not_blank()

    nuts_area_name = tab.excel_ref("C"+Min+":C"+Max).is_not_blank()

    industry_grouping = tab.excel_ref("D"+Min+":D"+Max).is_not_blank()

    trade_country_or_origin = tab.excel_ref("E"+Min+":E"+Max).is_not_blank()

    direction_of_trade = tab.excel_ref("F"+Min+":F"+Max).is_not_blank()

    measure_type = "Trade in Services Total Value"

    unit = "£ millions"


    observations = tab.excel_ref("G"+Min+":G"+Max).is_not_blank()

    dimensions = [
        HDimConst("Year", year),
        HDim(nuts_level, "NUTS Level", CLOSEST, ABOVE),
        HDim(nuts_code, "NUTS Code", CLOSEST, ABOVE),
        HDim(nuts_area_name, "NUTS Area Name", CLOSEST, ABOVE),
        HDim(industry_grouping, "Industry Grouping", CLOSEST, ABOVE),
        HDim(trade_country_or_origin, "Country or Origin of Trade", CLOSEST, ABOVE),
        HDim(direction_of_trade, "Direction of Trade", CLOSEST, ABOVE),
        HDimConst("Measure Type", measure_type),
        HDimConst("Unit", unit)
    ]

    if len(observations) != 0: # only use ConversionSegment if there is data
        cs_iteration = ConversionSegment(tab, dimensions, observations) # creating the conversionsegment
        tidy_sheet_iteration = cs_iteration.topandas() # turning conversionsegment into a pandas dataframe
        cs_list.append(cs_iteration) # add to list
        tidy_sheet_list.append(tidy_sheet_iteration) # add to list

tidy_sheet = pd.concat(tidy_sheet_list, sort=False) # dataframe for the whole tab

trace.Year("Hardcoded but could have been taken from tab title (cell A1)")
trace.NUTS_Level("Selected as all non-blank values between cell refs A5 and A7693")
trace.NUTS_Code("Selected as all non-blank values from cell ref B5 going down.")
trace.NUTS_Area_Name("Selected as all non-blank values from cell ref C5 going down.")
trace.Industry_Grouping("Selected as all non-blank values from cell ref D5 going down.")
trace.Country_or_Origin_of_Trade("Selected as all non-blank values from cell ref E5 going down.")
trace.Direction_of_Trade("Selected as all non-blank values from cell ref F5 going down.")
trace.Measure_Type("Hardcoded but could have been taken from cell A1")
trace.Unit("Hardcoded but could have been taken from cell A2")

trace.store("combined_" + tab_title, tidy_sheet)

df = trace.combine_and_trace(tab_title, "combined_" + tab_title)
df.rename(columns={'OBS' : 'Value', 'DATAMARKER' : 'Marker'}, inplace=True)

df = df[["Year", "NUTS Level", "NUTS Code", "NUTS Area Name", "Industry Grouping", "Country or Origin of Trade", "Direction of Trade", "Value", "Marker"]].fillna('')

df['Travel Type'] = df.apply(lambda x: 'Total' if (x['NUTS Level'] == 'NUTS1' and x['Industry Grouping'] == 'Travel') else 'NA', axis = 1)

df['NUTS Level'].unique()

df['Includes Travel'] = df.apply(lambda x: 'Includes Travel' if x['NUTS Level'] == 'NUTS1' else 'Excludes Travel', axis = 1)

df['Year'] = df.apply(lambda x: 'year/' + x['Year'], axis = 1)

df = df.rename(columns={'NUTS Code' : 'Location', 'Direction of Trade' : 'Flow', 'Year' : 'Period'})

# +
df['Location'] = df.apply(lambda x: 'http://data.europa.eu/nuts/code/' + x['Location'] if x['Location'] != 'N/A' else x['Location'], axis = 1) 
df['Location'] = df.apply(lambda x: 'http://data.europa.eu/nuts/code/UK' if (x['Location'] == 'N/A' and x['NUTS Area Name'] == 'United Kingdom') else x['Location'], axis = 1)

df['Location'] = df.apply(lambda x: x['NUTS Area Name'] if x['Location'] == 'N/A' else x['Location'], axis = 1)
# -

# df['Location'] = df.apply(lambda x: 'http://data.europa.eu/nuts/code/' + x['Location'] if x['Location'] != 'N/A' else x['Location'], axis = 1)
# df['Location'] = df.apply(lambda x: 'http://data.europa.eu/nuts/code/UK' if (x['Location'] == 'N/A' and x['NUTS Area Name'] == 'United Kingdom') else x['Location'], axis = 1)

# df['Location'] = df.apply(lambda x: x['NUTS Area Name'] if x['Location'] == 'N/A' else x['Location'], axis = 1)

df['Location'] = df.apply(lambda x: 'UK' if (x['Location'] == 'N/A' and x['NUTS Area Name'] == 'United Kingdom') else x['Location'], axis = 1)

df['Location'] = df.apply(lambda x: x['NUTS Area Name'] if x['Location'] == 'N/A' else x['Location'], axis = 1)


# +
df = df.replace({'Marker' : {'..' : 'Suppressed'}})

df = df.replace({'Marker' : {'..' : 'Suppressed'},
                 'Location' : {'Cambridgeshire and Peterborough Combined Authority' : 'http://statistics.data.gov.uk/id/statistical-geography/E47000008',
                               'Aberdeen City Region' : 'http://statistics.data.gov.uk/id/statistical-geography/S12000033', #NOTE DOWN
                               'Cardiff Capital Region' : 'http://statistics.data.gov.uk/id/statistical-geography/W42000001',
                               'Edinburgh and South East Scotland City Region' : 'http://statistics.data.gov.uk/id/statistical-geography/S11000003', #NOTE DOWN
                               'Glasgow City Region' : 'http://statistics.data.gov.uk/id/statistical-geography/S12000049', #NOTE DOWN
                               'Greater Manchester Combined Authority' : 'http://statistics.data.gov.uk/id/statistical-geography/E47000001',
                               'Inner London' : 'http://statistics.data.gov.uk/id/statistical-geography/E13000001',
                               'Liverpool City Region Combined Authority' : 'http://statistics.data.gov.uk/id/statistical-geography/E47000004',
                               'North of Tyne Combined Authority' : 'http://statistics.data.gov.uk/id/statistical-geography/E47000011',
                               'Outer London' : 'http://statistics.data.gov.uk/id/statistical-geography/E13000002',
                               'Sheffield City Region' : 'http://statistics.data.gov.uk/id/statistical-geography/E47000002',
                               'Swansea Bay City Region' : 'http://statistics.data.gov.uk/id/statistical-geography/W42000004',
                               'Tees Valley Combined Authority' : 'http://statistics.data.gov.uk/id/statistical-geography/E47000006',
                               'West Midlands Combined Authority' : 'http://statistics.data.gov.uk/id/statistical-geography/E47000007',
                               'West of England Combined Authority' : 'http://statistics.data.gov.uk/id/statistical-geography/E47000009'}})

# -

df = df.drop(['NUTS Level', 'NUTS Area Name'], axis=1)

COLUMNS_TO_NOT_PATHIFY = ['Value', 'Location']

for col in df.columns.values.tolist():
    if col in COLUMNS_TO_NOT_PATHIFY:
        continue
    try:
        df[col] = df[col].apply(pathify)
    except Exception as err:
        raise Exception('Failed to pathify column "{}".'.format(col)) from err

dfTidy = df[['Period', 'Location', 'Industry Grouping', 'Country or Origin of Trade', 'Flow', 'Travel Type', 'Includes Travel', 'Value', 'Marker']]
dfTidy


# %%

# %%
df = pd.concat([dfTravel, dfTidy])

cityregs =  [
    'Cambridgeshire and Peterborough Combined Authority', 
    'Aberdeen City Region',
    'Cardiff Capital Region',
    'Edinburgh and South East Scotland City Region',
    'Glasgow City Region',
    'Greater Manchester Combined Authority',
    'Inner London',
    'Liverpool City Region Combined Authority',
    'North of Tyne Combined Authority',
    'Outer London',
    'Sheffield City Region',
    'Swansea Bay City Region',
    'Tees Valley Combined Authority',
    'West Midlands Combined Authority',
    'West of England Combined Authority',]

# +
#df = df[~df.Location.isin(cityregs)]
#df = df.rename(columns={"Location":"NUTS Location"})
#df.head(10)
# -


# %%


# from IPython.core.display import HTML
for col in df:
    if col not in ['Value']:
        df[col] = df[col].astype('category')
        # display(HTML(f"<h2>{col}</h2>"))
        # display(df[col].cat.categories)


# %%
csvName = 'observations'

cubes.add_cube(scraper, df.drop_duplicates(), csvName)

trace.render()
cubes.output_all()


# %%
#Outputs:
    #tidied_sheets[0] = Total value of trade in services (including travel) in the UK by NUTS1 area and industry, 2018
    #tidied_sheets[1] = Total value of trade in services (including travel) in the UK by NUTS1 area, industry and destination, 2018
    #tidied_sheets[2] = Total value of trade in services (excluding travel) in Great Britain by NUTS2 area and industry group, 2018
    #tidied_sheets[3] = Total value of trade in services (excluding travel) in Great Britain by NUTS2 area, broad industry group and destination, 2018
    #tidied_sheets[4] = Total value of trade in services (excluding travel) in Great Britain by NUTS3 area and destination, 2018 - Trade Value
    #tidied_sheets[5] = Total value of trade in services (excluding travel) in Great Britain by NUTS3 area and destination, 2018 - EU Trade Percentage
    #tidied_sheets[6] = Total value of trade in services (excluding travel) in Great Britain by City Region and industry, 2018
    #tidied_sheets[7] = Total value of trade in services (excluding travel) in Great Britain by City Region, industry and destination, 2018
    #tidied_sheets[8] = Total value of travel-related service imports to the UK by NUTS1 area and country of origin, 2018
    #tidied_sheets[9] = Total value of trade in services in tidy format, 2018



