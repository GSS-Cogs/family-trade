# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.7
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
from gssutils import * 
import json 

info = json.load(open('info.json')) 
metadata = Scraper(seed="info.json")
# metadata  
# -

distribution = metadata.distribution(latest=True)
title = distribution.title
tabs = { tab.name: tab for tab in distribution.as_databaker() }
# distribution

# +
# tab = [tab for name, tab in tabs.items()]
# -

total_tabs = {tab_name for tab_name in tabs}
total_tabs

tabs_to_transform =['8. Travel', '9. Tidy format']

if len(set(tabs_to_transform)-(total_tabs)) != 2:
    raise ValueError(f"Aborting. A tab named{set(tabs_to_transform)-(total_tabs)} required but not found")

for name, tab in tabs.items():
    print(name)

tidied_sheets =[]

tab = tabs["8.Travel"]
footer = tab.filter(contains_string("Sources: UK Trade; International Passenger Survey")).expand(DOWN)
year = tab.filter(contains_string("Total value of travel"))
nuts1_area = tab.filter("NUTS1 area").fill(DOWN).is_not_blank().is_not_whitespace()-footer
travel_type = tab.filter("Personal travel-related").expand(RIGHT).is_not_blank().is_not_whitespace()
origin = tab.filter("EU").expand(RIGHT).is_not_blank().is_not_whitespace()
includes_travel = 'includes-travel'
industry_grouping = 'travel-related-trade'
flow = 'imports'
observations = nuts1_area.waffle(origin)
dimensions = [
    HDim(year, "Period", CLOSEST, LEFT),
    HDim(nuts1_area, "Location", CLOSEST, ABOVE),
    HDim(travel_type, "Travel Type", CLOSEST, LEFT),
    HDim(origin, "Origin", DIRECTLY, ABOVE),
    HDimConst("Includes Travel", includes_travel),
    HDimConst("Industry Grouping", industry_grouping),
    HDimConst("Flow", flow),
    ]
tidy_sheet = ConversionSegment(tab, dimensions, observations)
# savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
tidied_sheets.append(tidy_sheet.topandas())


tab = tabs["9.Tidy format"]
year = tab.filter(contains_string("Total value of trade"))
nuts_level = tab.filter(contains_string("ITL level")).fill(DOWN).is_not_blank().is_not_whitespace()
nuts_code = tab.filter("ITL code").fill(DOWN).is_not_blank().is_not_whitespace()
nuts_area_name = tab.filter("ITL name").fill(DOWN).is_not_blank().is_not_whitespace()
flow_direction = tab.filter("Direction of trade").fill(DOWN).is_not_blank().is_not_whitespace()
origin = tab.filter("Country destination").fill(DOWN).is_not_blank().is_not_whitespace()
industry_grouping = tab.filter("Industry").fill(DOWN).is_not_blank().is_not_whitespace()
observations = tab.filter("Value").fill(DOWN).is_not_blank().is_not_whitespace()
dimensions = [
    HDim(year, "Period", CLOSEST, LEFT),
    HDim(nuts_code, "Location", DIRECTLY, LEFT),
    HDim(nuts_level, "nuts_level", DIRECTLY, LEFT),
    HDim(nuts_area_name, "nuts_area_name", DIRECTLY, LEFT),
    HDim(flow_direction, "Flow", DIRECTLY, LEFT),
    HDim(origin, "Origin", DIRECTLY, LEFT),
    HDim(industry_grouping, "Industry Grouping", DIRECTLY, LEFT)
    ]
tidy_sheet = ConversionSegment(tab, dimensions, observations)
# savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
tidied_sheets.append(tidy_sheet.topandas())

df = pd.concat(tidied_sheets, sort = True).fillna('')

df['Travel Type'] = df.apply(lambda x: 'total' if (x['nuts_level'] == 'NUTS1' and x['Industry Grouping'] == 'Travel') else 'not-applicable', axis = 1)
df['Includes Travel'] = df['nuts_level'].map(lambda x: 'includes-travel' if 'NUTS1' in x else 'excludes-travel')
df['Location'] = df.apply(lambda x: 'http://data.europa.eu/nuts/code/' + x['Location'] if x['Location'] != 'N/A' else x['Location'], axis = 1) 
df['Location'] = df.apply(lambda x: 'http://data.europa.eu/nuts/code/UK' if (x['Location'] == 'N/A' and x['nuts_area_name'] == 'United Kingdom') else x['Location'], axis = 1)
df['Location'] = df.apply(lambda x: x['nuts_area_name'] if x['Location'] == 'N/A' else x['Location'], axis = 1)
df = df.drop(['nuts_level', 'nuts_area_name'], axis=1)

df.rename(columns= {'OBS':'Value', 'DATAMARKER' : 'Marker'}, inplace=True)
df['Marker'] = df['Marker'].replace('..', 'suppressed')
df["Marker"] = df["Marker"].str.replace("n/a", "not-applicable")
df["Flow"] = df["Flow"].str.replace("imports", "Imports")
df["Period"]= df["Period"].str.split(",", n = 1, expand = True)[1]
df['Period'] = df['Period'].str.strip()
df['Period'] = df.apply(lambda x: 'year/' + x['Period'], axis = 1)

df['Origin'] = df['Origin'].replace({'Rest of the World': 'Rest of world'})

df = df.replace({'Location' : {'North East' : 'http://data.europa.eu/nuts/code/UKC',
                                'North West' : 'http://data.europa.eu/nuts/code/UKD',
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
                                'UK' : 'http://data.europa.eu/nuts/code/UK',
                                'Cambridgeshire and Peterborough Combined Authority' : 'http://statistics.data.gov.uk/id/statistical-geography/E47000008',
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
                                'West of England Combined Authority' : 'http://statistics.data.gov.uk/id/statistical-geography/E47000009'},
                 'Travel Type' : {'Business travel-related' : 'business',
                                  'Personal travel-related' : 'personal',
                                  'Total travel-related' : 'total'},
                
                'Origin' : {'Total': 'All countries',
                            'Rest of the World': 'Rest of world'},
                 
                'Industry Grouping' : {'travel': 'travel-related-trade', 'Travel' : 'travel-related-trade'}
                })

df.to_csv("observations.csv", index = False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')
