# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
from gssutils import * 
import json 

trace = TransformTrace()
df = pd.DataFrame()
cubes = Cubes("info.json")

info = json.load(open('info.json')) 
scraper = Scraper(seed="info.json")   
distribution = scraper.distribution(latest=True)
title = distribution.title
tabs = { tab.name: tab for tab in distribution.as_databaker() }
distribution
# -

# Remove all sheets except for `9. Tidy Data` and `8. Travel`.
tabs_to_transform =['8. Travel', '9. Tidy format']
for name, tab in tabs.items():
    
    columns = ["Year", "NUTS1 Area", "Travel Type", "Origin", "Includes Travel", "Industry Grouping", "Flow", "Measure Type", "Unit"]
    trace.start(title, tab, columns, distribution.downloadURL)
    
    if name in tabs_to_transform:
        #dimensions shared on both tabs
        year = tab.excel_ref('A1').is_not_blank() #Period
        trace.Year("Selected as non-blank value in cell A1 (sheet title)")
        
        if name in tabs_to_transform[0]:
            nuts1_area = tab.excel_ref("A5:A17").is_not_blank() #Location
            trace.NUTS1_Area("Selected as all non-blank values between cell refs A5 and A17")
            
            travel_type = tab.excel_ref("B3").expand(RIGHT).is_not_blank()
            trace.Travel_Type("Selected as all non-blank values from cell ref B3 going right/across.")
            
            origin = tab.excel_ref("B4").expand(RIGHT).is_not_blank()
            trace.Origin("Selected as all non-blank values from cell ref B4 going right/across.")
            
            includes_travel = 'includes-travel'
            trace.Includes_Travel('Hard coded as includes-travel')
            
            industry_grouping = 'travel-related-trade'
            trace.Industry_Grouping('Hardcoded as travel-related-trade')
            
            flow = 'imports'
            trace.Flow('Hardcoded as imports')
            
            observations = origin.fill(DOWN).is_not_blank()
            
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
            #savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
            trace.with_preview(tidy_sheet)
            trace.store("combined_df", tidy_sheet.topandas())
           
        elif name in tabs_to_transform[1]:
            nuts_level = tab.excel_ref('A5').expand(DOWN).is_not_blank() #used to determine Travel Type and Includes Travel columns 
            
            nuts_code = tab.excel_ref('B5').expand(DOWN).is_not_blank() #Location
            
            nuts_area_name = tab.excel_ref('C5').expand(DOWN).is_not_blank()
            
            industry_grouping = tab.excel_ref('D5').expand(DOWN).is_not_blank()
            
            origin = tab.excel_ref('E5').expand(DOWN).is_not_blank()
            
            flow = tab.excel_ref('F5').expand(DOWN).is_not_blank()
            
            observations = tab.excel_ref('G5').expand(DOWN).is_not_blank()
            
            dimensions = [
                HDim(year, "Period", CLOSEST, LEFT),
                HDim(nuts_code, "Location", DIRECTLY, LEFT),
                HDim(nuts_level, "nuts_level", DIRECTLY, LEFT),
                HDim(nuts_area_name, "nuts_area_name", DIRECTLY, LEFT),
                HDim(origin, "Origin", DIRECTLY, LEFT),
                HDim(industry_grouping, "Industry Grouping", DIRECTLY, LEFT),
                HDim(flow, "Flow", DIRECTLY, LEFT),
                
            ]
            tidy_sheet = ConversionSegment(tab, dimensions, observations)
            #savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
            trace.with_preview(tidy_sheet)
            tidy_sheet = tidy_sheet.topandas()
            tidy_sheet['Travel Type'] = tidy_sheet.apply(lambda x: 'total' if (x['nuts_level'] == 'NUTS1' and x['Industry Grouping'] == 'Travel') else 'na', axis = 1)
            tidy_sheet['Includes Travel'] = tidy_sheet['nuts_level'].map(lambda x: 'includes-travel' if 'NUTS1' in x else 'excludes-travel')
            tidy_sheet['Location'] = tidy_sheet.apply(lambda x: 'http://data.europa.eu/nuts/code/' + x['Location'] if x['Location'] != 'N/A' else x['Location'], axis = 1) 
            tidy_sheet['Location'] = tidy_sheet.apply(lambda x: 'http://data.europa.eu/nuts/code/UK' if (x['Location'] == 'N/A' and x['nuts_area_name'] == 'United Kingdom') else x['Location'], axis = 1)
            tidy_sheet['Location'] = tidy_sheet.apply(lambda x: x['nuts_area_name'] if x['Location'] == 'N/A' else x['Location'], axis = 1)
            tidy_sheet = tidy_sheet.drop(['nuts_level', 'nuts_area_name'], axis=1)
            trace.store("combined_df", tidy_sheet) 
    else:
        continue

df = trace.combine_and_trace(distribution.title, "combined_df")
df.rename(columns= {'OBS':'Value', 'DATAMARKER' : 'Marker'}, inplace=True)
df['Marker'] = df['Marker'].replace('..', 'suppressed')
df["Period"]= df["Period"].str.split(",", n = 1, expand = True)[1]
df['Period'] = df['Period'].str.strip()
df['Period'] = df.apply(lambda x: 'year/' + x['Period'], axis = 1)

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
                
                'Origin' : {'Total': 'all-countries',
                            'Rest of the World': 'rest-of-world'},
                 
                'Industry Grouping' : {'travel': 'travel-related-trade', 'Travel' : 'travel-related-trade'}
                })

COLUMNS_TO_NOT_PATHIFY = ['Value', 'Location', 'Period', 'Marker']
for col in df.columns.values.tolist():
    if col in COLUMNS_TO_NOT_PATHIFY:
        continue
    try:
        df[col] = df[col].apply(pathify)
    except Exception as err:
        raise Exception('Failed to pathify column "{}".'.format(col)) from err

df = df[['Period', 'Location', 'Industry Grouping', 'Origin', 'Flow', 'Travel Type', 'Includes Travel', 'Value', 'Marker']]
df


cubes.add_cube(scraper, df.drop_duplicates(), title)
cubes.output_all()
trace.render()
