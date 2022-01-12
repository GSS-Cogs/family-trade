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
        period = anchor.fill(DOWN).is_not_blank().is_not_whitespace()-unwanted

    if tab_name == tabs_names_to_process[1]:
        anchor = tab.excel_ref('A8')
        bulletin_type = anchor.fill(RIGHT).is_not_blank().is_not_whitespace()
        measure_type = "clearances duty-receipts"
        unit = "hectolitres gbp-million"
        period = anchor.fill(DOWN).is_not_blank().is_not_whitespace()-unwanted

    elif tab_name == tabs_names_to_process[2]:
        anchor = tab.excel_ref('A8')
        bulletin_type = anchor.fill(RIGHT).is_not_blank().is_not_whitespace()
        measure_type = "production clearances duty-receipts"
        unit = "hectolitres-of-alcohol gbp-million"
        combined_unwanted = unwanted
        period = anchor.fill(DOWN).is_not_blank().is_not_whitespace()-unwanted

# Beer production
    elif tab_name == tabs_names_to_process[3]:
        anchor = tab.excel_ref('A6')
        unwanted_bulletin = anchor.fill(RIGHT).is_not_blank().is_not_whitespace().filter(lambda x: type(x.value) != "Total alcohol duty receipts(£ million)" not in x.value) 
        cider_lower = unwanted_bulletin.filter(contains_string("Total cider")).is_not_blank().is_not_whitespace()
        cider_upper = unwanted_bulletin.filter(contains_string("Total Cider")).is_not_blank().is_not_whitespace()
        total_cider = cider_lower|cider_upper
        bulletin_type = unwanted_bulletin-total_cider
        measure_type = "production clearances duty-receipts"
        unit = "hectolitres-of-alcohol gbp-million"
        period = anchor.fill(DOWN).is_not_blank().is_not_whitespace()-unwanted

    observations = period.waffle(bulletin_type)
    dimensions = [
        HDim(period, 'Period', DIRECTLY, LEFT),
        HDim(bulletin_type, 'Bulletin Type', DIRECTLY, ABOVE),
        HDimConst("Alcohol Type", tab.name),
        HDimConst("Measure Type", measure_type),
        HDimConst("Unit", unit)
        ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    # savepreviewhtml(tidy_sheet, fname=tab.name+ "Preview.html")
    tidied_sheets.append(tidy_sheet.topandas())

# +
# CIDER production.
if tab_name == tabs_names_to_process[3]:
        anchor = tab.excel_ref('A6')
        cider_lower = anchor.shift(7, 0).is_not_blank().is_not_whitespace()
        cider_upper = anchor.shift(9, 0).is_not_blank().is_not_whitespace()
        bulletin_type = cider_lower|cider_upper
        measure_type = "production clearances duty-receipts"
        unit = "hectolitres-of-alcohol gbp-million"
        period = anchor.fill(DOWN).is_not_blank().is_not_whitespace()-unwanted
        observations = period.waffle(bulletin_type)

dimensions = [
        HDim(period, 'Period', DIRECTLY, LEFT),
        HDim(bulletin_type, 'Bulletin Type', DIRECTLY, ABOVE),
        HDimConst("Alcohol Type", tab.name),
        HDimConst("Measure Type", measure_type),
        HDimConst("Unit", unit)
        ]
tidy_sheet = ConversionSegment(tab, dimensions, observations)
# savepreviewhtml(tidy_sheet, fname=tab.name+ "Preview.html")
tidied_sheets.append(tidy_sheet.topandas())
# -

df = pd.concat(tidied_sheets, sort = True).fillna('')

df.rename(columns = {'OBS': 'Value', 'DATAMARKER':'Marker'}, inplace = True)


# +
# Measure Type - Tax would be a more appropriate value rather than production.

#check column Bulletin Type & Cider Bulletin string contains the word clearances or Clearances and make Measure Type  = clearances
df.loc[(df['Bulletin Type']).str.contains('clearances') | (df['Bulletin Type']).str.contains('Clearances'),'Measure Type']='clearances'

#check column Bulletin Type & Cider Bulletin string contains the word receipts and make Measure Type  = duty-receipts
df.loc[(df['Bulletin Type']).str.contains('receipts'),'Measure Type']='duty-receipts'


#check column Bulletin Type & Cider Bulletin string contains the word receipts and make Measure Type  = duty-receipts
df.loc[(df['Bulletin Type']).str.contains('production'),'Measure Type']='tax'

#Setting the Unit based on Measure Type Column 
df["Unit"] = df["Measure Type"].map(lambda x: "hectolitres-of-alcohol" if x == "clearances" else 
                                    ("gbp-million" if x == "duty-receipts" else 
                                     ("hectolitres-of-alcohol" if x == "tax" else "U")))

# -


f1=(df['Bulletin Type'] =='Total alcohol duty receipts (£ million)')
df.loc[f1,'Alcohol Type'] = 'all'


df['Alcohol Type'].unique()

df["Alcohol Type"] = df["Alcohol Type"].map(lambda x: "wine" if x == tabs_names_to_process[0] else
                                    ("made-wine" if x == tabs_names_to_process[1] else
                                     ("spirits" if x == tabs_names_to_process[2] else
                                      ("beer" if x == tabs_names_to_process[3] else x))))


# cider in Alcohol Type column (seperate from beer)
df.loc[(df['Bulletin Type'] == 'Total cider clearances(thousand hectolitres)'), 'Alcohol Type'] = 'cider'
df.loc[(df['Bulletin Type'] == 'Total Cider Duty receipts(£ million)'), 'Alcohol Type'] = 'cider'

df['Bulletin Type'] = df['Bulletin Type'].str.replace('clearances (hectolitres of alcohol)','clearances (alcohol)', regex=False)
df['Bulletin Type'] = df['Bulletin Type'].str.replace('production (hectolitres of alcohol)','production (alcohol)', regex=False)
# df['Unit'] = df['Unit'].str.replace('hectolitres-of-alcohol','hectolitres', regex=False)


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
df['Marker'] = df['Marker'].str.replace('x','not-available')
df['Marker'] = df['Marker'].str.replace('d','data-not-provided')
df['Marker'].unique()


# The multimeasures for this dataset is yet to be defined by DMs.
# The way to proceed with cubes class for multimeasures is yet to be finalized.
df


df['Alcohol Type'].unique()

# Observations rounded to two decimal places
df['Value'] = pd.to_numeric(df.Value, errors = 'coerce')
df.round({"Value":2})

df['Bulletin Type'].unique()

# +
# df['Alcohol Type'].unique()

# +
# df['Measure Type'].unique()

# +
# df.loc[df['Alcohol Type'] == 'spirits', 'Measure Type'].unique()

# +
# Alcohol Type - Spirits are measured in hectolitres of alcohol
df.loc[df['Alcohol Type'] == 'spirits','Unit'] = 'hectolitres-of-alcohol'

# Duty receipts – hectolitres this should be pound/millions
df.loc[df['Measure Type'] == 'duty-receipts', 'Unit'] = 'gbp-million'
# -

df.loc[df['Unit'] == 'hectolitres-of-alcohol', "Alcohol Type"].unique()

df.loc[df['Alcohol Type'] == 'spirits', 'Unit'].unique()

df['Measure Type'].unique()

df.loc[df['Measure Type'] == 'tax', 'Unit'].unique()

df['Unit'].unique()

# +
#Split data for measure type tax only Clearances
df_clearance = df[df['Measure Type'] == 'clearances']
# Metadata for Clearances cube 
scraper.dataset.title = "Alcohol Bulletin - clearances"
scraper.dataset.comment = 'Monthly Production statistics from the 4 different alcohol duty regimes administered by HM Revenue and Customs'
scraper.dataset.description = scraper.dataset.comment + ' Monthly Production statistics from the 4 different alcohol duty regimes administered by HM Revenue and Customs Table of historic wine, made wine, spirits, beer and cider'

with open("info.json", "r") as jsonFile:
    data = json.load(jsonFile)
data["transform"]["columns"]["Value"]["measure"] = f"http://gss-data.org.uk/def/measure/clearances"
data["transform"]["columns"]["Value"]["unit"] = f"http://gss-data.org.uk/def/concept/measurement-units/hectolitres-of-alcohol"
with open("info.json", "w") as jsonFile:
    json.dump(data, jsonFile)
del data  

if 'Measure Type' in df_clearance.columns:
    del df_clearance['Measure Type']
if 'Unit' in df_clearance.columns:
    del df_clearance['Unit']
# -

cubes.add_cube(copy.deepcopy(scraper), df_clearance, scraper.dataset.title)

# +
#Split data for measure type tax only Duty-Receipts
df_duty_re = df[df['Measure Type'] == 'duty-receipts']
# Metadata for Duty-Receipts cube 
scraper.dataset.title = "Alcohol Bulletin - duty-receipts"
scraper.dataset.comment = 'Monthly Production statistics from the 4 different alcohol duty regimes administered by HM Revenue and Customs'
scraper.dataset.description = scraper.dataset.comment + ' Monthly Production statistics from the 4 different alcohol duty regimes administered by HM Revenue and Customs Table of historic wine, made wine, spirits, beer and cider'

with open("info.json", "r") as jsonFile:
    data = json.load(jsonFile)
data["transform"]["columns"]["Value"]["measure"] = f"http://gss-data.org.uk/def/measure/duty-receipts"
data["transform"]["columns"]["Value"]["unit"] = f"http://gss-data.org.uk/def/concept/measurement-units/gbp-million"
with open("info.json", "w") as jsonFile:
    json.dump(data, jsonFile)
del data   
     
if 'Measure Type' in df_duty_re.columns:
    del df_duty_re['Measure Type']
if 'Unit' in df_duty_re.columns:
    del df_duty_re['Unit']
# -

cubes.add_cube(copy.deepcopy(scraper), df_duty_re, scraper.dataset.title)

# +
#Split data for measure type tax only (Production)
df_tax = df[df['Measure Type'] == 'tax']
# Metadata for Production cube 
scraper.dataset.title = "Alcohol Bulletin - Production"
scraper.dataset.comment = 'Monthly Production statistics from the 4 different alcohol duty regimes administered by HM Revenue and Customs'
scraper.dataset.description = scraper.dataset.comment + ' Monthly Production statistics from the 4 different alcohol duty regimes administered by HM Revenue and Customs Table of historic spirits, beer and cider Production'

with open("info.json", "r") as jsonFile:
    data = json.load(jsonFile)
data["transform"]["columns"]["Value"]["measure"] = f"http://gss-data.org.uk/def/measure/tax"
data["transform"]["columns"]["Value"]["unit"] = f"http://gss-data.org.uk/def/concept/measurement-units/hectolitres-of-alcohol"
with open("info.json", "w") as jsonFile:
    json.dump(data, jsonFile)
del data 
        
if 'Measure Type' in df_tax.columns:
    del df_tax['Measure Type']
if 'Unit' in df_tax.columns:
    del df_tax['Unit']
# -

cubes.add_cube(copy.deepcopy(scraper), df_tax, scraper.dataset.title)

# +
# df
# -

cubes.output_all()
