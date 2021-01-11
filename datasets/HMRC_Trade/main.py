# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
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

# +
from gssutils import *
import json 
import requests
import pandas as pd

info = json.load(open('info.json'))

scraper = Scraper(seed = 'info.json')
scraper

trace = TransformTrace()
cubes = Cubes('info.json')
# -

scraper.select_dataset(title = lambda x: x.endswith('data tables'), latest = True)
scraper
scraper.dataset.family = info["families"]

dist = scraper.distributions[1].downloadURL
dist

tabs = {tab.name: tab for tab in scraper.distribution(title = lambda t : 'data tables' in t).as_databaker()}
list(tabs)

for name, tab in tabs.items():
    if 'Notes and Contents' in name or '5. Metadata' in name :
        continue
    datasetTitle = "uk-trade-in-goods-by-business-characteristics-2019"
    columns = ["Flow", "Period", "Country", "Zone", "Business Size", "Age", "Industry Group", "Value", 
               "Business Count", "Employee Count", "Flow Directions", "Year", "Marker"]

    trace.start(datasetTitle, tab, columns, dist) 

    cell = tab.excel_ref("A1")
    
    flow = cell.fill(DOWN).is_not_blank().is_not_whitespace()
    trace.Flow("Defined from cell ref A1 down")
    
    year = cell.shift(1,0).fill(DOWN).is_not_blank().is_not_whitespace()
    trace.Period("Defined form cell ref B1 down")
    
    country = cell.shift(2,0).fill(DOWN).is_not_blank().is_not_whitespace()
    trace.Country("Defined form cell ref C1 down")
    
    zone = cell.shift(3,0).fill(DOWN).is_not_blank().is_not_whitespace()
    trace.Zone("Defined form cell ref D1 down")
    
    business_size = cell.shift(4,0).fill(DOWN).is_not_blank().is_not_whitespace()
    trace.Business_Size("Defined form cell ref E1 down")
    
    age = cell.shift(5,0).fill(DOWN).is_not_blank().is_not_whitespace()
    trace.Age("Defined form cell ref F1 down")
    
    industry_group = cell.shift(6,0).fill(DOWN).is_not_blank().is_not_whitespace()
    trace.Industry_Group("Defined form cell ref G1 down")
    
    observations = cell.shift(7,0).fill(DOWN).is_not_blank().is_not_whitespace()
    
    business_count = cell.shift(8,0).fill(DOWN).is_not_blank().is_not_whitespace()
    trace.Business_Count("Defined form cell ref I1 down")
    
    employee_count = cell.shift(9,0).fill(DOWN).is_not_blank().is_not_whitespace()
    trace.Employee_Count("Defined form cell ref J1 down")

    dimensions = [
        HDim(flow, 'Flow', DIRECTLY, LEFT),
        HDim(year, 'Period', DIRECTLY, LEFT),
        HDim(country, 'Country', DIRECTLY, LEFT),
        HDim(zone, 'Zone', DIRECTLY, LEFT),
        HDim(business_size, 'Business Size', DIRECTLY, LEFT),
        HDim(age, 'Age', DIRECTLY, LEFT),
        HDim(industry_group, 'Industry Group', DIRECTLY, LEFT),
        HDim(business_count, 'Business Count', DIRECTLY, RIGHT),
        HDim(employee_count, 'Employee Count', DIRECTLY, RIGHT),
    ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    savepreviewhtml(tidy_sheet, fname = tab.name+ "Preview.html")
    trace.with_preview(tidy_sheet)
    trace.store("combined_dataframe", tidy_sheet.topandas())
df = trace.combine_and_trace(datasetTitle, "combined_dataframe")
df

df.rename(columns= {'OBS':'Value', 'Period':'Year', 'Flow':'Flow Directions', 'DATAMARKER':'Marker'}, inplace = True)

df['Flow Directions'] = df['Flow Directions'].apply(pathify)
trace.Flow_Directions("Renamed Flow to Flow Directions")

df['Country'] = df['Country'].apply(pathify)
trace.Country("Pathified Country")

df['Zone'] =df['Zone'].apply(pathify)
trace.Zone("Pathified Zone")

df['Business Size'] = df['Business Size'].apply(pathify)
trace.Business_Size("Pathified Business_Size")

df['Age'] = df['Age'].apply(pathify)
trace.Age("Pathified Age")

df['Industry Group'] = df['Industry Group'].apply(pathify)
trace.Industry_Group("Pathified Industry Group")


def left(s,amount):
    return s[:amount]
def right(s,amount):
    return s[-amount:]
def date_time(date):
    if len(date) == 5:
        return 'year/' + left(date, 4)
df['Year'] = df['Year'].astype(str).replace('\.', '', regex=True)
df['Year'] = df['Year'].apply(date_time)
trace.Year("Formating to be year/2019")

with pd.option_context('float_format', '{:f}'.format):
    print(df)

cubes.add_cube(scraper, df.drop_duplicates(), "uk-trade-in-goods-by-business-characteristics-2019")
cubes.output_all()

trace.render("spec_v1.html")
