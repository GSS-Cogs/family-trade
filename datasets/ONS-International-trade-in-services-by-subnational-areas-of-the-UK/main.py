# %%
from gssutils import * 
import json 

metadata = Scraper(seed='info.json')
distribution = metadata.distribution(latest = True)

# %%
tabs = { tab.name: tab for tab in distribution.as_databaker() }
tabs_to_transform =['8.Travel', '9.Tidy format']
tidied_sheets =[]
for name, tab in tabs.items():
    if name in tabs_to_transform:
        year = tab.excel_ref('A1').is_not_blank() #Period
        
        if name in tabs_to_transform[0]:#8.Travel
            nuts1_area = tab.excel_ref("A5:A17").is_not_blank() #Location
            travel_type = tab.excel_ref("B3").expand(RIGHT).is_not_blank()
            origin = tab.excel_ref("B4").expand(RIGHT).is_not_blank()
            observations = origin.fill(DOWN).is_not_blank()
            
            dimensions = [
                HDim(year, "Period", CLOSEST, LEFT),
                HDim(nuts1_area, "Location", CLOSEST, ABOVE),
                HDim(travel_type, "Travel Type", CLOSEST, LEFT),
                HDim(origin, "Origin", DIRECTLY, ABOVE),
                HDimConst("Includes Travel", "includes-travel"), #constant 
                HDimConst("Industry Grouping", "travel-related-trade"),#constant
                HDimConst("Flow", "imports"),#constant
            ]
            tidy_sheet = ConversionSegment(tab, dimensions, observations)
            tidy_sheet = tidy_sheet.topandas() #117 rows × 8 columns
            tidied_sheets.append(tidy_sheet)
            
        elif name in tabs_to_transform[1]:
            
            nuts_level = tab.excel_ref('A4').expand(DOWN).is_not_blank() #used to determine Travel Type and Includes Travel columns 
            nuts_code = tab.excel_ref('B4').expand(DOWN).is_not_blank() #Location
            nuts_area_name = tab.excel_ref('C4').expand(DOWN).is_not_blank()
            flow = tab.excel_ref('D4').expand(DOWN).is_not_blank()
            origin = tab.excel_ref('E4').expand(DOWN).is_not_blank()
            industry_grouping = tab.excel_ref('F4').expand(DOWN).is_not_blank()         
            observations = tab.excel_ref('G4').expand(DOWN).is_not_blank() 
            
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
            tidy_sheet = tidy_sheet.topandas() #9033 rows × 9 columns
            
            #TIDY UP 9.TIDY FORMAT
            tidy_sheet['Travel Type'] = tidy_sheet.apply(lambda x: 'total' if (x['nuts_level'] == 'NUTS1' and x['Industry Grouping'] == 'Travel') else 'na', axis = 1)
            tidy_sheet['Includes Travel'] = tidy_sheet['nuts_level'].map(lambda x: 'includes-travel' if 'NUTS1' in x else 'excludes-travel')
            tidy_sheet['Location'] = tidy_sheet.apply(lambda x: 'http://data.europa.eu/nuts/code/' + x['Location'] if x['Location'] != 'N/A' else x['Location'], axis = 1) 
            tidy_sheet['Location'] = tidy_sheet.apply(lambda x: 'http://data.europa.eu/nuts/code/UK' if (x['Location'] == 'N/A' and x['nuts_area_name'] == 'United Kingdom') else x['Location'], axis = 1)
            tidy_sheet['Location'] = tidy_sheet.apply(lambda x: x['nuts_area_name'] if x['Location'] == 'N/A' else x['Location'], axis = 1)
            tidy_sheet = tidy_sheet.drop(['nuts_level', 'nuts_area_name'], axis=1)
            tidied_sheets.append(tidy_sheet) 

# %%
df = pd.concat(tidied_sheets, sort = True).fillna('') #9150 rows × 9 columns
df.rename(columns= {'OBS':'Value', 'DATAMARKER' : 'Marker'}, inplace=True)
df['Marker'] = df['Marker'].replace('..', 'suppressed')
df["Period"]= df["Period"].str.split(",", n = 1, expand = True)[1]
df['Period'] = df['Period'].str.strip()

df['Flow'] = df['Flow'].apply(pathify)

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

df = df[['Period', 'Location', 'Industry Grouping', 'Origin', 'Flow', 'Travel Type', 'Includes Travel', 'Value', 'Marker']]
df = df.drop_duplicates() #remove valid duplicates, total appears in both tabs with same values. 
# %%
df.to_csv("observations.csv", index = False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')
