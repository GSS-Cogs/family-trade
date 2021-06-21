# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.4.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

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

# +
trace = TransformTrace()
cubes = Cubes("info.json")

scraper = Scraper(seed="info.json")
scraper.distributions = [x for x in scraper.distributions if hasattr(x, "mediaType")]
scraper

# +
# Conversion of ODS to XLS

original_tabs = scraper.distribution(latest=True, mediaType=ODS)

with original_tabs.open() as ods_obj:
    excel_obj = BytesIO()
    book = pyexcel.get_book(file_type = 'ods', file_content = ods_obj, library = 'pyexcel-ods3')
    old_tab_names = book.sheet_names()
    
    for old_tab in old_tab_names:
        if len(old_tab) > 31:
            new_tab_names = book.sheet_names()
            find_index = new_tab_names.index(old_tab)
            book.remove_sheet(book.sheet_names()[find_index])
            
    book.save_to_memory(file_type = 'xls', stream = excel_obj)
    tableset = messytables.excel.XLSTableSet(fileobj = excel_obj)
    tabs = list(xypath.loader.get_sheets(tableset, "*"))
# -

distribution = scraper.distribution(latest = True, mediaType=ODS)
datasetTitle = distribution.title
columns = ["Period", "Marker", "Bulletin Type", "Alcohol Type", "Measure Type", "Unit"]
distribution.downloadURL

