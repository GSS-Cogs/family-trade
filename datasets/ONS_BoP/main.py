#!/usr/bin/env python
# coding: utf-8
# %%
import pandas as pd
import numpy as np
from gssutils import *
import json
from gssutils.metadata import THEME
from os import environ


# %%
with open("info.json") as f:
    info = json.load(f)
cubes = Cubes("info.json")


# %%
landingPage = info["landingPage"]
landingPage


# %%
scraper = Scraper(landingPage)
scraper.dataset.family = info['families']
scraper


# %%
tabs = scraper.distributions[0].as_databaker()


# %%
# Create a dictionary of dataset names from 'Index' tab
index_tab = [x for x in tabs if x.name.lower().strip() == 'index']
if len(index_tab) != 1:
    raise Exception("Aborting extraction. The data source must but does not have a tab called 'index'")


# %%
a_cells = index_tab[0].excel_ref("A").is_not_blank().is_not_whitespace()
b_cells = index_tab[0].excel_ref("B").is_not_blank().is_not_whitespace()


# %%
table_name_lookup = {}
for b_cell in b_cells:
    a_cell = [x for x in a_cells if x.y == b_cell.y][0]
    table_name_lookup[a_cell.value] = b_cell.value


# %%
#table_name_lookup
# # BOP Services<br>
# <br>
# Data from the table: https://drive.google.com/uc?export=download&id=1jzQaLafdqfWUAlTt07gnLBZ02tdTMEnl<br>
# <br>
# Putting it inline instead (we're not using dict.get() so it'll blow up if anything's amiss).
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
for letter in "ABCDEFGHIJK":
    tab = [tab for tab in tabs if tab.name[-1] == letter][0]

    # TODO - how many tables do we want?
    #if letter != "F":     # commented to check relevance 
        #continue  # commented to check relevance

    # Quick grabs
    Code = tab.excel_ref('C').is_not_blank().is_not_whitespace()
    Year = tab.excel_ref('4').is_not_blank().is_not_whitespace()
    Quarter = tab.excel_ref('5')
    Trade = tab.excel_ref('B').filter(is_one_of(["Imports", "Exports", "Balances"]))
    
    Services = tab.excel_ref('B').is_not_blank().is_not_whitespace() - Trade
    Services = Services - tab.excel_ref('B1').expand(UP)
    Currency = tab.excel_ref('N3')
    observations = Services.waffle(Year).is_not_blank().is_not_whitespace()
    dimensions = [
                HDimConst('Geography', 'K02000001'),
                HDim(Year,'TIME',DIRECTLY,ABOVE),
                HDim(Quarter,'Quarter',DIRECTLY,ABOVE),
                HDim(Code,'CDID',DIRECTLY,LEFT),
                HDimConst('Measure Type', 'GBP Total'),
                HDimConst('Unit','GBP (Million)'),
                HDim(Services,'label',CLOSEST, ABOVE),
                HDim(Trade,'Flow Directions',CLOSEST,ABOVE)
    ]
    cs = ConversionSegment(observations, dimensions, processTIMEUNIT=True)
    #savepreviewhtml(cs, fname= tab.name + "PREVIEW.html") 
    df = cs.topandas()
    
    # Clean up whitespace
    for col in df.columns.values:
        try:
            df[col] = df[col].str.strip()
        except AttributeError:
            pass # not everything is a sting
    
    #Lookup BOP service dimension from the labels
    df["label"].replace(bop_services, inplace=True) 
    df.rename(columns={"label" : "BOP Services"}, inplace=True)
    
    # Lookup BOP service dimension from the labels
    #df["BOP Services"] = df["label"].map(lambda x: bop_services[x])
    
    # Sort out time
    df["Period"] = df["TIME"].astype(float).astype(int).astype(str) + "-" + df["Quarter"].astype(str)
    df["Period"] = df["Period"].map(format_time)
    df.drop(columns = ['TIME', "Quarter"], inplace=True)
    df.rename(columns={"OBS": "Value"}, inplace=True)
    df = df[['Geography','Period','CDID','BOP Services','Flow Directions','Measure Type','Value','Unit']]
    output = pd.concat([output, df], sort=False)


# %%
output["Flow Directions"].fillna('not-applicable', inplace=True)
output["Flow Directions"] = output["Flow Directions"].str.strip().apply(pathify)
output['Flow Directions'].unique()

# %%
output

# %%

output['BOP Services'].unique()

# %%
cubes.add_cube(scraper, output, info['title'])
cubes.output_all()
