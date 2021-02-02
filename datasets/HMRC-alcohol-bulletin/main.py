# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.7.1
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
<<<<<<< HEAD

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

# +
# distribution = Scraper.distribution(latest = True)
# datasetTitle = distribution.title
# columns = ["Period", "MARKER", "Alcohol Origin", "Alcohol Type"]
# trace.start(datasetTitle, tab, columns, distribution.downloadURL)
# -

tab = tabs[1]
tidy_sheets = []
for tab in tabs:
    if 'Document_contents' in tab.name:
        continue
    distribution = scraper.distribution(latest = True)
    datasetTitle = distribution.title
    columns = ["Period", "Marker", "Alcohol Origin", "Alcohol Type"]
    trace.start(datasetTitle, tab, columns, distribution.downloadURL)  
    
    period = tab.excel_ref("A7").expand(DOWN).is_not_blank().is_not_whitespace()
    trace.Period("Defined from cell ref A6 Down")
    
    alcohol_origin = tab.excel_ref("B6").expand(RIGHT).is_not_blank().is_not_whitespace()
    trace.Alcohol_Origin("Defined from cell ref B6 and across")
    
    observations = alcohol_origin.fill(DOWN).is_not_blank().is_not_whitespace()
    
    alcohol_type = tab.name
    trace.Alcohol_Type("Name of tabs in XLS sheet")
    
    dimensions = [
        HDim(period, 'Period', DIRECTLY, LEFT),
        HDim(alcohol_origin, 'Alcohol Origin', DIRECTLY, ABOVE),
        HDimConst("alcohol_type", tab.name),
    ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
    trace.with_preview(tidy_sheet)
    trace.store("combined_dataframe", tidy_sheet.topandas())
df = trace.combine_and_trace(datasetTitle, "combined_dataframe")
df

df['DATAMARKER'][df.Period == 'Aug-20 provisional'] == 'provisional'
df['DATAMARKER'][df.Period == 'Sep-20 provisional'] = "provisional"
df['DATAMARKER'][df.Period == 'Oct-20 provisional'] = "provisional"


# +
def left(s, amount):
    return s[:amount]
def right(s, amount):
    return s[-amount:]
def date_time (date):
    if len(date)  == 4:
        return 'year/' + left(date, 4)
    elif len(date) == 5:
        return 'year/'+left(date, 4)
    elif len(date) == 7:
        return 'year/'+left(date, 7)
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
# -

df.rename(columns = {'OBS': 'Value', 'Period':'Year', 'DATAMARKER':'Marker'}, inplace = True)
df

cubes.add_cube(scraper, df.drop_duplicates(), datasetTitle)
cubes.output_all()

# +
trace.render("spec_v1.html")

# The multimeasures for this dataset is yet to be defined by DMs.
# The way to proceed with cubes class for multimeasures is yet to be finalized.
=======

# +
# scraper = Scraper("https://www.gov.uk/government/statistics/alcohol-bulletin")
# scraper

scraper = Scraper(seed="info.json")
scraper.distributions = [x for x in scraper.distributions if hasattr(x, "mediaType")]
scraper

# +
# dist = scraper.distribution(title=lambda x: x.startswith('Alcohol Bulletin tables'), mediaType=ODS)
# tabs = (t for t in dist.as_databaker())
# dist

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

# tab = tabs[1]
tidy_sheets = []
for tab in tabs:
    if 'Document_contents' in tab.name:
        continue
    period = tab.excel_ref("A7").expand(DOWN).is_not_blank().is_not_whitespace()
    alcohol_origin = tab.excel_ref("B6").expand(RIGHT).is_not_blank().is_not_whitespace()
    observations = alcohol_origin.fill(DOWN).is_not_blank().is_not_whitespace()
    dimensions = [
        HDim(period, 'Period', DIRECTLY, LEFT),
        HDim(alcohol_origin, 'Alcohol Origin', DIRECTLY, ABOVE),
    ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
    tidy_sheets.append(tidy_sheet.topandas())
    df = pd.concat(tidy_sheets)
df

# +
# with pd.option_context('display.max_rows', None):
#     df['Alcohol Origin'] == 'Total Wine Duty receipts(£ million)'


# # with pd.option_context('display.max_rows', None):
# #     print(df)

# import functools


# f1 = df['Alcohol Origin'] == 'Total Wine Duty receipts(£ million)'
# f2 = df['Alcohol Origin'] == 'Total alcohol duty receipts(£ million)'

# cond_list = [f1, f2]
# all_cond = functools.reduce(lambda x,y:x & y, cond_list)
# df[all_cond]

# df.loc[df['Alcohol Origin'].isin(['Total Wine Duty receipts(£ million)']), 'OBS']

# new = df['Alcohol Origin'].isin(['Total Wine Duty receipts(£ million)'])
# df[new]

# +
# f2=(df['Alcohol by Volume'] =='£ million')
# df.loc[f2,'Unit'] = 'GBP Million'

f1 = (df['Alcohol Origin'] == 'Total Wine Duty receipts(£ million)')
df.loc[f1, 'Unit'] = 'GBP Million'
# df
# with pd.option_context('display.max_rows', None):
#     print(df)
df.info()

# +
# next_table = pd.Dataframe()

# +
# # %%capture

# # %run 'T1.py' 
# next_table = pd.concat([next_table, tidy])

# # %run 'T2.py'
# next_table = pd.concat([next_table, tidy])

# # %run 'T3.py'
# next_table = pd.concat([next_table, tidy])

# # %run 'T4.py'
# next_table = pd.concat([next_table, tidy])

# # %run 'R2.py'

# +
# for column in next_table:
#     if column in ('Alcohol by Volume', 'Alcohol Type', 'Alcohol Origin', 'Production and Clearance'):
#         next_table[column] = next_table[column].str.lstrip()
#         next_table[column] = next_table[column].map(lambda x: pathify(x))

# next_table['Value'] = next_table['Value'].round(decimals = 2)

# +
# destinationFolder = Path('out')
# destinationFolder.mkdir(exist_ok=True, parents=True)

# TITLE = 'HMRC Alcohol Releases, Production and Clearances - NSA'
# OBS_ID = pathify(TITLE)
# import os
# GROUP_ID = pathify(os.environ.get('JOB_NAME', 'gss_data/trade/' + Path(os.getcwd()).name))

# next_table.drop_duplicates().to_csv(destinationFolder / f'{OBS_ID}.csv', index = False)
# # # +
# from gssutils.metadata import THEME
# scraper.set_base_uri('http://gss-data.org.uk')
# scraper.set_dataset_id(f'{GROUP_ID}/{OBS_ID}')
# scraper.dataset.title = TITLE

# scraper.dataset.family = 'trade'
# with open(destinationFolder / f'{OBS_ID}.csv-metadata.trig', 'wb') as metadata:
#     metadata.write(scraper.generate_trig())
# # -

# schema = CSVWMetadata('https://gss-cogs.github.io/family-trade/reference/')
# schema.create(destinationFolder / f'{OBS_ID}.csv', destinationFolder / f'{OBS_ID}.csv-schema.json')

# next_table
>>>>>>> master