#tabs_names_to_process = ["Wine_statistics", "Made_wine_statistics", "Spirits_statistics", "Beer_and_cider_statistics" ]
tabs_names_to_process = ["Wine_Duty_(wine)_tables", "Wine_Duty_(made_wine)_tables", "Spirits_Duty_tables", "Beer_Duty_and_Cider_Duty_tables" ]
for tab_name in tabs_names_to_process:

    # Raise an exception if one of our required tabs is missing
    if tab_name not in [x.name for x in tabs]:
        raise ValueError(f'Aborting. A tab named {tab_name} required but not found')

    # Select the tab in question
    tab = [x for x in tabs if x.name == tab_name][0]
    
    trace.start(datasetTitle, tab, columns, distribution.downloadURL)

    #anchor = tab.excel_ref('A').filter(contains_string("by financial year")).assert_one()
    
    if tab_name == tabs_names_to_process[0]:
        anchor = tab.excel_ref('A').filter(contains_string("Table 1a. Wine Duty")).assert_one()
    elif tab_name == tabs_names_to_process[1]:
        anchor = tab.excel_ref('A').filter(contains_string("Table 2a. Wine Duty")).assert_one()
    elif tab_name == tabs_names_to_process[2]:
        anchor = tab.excel_ref('A').filter(contains_string("Table 3a. Spirits Duty")).assert_one()
    elif tab_name == tabs_names_to_process[3]:
        anchor = tab.excel_ref('A').filter(contains_string("Table 4a. Beer Duty and Cider Duty")).assert_one()
    print(tab_name)
    
    period = anchor.expand(DOWN).is_not_blank().is_not_whitespace()
    trace.Period("Taken from column A")

    bulletin_type = anchor.fill(RIGHT).is_not_blank().is_not_whitespace()
    trace.Bulletin_Type("Defined from column B obvious header and across")

    alcohol_type = tab.name
    trace.Alcohol_Type("Name of tabs in XLS sheet")

    #if tab_name == "Wine_statistics":
    if tab_name == tabs_names_to_process[0]:
        measure_type = "clearances duty-receipts"
        unit = "hectolitres gbp-million"
        observations = bulletin_type.fill(DOWN).is_not_blank().is_not_whitespace()

    #elif tab_name == "Made_wine_statistics":
    elif tab_name == tabs_names_to_process[1]:
        measure_type = "clearances duty-receipts"
        unit = "hectolitres gbp-million"
        observations = bulletin_type.fill(DOWN).is_not_blank().is_not_whitespace()-tab.excel_ref("J6").expand(DOWN)-tab.excel_ref("K6").expand(DOWN)
    
    #elif tab_name == "Spirits_statistics":
    elif tab_name == tabs_names_to_process[2]: 
        measure_type = "production clearances duty-receipts"
        unit = "hectolitres-of-alcohol gbp-million"
        observations = bulletin_type.fill(DOWN).is_not_blank().is_not_whitespace()-tab.excel_ref("J6").expand(DOWN)

    #elif tab_name == "Beer_and_cider_statistics":
    elif tab_name == tabs_names_to_process[3]:
        measure_type = "production clearances duty-receipts"
        unit = "hectolitres-of-alcohol gbp-million"
        observations = bulletin_type.fill(DOWN).is_not_blank().is_not_whitespace()-tab.excel_ref("K6").expand(DOWN)
    
    else:
        raise ValueError('Aborting, we don\`t have handling for tab: {tab_name}')

    trace.Measure_Type("Measure is different for different values")
    trace.Unit("Unit is different for different values")
    
    dimensions = [
        HDim(period, 'Period', DIRECTLY, LEFT),
        HDim(bulletin_type, 'Bulletin Type', DIRECTLY, ABOVE),
        HDimConst("Alcohol Type", tab.name),
        HDimConst("Measure Type", measure_type),
        HDimConst("Unit", unit)
        ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
    trace.with_preview(tidy_sheet)
    trace.store("combined_dataframe", tidy_sheet.topandas())
    

df = trace.combine_and_trace(datasetTitle, "combined_dataframe")
df.rename(columns = {'OBS': 'Value', 'DATAMARKER':'Marker'}, inplace = True)

df['Marker'].unique() 

# +
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
# -

f1=(df['Bulletin Type'] =='Total alcohol duty receipts (£ million)')
df.loc[f1,'Alcohol Type'] = 'all'

df["Alcohol Type"] = df["Alcohol Type"].map(lambda x: "wine" if x == "Wine_statistics" else 
                                    ("made-wine" if x == "Made_wine_statistics" else 
                                     ("spirits" if x == "Spirits_statistics" else
                                      ("beer-and-cider" if x == "Beer_and_cider_statistics" else x))))

df['Bulletin Type'] = df['Bulletin Type'].str.replace('clearances (hectolitres of alcohol)','clearances (alcohol)', regex=False)
df['Bulletin Type'] = df['Bulletin Type'].str.replace('production (hectolitres of alcohol)','production (alcohol)', regex=False)
df['Unit'] = df['Unit'].str.replace('hectolitres-of-alcohol','hectolitres', regex=False)

# +
df['Bulletin Type'] = df['Bulletin Type'].str.rsplit(pat = "(hectolitres)", expand = True)
df['Bulletin Type'] = df['Bulletin Type'].str.rsplit(pat = "(£ million)", expand = True)
#df['Bulletin Type'] = df['Bulletin Type'].str.rsplit(pat = "(hectolitres of alcohol)", expand = True)

df["Bulletin Type"] = df["Bulletin Type"].map(lambda x: pathify(x))
# -

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
    else:
        return date
df['Period'] =  df["Period"].apply(date_time)


#quick fix for odd values 
df = df.replace({'Period' : {'government-year/1999-1900' : 'government-year/1999-2000'}})

df['Marker'].unique()

# +
#cubes.add_cube(scraper, df.drop_duplicates(), datasetTitle)
#cubes.output_all()

# +
trace.render()

# The multimeasures for this dataset is yet to be defined by DMs.
# The way to proceed with cubes class for multimeasures is yet to be finalized.

# +
# This is a multi-unit and multi-measure dataset so splitting up for now as not sure what is going on with anything anymore! :-(
# Splitting data into 3 and changing scraper values based on output data
cubes = Cubes("info.json")
tchange = ['Clearances','Duty Receipts','Production']
uchange = ['hectolitres', 'gbp-million', 'hectolitres']
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

del df
cubes.output_all()

# +
#for c in df.columns:
#    if (c != 'Value') & (c != 'Period'):
#        print(c)
#        print(df[c].unique())
#        print("###################################")

# +
#scraper.dataset.family = 'trade'
#codelistcreation = ['Bulletin Type'] 
#df = df
#codeclass = CSVCodelists()#
#for cl in codelistcreation:
#    if cl in df.columns:
#        codeclass.create_codelists(pd.DataFrame(df[cl]), 'codelists', scraper.dataset.family, Path(os.getcwd()).name.lower())
