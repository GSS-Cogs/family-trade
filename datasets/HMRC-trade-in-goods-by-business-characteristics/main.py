# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.1.1
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

datasetTitle = scraper.title
datasetTitle

distribution = scraper.distribution(latest = True).downloadURL
distribution

tabs = {tab.name: tab for tab in scraper.distribution(title = lambda t : 'data tables' in t).as_databaker()}
list(tabs)
# tabs = {tab.name: tab for tab in distribution.as_databaker}

for name, tab in tabs.items():
    if 'Notes and Contents' in name or '5. Metadata' in name :
        continue
    datasetTitle = scraper.title
    columns = ["Flow", "Period", "Country", "Zone", "Business Size", "Age", "Industry Group", "Value", 
               "Business Count", "Employee Count", "Flow Directions", "Year", "Marker"]

    trace.start(datasetTitle, tab, columns, distribution) 

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
df['Country'].str.replace({"legacy-B5": "B5"}, inplace=True)
trace.Country("Pathified Country")

df['Zone'] = df['Zone'].apply(pathify)
df['Zone'].str.replace({"legacy-B5": "B5"}, inplace=True)
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

# +
df['Country'] = df['Country'].map({
    'belgium': 'BE', 'czech-republic': 'CZ', 'denmark': 'DK', 'france': 'FR',
    'germany': 'DE', 'republic-of-ireland': 'IE', 'italy': 'IT', 'netherlands': 'NL',
    'poland': 'PL', 'spain': 'ES', 'sweden': 'SE', 'algeria': 'DZ', 
    'australia': 'AU', 'bangladesh': 'BD', 'brazil': 'BR', 'canada': 'CA', 
    'china': 'CN', 'hong-kong': 'HK', 'india': 'IN', 'israel': 'IL', 
    'japan': 'JP', 'malaysia': 'MY', 'mexico': 'MX', 'nigeria': 'NG', 
    'norway': 'NO', 'qatar': 'QA', 'russia': 'RU', 'saudi-arabia': 'SA',
    'singapore': 'SG', 'south-africa': 'ZA', 'south-korea': 'KP', 'sri-lanka': 'LK',
    'switzerland': 'CH', 'taiwan': 'TW', 'thailand': 'TH', 'turkey': 'TR', 
    'uae': 'AE', 'united-states': 'US', 'vietnam': 'VN', 'eu': 'legacy-B5', 
    'non-eu': 'D5', 'world': 'W1'
})
df['Zone'] = df['Zone'].map({ 
    'eu': 'legacy-B5', 'non-eu': 'D5', 'world': 'W1'
})

df = df.rename(columns={'Flow Directions': "Flow", "Business Size": "Number of Employees", "Age": "Age of Business"})

df['Flow'].loc[(df['Flow'] == 'import')] = 'imports'
df['Flow'].loc[(df['Flow'] == 'export')] = 'exports'
df['Value'].loc[(df['Value'] == '')] = 0
df['Value'] = df['Value'].astype(int)
# -

desc = """
HM Revenue and Customs has linked the overseas trade statistics (OTS) trade in goods data with the Office for National Statistics (ONS) business statistics data, sourced from the Inter-Departmental Business Register (IDBR). 
These experimental statistics releases gives some expanded analyses showing overseas trade by business characteristics, which provides information about the businesses that are trading those goods. 
This release focuses on trade by industry group, age of business and size of business (number of employees) This is a collection of all experimental UK trade in goods statistics by business characteristics available on GOV.UK. 
These experimental releases are also accessible at www.uktradeinfo.com

Disclaimer
The methodology used to compute these statistics is still under development. 
All data should be considered experimental official statistics: https://webarchive.nationalarchives.gov.uk/20160106005532/http://www.ons.gov.uk/ons/guide-method/method-quality/general-methodology/guide-to-experimental-statistics/index.html

Notes

1. This data contains estimates of Trade in Goods data matched with registered businesses from the Inter-Departmental Business Register (IDBR) for exporters and importers in 2019 for a selection of countries (see Metadata tab for more information).
2. This data is now presented on a 'Special Trade' basis, in line with the change in the compilation method  for the UK Overseas Trade Statistics (OTS) - See section 3.1.1 in OTS Methodology: https://www.gov.uk/government/statistics/overseas-trade-statistics-methodologies
3. More details on the methodology used to produce these estimates and issues to be aware of when using the data can be found on the metadata tab.
4. These estimates do not cover all businesses. They do not cover:
    • Unregistered businesses (those not registered for VAT or Economic Operator Registration and Identification (EORI)).
5. Due to these experimental statistics being subject to active disclosure controls the data has been suppressed according to GSS guidance on disclosure control. 
    Suppressed cells are shown as 'Suppressed'.
7. The industry groups are based on UK Standard Industrial Classification 2007 (UK SIC 2007)
8. Information about trade in goods statistics can be found here - https://www.uktradeinfo.com/trade-data/help-with-using-our-data/help
    Information about trade the Inter-Departmental Business Register (IDBR) can be found here - https://www.ons.gov.uk/aboutus/whatwedo/paidservices/interdepartmentalbusinessregisteridbr		the ONS IDBR webpages
    Information about UK Standard Industrial Classification 2007 (UK SIC 2007) can be found here - https://www.ons.gov.uk/methodology/classificationsandstandards/ukstandardindustrialclassificationofeconomicactivities/uksic2007

Copyright
© Crown copyright 2020
This publication is licensed under the terms of the Open Government Licence v3.0
except where otherwise stated. To view this licence, visit:
nationalarchives.gov.uk/doc/open-government-licence/version/3

You may re-use this document/publication free of charge in any format for research,
private study or internal circulation within an organisation. You must re-use it accurately
and not use it in a misleading context. The material must be acknowledged as Crown
copyright and you must give the title of the source document / publication.

Where we have identified any third party copyright information you will need to obtain
permission from the copyright holders concerned.

Any enquiries regarding this publication should be sent to:
uktradeinfo@hmrc.gov.uk

Contact Details

HM Revenue and Customs
Alexander House
21 Victoria Avenue
Southend on Sea
SS99 1AA

Email: uktradeinfo@hmrc.gov.uk

Telephone: +44 (0) 3000 594250
"""

scraper.dataset.description = ""
scraper.dataset.comment = """
HM Revenue and Customs has linked the overseas trade statistics (OTS) trade in goods data with the Office for National Statistics (ONS) business statistics data, sourced from the Inter-Departmental Business Register (IDBR). 
These experimental statistics releases gives some expanded analyses showing overseas trade by business characteristics, which provides information about the businesses that are trading those goods. 
This release focuses on trade by industry group, age of business and size of business (number of employees) This is a collection of all experimental UK trade in goods statistics by business characteristics available on GOV.UK. 
These experimental releases are also accessible at www.uktradeinfo.com
"""

with pd.option_context('float_format', '{:f}'.format):
    print(df)

cubes.add_cube(scraper, df.drop_duplicates(), datasetTitle)
cubes.output_all()

trace.render("spec_v1.html")

# +
#for c in df.columns:
#    if (c not in ['Business Count','Employee Count','Value']):
#        print(c)
#        print(df[c].unique())
#        print("###############################################################")

# +
#'UK trade in goods by business characteristics 2019 - data tables'
# -









