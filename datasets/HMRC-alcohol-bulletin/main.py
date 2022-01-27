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
scraper = Scraper(seed='info.json')
distribution = scraper.distribution(latest = True, mediaType=ODS)
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
    clearance_origin = anchor.fill(RIGHT).is_not_blank().is_not_whitespace() #other dimensions and unit is held within this dimension, will be broken out during post processing.
    unwanted = tab.filter(contains_string("Table")).expand(RIGHT)
    observations = clearance_origin.fill(DOWN).is_not_blank().is_not_whitespace() - unwanted
    
    #remove duplicate cells and defining observations based on tab
    if tab_name == tabs_names_to_process[1]:
        observations = observations - tab.excel_ref('J8').expand(RIGHT).expand(DOWN) 
    elif tab_name == tabs_names_to_process[2]:
        observations = observations - tab.excel_ref('J7').expand(RIGHT).expand(DOWN) 
    elif tab_name == tabs_names_to_process[3]:
        observations = observations - tab.excel_ref('K5').expand(RIGHT).expand(DOWN) 
    
    
    dimensions = [
        HDim(period, 'Period', DIRECTLY, LEFT),
        HDim(clearance_origin, 'Clearance Origin', DIRECTLY, ABOVE),
        HDimConst("Alcohol Type", tab.name),
        ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    df = tidy_sheet.topandas()
    #add unit and removed from end of Clearance Origin. 
    df['Unit'] = df['Clearance Origin'].str.extract('.*\((.*)\).*')
    df["Unit"] = df["Unit"].map(lambda x: pathify(x))
    df['Unit'] = df['Unit'].str.replace("ps-million","gbp-million").str.strip()
    df['Clearance Origin'] = df['Clearance Origin'].str.replace(r"\(.*\)","").str.strip().str.lower()
    tidied_sheets.append(df)

# %%
#bring sheets together and start Post Processing
df = pd.concat(tidied_sheets, sort = True).fillna('') 
df.rename(columns = {'OBS': 'Value', 'DATAMARKER':'Marker'}, inplace = True)

# add Measure Type 
df["Measure Type"] = df["Clearance Origin"].map(lambda x: "clearances" if "clearances" in x else 
                                    ("alcohol-duty-receipts" if "total alcohol duty receipts" in x else 
                                     ("wine-duty-receipts" if "total wine duty receipts" in x else
                                      ('production' if 'production' in x else 
                                       ("spirits-duty-receipts" if "total spirits duty receipts" in x else 
                                        ("beer-duty-receipts" if "beer duty receipts" in x else 
                                         ("cider-duty-receipts" if "total cider duty receipts" in x else x )))))))
                                        
# fix Alcohol Type
df['Alcohol Type'] = df['Alcohol Type'].str.lower()
df["Alcohol Type"] = df["Alcohol Type"].map(lambda x: "made-wine" if "(made_wine)" in x else 
                                    ("wine" if "wine" in x else 
                                     ("spirits" if "spirits" in x else 
                                      ("beer-and-cider" if "beer_duty_and_cider_duty_tables" in x else  x))))
df.loc[(df['Clearance Origin'].str.contains("beer")) , 'Alcohol Type'] = 'beer'
df.loc[(df['Clearance Origin'].str.contains("cider")) , 'Alcohol Type'] = 'cider'

# fix Alcohol sub type
df['Alcohol Sub Type'] = df['Clearance Origin'].map(lambda x: "still" if "still" in x else 
                                    ("sparkling" if "sparkling" in x else 
                                     ("uk-potable" if "uk potable spirits" in x else
                                      ("uk-malt" if "uk malt whiskey" in x else
                                       ("uk-grain-and-blend" if "uk grain and blend" in x else
                                        ('uk' if "uk beer production" in x else
                                         ('uk-registered' if "uk registered clearances" in x else  
                                            ("all" if "total" in x else
                                             ("all" if "clearances" in x else x )))))))))
#fix Alcohol Content 
df['Alcohol Content'] = df['Clearance Origin'].map(lambda x: "up-to-15" if "up to 15% abv" in x else
                                                ("over-15" if "over 15% abv" in x else 
                                                 ("over-5.5" if "over 5.5% abv" in x else 
                                                  ("1.2-to-5.5" if "1.2% to 5.5% abv" in x else 
                                                   ("5.5-to-15" if "5.5% to 15% abv" in x else 'all' )))))
#fix Clearance Origin
df['Clearance Origin'] = df['Clearance Origin'].map(lambda x:"ex-warehouse-and-ex-ship" if "ex-warehouse and ex-ship clearances" in x else
                                                    ("ex-ship" if "ex-ship clearances" in x else
                                                     ("ex-warehouse" if "ex-warehouse clearances" in x else
                                                       ("uk-origin" if "uk origin clearances" in x else (
                                                         ('ex-ship' if "ex-ship and other clearances" in x 
                                                           else "all"))))))

#Fix up units / Measure Type
f1=((df['Alcohol Type'].str.contains("spirits")) & (df["Measure Type"] == 'clearances'))
df.loc[f1,'Measure Type'] = "clearances-of-alcohol"
df.loc[f1,'Unit'] = "hectolitres"

f1=((df['Alcohol Type'].str.contains("spirits")) & (df["Measure Type"] == 'production'))
df.loc[f1,'Measure Type'] = "production-of-alcohol"
df.loc[f1,'Unit'] = "hectolitres"

f1=((df['Alcohol Type'].str.contains("beer")) & (df["Measure Type"] == 'production'))
df.loc[f1,'Measure Type'] = "production-of-alcohol"
df.loc[f1,'Unit'] = "thousand-hectolitres"

f1=((df['Unit'].str.contains("thousand-hectolitres-of-alcohol")) & (df["Measure Type"] == 'clearances'))
df.loc[f1,'Measure Type'] = "clearances-of-alcohol"
df.loc[f1,'Unit'] = "thousand-hectolitres"

# %%
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
df = df.replace({'Period' : {'government-year/1999-1900' : 'government-year/1999-2000'}}) #quick hack


# Observations rounded to two decimal places
df['Value'] = pd.to_numeric(df.Value, errors = 'coerce')
df = df.round({"Value":2}).fillna('') 
df = df[[ 'Period', 'Alcohol Type', 'Alcohol Sub Type', 'Alcohol Content', 'Clearance Origin','Value','Measure Type', 'Unit', 'Marker']].drop_duplicates()
df
# %%
df.to_csv('observations.csv', index=False)
catalog_metadata = scraper.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')

# %%

