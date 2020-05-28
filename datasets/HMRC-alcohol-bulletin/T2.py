# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
from gssutils import *

scraper = Scraper("https://www.gov.uk/government/statistics/alcohol-bulletin")
scraper
# -

dist = scraper.distributions[1]
tabs = (t for t in dist.as_databaker())
tidied_sheets = []
dist


# +
def left(s, amount):
    return s[:amount]
def right(s, amount):
    return s[-amount:]

def date_time(time_value):
    time_string = str(time_value).replace(".0", "").strip()
    time_len = len(time_string)
    if time_len == 4:
        return "year/" + time_string
    elif time_len == 7:
        return 'government-year/' + time_string[:4] + '-20' + time_string[5:7]
    elif time_len == 10:       
        return 'gregorian-interval/' + time_string[:7] + '-01T00:00:00/P1M'


# -

# T2: Wine Duty (made-wine) statistics

for tab in tabs:
            if (tab.name == 'T2'):
                period = tab.excel_ref('B12').expand(DOWN).is_not_blank() 
                alcohol_by_volume = tab.excel_ref('C8').expand(RIGHT).is_not_blank() 
                alcohol_origin = tab.excel_ref('B9').expand(RIGHT).is_not_blank()
                revision = tab.excel_ref('D10').expand(DOWN)
                observations = alcohol_origin.fill(DOWN).is_not_blank()
      
                dimensions = [
                    HDim(period, 'Period', DIRECTLY, LEFT),
                    HDim(revision, 'Revision', DIRECTLY, LEFT),
                    HDim(alcohol_origin, 'Alcohol Origin', DIRECTLY, ABOVE),
                    HDim(alcohol_by_volume, 'Alcohol by Volume', CLOSEST, LEFT),
                    HDimConst('Alcohol Type', 'Made-Wine'),
                    HDimConst('Production and Clearance', 'Not Applicable'),
                    HDimConst('Measure Type', 'Released for Consumption'),
                    HDimConst('Unit', 'Hectolitres') #will filtered to Hectolitre Or GBP Million after transformation
                ]
                tidy_sheet = ConversionSegment(tab, dimensions, observations)        
                #savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
                tidied_sheets.append(tidy_sheet.topandas())

# +
df = pd.concat(tidied_sheets, ignore_index = True, sort = False)
df.rename(columns={'OBS' : 'Value','DATAMARKER' : 'Marker'}, inplace=True)
df["Period"] = df["Period"].apply(date_time)

if 'Marker' in df.columns:
    df['Marker'].replace('*', 'estimated', inplace=True)

df['Value'] = pd.to_numeric(df['Value'], errors='coerce')

# +
f1=(df['Alcohol Origin'] =='Above 1.2% but not exceeding 5.5% ABV ')
df.loc[f1,'Alcohol by Volume'] = 'Above 1.2% but not exceeding 5.5% ABV '
df.loc[f1,'Alcohol Origin'] = 'all'

f2=(df['Alcohol Origin'] =='Over 15% ABV')
df.loc[f2,'Alcohol by Volume'] = 'Over 15% ABV'
df.loc[f2,'Alcohol Origin'] = 'all'

f3=(df['Alcohol Origin'] =='Total made wine')
df.loc[f3,'Alcohol by Volume'] = 'Total made wine'
df.loc[f3,'Alcohol Origin'] = 'all'

f4=(df['Alcohol by Volume'] =='£ million')
df.loc[f4,'Unit'] = 'GBP Million'

f5=(df['Revision'] =='P')
df.loc[f5,'Marker'] = 'provisional'

f6=(df['Revision'] =='R')
df.loc[f6,'Marker'] = 'revised'

df = df.replace({'Alcohol Origin' : {'Still1 ' : 'Still', 'Imported \nex-ship' :'Imported ex-ship', 'Total wine2 ' : 'Total Wine'}})
df = df.replace({'Alcohol by Volume' : {'£ million' : 'all'}})

# -

tidy = df[['Period', 'Alcohol by Volume', 'Alcohol Type', 'Alcohol Origin', 'Production and Clearance', 'Measure Type', 'Unit', 'Marker', 'Value']]
