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
import numpy as np

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

# +
# tabs = distribution.as_databaker()

# +
# for tab in tabs:
#     print(tab.name)
# -

    # columns = ["Flow", "Period", "Country", "Zone", "Business Size", "Age", "Industry Group", "Value", 
    #            "Business Count", "Employee Count", "Flow Directions", "Year", "Marker"]

# +
# tidied_sheets = []

# +
# for tab in tabs:
#     # if tab.name in ["Notes and Contents", "2. Age Group","3. Business Size","4. Industry_Age", "5. Industry_BusinessSize", "6. BusinessSize_Age", "7. Metadata"]:
#     if tab.name not in ["1. Industry Group"]:
#         continue
#     # print(tab.name)

#     cell = tab.excel_ref("A1")

#     del_row_21 = tab.filter("Total").expand(RIGHT).is_not_blank()|tab.filter("Total [note 9]").expand(RIGHT).is_not_blank()

#     del_row_22 = del_row_21.fill(DOWN).is_blank()

#     del_row_23 = tab.filter(contains_string("by industry group")).expand(RIGHT).is_not_blank()

#     del_row_24 = tab.filter(contains_string("Export")).fill(LEFT)

#     del_row_25 = tab.filter(contains_string("Industry group")).expand(RIGHT)

#     del_row_54 = tab.filter(contains_string("Source")).expand(DOWN)

#     del_row_56 = tab.filter(contains_string("Notes")).expand(DOWN)

#     total_del = del_row_21|del_row_22|del_row_23|del_row_24|del_row_25|del_row_54|del_row_56

#     flow = tab.filter("Exports")|tab.filter("Imports")

#     industry_group = cell.shift(0,8).fill(DOWN).is_not_blank().is_not_whitespace()-total_del

#     count = tab.filter(contains_string("by industry group")) #Can be used latter for multimeasure extraction

#     observations = flow.waffle(industry_group)-total_del
#     # savepreviewhtml(observations, fname=tab.name +"Preview.html")
    
#     dimensions = [
#         HDim(flow, "Flow", DIRECTLY, ABOVE),
#         HDim(industry_group, "Industry Group", DIRECTLY, LEFT),
#         HDim(count, "Count", CLOSEST, ABOVE)
#     ]
#     tidy_sheet = ConversionSegment(tab, dimensions, observations)
#     tidied_sheets.append(tidy_sheet.topandas())

# +
# for tab in tabs:
#     if tab.name not in ["2. Age Group"]:
#         continue

#     cell = tab.excel_ref("A1")

#     del_row_17 = tab.filter("Total").expand(RIGHT).is_not_blank()|tab.filter("Total [note 8]").expand(RIGHT).is_not_blank()

#     del_row_18 = del_row_17.fill(DOWN).is_blank()

#     del_row_19 = tab.filter(contains_string("by age of business")).expand(RIGHT).is_not_blank()

#     del_row_20 = tab.filter(contains_string("Export")).fill(LEFT)

#     del_row_21 = tab.filter(contains_string("Age (years)")).expand(RIGHT)

#     del_row_42 = tab.filter(contains_string("Source")).expand(DOWN)

#     del_row_56 = tab.filter(contains_string("Notes")).expand(DOWN)

#     total_del = del_row_17|del_row_18|del_row_19|del_row_20|del_row_21|del_row_42|del_row_56

#     flow = tab.filter("Exports")|tab.filter("Imports")

#     age = cell.shift(0,8).fill(DOWN).is_not_blank().is_not_whitespace()-total_del

#     count = tab.filter(contains_string("by age of business")) #Can be used latter for multimeasure extraction

#     observations = flow.waffle(age)-total_del
#     # savepreviewhtml(observations, fname=tab.name+ "Preview.html")

#     dimensions = [
#         HDim(flow, "Flow", DIRECTLY, ABOVE),
#         HDim(age, "Age", DIRECTLY, LEFT),
#         HDim(count, "Count", CLOSEST, ABOVE)
#     ]
#     tidy_sheet = ConversionSegment(tab, dimensions, observations)
#     tidied_sheets.append(tidy_sheet.topandas())

# +
# for tab in tabs:
#     if tab.name not in ["3. Business Size"]:
#         continue

#     cell = tab.excel_ref("A1")

#     del_row_16 = tab.filter("Total").expand(RIGHT).is_not_blank()|tab.filter("Total [note 8]").expand(RIGHT).is_not_blank()

#     del_row_17 = del_row_16.fill(DOWN).is_blank()

#     del_row_18 = tab.filter(contains_string("by business size")).expand(RIGHT).is_not_blank()
    
#     del_row_19 = tab.filter(contains_string("Export")).fill(LEFT)

#     del_row_20 = tab.filter(contains_string("Business size  (no. of employees)")).expand(RIGHT)

#     del_row_39 = tab.filter(contains_string("Source")).expand(DOWN)

#     del_row_56 = tab.filter(contains_string("Notes")).expand(DOWN)

#     total_del = del_row_16|del_row_17|del_row_18|del_row_19|del_row_20|del_row_39|del_row_56

#     flow = tab.filter("Exports")|tab.filter("Imports")

#     business_size = cell.shift(0,8).fill(DOWN).is_not_blank().is_not_whitespace()-total_del

