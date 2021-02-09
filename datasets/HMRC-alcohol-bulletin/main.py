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

# import glob
from gssutils import *
from gssutils.metadata import THEME
import pandas as pd
import pyexcel
import messytables
from io import BytesIO
import numpy as np

# +
# # scraper = Scraper("https://www.gov.uk/government/statistics/alcohol-bulletin")
# # scraper

scraper = Scraper(seed="info.json")
scraper.distributions = [x for x in scraper.distributions if hasattr(x, "mediaType")]
scraper
trace = TransformTrace()
cubes = Cubes("info.json")

# +
# Conversion of ODS to XLS

original_tabs = scraper.distributions[0]

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

distribution = scraper.distribution(latest = True)
datasetTitle = distribution.title
columns = ["Period", "Marker", "Bulletin Type", "Alcohol Type", "Measure Type", "Unit"]

tabs_names_to_process = ["Wine_statistics", "Made_wine_statistics", "Spirits_statistics", "Beer_and_cider_statistics" ]
for tab_name in tabs_names_to_process:

    # Raise an exception if one of our required tabs is missing
    if tab_name not in [x.name for x in tabs]:
        raise ValueError(f'Aborting. A tab named {tab_name} required but not found')

    # Select the tab in question
    tab = [x for x in tabs if x.name == tab_name][0]
    
    trace.start(datasetTitle, tab, columns, distribution.downloadURL)

    period = tab.excel_ref("A7").expand(DOWN).is_not_blank().is_not_whitespace()
    trace.Period("Defined from cell ref A6 Down")

    bulletin_type = tab.excel_ref("B6").expand(RIGHT).is_not_blank().is_not_whitespace()
    trace.Bulletin_Type("Defined from cell ref B6 and across")

    alcohol_type = tab.name
    trace.Alcohol_Type("Name of tabs in XLS sheet")

    if tab_name == "Wine_statistics":
        measure_type = "clearances duty-receipts"
        unit = "hectolitres gbp-million"
        observations = bulletin_type.fill(DOWN).is_not_blank().is_not_whitespace()

    elif tab_name == "Made_wine_statistics":
        measure_type = "clearances duty-receipts"
        unit = "hectolitres gbp-million"
        observations = bulletin_type.fill(DOWN).is_not_blank().is_not_whitespace()-tab.excel_ref("J6").expand(DOWN)-tab.excel_ref("K6").expand(DOWN)
    
    elif tab_name == "Spirits_statistics":
        measure_type = "production clearances duty-receipts"
        unit = "hectolitres-of-alcohol gbp-million"
        observations = bulletin_type.fill(DOWN).is_not_blank().is_not_whitespace()-tab.excel_ref("J6").expand(DOWN)

    elif tab_name == "Beer_and_cider_statistics":
        measure_type = "production clearances duty-receipts"
        unit = "hectolitres-of-alcohol gbp-million"
        observations = bulletin_type.fill(DOWN).is_not_blank().is_not_whitespace()-tab.excel_ref("K6").expand(DOWN)
    
    else:
        raise ValueError('Aborting, we don\`t have handling for tab: {tab_name}')

    trace.Measure_Type("Measure is different for different columns")
    trace.Unit("Unit is different for different columns")
    
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

# +
#check column Bulletin Type string contains the word clearances or Clearances and make Measure Type  = clearances
df.loc[(df['Bulletin Type']).str.contains('clearances') | (df['Bulletin Type']).str.contains('Clearances'),'Measure Type']='clearances'
#check column Bulletin Type string contains the word receipts and make Measure Type  = duty-receipts
df.loc[(df['Bulletin Type']).str.contains('receipts'),'Measure Type']='duty-receipts'
#check column Bulletin Type string contains the word receipts and make Measure Type  = duty-receipts
df.loc[(df['Bulletin Type']).str.contains('production'),'Measure Type']='production'

#Setting the Unit basded on Measure Type Column 
df["Unit"] = df["Measure Type"].map(lambda x: "hectolitres" if x == "clearances" else 
                                    ("gbp-million" if x == "duty-receipts" else 
                                     ("hectolitres-of-alcohol" if x == "production" else "U")))
df
# -

df['Measure Type'].unique()

df['Unit'].unique()

# +
# Period column - requirements satisfied
df['Marker'][df.Period == 'Aug-20 provisional'] = 'provisional'
df['Marker'][df.Period == 'Sep-20 provisional'] = "provisional"
df['Marker'][df.Period == 'Oct-20 provisional'] = "provisional"
df['Marker'].unique()

#Some of marker noations below might need changed ? 
# -

#Period column 
def left(s, amount):
    return s[:amount]
def right(s, amount):
    return s[-amount:]
def date_time (date):
    if len(date)  == 4:
        #year/{yr}
        return 'year/' + left(date, 4)
    if len(date)  == 6:
        #year/{yr}
        return 'year/' + left(date, 4)
    if len(date)  == 7:
        #government-year/{year1}-{year2}
        return 'government-year/' + left(date, 4) + '-' + left(date, 2) + right(date, 2)
    elif len(date) == 10:
        #month/{yr}-{mth}
        return 'month/' + left(date, 7) 
    else:
        return date
df['Period'] =  df["Period"].apply(date_time)
#quick fix for odd values 
df = df.replace({'Period' : {'government-year/1999-1900' : 'government-year/1999-2000', 
                             'Aug-20 provisional': 'month/2020-08',
                            'Sep-20 provisional': 'month/2020-09',
                            'Oct-20 provisional': 'month/2020-10'}})


df['Period'].unique()

df.dtypes

df

cubes.add_cube(scraper, df.drop_duplicates(), datasetTitle)
cubes.output_all()

# +
trace.render("spec_v1.html")

# The multimeasures for this dataset is yet to be defined by DMs.
# The way to proceed with cubes class for multimeasures is yet to be finalized.
