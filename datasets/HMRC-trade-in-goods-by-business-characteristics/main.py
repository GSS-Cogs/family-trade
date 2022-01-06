# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# +
from gssutils import *
import json 
import requests
import pandas as pd
import numpy as np

scraper = Scraper(seed = 'info.json')
scraper
# -

info = json.load(open('info.json'))

cubes = Cubes('info.json')

scraper.select_dataset(title = lambda x: x.endswith('data tables'), latest = True)
scraper.dataset.family = info["families"]

datasetTitle = scraper.title
datasetTitle = "UK trade in goods by business characteristics - data tables"

distribution = scraper.distribution(title = lambda t : 'data tables' in t, latest = True)
distribution

tabs = {tab.name: tab for tab in scraper.distribution(title = lambda t : 'data tables' in t).as_databaker()}
list(tabs)

tidied_sheets = []

for name, tab in tabs.items():
    if 'Notes and Contents' in name or '5. Metadata' in name :
        continue
    
    cell = tab.excel_ref("A1")
    flow = tab.filter(contains_string("Flow")).fill(DOWN).is_not_blank().is_not_whitespace()
    
   # year = tab.filter(contains_string("Year")).fill(DOWN).is_not_blank().is_not_whitespace()
   # savepreviewhtml(year, fname = tab.name+ "Preview.html")
    
    year = cell.shift(1,3).expand(DOWN).is_not_blank().is_not_whitespace()
    
    country = tab.filter(contains_string("Country")).fill(DOWN).is_not_blank().is_not_whitespace()
    zone = tab.filter(contains_string("Zone")).fill(DOWN).is_not_blank().is_not_whitespace()
    business_size = tab.filter(contains_string("Business Size")).fill(DOWN).is_not_blank().is_not_whitespace()
    age = tab.filter(contains_string("Age (Years)")).fill(DOWN).is_not_blank().is_not_whitespace()
    industry_group = tab.filter(contains_string("Industry Group")).fill(DOWN).is_not_blank().is_not_whitespace()
    business_count = tab.filter(contains_string("Business Count")).fill(DOWN).is_not_blank().is_not_whitespace()
    employee_count = tab.filter(contains_string("Employee Count")).fill(DOWN).is_not_blank().is_not_whitespace()
    
    
    observations = cell.shift(7,2).fill(DOWN).is_not_blank().is_not_whitespace()
    
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
    #savepreviewhtml(tidy_sheet, fname = tab.name+ "Preview.html")
    tidied_sheets.append(tidy_sheet.topandas())

df = pd.concat(tidied_sheets, sort = True)

df.rename(columns= {'OBS':'Value', 'Period':'Year', 'Flow':'Flow Directions', 'DATAMARKER':'Marker'}, inplace = True)

df['Flow Directions'] = df['Flow Directions'].apply(pathify)


# +
df['Country'] = df['Country'].apply(pathify)

#df['Country'].unique()
# -


df['Zone'] = df['Zone'].apply(pathify)

df['Business Size'] = df['Business Size'].apply(pathify)

df['Age'] = df['Age'].apply(pathify)

df['Industry Group'] = df['Industry Group'].apply(pathify)

df["Employee Count"] = df["Employee Count"].apply(lambda x: str(x).split(".")[0])
df["Business Count"] = df["Business Count"].apply(lambda x:str(x).split(".")[0])

df['Marker'] = df['Marker'].replace('Suppressed', 'suppressed', regex=True)


def left(s,amount):
    return s[:amount]
def right(s,amount):
    return s[-amount:]
def date_time(date):
    if len(date) == 5:
        return 'year/' + left(date, 4)
df['Year'] = df['Year'].astype(str).replace('\.', '', regex=True)
df['Year'] = df['Year'].apply(date_time)

df['Country'] = df['Country'].map({
    'belgium': 'BE', 'czech-republic': 'CZ', 'denmark': 'DK', 'france': 'FR',
    'germany': 'DE', 'republic-of-ireland': 'IE', 'ireland' : 'IE', 'italy': 'IT', 'netherlands': 'NL',
    'poland': 'PL', 'spain': 'ES', 'sweden': 'SE', 'algeria': 'DZ', 
    'australia': 'AU', 'bangladesh': 'BD', 'brazil': 'BR', 'canada': 'CA', 
    'china': 'CN', 'hong-kong': 'HK', 'india': 'IN', 'israel': 'IL', 
    'japan': 'JP', 'malaysia': 'MY', 'mexico': 'MX', 'nigeria': 'NG', 
    'norway': 'NO', 'qatar': 'QA', 'russia': 'RU', 'saudi-arabia': 'SA',
    'singapore': 'SG', 'south-africa': 'ZA', 'south-korea': 'KP', 'sri-lanka': 'LK',
    'switzerland': 'CH', 'taiwan': 'TW', 'thailand': 'TH', 'turkey': 'TR', 
    'uae': 'AE', 'united-states': 'US', 'vietnam': 'VN', 'eu': 'B5', 
    'non-eu': 'D5', 'world': 'W1'
})

df['Zone'] = df['Zone'].map({ 
    'eu': 'B5', 'non-eu': 'D5', 'world': 'W1'
})

df = df.rename(columns={'Flow Directions': "Flow", "Business Size": "Number of Employees", "Age": "Age of Business"})

df['Flow'].loc[(df['Flow'] == 'import')] = 'imports'
df['Flow'].loc[(df['Flow'] == 'export')] = 'exports'
df['Value'].loc[(df['Value'] == '')] = 0
df['Value'] = df['Value'].astype(int)

scraper.dataset.comment = 'UK trade in goods by business characteristics data details international trade in goods by industry, age and size of business'

scraper.dataset.description = """HM Revenue and Customs has linked the overseas trade statistics (OTS) trade in goods data with the Office for National Statistics (ONS) business statistics data, sourced from the Inter-Departmental Business Register (IDBR). These experimental statistics releases gives some expanded analyses showing overseas trade by business characteristics, which provides information about the businesses that are trading those goods. This release focuses on trade by industry group, age of business and size of business (number of employees) This is a collection of all experimental UK trade in goods statistics by business characteristics available on GOV.UK.
"""

cubes.add_cube(scraper, df.drop_duplicates(), datasetTitle)
cubes.output_all()
