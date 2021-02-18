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
dist  = scraper.distribution(latest=True)
tabs = dist.as_databaker()

# %%

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
# ## Reusable Functions
def format_time(value):
    """
    the "value" is a concatenation of TIME and Quarter extracted values per observation, seperated by a single hyphen
    """
    value = str(value).strip()
    if value[-1] == "-":
        return "year/"+value[:-1]
    else:
        return "quarter/"+value


# %%
class is_one_of(object):
    def __init__(self, allowed):
        self.allowed = allowed
    def __call__(self, xy_cell):
        if xy_cell.value.strip() in self.allowed:
            return True
        return False


# %%

# ## Extract and Transform
output = pd.DataFrame()
for letter in "ABCDEFGHIJKX":#BCDEFGHIJKX":
    tab = [tab for tab in tabs if tab.name[-1] == letter][0]
    # Quick grabs
    Code = tab.excel_ref('C').is_not_blank().is_not_blank()
    Year = tab.excel_ref('4').is_not_blank().is_not_blank()
    Quarter = tab.excel_ref('5')
    Trade = tab.excel_ref('B1').expand(DOWN).filter(is_one_of(["Imports", "Exports", "Balances", "Credits", "Debits", "Balances (net transactions)"]))
    seasonal = tab.excel_ref('B').filter(is_one_of(["Seasonally adjusted", "Not seasonally adjusted"]))
    account_type = tab.excel_ref('B1').is_not_blank()
    Services = tab.excel_ref('B').is_not_blank().is_not_blank() - Trade
    Services = Services - tab.excel_ref('B1').expand(UP)
    Currency = tab.excel_ref('N3')

    if letter == 'B' or letter == 'X':
        observations = Services.waffle(Year).is_not_blank().is_not_blank() - tab.excel_ref('B67').expand(RIGHT).expand(DOWN)
    else:
        observations = Services.waffle(Year).is_not_blank().is_not_blank()
    
    dimensions = [
                HDimConst('Geography', 'K02000001'),
               # HDimConst('Letter', letter),
                HDim(Year,'TIME',DIRECTLY,ABOVE),
                HDim(Quarter,'Quarter',DIRECTLY,ABOVE),
                HDim(Code,'CDID',DIRECTLY,LEFT),
                HDim(Services,'label',CLOSEST, ABOVE),
                HDim(account_type,'Account Type',CLOSEST, ABOVE),
                HDim(seasonal,'Seasonal Adjustment',CLOSEST, ABOVE),
                HDim(Trade,'Flow Directions',CLOSEST,ABOVE)
    ]
    cs = ConversionSegment(observations, dimensions, processTIMEUNIT=True)
   # savepreviewhtml(cs, fname= letter + "PREVIEW.html") 
    df = cs.topandas()
    output = pd.concat([output, df], sort=False)


# %%
#Lookup BOP service dimension from the labels
#df["label"].replace(bop_services, inplace=True) 
output.rename(columns={"label" : "BOP Services"}, inplace=True)
output['TIME'] = output['TIME'].str.strip()
output['Quarter'] = output['Quarter'].str.strip()
output['CDID'] = output['CDID'].str.strip()
# Sort out time
output["Period"] = output["TIME"].astype(float).astype(int).astype(str) + "-" + output["Quarter"].astype(str)
output["Period"] = output["Period"].map(format_time)
output.drop(columns = ['TIME', "Quarter"], inplace=True)
output.rename(columns={"OBS": "Value", 'DATAMARKER' : 'Marker'}, inplace=True)

# %%
output["Flow Directions"].fillna('not-applicable', inplace=True)
output["Flow Directions"] = output["Flow Directions"].str.strip().apply(pathify)
output["Account Type"] = output["Account Type"].str.strip().apply(pathify)
output = output.replace({'Flow Directions' : {'balances-net-transactions' : 'balances' }})
output["BOP Services"] = output["BOP Services"].str.strip().apply(pathify)
output = output.replace({'Marker' : {'-' : 'unknown'}})
output = output.replace({'Seasonal Adjustment' : {' Seasonally adjusted' : 'sa', ' Not seasonally adjusted' : 'nsa' }})
output["Seasonal Adjustment"].fillna('nsa', inplace=True)

# %%
output = output[[ 'Period', 'CDID', 'Seasonal Adjustment', 'BOP Services', 'Flow Directions', 'Account Type', 'Marker' ,'Value',]].drop_duplicates()
output

# %%
output['Account Type'].unique()

# %%
output['Flow Directions'].unique()

# %%
output['Seasonal Adjustment'].unique()

# %%
output['BOP Services'].unique()

# %%
cubes.add_cube(scraper, output.drop_duplicates(), dist.title)
cubes.output_all()
