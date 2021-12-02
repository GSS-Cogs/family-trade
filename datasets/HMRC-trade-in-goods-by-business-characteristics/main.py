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
dcat_data = distribution.downloadURL
display(dcat_data)

    # columns = ["Flow", "Period", "Country", "Zone", "Business Size", "Age", "Industry Group", "Value", 
    #            "Business Count", "Employee Count", "Flow Directions", "Year", "Marker"]

df = distribution.as_pandas()

# +
# the input file is not in the format I want, and that I am doing something to go around it
# xl = pd.ExcelFile('https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1033097/IDBR_OTS_tables_2020.xlsx')
# df = xl.parse("1. Industry Group", header=None, names=['Industry Group', 'Exports', 'Imports'])# 

# +

df = pd.read_excel(dcat_data, sheet_name="1. Industry Group", header=None, names=["Industry_Group", "Exports", "Imports"], skiprows=9, usecols = "A:D", comment = "Total", skipfooter=13) 
# -

# df.head(55)
df.shape

values = ["Business count by industry group", "Industry group", "Employee count for businesses by industry group"]
df = df[df.Industry_Group.isin(values) == False]
df=df.dropna(how="all")
df = df[(df.Exports != "Exports") & (df.Imports != "Imports")]
df = df[(df.Industry_Group != "Industry group") & (df.Exports != 2020) & (df.Imports != 2020)]

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

for i, row in df.iloc[:11].iterrows():
    for column in ["measure_map"]:
        df.at[i,column] = "£ millions"

# df.head(50)
df.shape

for i, row in df.iloc[11:40].iterrows():
    for column in ["measure_map"]:
        df.at[i,column] = "number"

# +
# df.head

# +
# df.shape
# -

df1 = pd.melt(df, id_vars = ["Industry_Group", "measure_map"], value_vars = ["Exports", "Imports"], var_name = "flow", value_name = "value")

# +
# df1

# +
#########################################################################################
# End of first tab

# +

df2 = pd.read_excel(dcat_data, sheet_name="2. Age Group", header=None, names=["Age", "Exports", "Imports"], skiprows=9, usecols = "A:D", comment = "Total", skipfooter=13) 

# +
# df2
# -

df2.shape

values = ["Business count by age of business", "Age (years)", "Employee count for businesses by age of business"]
df2 = df2[df2.Age.isin(values) == False]
df2=df2.dropna(how="all")
df2 = df2[(df2.Exports != "Exports") & (df2.Imports != "Imports")]
df2 = df2[(df2.Age != "Age (years)") & (df2.Exports != 2020) & (df2.Imports != 2020)]

df2.shape

# +
# df2
# -

df2["measure_map"] = df2["Age"]

df2.shape

for i, row in df.iloc[:7].iterrows():
    for column in ["measure_map"]:
        df2.at[i,column] = "£ millions"

# +
# df2
# -

df2.shape

for i, row in df2.iloc[7:21].iterrows():
    for column in ["measure_map"]:
        df2.at[i,column] = "number"

# +
# df2
# -

df2.head(1)

df2 = pd.melt(df2, id_vars = ["Age", "measure_map"], value_vars = ["Exports", "Imports"], var_name = "flow", value_name = "value")

# +
# df2
# -

df2.shape

# +
#####################################
# End of second dataframe df2

# +

df3 = pd.read_excel(dcat_data, sheet_name="3. Business Size", header=None, names=["Business_size", "Exports", "Imports"], skiprows=9, comment = "Total", skipfooter=14) 

# +
# df3
# -

df3.shape

values = ["Business size  (no. of employees)", "Business count by business size", "Employee count for businesses by business size"]
df3 = df3[df3.Business_size.isin(values) == False]
df3=df3.dropna(how="all")
df3 = df3[(df3.Exports != "Exports") & (df3.Imports != "Imports")]
df3 = df3[(df3.Business_size != "Business size (no. of employees)") & (df3.Exports != 2020) & (df3.Imports != 2020)]

df3.shape

# +
# df3
# -

df3["measure_map"] = df3["Business_size"]

# +
# df3
# -

for i, row in df3.iloc[:6].iterrows():
    for column in ["measure_map"]:
        df3.at[i,column] = "£ millions"

# +
# df3
# -

for i, row in df3.iloc[6:18].iterrows():
    for column in ["measure_map"]:
        df3.at[i,column] = "number"

# +
# df3
# -

df3.shape


