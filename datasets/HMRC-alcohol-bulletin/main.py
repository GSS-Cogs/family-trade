# -*- coding: utf-8 -*-
# import glob
from gssutils import *
from gssutils.metadata import THEME
from gssutils.metadata.mimetype import ODS
import pandas as pd
import pyexcel
import messytables
from io import BytesIO
import numpy as np
import json
import copy 
import datetime


import json
import pandas as pd
from gssutils import *
from pandas import ExcelWriter


# +
trace = TransformTrace()
cubes = Cubes("info.json")

scraper = Scraper(seed="info.json")

distribution = scraper.distribution(latest = True, mediaType=ODS)
datasetTitle = distribution.title
columns = ["Period", "Marker", "Bulletin Type", "Alcohol Type", "Measure Type", "Unit"]
distribution
# -


xls = pd.ExcelFile(distribution.downloadURL, engine="odf")
with ExcelWriter("data.xls") as writer:
    for sheet in xls.sheet_names[0:6]:
        pd.read_excel(xls, sheet).to_excel(writer,sheet, index=False)
    writer.save()
tabs = loadxlstabs("data.xls")


tidied_sheets = []

# +
# Old tab names
#tabs_names_to_process = ["Wine_statistics", "Made_wine_statistics", "Spirits_statistics", "Beer_and_cider_statistics" ]
# New tab names
tabs_names_to_process = ["Wine_Duty_(wine)_tables", "Wine_Duty_(made_wine)_tables", "Spirits_Duty_tables", "Beer_Duty_and_Cider_Duty_tables" ]

for tab_name in tabs_names_to_process:

    # Raise an exception if one of our required tabs is missing
    if tab_name not in [x.name for x in tabs]:
        raise ValueError(f'Aborting. A tab named {tab_name} required but not found')

    tab = [x for x in tabs if x.name == tab_name][0]
    # savepreviewhtml(tab, fname=tab.name+ "Preview.html")

# +
# Old tab names
#tabs_names_to_process = ["Wine_statistics", "Made_wine_statistics", "Spirits_statistics", "Beer_and_cider_statistics" ]
# New tab names
tabs_names_to_process = ["Wine_Duty_(wine)_tables", "Wine_Duty_(made_wine)_tables", "Spirits_Duty_tables", "Beer_Duty_and_Cider_Duty_tables" ]

