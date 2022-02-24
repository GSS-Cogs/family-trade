# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.5
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# UK trade in services: all countries, non-seasonally adjusted

import json
import pandas as pandas
from gssutils import *

info = json.load(open('info.json'))
landingPage = info['landingPage']

metadata = Scraper(seed="info.json")
distribution = metadata.distribution(latest = True)

title = distribution.title
tabs = distribution.as_databaker()
tidied_sheets = []


def date_time(date):
    # Various ways they're representing a 4 digit year
    if isinstance(date, float) or len(date) == 6 and date.endswith(".0") or len(date) == 4:
        return f'year/{str(date).replace(".0", "")}'
    # Month and year
    elif len(date) == 7:
        date = pd.to_datetime(date, format='%Y%b')
        return date.strftime('month/%Y-%m')
    else:
        raise Exception(f'Aborting, failing to convert value "{date}" to period')


for tab in tabs:

    anchor = tab.excel_ref("A1")
    flow = str(tab.name.split()[1]).lower()
    observations = anchor.shift(2, 5).expand(DOWN).expand(RIGHT).is_not_blank().is_not_whitespace()
    year = anchor.shift(2, 3).expand(RIGHT).is_not_blank().is_not_whitespace()
    footer = tab.filter(contains_string("Earliest date for revisions")).expand(DOWN)
    geo = anchor.shift(0, 5).expand(DOWN).is_not_blank().is_not_whitespace()-footer
    dimensions = [
        HDim(year,'Period',DIRECTLY,ABOVE),
        HDim(geo,'ONS Partner Geography',DIRECTLY,LEFT),
        HDimConst("Flow", flow),
        HDimConst("Seasonal Adjustment", "SA")
    ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    table = tidy_sheet.topandas()
    tidied_sheets.append(table)
    # savepreviewhtml(tidy_sheet, fname=tab.name+"Preview.html")

df = pd.concat(tidied_sheets, sort=True)

df.rename(columns={'OBS' : 'Value', 'DATAMARKER' : 'Marker'}, inplace=True)
df["Period"] =  df["Period"].apply(date_time)
df = df.fillna('')
df["Marker"] = df["Marker"].str.replace("N/A", "not-applicable")
df = df[["Period", "ONS Partner Geography", "Seasonal Adjustment", "Flow", "Value", "Marker"]]

df['Unit'] = "GBP Million"
df['Measure Type'] = "Current prices"

#scraper.dataset.family = 'trade'
metadata.dataset.description = metadata.dataset.description + """
These data are our best estimate of these bilateral UK trade flows. Users should note that alternative estimates are available, in some cases, via the statistical agencies for bilateral countries or through central databases such as 
UN Comtrade (https://comtrade.un.org/).

Some data for countries have been marked with N/A. This is because Trade in Goods do not collate data from these countries.
"""

df.to_csv("observations.csv", index = False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')
