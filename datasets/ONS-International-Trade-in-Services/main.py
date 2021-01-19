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


info = json.load(open("info.json"))
scraper = Scraper(seed = "info.json")
cubes = Cubes("info.json")
trace = TransformTrace()

scraper
# -

tabs = {tab.name: tab for tab in scraper.distribution(latest = True, mediaType = Excel).as_databaker()}

distribution = scraper.distribution(latest = True)
datasetTitle = distribution.title
columns = ["Period", "Flow", "Continent", "Country", "Industry Origin", "Industry", "Industry Total", "Marker", "Flow Directions"]

for name, tab in tabs.items():
    if 'Table A0' in tab.name or 'Table B1' in tab.name or 'Table B3' in tab.name or 'Table D1' in tab.name or 'Table D2' in tab.name:
#         continue
#         print(tab.name)
        trace.start(datasetTitle, tab, columns,distribution.downloadURL)
        cell = tab.excel_ref("A5")
        
        observations = cell.shift(4, 0).expand(DOWN).expand(RIGHT).is_not_blank().is_not_whitespace()

        period = cell.shift(0, -1).expand(RIGHT).is_not_blank().is_not_whitespace()
        trace.Period("Defined from cell ref E4 right which is not blank")

        flow = cell.shift(0, -2).expand(RIGHT).is_not_blank().is_not_whitespace()
        trace.Flow("Defined from cell ref E3 right which is not blank")
        
        continent = cell.expand(DOWN).is_not_blank().is_not_whitespace()
        trace.Continent("Defined form cell ref A5 and down which is not blank")

        country = cell.shift (2, 0).expand(DOWN).is_not_blank()
        trace.Country("Defined from cell ref C7 and down which is not blank")
        
        dimensions =[
            HDim(period, "Period", DIRECTLY, ABOVE),
            HDim(flow, "Flow", CLOSEST, LEFT),
            HDim(continent, "Continent", CLOSEST, ABOVE),
            HDim(country, "Country", CLOSEST, ABOVE),
        ]
        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        savepreviewhtml(tidy_sheet, fname = tab.name + "Preview.html")
        trace.with_preview(tidy_sheet)
trace.store("combined_dataframe", tidy_sheet.topandas())

# +
tab = tabs["Table B2"]
trace.start(datasetTitle, tab, columns,distribution.downloadURL)

cell = tab.excel_ref("A5")

observations = cell.shift(3, 0).expand(DOWN).expand(RIGHT).is_not_blank().is_not_whitespace()

period = cell.shift(0, -1).expand(RIGHT).is_not_blank().is_not_whitespace()
trace.Period("Defined from cell ref E4 right which is not blank")

flow = cell.shift(0, -2).expand(RIGHT).is_not_blank().is_not_whitespace()
trace.Flow("Defined from cell ref E3 right which is not blank")

continent = cell.expand(DOWN).is_not_blank().is_not_whitespace()   
trace.Continent("Defined form cell ref A5 and down which is not blank")

country = cell.shift (2, 0).expand(DOWN).is_not_blank()
trace.Country("Defined from cell ref C7 and down which is not blank")
        
dimensions =[
    HDim(period, "Period", DIRECTLY, ABOVE),
    HDim(flow, "Flow", CLOSEST, LEFT),
    HDim(continent, "Continent", CLOSEST, ABOVE),
    HDim(country, "Country", CLOSEST, ABOVE),
]
tidy_sheet = ConversionSegment(tab, dimensions, observations)
savepreviewhtml(tidy_sheet, fname = tab.name + "Preview.html")
trace.with_preview(tidy_sheet)
trace.store("combined_dataframe", tidy_sheet.topandas())
# -

for name, tab in tabs.items():
    if 'Table C1 2009-2012'in name or 'Table C1 2013-2018' \
    in name or'Table C2 2009-2012' in name or 'Table C2 2013-2018' \
    in name or 'Table C3 2009-2012' in name or 'Table C3 2013-2018'\
    in name or 'Table C4 2009-2012' in name or 'Table C5 2009-2012'\
    in name or 'Table C6 2009-2012' in name or 'Table C7 2009-2012' in name:
        
            trace.start(datasetTitle, tab, columns,distribution.downloadURL)
            cell = tab.excel_ref("A5")

            observations = cell.shift(4, 0).expand(DOWN).expand(RIGHT).is_not_blank().is_not_whitespace()

            period = cell.shift(0, -1).expand(RIGHT).is_not_blank().is_not_whitespace()
            trace.Period("Defined from cell ref E4 right which is not blank")

            flow = cell.shift(0, -2).expand(RIGHT).is_not_blank().is_not_whitespace()
            trace.Flow("Defined from cell ref E3 right which is not blank")

            industry_origin = cell.expand(DOWN).is_not_blank().is_not_whitespace()
            trace.Industry_Origin("Defined form cell ref A5 and down which is not blank")

            industry = cell.shift (2, 0).expand(DOWN).is_not_blank()
            trace.Industry("Defined from cell ref C7 and down which is not blank")

            industry_total = cell.shift(1, 0).expand(DOWN).is_not_blank()
            trace.Industry_Total("Defined from cell ref B2 and down")

            dimensions =[
                HDim(period, "Period", DIRECTLY, ABOVE),
                HDim(flow, "Flow", CLOSEST, LEFT),
                HDim(industry_origin, "Industry Origin", CLOSEST, ABOVE),
                HDim(industry, "Industry", CLOSEST, ABOVE),
                HDim(industry_total, "Industry Total", CLOSEST, ABOVE),
            ]
            tidy_sheet = ConversionSegment(tab, dimensions, observations)
            savepreviewhtml(tidy_sheet, fname = tab.name + "Preview.html")
            trace.with_preview(tidy_sheet)
