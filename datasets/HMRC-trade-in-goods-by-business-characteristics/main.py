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

for tab in tabs:
    # if tab.name in ["Notes and Contents", "2. Age Group","3. Business Size","4. Industry_Age", "5. Industry_BusinessSize", "6. BusinessSize_Age", "7. Metadata"]:
    if tab.name not in ["1. Industry Group"]:
        continue
    # print(tab.name)

    cell = tab.excel_ref("A1")

    del_row_21 = tab.filter("Total").expand(RIGHT).is_not_blank()|tab.filter("Total [note 9]").expand(RIGHT).is_not_blank()

    del_row_22 = del_row_21.fill(DOWN).is_blank()

    del_row_23 = tab.filter(contains_string("by industry group")).expand(RIGHT).is_not_blank()

    del_row_24 = tab.filter(contains_string("Export")).fill(LEFT)

    del_row_54 = tab.filter(contains_string("Source")).expand(DOWN)

    del_row_56 = tab.filter(contains_string("Notes")).expand(DOWN)

    total_del = del_row_21|del_row_22|del_row_23|del_row_24|del_row_54|del_row_56

    flow = tab.filter("Exports")|tab.filter("Imports")

    industry_group = cell.shift(0,8).fill(DOWN).is_not_blank().is_not_whitespace()

    observations = flow.waffle(industry_group)-total_del
    # savepreviewhtml(observations, fname=tab.name +"Preview.html")
    
    dimensions = [
        HDim(flow, "Flow", DIRECTLY, ABOVE),
        HDim(industry_group, "Industry Group", DIRECTLY, LEFT)
    ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    tidied_sheets.append(tidy_sheet.topandas())

df = pd.concat(tidied_sheets, ignore_index = True, sort = False)
df
