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
# -

distribution = metadata.distribution(latest=True)
title = distribution.title
tabs = { tab.name: tab for tab in distribution.as_databaker() }

total_tabs = {tab_name for tab_name in tabs}

tabs_to_transform =['8. Travel', '9. Tidy format']

if len(set(tabs_to_transform)-(total_tabs)) != 2:
    raise ValueError(f"Aborting. A tab named{set(tabs_to_transform)-(total_tabs)} required but not found")

tidied_sheets =[]

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
df = ConversionSegment(tab, dimensions, observations)
# savepreviewhtml(df, fname=tab.name + "Preview.html")
df = df.topandas()


# +

df['Travel Type'] = df.apply(lambda x: 'total' if (x['nuts_level'] == 'NUTS1' and x['Industry Grouping'] == 'Travel') else 'not-applicable', axis = 1)
df['Includes Travel'] = df.apply(lambda x: 'includes-travel' if x['nuts_level'] == 'NUTS1' else 'excludes-travel', axis = 1) 
df['Location'] = df.apply(lambda x: 'UK' if (x['Location'] == 'N/A' and x['nuts_area_name'] == 'United Kingdom') else x['Location'], axis = 1)
df = df.drop(['nuts_level', 'nuts_area_name'], axis=1)
# -

tidied_sheets.append(df)

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
    HDimConst("Flow", flow)
    ]
tidy_sheet = ConversionSegment(tab, dimensions, observations)
# savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
tidy_sheet = tidy_sheet.topandas()

tidied_sheets.append(tidy_sheet)

df = pd.concat(tidied_sheets, sort = True).fillna('')

df.rename(columns= {'OBS':'Value', 'DATAMARKER' : 'Marker'}, inplace=True)
df['Marker'] = df['Marker'].replace('..', 'suppressed')
df["Marker"] = df["Marker"].str.replace("n/a", "not-applicable")
df["Flow"] = df["Flow"].str.replace("imports", "Imports")
df["Period"]= df["Period"].str.split(",", n = 1, expand = True)[1]
df['Period'] = df['Period'].str.strip()
df['Includes Travel'] = df['Includes Travel'].str.title()
df['Travel Type'] = df['Travel Type'].str.title()
df['Period'] = df.apply(lambda x: 'year/' + x['Period'], axis = 1)

df['Origin'] = df['Origin'].replace({'Rest of the World': 'Rest of world'})

df = df.replace({'Location' : {'North East' : 'UKC',
                                'North West' : 'UKD',
                                'Yorkshire and The Humber' : 'UKE',
                                'East Midlands' : 'UKF',
                                'West Midlands' : 'UKG',
                                'East of England' : 'UKH',
                                'London' : 'UKI',
                                'South East' : 'UKJ',
                                'South West ' : 'UKK',
                                'Wales' : 'UKL',
                                'Scotland' : 'UKM',
                                'Northern Ireland' : 'UKN',
                                'UK' : 'UK',
                                'N/A': 'Not-applicable'},

                 'Travel Type' : {'Business travel-related' : 'business',
                                  'Personal travel-related' : 'personal',
                                  'Total travel-related' : 'total'},
                
                'Origin' : {'Total': 'All countries',
                            'Rest of the World': 'rest-of-world'},
                 
                'Industry Grouping' : {'travel': 'travel-related-trade', 'Travel' : 'travel-related-trade', 'All Industries' : 'All industries'}
                })

df = df[['Flow', 'Period', 'Includes Travel', 'Industry Grouping', 'Travel Type', 
        'Origin', 'Location', 'Value', 'Marker']]

# Output - 1
# With respect to "Value", if there are duplicate rows(same value in all the DataFrame columns), keep the first occurance and drop all other duplicate rows
# Output is a dataframe with no duplicates
# Same as output-2
df.drop_duplicates(subset = df.columns.difference(['Value']), inplace = True)

# +
# df
# -

# see if there are any duplicates in Dataframe after droping the duplicates. There shouln't be anything as the duplicates are already dropped
duplicate_df = df[df.duplicated(['Flow', 'Period', 'Includes Travel', 'Industry Grouping', 'Travel Type',
       'Origin', 'Location', 'Value', 'Marker'], keep = False)]
duplicate_df


# Output - 2
# This function compares to drop duplicates from the DataFrame(df) without duplicates and DataFrame with duplicates if we have one(duplicate_df:-empty as of now)
# We have achieved already what is wanted, this step is to reiterate in another way that there are no duplicates and the out put of both the methods are same
# Same as output - 1
def dataframe_difference(df1: df, df2: df, which=None):
    """Find rows which are different between two DataFrames."""
    comparison_df = df1.merge(
        df2,
        indicator=True,
        how='outer'
    )
    if which is None:
        diff_df = comparison_df[comparison_df['_merge'] != 'both']
    else:
        diff_df = comparison_df[comparison_df['_merge'] == which]
    diff_df.drop(columns=['_merge'],axis = 1, inplace = True)
    return diff_df


df = dataframe_difference(df, duplicate_df)

# +
# This should be same as droping the duplicate rows with respect to column "Value" or same as output - 1
# df
# -

df.to_csv("observations.csv", index = False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')
