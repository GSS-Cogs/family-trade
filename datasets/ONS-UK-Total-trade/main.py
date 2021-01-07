# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
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

# UK trade in services: all countries, non-seasonally adjusted

# +
from gssutils import *
import json
import numpy as np

trace = TransformTrace()
df = pd.DataFrame()
cubes = Cubes("info.json")
scraper = Scraper(json.load(open('info.json'))['landingPage'])
scraper
# -

tabs = { tab.name: tab for tab in scraper.distribution(latest=True).as_databaker() }


# +
def left(s, amount):
    return s[:amount]
def right(s, amount):
    return s[-amount:]

def date_time (date):
    if len(date)  == 4:
        return 'year/' + date
    elif len(date) == 6:
        return 'quarter/' + left(date,4) + '-' + right(date,2)
    else:
        return date

for name, tab in tabs.items():
    datasetTitle = 'uk-total-trade-all-countries-non-seasonally-adjusted'
    columns=['Period','Country','Flow','Trade Type', 'Marker']
    trace.start(datasetTitle, tab, columns, scraper.distributions[0].downloadURL)
    
    if 'Index' in name or '7 Contact Sheet' in name:
        continue
    observations = tab.excel_ref('C7').expand(DOWN).expand(RIGHT).is_not_blank().is_not_whitespace()
    period = tab.excel_ref('C4').expand(RIGHT).is_not_blank().is_not_whitespace()
    trace.Period("Taken from row 4")
    flow = tab.fill(DOWN).one_of(['Exports','Imports'])
    trace.Flow("Either one of Exports or Imports: rows 7 to 251 are Exports and rows 255 to 499 are Imports")
    country = tab.excel_ref('A7').expand(DOWN).is_not_blank().is_not_whitespace()
    trace.Country("2 letter code taken from column A")
    trade_type = tab.excel_ref('B1')
    trace.Trade_Type("Taken from sheet title ")
    dimensions = [
        HDim(period,'Period',DIRECTLY,ABOVE),
        HDim(country,'Country',DIRECTLY,LEFT),
        HDim(flow, 'Flow',CLOSEST,ABOVE),
        HDim(trade_type, 'Trade Type',CLOSEST,LEFT),
    ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)   
    #savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
    trace.with_preview(tidy_sheet)
    trace.store("combined_dataframe", tidy_sheet.topandas())
# -

#Post Processing 
df = trace.combine_and_trace(datasetTitle, "combined_dataframe")
df.rename(columns={'OBS' : 'Value','DATAMARKER' : 'Marker'}, inplace=True)
#df['Value'] = df['Value'].astype(float)
df['Value'] = pd.to_numeric(df.Value, errors='coerce')
df['Marker'].replace('N/A', 'not-collated', inplace=True)
trace.Marker("replacing N/A with not-collated")
df['Flow'] = df['Flow'].map(lambda s: s.lower().strip())
df["Country"] = df["Country"].map(lambda x: pathify(x))
df['Trade Type'] = df['Trade Type'].apply(lambda x: 'total' if 'Total Trade' in x else 
                                      ('goods' if 'Trade in Goods' in x else 
                                       ('services' if 'Trade in Services' in x else x)))
trace.Trade_Type("Replacing Trade Type output to one of; total, goods, services if the title contains the one of those words.")
df['Period'] = df['Period'].astype(str).replace('\.0', '', regex=True)
trace.Period('Formatingyear values into year/{yr} (year/2020) and quarter values into quarter/{qtr} (quarter/Q1)')
df['Period'] =  df["Period"].apply(date_time)
df = df[['Period', 'Country', 'Flow', 'Trade Type', 'Value', 'Marker']]

#additional scraper info needed
scraper.dataset.family = 'trade'
add_to_des = """
These tables have been produced to provide an aggregated quarterly goods and services estimate and combines the most recent estimates for goods and services split by country.
Data for goods and services is consistent for annual whole world totals and quarters (from Q1 2016) with the trade data published in the Quarterly National Accounts, Quarterly Sector Accounts and Quarterly Balance of Payments on 30th September 2020.
These data are our best estimate of these bilateral UK trade flows. Users should note that alternative estimates are available, in some cases, via the statistical agencies for bilateral countries or through central databases such as:
UN Comtrade.
Some data for countries have been marked with N/A. This is because Trade in Goods do not collate data from these countries, therefore only Trade in Services is reflected within total trade for these countries
The data within these tables are also consistent with the below releases:
For Trade in Goods the data is consistent with UK Trade: August 2020 publication on 9th October 2020
For Trade in Services the data is consistent with UK Trade in services by partner country: April to June 2020 publication on 4th November 2020
"""
scraper.dataset.description = scraper.dataset.description + add_to_des


cubes.add_cube(scraper, df.drop_duplicates(), "ons-uk-total-trade")
cubes.output_all()
trace.render("spec_v1.html")


df.dtypes
