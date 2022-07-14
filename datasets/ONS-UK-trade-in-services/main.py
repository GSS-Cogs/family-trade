#!/usr/bin/env python
# coding: utf-8
import pandas as pd
from gssutils import *

metadata = Scraper(seed="info.json")

distribution = metadata.distribution(latest=True)

title = distribution.title

tabs = {tab.name: tab for tab in distribution.as_databaker()}

# +
tidied_sheets = []

tab = tabs['Time Series']

observations = tab.excel_ref("F2").expand(RIGHT).expand(DOWN).is_not_blank()

period = tab.excel_ref("F1").expand(RIGHT).is_not_blank()

flow = tab.excel_ref("A2").expand(DOWN).is_not_blank()

trade_services = tab.excel_ref("B2").expand(DOWN).is_not_blank()

ons_partner_geography = tab.excel_ref("D2").expand(DOWN).is_not_blank()

dimensions =[
        HDim(period, 'Period', DIRECTLY, ABOVE),
        HDim(flow, 'Flow', DIRECTLY, LEFT),
        HDim(trade_services, 'Trade Services', DIRECTLY, LEFT),
        HDim(ons_partner_geography, 'ONS Partner Geography', DIRECTLY, LEFT),
    ]

tidy_sheet = ConversionSegment(tab, dimensions, observations)
# savepreviewhtml(tidy_sheet, fname = tab.name +"PREVIEW.html")
tidied_sheets.append(tidy_sheet.topandas())
# -

df = pd.concat(tidied_sheets, sort = True)

df.rename(columns = {'OBS':'Value', 'DATAMARKER':'Marker', 'ONS Partner Geography':'Country'},inplace = True)
df['Value'] = pd.to_numeric(df['Value'], errors = 'coerce')


def left(s, amount):
    return s[:amount]
def right(s, amount):
    return s[-amount:]
def date_time (date):
    if len(date)  == 5:
        return 'year/' + left(date, 4)
    #year/2019
    elif len(date) == 6:
        return 'quarter/' + left(date,4) + '-' + right(date,2)
    #quarter/2019-01
    else:
        return date       


#Post Processing 
df['Period'] = df['Period'].astype(str).replace('\.', '', regex=True)
df['Period'] =  df["Period"].apply(date_time)
df = df.replace({'Marker' : {'-' : 'itis-nil', '..' : 'disclosive'}})
df['Seasonal Adjustment'] =  'NSA'
df['Flow'] = df['Flow'].apply(pathify)
df = df[['Period','Flow','Trade Services','Country','Seasonal Adjustment','Value','Marker' ]]
df['Trade Services'] = df['Trade Services'].astype(str).replace('\.0', '', regex=True)
df.loc[(df['Marker'] == 'disclosive'),'Value'] = 0
df['Value'] = df['Value'].astype(int)
df['Marker'].fillna('', inplace=True)

df.to_csv("observations.csv", index = False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')
