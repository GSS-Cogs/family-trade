#!/usr/bin/env python
# coding: utf-8
# %%
from gssutils import *
import json
import numpy as np

trace = TransformTrace()
df = pd.DataFrame()
cubes = Cubes("info.json")
info = json.load(open('info.json')) 
scraper = Scraper(seed="info.json")   
scraper 

# %%
bop_services = {
        "Total":"0",
        "Manufacturing and maintenance services":"1+2",
        "Transport":"3",
        "Travel":"4",
        "Construction":"5",
        "Insurance and pension services":"6",
        "Financial":"7",
        "Intellectual property":"8",
        "Telecommunication, computer and information services":"9",
        "Other business":"10",
        "Personal, cultural and recreational services":"11",
        "Government":"12",
}


# %%
# Reusable Functions
class is_one_of(object):
    def __init__(self, allowed):
        self.allowed = allowed
    def __call__(self, xy_cell):
        if xy_cell.value.strip() in self.allowed:
            return True
        return False   
#Format Date/Quarter
def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

def date_time(date):
    if len(date)  == 4:
        return 'year/' + date
    elif len(date) == 6:
        return 'quarter/' + left(date,4) + '-' + right(date,2)
    else:
        return "Date Formatting Error Unknown"


# %%
distribution = scraper.distribution(latest = True)
datasetTitle = distribution.title
tabs = { tab.name: tab for tab in distribution.as_databaker() }

# %%
for name, tab in tabs.items():
    columns=['Period', 'CDID', 'Seasonal Adjustment', 'BOP Services', 'Flow Directions', 'Measure Type', 'Marker']
    trace.start(datasetTitle, tab, columns, distribution.downloadURL)
    if 'Index' in name or 'Records' in name or 'Table R1' in name or 'Table R2' in name or 'Table R3' in name:
        continue 
    cdid = tab.excel_ref('C5').expand(DOWN).is_not_blank()
    trace.CDID("CDID's taken from column C in tab")
    
    year = tab.excel_ref('C4').expand(RIGHT).is_not_blank()
    quarter = tab.excel_ref('D5').expand(RIGHT)
    trace.Period("Taken from Year and Quarter ; rows 4 and 5")
    
    flow = tab.excel_ref('B1').expand(DOWN).filter(is_one_of(["Imports", "Exports", "Balances", "Credits", "Debits", "Balances (net transactions)"])) | tab.excel_ref('A1')
    trace.Flow_Directions("flow taken from tab values in column B as one of: Imports, Exports, Balances, Credits, Debits, Balances (net transactions) ")   
    
    seasonal_adjustment = tab.excel_ref('B').filter(is_one_of(["Seasonally adjusted", "Not seasonally adjusted"])) | tab.excel_ref('A1')
    trace.Seasonal_Adjustment("Taken from column B as one of the following values: Seasonally Adjusted , Not Seasonally Adjusted")
    
    measure_type = tab.excel_ref('B1').is_not_blank()
    trace.Measure_Type("Taken from tab title")
    
    services = tab.excel_ref('B').is_not_blank() - flow
    services = services - tab.excel_ref('B1').expand(UP)
    Currency = tab.excel_ref('N3')
    
    if name == 'Table B' or name == 'Table BX':
        observations = services.waffle(year).is_not_blank() - tab.excel_ref('B67').expand(RIGHT).expand(DOWN)
    else:
        observations = services.waffle(year).is_not_blank()
    dimensions = [
                HDimConst('Geography', 'K02000001'),
                HDim(year,'Year',DIRECTLY,ABOVE),
                HDim(quarter,'Quarter',DIRECTLY,ABOVE),
                HDim(cdid,'CDID',DIRECTLY,LEFT),
                HDim(services,'BOP Services',CLOSEST, ABOVE),
                HDim(measure_type,'Measure Type',CLOSEST, ABOVE),
                HDim(seasonal_adjustment,'Seasonal Adjustment',CLOSEST, ABOVE),
                HDim(flow,'Flow Directions',CLOSEST,ABOVE)
    ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    savepreviewhtml(tidy_sheet, fname= name + "PREVIEW.html")
    trace.with_preview(tidy_sheet)
    trace.store("combined_dataframe", tidy_sheet.topandas())
    
    

# %%
#Post Processing
df = trace.combine_and_trace(datasetTitle, "combined_dataframe")
df.rename(columns={'OBS' : 'Value', 'DATAMARKER' : 'Marker'}, inplace=True)
df['Year'] = df['Year'].astype(str).replace('\.0', '', regex=True)
df['Year'] = df['Year'].str.strip()
df['Quarter'] = df['Quarter'].str.strip()
df['Period'] = df['Year'] + df['Quarter']
df["Period"] =  df["Period"].apply(date_time)
df['CDID'] = df['CDID'].str.strip()
df["Flow Directions"].fillna('not-applicable', inplace=True)
for column in df:
    if column in ('Measure Type', 'Flow Directions', 'BOP Services'):
        df[column] = df[column].str.strip()
        df[column] = df[column].map(lambda x: pathify(x))
df = df.replace({'Flow Directions' : {'balances-net-transactions' : 'balances', 'd' : 'not-applicable', 'j' : 'not-applicable', 'k' : 'not-applicable' }})
df = df.replace({'Marker' : {'-' : 'unknown'}})
df = df.replace({'Seasonal Adjustment' : {' Seasonally adjusted' : 'SA', ' Not seasonally adjusted' : 'NSA', ' K' : 'NSA' }})
df["Seasonal Adjustment"].fillna('nsa', inplace=True)
df = df.replace({'Measure Type': {
    'financial-account1-2': 'financial-account', 
    'current-account-excluding-precious-metals1': 'current-account-excluding-precious-metals', 
    'international-investment-position1': 'international-investment-position'}})
df = df.replace({"BOP Services": {
    "net-errors-and-omissions2": "net-errors-and-omissions",
    "exports-of-services6": "exports-of-services",
    "exports-of-goods6": "exports-of-goods",
    "total-exports-of-goods-and-services6": "total-exports-of-goods-and-services",
    "imports-of-goods6": "imports-of-goods",
    "imports-of-services6": "imports-of-services",
    "total-imports-of-goods-and-services6": "total-imports-of-goods-and-services",
    "trade-in-goods6": "trade-in-goods",
    "trade-in-services6": "trade-in-services",
    "total-trade-in-goods-and-services6": "total-trade-in-goods-and-services",
    "of-which-eu-institutions1": "of-which-eu-institutions"
}})

# %%
df = df[[ 'Period', 'CDID', 'Seasonal Adjustment', 'BOP Services', 'Flow Directions', 'Measure Type', 'Marker' ,'Value',]].drop_duplicates()
df

# %%
df['Period'].unique()

# %%
df['Measure Type'].unique()

# %%
df['Flow Directions'].unique()

# %%
df['Seasonal Adjustment'].unique()

# %%
df['BOP Services'].unique()

# %%
df['CDID'].unique()

# %%
cubes.add_cube(scraper, df.drop_duplicates(), datasetTitle)
cubes.output_all()
trace.render("spec_v1.html")

# %%