#     count = tab.filter(contains_string("by business size")) #Can be used latter for multimeasure extraction

#     observations = flow.waffle(business_size)-total_del
#     # savepreviewhtml(observations, fname=tab.name+ "Preview.html")

#     dimensions = [
#         HDim(flow, "Flow", DIRECTLY, ABOVE),
#         HDim(business_size, "Business Size", DIRECTLY, LEFT),
#         HDim(count, "Count", CLOSEST, ABOVE)
#     ]
#     tidy_sheet = ConversionSegment(tab, dimensions, observations)
#     tidied_sheets.append(tidy_sheet.topandas())

# +
# for tab in tabs:
#     if tab.name not in ["4. Industry_Age"]:
#         continue
#     # print(tab.name)

#     del_row_82 = tab.filter(contains_string("Grand Total [note 9]")).expand(RIGHT).expand(DOWN)
    
#     # industry_group = tab.filter(contains_string("Industry group")).fill(DOWN).is_not_blank()-del_row_82

#     age = tab.filter(contains_string("Age (years)")).fill(DOWN).is_not_blank().is_not_whitespace()-del_row_82

#     industry_group = age.shift(LEFT).is_not_blank().is_not_whitespace()
#     # savepreviewhtml(industry_group, fname=tab.name+ "Preview.html")

#     flow = tab.filter(contains_string("Exports")).expand(RIGHT).is_not_blank().is_not_whitespace()

#     value = tab.filter(contains_string("Value £ m")).fill(DOWN).is_not_blank().is_not_whitespace()-del_row_82

#     business_count = tab.filter(contains_string("Business Count")).fill(DOWN).is_not_blank().is_not_whitespace()-del_row_82

#     employee_count = tab.filter(contains_string("Employee Count")).fill(DOWN).is_not_blank().is_not_whitespace()-del_row_82

#     # observations = value|business_count|employee_count

#     required_column_names = tab.filter(contains_string("Value £ m")).expand(RIGHT).is_not_blank().is_not_whitespace()

#     observations = age.waffle(required_column_names)

#     dimensions = [
#         HDim(industry_group, "Industry Group", CLOSEST, ABOVE),
#         HDim(age, "Age", DIRECTLY, LEFT),
#         # HDim(flow, "Flow", CLOSEST, ABOVE),
#         # HDim(value, "Value", DIRECTLY, ABOVE),
#         # HDim(business_count, "Business Count", DIRECTLY, ABOVE),
#         # HDim(employee_count, "Employee Count", DIRECTLY, ABOVE)
#     ]
#     tidy_sheet = ConversionSegment(tab, dimensions, observations)
#     tidied_sheets.append(tidy_sheet.topandas())

# +
# df = pd.concat(tidied_sheets, ignore_index = True, sort = False)
# df
# -

df = distribution.as_pandas()

# +
# the input file is not in the format I want, and that I am doing something to go around it
# xl = pd.ExcelFile('https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1033097/IDBR_OTS_tables_2020.xlsx')
# df = xl.parse("1. Industry Group", header=None, names=['Industry Group', 'Exports', 'Imports'])# 

# +

df = pd.read_excel('https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1033097/IDBR_OTS_tables_2020.xlsx', sheet_name="1. Industry Group", header=None, names=["Industry_Group", "Exports", "Imports"], skiprows=9, usecols = "A:D", comment = "Total", skipfooter=13) 
# -

# df.head(55)
df.shape

values = ["Business count by industry group", "Industry group", "Employee count for businesses by industry group"]
df = df[df.Industry_Group.isin(values) == False]
df=df.dropna(how="all")
df = df[(df.Exports != "Exports") & (df.Imports != "Imports")]
df = df[(df.Industry_Group != "Industry group") & (df.Exports != 2020) & (df.Imports != 2020)]
# df['count'] = df['Industry_Group'].map(lambda x: np.random.random())

# df.head(55)
df.shape

# +
# df["measure_map"] = df["Industry_Group"].copy()
# discount = df["measure_map"]
# -

# df1=df.merge(discount,left_index=True, right_index=True)


df["measure_map"] = df["Industry_Group"]

# df.drop(["measure_map_y"], axis = 1)
# df.head(55)
df.shape

# +
# for index, element in enumerate(df['Industry_Group']):
#     print(f"index={index}, element={element}")

# +
# print(df["Industry_Group"])

# +
# columns = ["measure_map"]
# -

# limit = 10
for i, row in df.iloc[:11].iterrows():
    # print(f"index={i} row={row}")
    # print(f"{row}")
    # df[:limit].iloc[df[:10]== i]
    for column in ["measure_map"]:
        df.at[i,column] = "£ millions"

# df.head(50)
df.shape

# +
# df.loc[df["measure_map"] != "£ millions"] = "number"
# -

for i, row in df.iloc[11:40].iterrows():
    for column in ["measure_map"]:
        df.at[i,column] = "number"

df.shape

df.head

# +
# print(df.iloc[0:10])

# +
# df.shape
# -

df.shape

df1 = pd.melt(df, id_vars = ["Industry_Group", "measure_map"], value_vars = ["Exports", "Imports"], var_name = "flow", value_name = "value")

df1


