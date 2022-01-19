# -*- coding: utf-8 -*-
# %%
from gssutils import *
from gssutils.metadata.mimetype import ODS
import pandas as pd
import numpy as np
import json
import copy 
import datetime
from pandas import ExcelWriter
import calendar
import datetime
from csvcubed.models.cube.qb.catalog import CatalogMetadata

def left(s, amount):
    return s[:amount]
def right(s, amount):
    return s[-amount:]
# %%
metadata = Scraper(seed='alcohol_bulletin_clearances-info.json')
distribution = metadata.distribution(latest = True, mediaType=ODS)
datasetTitle = distribution.title

# %%
xls = pd.ExcelFile(distribution.downloadURL, engine="odf")
with ExcelWriter("data.xls") as writer:
    for sheet in xls.sheet_names[0:6]:
        pd.read_excel(xls, sheet).to_excel(writer,sheet, index=False)
    writer.save()
tabs = loadxlstabs("data.xls")

# %%
tidied_sheets = []
tabs_names_to_process = ["Wine_Duty_(wine)_tables", "Wine_Duty_(made_wine)_tables", "Spirits_Duty_tables", "Beer_Duty_and_Cider_Duty_tables" ]

for tab_name in tabs_names_to_process:
    # Raise an exception if one of our required tabs is missing
    if tab_name not in [x.name for x in tabs]:
        raise ValueError(f'Aborting. A tab named {tab_name} required but not found')

    tab = [x for x in tabs if x.name == tab_name][0]
    if tab_name == tabs_names_to_process[0]:
        anchor = tab.excel_ref('A7')
    elif tab_name == tabs_names_to_process[1]:
        anchor = tab.excel_ref('A8')
    elif tab_name == tabs_names_to_process[2]:
        anchor = tab.excel_ref('A8')
    elif tab_name == tabs_names_to_process[3]:
        anchor = tab.excel_ref('A6')
    
    alcohol_type = tab.name #will neeed to be fixed during post ptocessing.
    period = anchor.shift(0,1).expand(DOWN).is_not_blank().is_not_whitespace()
    bulletin_type = anchor.fill(RIGHT).is_not_blank().is_not_whitespace() #unit is held at end inside brackets.
    unwanted = tab.filter(contains_string("Table")).expand(RIGHT)
    observations = bulletin_type.fill(DOWN).is_not_blank().is_not_whitespace() - unwanted
    
    dimensions = [
        HDim(period, 'Period', DIRECTLY, LEFT),
        HDim(bulletin_type, 'Bulletin Type', DIRECTLY, ABOVE),
        HDimConst("Alcohol Type", tab.name),
        ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    df = tidy_sheet.topandas()
    #add unit and removed from end of Bulletin Type. 
    df['Unit'] = df['Bulletin Type'].str.extract('.*\((.*)\).*')
    df["Unit"] = df["Unit"].map(lambda x: pathify(x))
    df['Unit'] = df['Unit'].str.replace("ps-million","gbp-million").str.strip()
    df['Bulletin Type'] = df['Bulletin Type'].str.replace(r"\(.*\)","").str.strip().str.lower()
    df['Alcohol Type'] = df['Alcohol Type'].str.lower()
    #add Measure Type 
    df["Measure Type"] = df["Bulletin Type"].map(lambda x: "clearances" if "clearances" in x else 
                                    ("duty-receipts" if "receipts" in x else 
                                     ("tax" if "production" in x else x)))
    tidied_sheets.append(df)

# %%
#Post Processing
df = pd.concat(tidied_sheets, sort = True).fillna('') 
df.rename(columns = {'OBS': 'Value', 'DATAMARKER':'Marker'}, inplace = True)

#Fixing Alcohol Type to be either ; beer, cider, wine, made wine or spirits
df.loc[(df['Bulletin Type'].str.contains("beer")) , 'Alcohol Type'] = 'beer'
df.loc[(df['Bulletin Type'].str.contains("cider")) , 'Alcohol Type'] = 'cider'
df.loc[(df['Alcohol Type'].str.contains("beer_duty_and_cider_duty_tables")) , 'Alcohol Type'] = 'all'
df["Alcohol Type"] = df["Alcohol Type"].map(lambda x: "wine" if "wine" in x else 
                                    ("made wine" if "made_wine" in x else 
                                     ("spirits" if "spirits" in x else x)))
df["Bulletin Type"] = df["Bulletin Type"].map(lambda x: pathify(x))
df["Alcohol Type"] = df["Alcohol Type"].map(lambda x: pathify(x))

#Fixing Marker column : '', '[x]', '[d]' and taking provisonal / revised from period column. 
df = df.replace({'Marker' : {'[x]' : 'not-available', '[d]':'data-not-provided'}})
f1=((df['Period'].str.contains("provisional")) & (df["Marker"] == ''))
df.loc[f1,'Marker'] = "provisional"
f1=((df['Period'].str.contains("revised")) & (df["Marker"] == ''))
df.loc[f1,'Marker'] = "revised"
df['Period'] = df['Period'].str.replace(r"\[.*\]","").str.strip()
df['Period'] = df['Period'].astype(str).replace('\.0', '', regex=True)


#Fixing period column 
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
df = df.replace({'Period' : {'government-year/1999-1900' : 'government-year/1999-2000'}})


# Observations rounded to two decimal places
df['Value'] = pd.to_numeric(df.Value, errors = 'coerce')
df = df.round({"Value":2})
df = df[[ 'Period', 'Alcohol Type', 'Bulletin Type','Value','Measure Type', 'Unit', 'Marker']].drop_duplicates()

#Split out data into 3 seperate cubes depending on their Measure Type. 
df_clearance = df[df['Measure Type'] == 'clearances']
df_duty_re = df[df['Measure Type'] == 'duty-receipts']
df_tax = df[df['Measure Type'] == 'tax']


# %%
#Make a deep copy of scraper/metadata to alter for each cube.
metadata_copy = copy.deepcopy(metadata)

# %%
#Cube 1 - Alcohol Bulletin - Clearances (Multi Unit, Single Measure Type)
df_clearance.to_csv('alcohol_bulletin_clearances-observations.csv', index=False)
catalog_metadata: CatalogMetadata = metadata_copy.as_csvqb_catalog_metadata()
catalog_metadata.title = catalog_metadata.title + ' - Clearance'
#catalog_metadata = metadata_copy.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('alcohol_bulletin_clearances-catalog-metadata.json')

# %%
#Cube 2 - Alcohol Bulletin - Duty Receipts (Multi Unit, Single Measure Type)
df_duty_re.to_csv('alcohol_bulletin_duty_receipts-observations.csv', index=False)
catalog_metadata: CatalogMetadata = metadata_copy.as_csvqb_catalog_metadata()
catalog_metadata.title = catalog_metadata.title + ' - Duty Receipts'
#catalog_metadata = metadata_copy.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('alcohol_bulletin_duty_receipts-catalog-metadata.json')

# %%
#Cube 3 - Alcohol Bulletin - Production (Multi Unit, Single Measure Type)
df_tax.to_csv('alcohol_bulletin_production-observations.csv', index=False)
catalog_metadata: CatalogMetadata = metadata_copy.as_csvqb_catalog_metadata()
catalog_metadata.title = catalog_metadata.title + ' - Production'
#catalog_metadata = metadata_copy.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('alcohol_bulletin_production-catalog-metadata.json')
