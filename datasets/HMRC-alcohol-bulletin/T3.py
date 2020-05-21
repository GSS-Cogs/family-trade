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
# T3: Spirits Duty statistics 

for tab in tabs:               
            if (tab.name == 'T3'):
                period = tab.excel_ref('B12').expand(DOWN).is_not_blank() 
                production_and_clearance = tab.excel_ref('C8').expand(RIGHT).is_not_blank()                
                alcohol_origin = tab.excel_ref('B10').expand(RIGHT).is_not_blank()  
                whisky_total_type = tab.excel_ref('D9').expand(RIGHT) - tab.excel_ref('L9').expand(RIGHT) - tab.excel_ref('I9') - tab.excel_ref('H9')
                revision = tab.excel_ref('D10').expand(DOWN)
                observations = alcohol_origin.fill(DOWN).is_not_blank()
      
                dimensions = [
                    HDim(period, 'Period', DIRECTLY, LEFT),
                    HDim(revision, 'Revision', DIRECTLY, LEFT),
                    HDim(alcohol_origin, 'Alcohol Origin', DIRECTLY, ABOVE),
                    HDim(production_and_clearance, 'Production and Clearance', CLOSEST, LEFT),
                    HDim(whisky_total_type, 'Whisky Total Type', CLOSEST, LEFT), #will be dropped. Whisky total
                    HDimConst('Alcohol Type', 'Spirits'),
                    HDimConst('Alcohol by Volume', 'All'),
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
f1=((df['Whisky Total Type'] =='Home Produced Whisky') & (df['Alcohol Origin'] == 'Total'))
df.loc[f1,'Alcohol Origin'] = 'Home Produced Whiskey Total'

f2=(df['Revision'] =='P')
df.loc[f2,'Marker'] = 'provisional'

f3=(df['Revision'] =='R')
df.loc[f3,'Marker'] = 'revised'

f4=(df['Production and Clearance'] =='£ million')
df.loc[f4,'Unit'] = 'GBP Million'

df = df.replace({'Production and Clearance' : {'£ million' : 'All', 'Net Quantities of Spirits \nCharged with Duty' : 'Net Quantities of Spirits Charged with Duty', 'Production of Potable Spirits 1' : 'Production of Potable Spirits'}})

df = df.replace({'Alcohol Origin' : {'£ million' : 'all',
                                       'Malt' : 'Home Produced Whiskey Malt',
                                       'Grain and Blended 2' : 'Home Produced Whiskey Grain and Blended',
                                       }})


# -

tidy = df[['Period', 'Alcohol by Volume', 'Alcohol Type', 'Alcohol Origin', 'Production and Clearance', 'Measure Type', 'Unit', 'Marker', 'Value']]

