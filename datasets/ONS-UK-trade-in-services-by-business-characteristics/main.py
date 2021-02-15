# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
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

# +
from gssutils import *
import json
import numpy as np

trace = TransformTrace()
df = pd.DataFrame()
cubes = Cubes("info.json")
info = json.load(open('info.json'))
scraper = Scraper(seed = 'info.json')
scraper
# -

distribution = scraper.distribution(latest = True)
title = distribution.title
tabs = { tab.name: tab for tab in distribution.as_databaker() }

for name, tab in tabs.items():
    datasetTitle = title
    columns=['Period','Business Size','Ownership', 'Country','Industry', 'Flow', 'Measure type', 'Unit', 'Marker']
    trace.start(datasetTitle, tab, columns, distribution.downloadURL)
    
    period = tab.name[0:4]
    trace.Period("Taken from tab name")
        
    if 'Contents' in name:
        continue   
    elif len(tab.name) > 4:
        
        country = 'World'
        trace.Country("Hardcodded as World")
        
        #Ownership
        industry = tab.excel_ref('A2').expand(DOWN)
        trace.Industry("Taken from columnns with title Industry down. A2 Down")
        flow = tab.excel_ref('C1').expand(RIGHT) - tab.excel_ref('E1').expand(RIGHT) 
        trace.Flow("Taken from headers Exports £m or Imports £m")
        ownership = tab.filter(contains_string('Ownership')).shift(0,1).expand(DOWN)
        trace.Ownership("Ownership taken from colum headed Ownership down")
        business_size = 'all'
        trace.Business_Size("Hardcodded as All")
        observations_ownership = (tab.excel_ref('C1').expand(RIGHT) - tab.excel_ref('E1').expand(RIGHT)).fill(DOWN).is_not_blank()
        
        dimensions = [
            HDimConst("Period", period),
            HDimConst("Business size", business_size),
            HDimConst("Country", country),
            HDim(industry,'Industry',DIRECTLY,LEFT),
            HDim(flow, 'Flow',CLOSEST,LEFT),
            HDim(ownership,'Ownership',DIRECTLY,LEFT),
        ]
        tidy_sheet = ConversionSegment(tab, dimensions, observations_ownership)   
        trace.with_preview(tidy_sheet)
        trace.store("combined_dataframe", tidy_sheet.topandas())
        
        #Business Size
        industry = tab.excel_ref('F2').expand(DOWN)
        trace.Industry("Taken from columnns with title Industry down. F2 Down")
        flow = tab.excel_ref('H1').expand(RIGHT)
        trace.Flow("Taken from headers Exports £m or Imports £m")
        business_size = tab.filter(contains_string('Business Size')).shift(0,1).expand(DOWN)
        trace.Business_Size("Taken from colum headed Business Size down")
        ownership = 'any'
        trace.Ownership("Hardcodded as Any")
        observations_business_size = (tab.excel_ref('H1').expand(RIGHT)).fill(DOWN).is_not_blank()
        dimensions = [
            HDimConst("Period", period),
            HDimConst("Ownership", ownership),
            HDimConst("Country", country),
            HDim(industry,'Industry',DIRECTLY,LEFT),
            HDim(flow, 'Flow',DIRECTLY,ABOVE),
            HDim(business_size,'Business size',DIRECTLY,LEFT),
        ]
        tidy_sheet = ConversionSegment(tab, dimensions, observations_business_size)   
        trace.with_preview(tidy_sheet)
        trace.store("combined_dataframe", tidy_sheet.topandas())
        
    elif len(tab.name) == 4:
        country = tab.filter(contains_string('Country')).shift(0,1).expand(DOWN).is_not_blank()
        trace.Country("Taken from columns with header Country : A11 Down. The first box in tab will have world as country value.")
        business_size = tab.filter(contains_string('Business Size')).shift(0,1).expand(DOWN) - country
        trace.Business_Size("Taken from columns with header Buiness Size :B2 Down and B11 Down. The second second box on the tab will have any as the business size value")            
        ownership = tab.filter(contains_string('Ownership')).shift(0,1).expand(DOWN) - business_size
        trace.Ownership("Taken from columns with header Ownership :A2 Down and B21 Down. The second 3rd box on the tab will have any as the Ownership value")            
        flow = tab.expand(DOWN).one_of(['Exports £m','Imports £m'])
        trace.Flow("Taken from headers Exports £m or Imports £m")
        industry = "all"
        trace.Industry("Hardcodded as all")
        observations = flow.fill(DOWN).is_not_blank() - flow
        
        dimensions = [
            HDimConst("Period", period),
            HDimConst("Industry", industry),
            HDim(flow, 'Flow',DIRECTLY,ABOVE),
            HDim(business_size, 'Business size',CLOSEST,ABOVE),
            HDim(ownership, 'Ownership',CLOSEST,ABOVE),
            HDim(country, 'Country',CLOSEST,ABOVE),
        ]
        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        trace.with_preview(tidy_sheet)
        trace.store("combined_dataframe", tidy_sheet.topandas())
    else:   
        continue


