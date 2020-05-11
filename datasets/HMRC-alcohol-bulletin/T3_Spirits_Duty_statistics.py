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
                category = tab.excel_ref('D10').expand(RIGHT).is_not_blank()
                revision = tab.excel_ref('D10').expand(DOWN)
                measure_type = tab.excel_ref('D8').expand(RIGHT).is_not_blank()  # - tab.excel_ref('L8').expand(RIGHT) - tab.excel_ref('I8') - tab.excel_ref('H8')
                whisky_total_type = tab.excel_ref('D9').expand(RIGHT) - tab.excel_ref('L9').expand(RIGHT) - tab.excel_ref('I9') - tab.excel_ref('H9')
                alcohol_content = 'pure alcohol'
                alcohol_duty = 'spirits'
               # measure_type = 'quantities-consumption'
                unit = 'hectolitres'
                observations = category.fill(DOWN).is_not_blank()
                
                dimensions = [
                    HDim(period, 'Period', DIRECTLY, LEFT),
                    HDim(revision, 'Revision', DIRECTLY, LEFT),
                    HDim(category, 'Alcohol Category', DIRECTLY, ABOVE),
                    HDim(measure_type, 'Measure Type', CLOSEST, LEFT),  
                    HDim(whisky_total_type, 'Whisky Total Type', CLOSEST, LEFT), #will be dropped. Whisky total
                    HDimConst('Alcohol Content', alcohol_content),
                    HDimConst('Alcohol Duty', alcohol_duty),
                    #HDimConst('Measure Type', measure_type),
                    HDimConst('Unit', unit),
                ]
                
                tidy_sheet = ConversionSegment(tab, dimensions, observations)        
                #savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
                tidied_sheets.append(tidy_sheet.topandas())

# +
df = pd.concat(tidied_sheets, ignore_index = True, sort = False)
df.rename(columns={'OBS' : 'Value','DATAMARKER' : 'Marker'}, inplace=True)

if 'Marker' in df.columns:
    df['Marker'].replace('*', 'estimated', inplace=True)
else:
    df['Marker'] = ''

df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
# -

df['Measure Type'].unique()

df['Whisky Total Type'].unique()

df['Alcohol Category'].unique()

# +
f1=(df['Revision'] =='P')
df.loc[f1,'Marker'] = 'provisional'
df.drop(['Revision'], axis=1)

f2=((df['Measure Type'] =='Production of Potable Spirits 1') & (df['Alcohol Category'] == 'Total'))
df.loc[f2,'Alcohol Category'] = 'Total Spirits'

f3=((df['Whisky Total Type'] =='Home Produced Whisky') & (df['Alcohol Category'] == 'Total'))
df.loc[f3,'Alcohol Category'] = 'Total Home Produced Whisky'

f4=((df['Measure Type'] =='Net Quantities of Spirits \nCharged with Duty') & (df['Alcohol Category'] == 'Total'))
df.loc[f4,'Alcohol Category'] = 'Total Spirits'


df = df.replace({'Measure Type' : {'Net Quantities of Spirits \nCharged with Duty' : 'net-quantities-spirits',
                                       'Production of Potable Spirits 1': 'potable-spirits', 
                                       '£ million': 'revenue',
                                      }})

df = df.replace({'Alcohol Category' : {'Grain and Blended 2' : 'hpw-grain-blended',
                                       'Malt': 'hpw-malt', 
                                       'Total Home Produced Whisky' : 'hpw-total',
                                      }})

def user_perc5(x):
    if ((str(x) == 'potable-spirits')) | ((str(x) == 'net-quantities-spirits')): 
        return 'hectolitres'
    else:
        return 'gbp-million'
    
df['Unit'] = df.apply(lambda row: user_perc5(row['Measure Type']), axis = 1)


def user_perc8(x,y):
    if ((str(x) == 'Total Alcohol')):   
        return 'all'
    else:
        return y

df['Alcohol Content'] = df.apply(lambda row: user_perc8(row['Alcohol Category'], row['Alcohol Content']), axis = 1)

df['Value'] = df['Value'].round(decimals=2)
df["Period"] = df["Period"].apply(date_time)
# -

df['Alcohol Category'].unique()

df['Measure Type'].unique()

Final_table = df[['Period','Alcohol Duty','Alcohol Category','Alcohol Content','Measure Type','Value','Unit', 'Marker']]
Final_table['Alcohol Category'] = Final_table['Alcohol Category'].map(lambda x: pathify(x))
Final_table['Alcohol Content'] = Final_table['Alcohol Content'].map(lambda x: pathify(x))



Final_table



