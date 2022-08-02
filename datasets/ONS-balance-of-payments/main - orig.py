#!/usr/bin/env python
# coding: utf-8
# +
from gssutils import *
import json
import numpy as np


info_json_file = 'info.json'
# -

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


# +
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

def date_time(date: str) -> str:
    '''
    function to format numeric date to descriptive
    e.g. '2022' becomes 'year/2022'
    '''
    if len(date)  == 4:
        return 'year/' + date
    elif len(date) == 6:
        return 'quarter/' + left(date,4) + '-' + right(date,2)
    else:
        return "Date Formatting Error Unknown"
# +


# get first landing page details
metadata = Scraper(seed = info_json_file)
# display(metadata) #  to see exactly the data we are loading
#metadata
# -
distribution = metadata.distribution(latest = True)
#distribution

tabs = distribution.as_databaker()

# +
datasetTitle = distribution.title

# keep tabs we're interested in. The Annex A and Annex B tabs weren't in  previous code so maybe new additions?
tabs = [x for x in tabs if x.name not in ('Index', 'Records','Table R1', 'Table R2','Table R3','Annex A', 'Annex B') ]

# +

# to collate the transformed files later
tidied_sheets = []
# -

for tab in tabs:
    # example value: "BOKI"
    cdid = tab.excel_ref('C5').expand(DOWN).is_not_blank()

    year = tab.excel_ref('C4').expand(RIGHT).is_not_blank()

    quarter = tab.excel_ref('D5').expand(RIGHT)
    flow = tab.excel_ref('B1').expand(DOWN).filter(is_one_of(["Imports", "Exports", "Balances", "Credits", "Debits", "Balances (net transactions)"])) | tab.excel_ref('A1')
    
    seasonal_adjustment = tab.excel_ref('B').filter(is_one_of(["Seasonally adjusted", "Not seasonally adjusted"])) | tab.excel_ref('A1')
    
    measure_type = tab.excel_ref('B1').is_not_blank()
    
    services = tab.excel_ref('B').is_not_blank() - flow
    services = services - tab.excel_ref('B1').expand(UP)
    Currency = tab.excel_ref('N3')

    if tab.name == 'Table B' or tab.name == 'Table BX':
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
    cs = ConversionSegment(tab, dimensions, observations)

    # create preview files of each tabs data
    
    tidy_sheet = cs.topandas()
    # savepreviewhtml(services, fname= tab.name + "PREVIEW.html")
    tidied_sheets.append(tidy_sheet)

#convert separate tabs into one dataframe
df = pd.concat(tidied_sheets, sort = True).fillna('')
df

# +
#Post Processing

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
df = df.replace({'Marker' : {' -' : 'unknown'}})
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

# +
# TODO: i think i remember Andrew saying not to drop duplicates as if there are any something is wrong. To the PR reviewer - should i remove it?
# df = df[[ 'Period', 'CDID', 'Seasonal Adjustment', 'BOP Services', 'Flow Directions', 'Measure Type', 'Marker' ,'Geography', 'Quarter', 'Year', 'Value',]].drop_duplicates()
# df
# -

duplicated_df = df[df.duplicated(['BOP Services', 'CDID', 'Marker', 'Flow Directions', 'Geography',
       'Measure Type', 'Quarter', 'Seasonal Adjustment', 'Year',
       'Period', 'Value'], keep = False)]
duplicated_df.sort_values(by = 'Value').to_csv("duplicates.csv")

df.drop_duplicates(subset = df.columns.difference(["Value"]), inplace = True)

duplicated_df = df[df.duplicated(['BOP Services', 'CDID', 'Marker', 'Flow Directions', 'Geography',
       'Measure Type', 'Quarter', 'Seasonal Adjustment', 'Year',
       'Period', 'Value'], keep = False)]
duplicated_df

df["Unit"] = "gbp-million"

# TODO: add unit column and check with santhosh monday how to add values in there
df["Unit"] = df.apply(lambda x: "gbp-billion" if x['Measure Type'] == 'summary-of-international-investment-position-financial-account-and-investment-income' 
                        else "gbp-billion" if x['Measure Type'] == 'international-investment-position' else x['Unit'], axis = 1)

df = df.drop(columns = ["Year", "Quarter"],  axis = 1)

# +

df.to_csv('observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')