trace.store("combined_dataframe", tidy_sheet.topandas())

for name, tab in tabs.items():
    print(name)

# +
tab = tabs["Table C0"]
trace.start(datasetTitle, tab, columns,distribution.downloadURL)

cell = tab.excel_ref("C3")

observations = cell.shift(1, 2).expand(DOWN).expand(RIGHT).is_not_blank().is_not_whitespace()

period = cell.shift(1, 1).expand(RIGHT).is_not_blank().is_not_whitespace()
trace.Period("Defined from cell ref D4 right which is not blank")

flow = cell.shift(1, 0).expand(RIGHT).is_not_blank().is_not_whitespace()
trace.Flow("Defined from cell ref D3 right which is not blank")

industry = cell.fill(DOWN).is_not_blank().is_not_whitespace()   
trace.Industry("Defined form cell ref C5 and down which is not blank")

dimensions =[
    HDim(period, "Period", DIRECTLY, ABOVE),
    HDim(flow, "Flow", CLOSEST, LEFT),
    HDim(industry, "Industry", CLOSEST, ABOVE),
]
tidy_sheet = ConversionSegment(tab, dimensions, observations)
savepreviewhtml(tidy_sheet, fname = tab.name + "Preview.html")
trace.with_preview(tidy_sheet)
trace.store("combined_dataframe", tidy_sheet.topandas())
# -

for name, tab in tabs.items():
    if 'Table C4 2013-2018'in name or 'Table C5 2013-2018' \
    in name or'Table C6 2013-2018' in name or 'Table C7 2013-2018' in name:
        
            trace.start(datasetTitle, tab, columns,distribution.downloadURL)
            cell = tab.excel_ref("A5")

            observations = cell.shift(3, 0).expand(DOWN).expand(RIGHT).is_not_blank().is_not_whitespace()

            period = cell.shift(0, -1).expand(RIGHT).is_not_blank().is_not_whitespace()
            trace.Period("Defined from cell ref E4 right which is not blank")

            flow = cell.shift(0, -2).expand(RIGHT).is_not_blank().is_not_whitespace()
            trace.Flow("Defined from cell ref E3 right which is not blank")

            industry_origin = cell.expand(DOWN).is_not_blank().is_not_whitespace()
            trace.Industry_Origin("Defined form cell ref A5 and down which is not blank")

            industry = cell.shift (2, 0).expand(DOWN).is_not_blank()
            trace.Industry("Defined from cell ref C7 and down which is not blank")

            industry_total = cell.shift(1, 0).expand(DOWN).is_not_blank()
            trace.Industry_Total("Defined from cell ref B2 and down")

            dimensions =[
                HDim(period, "Period", DIRECTLY, ABOVE),
                HDim(flow, "Flow", CLOSEST, LEFT),
                HDim(industry_origin, "Industry Origin", CLOSEST, ABOVE),
                HDim(industry, "Industry", CLOSEST, ABOVE),
                HDim(industry_total, "Industry Total", CLOSEST, ABOVE),
            ]
            tidy_sheet = ConversionSegment(tab, dimensions, observations)
            savepreviewhtml(tidy_sheet, fname = tab.name + "Preview.html")
            trace.with_preview(tidy_sheet)
trace.store("combined_dataframe", tidy_sheet.topandas())

df = trace.combine_and_trace(datasetTitle, "combined_dataframe")

# +
# post processing
df.rename(columns={'OBS' : 'Value','DATAMARKER' : 'Marker'}, inplace=True)

df['Marker'] = df['Marker'].map(lambda x: {'-':'itis-nil or less than £500000', '..':'disclosive'}.get(x, x))


# -

def left(s, amount):
   return s[:amount]
def date_time (date):
   if len(date)  == 5:
       return 'year/' + left(date, 4)
df['Period'] = df['Period'].astype(str).replace('\.','',regex = True)
df['Period'] = df['Period'].apply(date_time)
trace.Period("added a prefix called year to values in period column")

df.rename(columns = {'Flow':'Flow Directions'}, inplace = True)

df['Flow Directions'] = df['Flow Directions'].str.lower()
trace.Flow_Directions("Converted values of Flow Directionsto lower")

df['Continent'] = df['Continent'].str.lower()
trace.Continent("Converted values of continent to lower case")

df['Country'] = df['Country'].str.lower()
trace.Country("Converted values of country to lower case")

df['Industry Origin'] = df['Industry Origin'].str.lower()
trace.Industry_Origin("Converted values of Industry Origin to lower case")

df['Industry'] = df['Industry'].str.lower()
trace.Industry("Converted values of Industry to lower case")

df['Industry Total'] = df['Industry Total'].str.lower()
trace.Industry_Total("Converted values of Industry Total to lower case")
df

cubes.add_cube(scraper, df.drop_duplicates(), datasetTitle)
trace.render("spec_v1.html")

cubes.output_all()