for tab_name in tabs_names_to_process:

    # Raise an exception if one of our required tabs is missing
    if tab_name not in [x.name for x in tabs]:
        raise ValueError(f'Aborting. A tab named {tab_name} required but not found')

    tab = [x for x in tabs if x.name == tab_name][0]
    # savepreviewhtml(tab, fname=tab.name+ "Preview.html")


    unwanted = tab.filter(contains_string("End of worksheet"))
    alcohol_type = tab.name

    if tab_name == tabs_names_to_process[0]:
        anchor = tab.excel_ref('A7')#.filter(contains_string("Table 1a:")).assert_one()
        bulletin_type = anchor.fill(RIGHT).is_not_blank().is_not_whitespace()
        measure_type = "clearances duty-receipts"
        unit = "hectolitres gbp-million"
        year_month = tab.filter(contains_string("clearances data"))
        # savepreviewhtml(year_month, fname=tab.name+ "Preview.html")
        combined_unwanted = unwanted|year_month
        period = anchor.fill(DOWN).is_not_blank().is_not_whitespace()-combined_unwanted
        observations = period.waffle(bulletin_type)

    if tab_name == tabs_names_to_process[1]:
        anchor = tab.excel_ref('A8')
        bulletin_type = anchor.fill(RIGHT).is_not_blank().is_not_whitespace()
        measure_type = "clearances duty-receipts"
        unit = "hectolitres gbp-million"
        year_month = tab.filter(contains_string("clearances statistics by"))
        combined_unwanted = unwanted|year_month
        period = anchor.fill(DOWN).is_not_blank().is_not_whitespace()-combined_unwanted
        observations = period.waffle(bulletin_type)

    elif tab_name == tabs_names_to_process[2]:
        anchor = tab.excel_ref('A8')
        bulletin_type = anchor.fill(RIGHT).is_not_blank().is_not_whitespace()
        measure_type = "production clearances duty-receipts"
        unit = "hectolitres-of-alcohol gbp-million"
        year_month = tab.filter(contains_string("clearances statistics by"))
        combined_unwanted = unwanted|year_month
        period = anchor.fill(DOWN).is_not_blank().is_not_whitespace()-combined_unwanted
        observations = period.waffle(bulletin_type)

    elif tab_name == tabs_names_to_process[3]:
        anchor = tab.excel_ref('A6')
        unwanted_bulletin = anchor.fill(RIGHT).is_not_blank().is_not_whitespace().filter(lambda x: type(x.value) != ("Total alcohol duty receipts(£ million)") not in x.value)
        cider_lower = bulletin_type.filter(contains_string("Total cider")).is_not_blank().is_not_whitespace()
        cider_upper = bulletin_type.filter(contains_string("Total Cider")).is_not_blank().is_not_whitespace()
        total_cider = cider_lower|cider_upper
        bulletin_type = unwanted_bulletin-total_cider
        # savepreviewhtml(bulletin_type, fname=tab.name+ "Preview.html")
        measure_type = "production clearances duty-receipts"
        unit = "hectolitres-of-alcohol gbp-million"
        year_month = tab.filter(contains_string("production statistics by"))
        combined_unwanted = unwanted|year_month
        period = anchor.fill(DOWN).is_not_blank().is_not_whitespace()-combined_unwanted
        observations = period.waffle(bulletin_type)

    dimensions = [
        HDim(period, 'Period', DIRECTLY, LEFT),
        HDim(bulletin_type, 'Bulletin Type', DIRECTLY, ABOVE),
        HDim(year_month, "Break Down", CLOSEST, ABOVE),
        HDimConst("Alcohol Type", tab.name),
        HDimConst("Measure Type", measure_type),
        HDimConst("Unit", unit)
        ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    savepreviewhtml(tidy_sheet, fname=tab.name+ "Preview.html")
    tidied_sheets.append(tidy_sheet.topandas())

# +
# Old tab names
#tabs_names_to_process = ["Wine_statistics", "Made_wine_statistics", "Spirits_statistics", "Beer_and_cider_statistics" ]
# New tab names
# tabs_names_to_process = ["Wine_Duty_(wine)_tables", "Wine_Duty_(made_wine)_tables", "Spirits_Duty_tables", "Beer_Duty_and_Cider_Duty_tables" ]

# for tab_name in tabs_names_to_process:

#     # Raise an exception if one of our required tabs is missing
#     if tab_name not in [x.name for x in tabs]:
#         raise ValueError(f'Aborting. A tab named {tab_name} required but not found')

    # Select the tab in question
tab = [x for x in tabs if x.name == tab_name][0]

unwanted = tab.filter(contains_string("End of worksheet"))
alcohol_type = tab.name
     
if tab_name == tabs_names_to_process[0]:
    anchor = tab.excel_ref('A7')#.filter(contains_string("Table 1a:")).assert_one()
    bulletin_type = anchor.fill(RIGHT).is_not_blank().is_not_whitespace()
    measure_type = "clearances duty-receipts"
    unit = "hectolitres gbp-million"
    year_month = tab.filter(contains_string("clearances data"))
    combined_unwanted = unwanted|year_month
    period = anchor.fill(DOWN).is_not_blank().is_not_whitespace()-combined_unwanted
    observations = period.waffle(bulletin_type)
        # savepreviewhtml(observations, fname=tab.name+ "Preview.html")
    # elif tab_name == tabs_names_to_process[1]:
    #     anchor = tab.excel_ref('A8')
    #     bulletin_type = anchor.fill(RIGHT).is_not_blank().is_not_whitespace()
    #     measure_type = "clearances duty-receipts"
    #     unit = "hectolitres gbp-million"
    #     year_month = tab.filter(contains_string("clearances statistics by"))
    #     combined_unwanted = unwanted|year_month
    #     period = anchor.fill(DOWN).is_not_blank().is_not_whitespace()-combined_unwanted
    # elif tab_name == tabs_names_to_process[2]:
    #     anchor = tab.excel_ref('A8')
    #     bulletin_type = anchor.fill(RIGHT).is_not_blank().is_not_whitespace()
    #     measure_type = "production clearances duty-receipts"
    #     unit = "hectolitres-of-alcohol gbp-million"
    #     year_month = tab.filter(contains_string("clearances statistics by"))
    #     combined_unwanted = unwanted|year_month
    #     period = anchor.fill(DOWN).is_not_blank().is_not_whitespace()-combined_unwanted

    # elif tab_name == tabs_names_to_process[3]:
    #     anchor = tab.excel_ref('A6')
    #     unwanted_bulletin = anchor.fill(RIGHT).is_not_blank().is_not_whitespace().filter(lambda x: type(x.value) != ("Total alcohol duty receipts(£ million)") not in x.value)
    #     cider_lower = bulletin_type.filter(contains_string("Total cider")).is_not_blank().is_not_whitespace()
    #     cider_upper = bulletin_type.filter(contains_string("Total Cider")).is_not_blank().is_not_whitespace()
    #     total_cider = cider_lower|cider_upper
    #     bulletin_type = unwanted_bulletin-total_cider
    #     savepreviewhtml(bulletin_type, fname=tab.name+ "Preview.html")
    #     measure_type = "production clearances duty-receipts"
    #     unit = "hectolitres-of-alcohol gbp-million"
    #     year_month = tab.filter(contains_string("production statistics by"))
    #     combined_unwanted = unwanted|year_month
    #     period = anchor.fill(DOWN).is_not_blank().is_not_whitespace()-combined_unwanted


    # bulletin_type = anchor.fill(RIGHT).is_not_blank().is_not_whitespace()
    
    # alcohol_type = tab.name


    # if tab_name == tabs_names_to_process[0]:
    #     measure_type = "clearances duty-receipts"
    #     unit = "hectolitres gbp-million"
    #     year_month = tab.filter(contains_string("clearances data"))
    #     combined_unwanted = unwanted|year_month
    #     period = anchor.fill(DOWN).is_not_blank().is_not_whitespace()-combined_unwanted

    # elif tab_name == tabs_names_to_process[1]:
    #     measure_type = "clearances duty-receipts"
    #     unit = "hectolitres gbp-million"
    #     year_month = tab.filter(contains_string("clearances statistics by"))
    #     combined_unwanted = unwanted|year_month
    #     period = anchor.fill(DOWN).is_not_blank().is_not_whitespace()-combined_unwanted
    
    # elif tab_name == tabs_names_to_process[2]:
    #     measure_type = "production clearances duty-receipts"
    #     unit = "hectolitres-of-alcohol gbp-million"
    #     year_month = tab.filter(contains_string("clearances statistics by"))
    #     combined_unwanted = unwanted|year_month
    #     period = anchor.fill(DOWN).is_not_blank().is_not_whitespace()-combined_unwanted

    # elif tab_name == tabs_names_to_process[3]:
    #     measure_type = "production clearances duty-receipts"
    #     unit = "hectolitres-of-alcohol gbp-million"
    #     year_month = tab.filter(contains_string("production statistics by"))
    #     combined_unwanted = unwanted|year_month
    #     period = anchor.fill(DOWN).is_not_blank().is_not_whitespace()-combined_unwanted
    
    # else:
    #     raise ValueError('Aborting, we don\`t have handling for tab: {tab_name}')

    # observations = period.waffle(bulletin_type)

    dimensions = [
        HDim(period, 'Period', DIRECTLY, LEFT),
        HDim(bulletin_type, 'Bulletin Type', DIRECTLY, ABOVE),
        HDim(year_month, "Break Down", CLOSEST, ABOVE),
        HDimConst("Alcohol Type", tab.name),
        HDimConst("Measure Type", measure_type),
        HDimConst("Unit", unit)
        ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    savepreviewhtml(tidy_sheet, fname=tab.name+ "Preview.html")
    tidied_sheets.append(tidy_sheet.topandas())


# +
if tab_name == tabs_names_to_process[3]:
        anchor = tab.excel_ref('A6')
        unwanted_bulletin = anchor.fill(RIGHT).is_not_blank().is_not_whitespace().filter(lambda x: type(x.value) != ("Total alcohol duty receipts(£ million)") not in x.value)
        cider_lower = bulletin_type.filter(contains_string("Total cider")).is_not_blank().is_not_whitespace()
        cider_upper = bulletin_type.filter(contains_string("Total Cider")).is_not_blank().is_not_whitespace()
        total_cider = cider_lower|cider_upper
        bulletin_type = unwanted_bulletin-total_cider
        measure_type = "production clearances duty-receipts"
        unit = "hectolitres-of-alcohol gbp-million"
        year_month = tab.filter(contains_string("production statistics by"))
        combined_unwanted = unwanted|year_month
        period = anchor.fill(DOWN).is_not_blank().is_not_whitespace()-combined_unwanted
        observations = period.waffle(bulletin_type)
        savepreviewhtml(observations, fname=tab.name+ "Preview.html")

dimensions = [
        HDim(period, 'Period', DIRECTLY, LEFT),
        HDim(bulletin_type, 'Bulletin Type', DIRECTLY, ABOVE),
        HDim(year_month, "Break Down", CLOSEST, ABOVE),
        HDimConst("Alcohol Type", tab.name),
        HDimConst("Measure Type", measure_type),
        HDimConst("Unit", unit)
        ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    # savepreviewhtml(tidy_sheet, fname=tab.name+ "Preview.html")
    tidied_sheets.append(tidy_sheet.topandas())
# -



df = pd.concat(tidied_sheets, sort = True)

df

df.rename(columns = {'OBS': 'Value', 'DATAMARKER':'Marker'}, inplace = True)


# +
# Measure Type - Tax would be a more appropriate value rather than production.

#check column Bulletin Type string contains the word clearances or Clearances and make Measure Type  = clearances
df.loc[(df['Bulletin Type']).str.contains('clearances') | (df['Bulletin Type']).str.contains('Clearances'),'Measure Type']='clearances'
#check column Bulletin Type string contains the word receipts and make Measure Type  = duty-receipts
df.loc[(df['Bulletin Type']).str.contains('receipts'),'Measure Type']='duty-receipts'
#check column Bulletin Type string contains the word receipts and make Measure Type  = duty-receipts
df.loc[(df['Bulletin Type']).str.contains('production'),'Measure Type']='production'

#Setting the Unit based on Measure Type Column 
df["Unit"] = df["Measure Type"].map(lambda x: "hectolitres" if x == "clearances" else 
                                    ("gbp-million" if x == "duty-receipts" else 
                                     ("hectolitres-of-alcohol" if x == "production" else "U")))



# +
# #check column Bulletin Type string contains the word receipts and make Measure Type  = duty-receipts
# df.loc[(df['Bulletin Type']).str.contains('production'),'Measure Type']='Tax'

# #Setting the Unit based on Measure Type Column 
# df["Unit"] = df["Measure Type"].map(lambda x: "hectolitres" if x == "clearances" else 
#                                     ("gbp-million" if x == "duty-receipts" else 
#                                      ("hectolitres-of-alcohol" if x == "Tax" else "U")))
# -

df

df['Measure Type'].unique()

f1=(df['Bulletin Type'] =='Total alcohol duty receipts (£ million)')
df.loc[f1,'Alcohol Type'] = 'all'


df["Alcohol Type"] = df["Alcohol Type"].map(lambda x: "wine" if x == tabs_names_to_process[0] else
                                    ("made-wine" if x == tabs_names_to_process[1] else
                                     ("spirits" if x == tabs_names_to_process[2] else
                                      ("beer-and-cider" if x == tabs_names_to_process[3] else x))))


df['Bulletin Type'] = df['Bulletin Type'].str.replace('clearances (hectolitres of alcohol)','clearances (alcohol)', regex=False)
df['Bulletin Type'] = df['Bulletin Type'].str.replace('production (hectolitres of alcohol)','production (alcohol)', regex=False)
df['Unit'] = df['Unit'].str.replace('hectolitres-of-alcohol','hectolitres', regex=False)


# +
# # Duty receipts – hectolitres this should be pound/millions
# df['Unit'] = df['Unit'].str.replace('hectolitres-of-alcohol','pound/millions', regex=False)
# -

df['Bulletin Type'] = df['Bulletin Type'].str.replace("(hectolitres)","")
df['Bulletin Type'] = df['Bulletin Type'].str.replace("(£ million)","")
df["Bulletin Type"] = df["Bulletin Type"].map(lambda x: pathify(x))


#N/As change to 0 and put not-applicable in Marker column
df['Marker'].replace('N/A', 'not-applicable', inplace=True)
f1=(df['Marker'] =='not-applicable')
df.loc[f1,'Value'] = 0
df['Period'] = df['Period'].str.strip()


# Marker column - requirements satisfied
df['Marker'][df['Period'].str.contains("provisional")] = 'provisional'
df['Period'] = df['Period'].str.replace('provisional','')
df['Marker'][df['Period'].str.contains("revised")] = 'revised'
df['Period'] = df['Period'].str.replace('revised','')
df['Period'] = df['Period'].astype(str).replace('\.0', '', regex=True)
df['Period'] = df['Period'].str.strip()
# As the value 2815(estimate) and 2460(estimate) in the spread sheet is not picked up by databaker properly
# A quick fix is done to resolve the issue
df['Value'][df.Marker == ',815 (estimate)'] = 2815
df['Value'][df.Marker == ',460 (estimate)'] = 2460
df = df.replace(np.nan, '', regex=True)
df.loc[df['Marker'].str.contains('estimate'), 'Marker'] = 'estimate'


import calendar
import datetime
tables = ['Table 1a','Table 1b','Table 1c','Table 2a','Table 2b','Table 2c','Table 3a','Table 3b','Table 3c','Table 4a','Table 4b', 'Table 4c']
for t in tables:
    df = df[~df['Period'].str.contains(t)]
df['Period'] = df['Period'].str.replace('[ [ ]]', '')
df['Period'] = df['Period'].str.strip()


# +
now = datetime.datetime.now()
yrnow = now.year
yrlast = yrnow - 1

for i in range(1,12):
    yrmthlast = calendar.month_name[i] + ' ' + str(yrlast)
    yrmthnow = calendar.month_name[i] + ' ' + str(yrnow)
    if i < 10:
        mthstr = '0' + str(i)
    else:
        mthstr = str(i)
    df['Period'][df['Period'].str.contains(yrmthlast)] = 'month/' + str(yrlast) + '-' + mthstr
    df['Period'][df['Period'].str.contains(yrmthnow)] = 'month/' + str(yrnow) + '-' + mthstr

df['Period'][df['Period'].str.contains(str(yrlast) + ' to ' + str(yrnow))] = 'government-year/' + str(yrlast) + '-' + str(yrnow)


# -

#Period column 
def left(s, amount):
    return s[:amount]
def right(s, amount):
    return s[-amount:]
def date_time (date):
    if len(date)  == 4:
        return 'year/' + left(date, 4)
    if len(date)  == 6:
        month_name = left(date, 3)
        month_number = datetime.datetime.strptime(month_name, '%b').month
        month_number = '{:02}'.format(month_number)
        return 'month/' + '20' + right(date, 2) + '-' + str(month_number) 
    if len(date)  == 7:
        return 'government-year/' + left(date, 4) + '-' + left(date, 2) + right(date, 2)
    elif len(date) == 10:
        return 'month/' + left(date, 7) 
    elif len(date) == 12:
        return 'government-year/' + left(date, 4) + '-' + left(date, 2) + right(date, 2)
    else:
        return date
df['Period'] =  df["Period"].apply(date_time)


#quick fix for odd values 
df = df.replace({'Period' : {'government-year/1999-1900' : 'government-year/1999-2000', 'December 2020' : 'month/2020-12'}})


df['Marker'] = df['Marker'].str.replace('[','')
df['Marker'] = df['Marker'].str.replace(']','')
df['Marker'] = df['Marker'].apply(pathify)
df['Marker'].unique()


# The multimeasures for this dataset is yet to be defined by DMs.
# The way to proceed with cubes class for multimeasures is yet to be finalized.
df


df['Alcohol Type'].unique()

df['Measure Type'].unique()

df['Unit'].unique()

# +
# Alcohol Type - Spirits are measured in hectolitres of alcohol

# df.loc[df['Alcohol Type'] == 'spirits', 'Unit'].unique()
# df.query('Alcohol Type == spirits')['Unit']
df['Unit'][df['Alcohol Type'] == 'spirits']
# -

# This is a multi-unit and multi-measure dataset so splitting up for now as not sure what is going on with anything anymore! :-(
# Splitting data into 3 and changing scraper values based on output data
cubes = Cubes("info.json")
tchange = ['Clearances','Duty Receipts','Production']
uchange = ['hectolitres', 'gbp-million', 'hectolitres']
# mchange = ['Clearances','Duty Receipts','Tax']
scraper.dataset.family = 'trade'
for x in range(3): 
    dat = df[df['Measure Type'] == pathify(tchange[x])]
    scraper.dataset.title = f"Alcohol Bulletin - {tchange[x]}"
    scraper.dataset.comment = f"Monthly {tchange[x]} statistics from the 4 different alcohol duty regimes administered by HM Revenue and Customs"
    if x == 2:
        scraper.dataset.description = scraper.dataset.comment + f'\n Table of historic spirits, beer and cider {tchange[x]}'  
    else :
        scraper.dataset.description = scraper.dataset.comment + f'\n Table of historic wine, made wine, spirits, beer and cider {tchange[x]}'
    print(str(x) + " - " + scraper.dataset.title + " - " + pathify(tchange[x]))
    #print(dat.columns)
    with open("info.json", "r") as jsonFile:
        data = json.load(jsonFile)
    data["transform"]["columns"]["Value"]["measure"] = f"http://gss-data.org.uk/def/measure/{pathify(tchange[x])}"
    data["transform"]["columns"]["Value"]["unit"] = f"http://gss-data.org.uk/def/concept/measurement-units/{uchange[x]}"
    with open("info.json", "w") as jsonFile:
        json.dump(data, jsonFile)
    del data
    
    if 'Measure Type' in dat.columns:
        del dat['Measure Type']
    if 'Unit' in dat.columns:
        del dat['Unit']
    
    cubes.add_cube(copy.deepcopy(scraper), dat, scraper.dataset.title)
#del df
cubes.output_all()


