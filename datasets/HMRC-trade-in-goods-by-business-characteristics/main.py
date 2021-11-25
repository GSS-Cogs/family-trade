# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.10.2
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

scraper = Scraper(seed = '/workspaces/family-trade/datasets/HMRC-trade-in-goods-by-business-characteristics/info.json')
scraper
# -

info = json.load(open('/workspaces/family-trade/datasets/HMRC-trade-in-goods-by-business-characteristics/info.json'))

cubes = Cubes('/workspaces/family-trade/datasets/HMRC-trade-in-goods-by-business-characteristics/info.json')

trace = TransformTrace()

scraper.select_dataset(title = lambda x: x.endswith('data tables'), latest = True)
scraper.dataset.family = info["families"]

distribution = scraper.distribution(latest = True)
# datasetTitle = scraper.title
display(distribution)

tabs = distribution.as_databaker()

for tab in tabs:
    print(tab.name)

    columns = ["Flow", "Period", "Country", "Zone", "Business Size", "Age", "Industry Group", "Value", 
               "Business Count", "Employee Count", "Flow Directions", "Year", "Marker"]

# +

# datasetTitle = "UK trade in goods by business characteristics - data tables" #removing date from title 

# +
# tabs = {tab.name: tab for tab in scraper.distribution(title = lambda t : 'data tables' in t).as_databaker()}
# print(type(tabs))
# -

tidied_sheets = []

# +
for tab in tabs:
    # if tab.name in ["Notes and Contents", "2. Age Group","3. Business Size","4. Industry_Age", "5. Industry_BusinessSize", "6. BusinessSize_Age", "7. Metadata"]:
    if tab.name not in ["1. Industry Group"]:
        continue
    print(tab.name)
    # trace.start(datasetTitle, tab, columns, distribution)
    cell = tab.excel_ref("A1")
    # df = pd.DataFrame(cell)
    # print(df)
    # list(cell)

    unwanted_1 = cell.shift(0,20).fill(DOWN).expand(RIGHT)|tab.filter(contains_string('Total'))
    # savepreviewhtml(unwanted_1, fname=tab.name +"Preview.html")

    flow = cell.shift(0,7).fill(RIGHT).is_not_blank().is_not_whitespace()
    # savepreviewhtml(flow, fname=tab.name +"Preview.html")
    
    industry_group = cell.shift(0,8).fill(DOWN).is_not_blank().is_not_whitespace()-unwanted_1
    # savepreviewhtml(industry_group, fname=tab.name +"Preview.html")

    observations = flow.waffle(industry_group)
    # savepreviewhtml(observations, fname=tab.name +"Preview.html")

    dimensions = [
        HDim(flow, "Flow", DIRECTLY, ABOVE),
        HDim(industry_group, "Industry Group", DIRECTLY, LEFT)
    ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    tidied_sheets.append(tidy_sheet.topandas())

df = pd.concat(tidied_sheets, ignore_index = True, sort = False)
df