# +
#Post Processing 
df = trace.combine_and_trace(datasetTitle, "combined_dataframe")
df.rename(columns={'OBS' : 'Value','DATAMARKER' : 'Marker'}, inplace=True)
df['Marker'].replace('..', 'suppressed', inplace=True)
trace.Marker("Formatting .. to equal suppressed")
df['Period'] =  'year/' + df['Period']
trace.Period("Formatting to year/0000")
df['Business size'].replace('Country', 'any', inplace=True)
df['Ownership'].replace('Business Size', 'any', inplace=True)
df['Country'].replace(np.nan, 'World', inplace=True)
df["Flow"] = df["Flow"].map(lambda x: "exports" if x == "Exports £m" else ("imports" if x == "Imports £m" else "unknown"))
df["Business size"] = df["Business size"].map(lambda x: "0-to-49" if x == "Small (0-49)" 
                                              else ("50-to-249" if x == "Medium (50-249)" 
                                                    else ("250" if x == "Large (250+)" 
                                                          else ("unknown-employees" if x == "Unknown" else "any"))))   
df["Ownership"] = df["Ownership"].map(lambda x: "uk" if x == "Domestic" 
                                                         else ("foreign" if x == "Foreign" 
                                                               else ("unknown" if x == "Unknown" else "any")))                                                          

df['Country'] = df['Country'].apply(lambda x: 'WW' if 'World' in x else 
                                      ('RW' if 'Non-EU' in x else 
                                       ('EU' if 'Total EU28' in x else x)))

df['Value'] = pd.to_numeric(df['Value'], errors='coerce').astype('Int64')
df['Industry']= df['Industry'].str.split(" ", n = 1, expand = True) 

df = df[['Period', 'Business size', 'Country', 'Ownership', 'Industry', 'Flow', 'Value', 'Marker']]
# -

#additional scraper info needed
comment = "Trade in goods data, including breakdown of imports and exports by Standard Industrial Classification, region (EU and non-EU), business size and by domestic and foreign ownership."
des = """
Trade in goods data, including breakdown of imports and exports by Standard Industrial Classification, region (EU and non-EU), business size and by domestic and foreign ownership.

Users should note the following:
Industry data has been produced using Standard Industrial Classification 2007 (SIC07).

Business size is defined using the following employment size bands:
   Small - 0-49 employees
   Medium - 50-249 employees
   Large - 250+ employees
   Unknown - number of employees cannot be determined via IDBR
   
Ownership status is defined as:
   Domestic - ultimate controlling parent company located in the UK
   Foreign - ultimate controlling parent company located outside the UK
   Unknown - location of ultimate controlling parent company cannot be determined via IDBR

Some data cells have been suppressed to protect confidentiality so that individual traders cannot be identified.

Data
All data is in £ million, current prices

Rounding
Some of the totals within this release (e.g. EU, Non EU and world total) may not exactly match data published via other trade releases due to small rounding differences.

Trade Asymmetries 
These data are our best estimate of these bilateral UK trade flows. Users should note that alternative estimates are available, in some cases, via the statistical agencies for bilateral countries or through central databases such as UN Comtrade

"""
scraper.dataset.description = des
scraper.dataset.comment = comment
scraper.dataset.title = datasetTitle

df.head(10)
for c in df.columns:
    if c != "Value":
        print(c)
        print(df[c].unique())
        print("########################################################")

cubes.add_cube(scraper, df.drop_duplicates(), datasetTitle)
cubes.output_all()
trace.render("spec_v1.html")

import pandas as pd
df = pd.read_csv("out/uk-trade-in-services-by-business-characteristics.csv")
df["all_dimensions_concatenated"] = ""
for col in df.columns.values:
    if col != "Value":
        df["all_dimensions_concatenated"] = df["all_dimensions_concatenated"]+df[col].astype(str)
found = []
bad_combos = []
for item in df["all_dimensions_concatenated"]:
    if item not in found:
        found.append(item)
    else:
        bad_combos.append(item)
df = df[df["all_dimensions_concatenated"].map(lambda x: x in bad_combos)]
drop_these_cols = []
for col in df.columns.values:
    if col != "all_dimensions_concatenated" and col != "Value":
        drop_these_cols.append(col)
for dtc in drop_these_cols:
    df = df.drop(dtc, axis=1)
df = df[["all_dimensions_concatenated", "Value"]]
df = df.sort_values(by=['all_dimensions_concatenated'])
df.to_csv("duplicates_with_values.csv", index=False)
print("DONE")


