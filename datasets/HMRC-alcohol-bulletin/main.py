# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.9.1
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

<<<<<<< HEAD
=======
# The selections are ..almost..identicial so process in a loop
tabs_names_to_process = ["Wine_statistics", "Made_wine_statistics", "Spirits_statistics"]
for tab_name in tabs_names_to_process:

    # Raise an exception if one of our required tabs is missing
    if tab_name not in [x.name for x in tabs]:
        raise ValueError(f'Aborting. A tab named {tab_name} required but not found')

    # Select the tab in question
    tab = [x for x in tabs if x.name == tab_name][0]
    
    trace.start(datasetTitle, tab, columns, distribution.downloadURL)

>>>>>>> 64641f2cdf98fadccbbd9a907f9617de1b4bdcc0
    period = tab.excel_ref("A7").expand(DOWN).is_not_blank().is_not_whitespace()
    trace.Period("Defined from cell ref A6 Down")

    bulletin_type = tab.excel_ref("B6").expand(RIGHT).is_not_blank().is_not_whitespace()
    trace.Bulletin_Type("Defined from cell ref B6 and across")

    alcohol_type = tab.name
    trace.Alcohol_Type("Name of tabs in XLS sheet")
    
    if tab_name == "Wine_statistics":
<<<<<<< HEAD
        measure_type = "clearances_duty-receipts"
=======
        measure = "clearances_duty-receipts"
>>>>>>> 64641f2cdf98fadccbbd9a907f9617de1b4bdcc0
        unit = "hectolitres_gbp-million"
        observations = bulletin_type.fill(DOWN).is_not_blank().is_not_whitespace()

    elif tab_name == "Made_wine_statistics":
<<<<<<< HEAD
        measure_type = "clearances_duty-receipts"
=======
        measure = "clearances_duty-receipts"
>>>>>>> 64641f2cdf98fadccbbd9a907f9617de1b4bdcc0
        unit = "hectolitres_gbp-million"
        observations = bulletin_type.fill(DOWN).is_not_blank().is_not_whitespace()-tab.excel_ref("J6").expand(DOWN)-tab.excel_ref("K6").expand(DOWN)
    
    elif tab_name == "Spirits_statistics":
<<<<<<< HEAD
        measure_type = "production_clearances_duty-receipts"
=======
        measure = "production_clearances_duty-receipts"
>>>>>>> 64641f2cdf98fadccbbd9a907f9617de1b4bdcc0
        unit = "hectolitres_of_alcohol_gbp-million"
        observations = bulletin_type.fill(DOWN).is_not_blank().is_not_whitespace()-tab.excel_ref("J6").expand(DOWN)

    elif tab_name == "Beer_and_cider_statistics":
<<<<<<< HEAD
        measure_type = "production_clearances_duty-receipts"
=======
        measure = "production_clearances_duty-receipts"
>>>>>>> 64641f2cdf98fadccbbd9a907f9617de1b4bdcc0
        unit = "hectolitres_of_alcohol_gbp-million"
        observations = bulletin_type.fill(DOWN).is_not_blank().is_not_whitespace()-tab.excel_ref("K6").expand(DOWN)
    
    else:
        raise ValueError('Aborting, we don\`t have handling for tab: {tab_name}')

<<<<<<< HEAD
    trace.Measure_Type("Measure is different for different columns")
    trace.Unit("Unit is different for different columns")
    
=======
    trace.Measure("Measure is different for different columns")
    trace.Unit("Unit is different for different columns")
 
>>>>>>> 64641f2cdf98fadccbbd9a907f9617de1b4bdcc0
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

df

# Period column - requirements satisfied
df['DATAMARKER'][df.Period == 'Aug-20 provisional'] = 'provisional'
df['DATAMARKER'][df.Period == 'Sep-20 provisional'] = "provisional"
df['DATAMARKER'][df.Period == 'Oct-20 provisional'] = "provisional"

df["Measure Type"].unique()


# +
#Period column - requirements not satisfied
def left(s, amount):
    return s[:amount]
def right(s, amount):
    return s[-amount:]
def date_time (date):
    if len(date)  == 4:
        return 'year/' + left(date, 4)
    elif len(date) == 5:
        return 'year/' + left(date, 4)
#     elif len(date) == 18:
#         return 'month/' + 
#     elif len(date) == 5:
#         return 'year/'+left(date, 4)
#     elif len(date) == 7:
#         return 'year/'+left(date, 7)
#     elif len(date) == 10:
#         return strftime(%Y-%b-%d)
    #year/2019
#     elif len(date) == 6:
#         return 'quarter/' + left(date,4) + '-' + right(date,2)
#     #quarter/2019-01
    else:
        return date

df['Period'] = df['Period'].astype(str).replace('\.', '', regex=True)
df['Period'] =  df["Period"].apply(date_time)
trace.Period("Formating to be year/0000")

# +
# df['Period'].unique()
# -

df['Bulletin Type'] = df['Bulletin Type'].str.rsplit(pat = "(hectolitres)", expand = True)
df['Bulletin Type'] = df['Bulletin Type'].str.rsplit(pat = "(£ million)", expand = True)
df['Bulletin Type'] = df['Bulletin Type'].str.rsplit(pat = "(hectolitres of alcohol)", expand = True)

# +
# df['Measure Type'] = df['Measure Type'].apply(lambda x: 'clearances' if x['Bulletin Type'] != 'Total Wine Duty receipts' in x 
#                                               else 'duty-receipts' if 'production_clearances_duty-receipts' in x else x)

# +
# for x in df['Bulletin Type']:
#     for y in df['Alcohol Type']:
#         if x != "Total Wine Duty receipts":
#             if y == "Wine_statistics":                    
# -

df.columns

# +
# with pd.option_context("display.max_rows", None):
#     print(df["OBS"])
# -

with pd.option_context("display.max_rows", None):
    print(df['Measure Type'])

df['Measure Type'].unique()

df.rename(columns = {'OBS': 'Value', 'DATAMARKER':'Marker'}, inplace = True)
df

df.dtypes

cubes.add_cube(scraper, df.drop_duplicates(), datasetTitle)
cubes.output_all()

# +
trace.render("spec_v1.html")

# The multimeasures for this dataset is yet to be defined by DMs.
# The way to proceed with cubes class for multimeasures is yet to be finalized.
