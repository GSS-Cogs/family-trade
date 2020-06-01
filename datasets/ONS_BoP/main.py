#!/usr/bin/env python
# coding: utf-8
# %%
from gssutils import *
import json
from gssutils.metadata import THEME
from os import environ

with open("info.json") as f:
    info = json.load(f)

scraper = Scraper(seed="info.json")
scraper


# %%
tabs = scraper.distributions[0].as_databaker()
scraper.dataset.issued


# %%


# Create a dictionary of dataset names from 'Index' tab

index_tab = [x for x in tabs if x.name.lower().strip() == 'index']
if len(index_tab) != 1:
    raise Exception("Aborting extraction. The data source must but does not have a tab called 'index'")
    
a_cells = index_tab[0].excel_ref("A").is_not_blank().is_not_whitespace()
b_cells = index_tab[0].excel_ref("B").is_not_blank().is_not_whitespace()

table_name_lookup = {}
for b_cell in b_cells:
    a_cell = [x for x in a_cells if x.y == b_cell.y][0]
    table_name_lookup[a_cell.value] = b_cell.value
    
table_name_lookup    


# # BOP Services
# 
# Data from the table: https://drive.google.com/uc?export=download&id=1jzQaLafdqfWUAlTt07gnLBZ02tdTMEnl
#     
# Putting it inline instead (we're not using dict.get() so it'll blow up if anything's amiss).

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
        "Government":"12"
}


# ## Reusable Functions

# %%



def format_time(value):
    """
    the "value" is a concatenation of TIME and Quarter extracted values per observation, seperated by a single hyphen
    """
    value = str(value).strip()
    if value[-1] == "-":
        return "year/"+value[:-1]
    else:
        return "quarter/"+value
    
    
class is_one_of(object):
    
    def __init__(self, allowed):
        self.allowed = allowed
        
    def __call__(self, xy_cell):
        if xy_cell.value.strip() in self.allowed:
            return True
        return False
        


# ## Extract and Transform

# %%

prov = Providence()

for letter in "ABCDEFGHIJK":
    
    tab = [x for x in tabs if x.name[-1] == letter][0]
    
    # TODO - how many tables do we want?
    if letter != "F":
        continue
    
    columns=["Geography", "Time", "Quarter", "Currency", "BOP Services", "CDID","Measure Type","Unit","Flow Directions"]
    prov.of_cube("Table F", columns, source=scraper.distributions[0].downloadURL)
    
    prov.CDID("Select the non blank items in column C.")
    Code = tab.excel_ref('C').is_not_blank().is_not_whitespace()

    prov.Time("Select the non blank items on row 4.")
    Year = tab.excel_ref('4').is_not_blank().is_not_whitespace()
    
    prov.Quarter("Select the items on row 3")
    Quarter = tab.excel_ref('3')
    
    prov.BOP_Services("Select the non blank items from column B except for Imports, Exports and Balances")
    Trade = tab.excel_ref('B').filter(is_one_of(["Imports", "Exports", "Balances"]))
    Services = tab.excel_ref('B').is_not_blank().is_not_whitespace() - Trade
    Services = Services - tab.excel_ref('B1').expand(UP)
    
    prov.Currency("Select whatever is in cell N3")
    Currency = tab.excel_ref('N3')
    
    observations = Services.waffle(Year).is_not_blank().is_not_whitespace()
    
    prov.Geography("Hard coded to {}", var='K02000001')
    prov.Measure_Type("Hard coded to {}", var="GBP Total")
    prov.Unit("Hard coded to {}", var ="GBP million")

    dimensions = [
                HDimConst(prov.Geography.label, prov.Geography.var),
                HDim(Year, prov.Time.label, DIRECTLY, ABOVE),
                HDim(Code, prov.CDID.label, DIRECTLY, LEFT),
                HDimConst(prov.Measure_Type.label, prov.Measure_Type.var),
                HDimConst(prov.Unit.label, prov.Unit.var),
                HDim(Quarter, prov.Quarter.label, DIRECTLY, ABOVE),
                HDim(Services,prov.BOP_Services.label, CLOSEST, ABOVE),
                HDim(Trade, prov.Flow_Directions.label,CLOSEST,ABOVE)
    ]

    cs = ConversionSegment(observations, dimensions)
    prov.create_preview(cs)
    df = cs.topandas()
    
    # Clean up whitespace
    prov.ALL("Strip whitespace from string values in all columns")
    for col in df.columns.values:
        try:
            df[col] = df[col].str.strip()
        except AttributeError:
            pass # not everything is a sting
        
    # Lookup BOP service dimension from the labels
    prov.BOP_Services("Lookup new values using the dictionary: {}".format(str(bop_services)))
    df["BOP Services"] = df["BOP Services"].map(lambda x: bop_services[x])
    
    # Sort out time
    prov.add_column("Period")
    prov.multi(["Time", "Quarter", "Period"], "Amalagamate TIME and Quarter columns into a 'Period' column.")
    df["Period"] = df["Time"].str.strip() + "-" + df["Quarter"].str.strip()
    df["Period"] = df["Period"].map(format_time)
        
    prov.multi(["Time", "Quarter"],"Drop the Time and Quarter columns")
    df = df.drop(["Time", "Quarter"], axis=1)
    
    prov.Flow_Directions("Strip whitespace and pathify all values")
    df["Flow Directions"] = df["Flow Directions"].str.strip().apply(pathify)
    
    df = df.rename(columns={"OBS": "Value"})
    df = df[['Geography','Period','CDID','BOP Services','Flow Directions','Measure Type','Value','Unit']]
    
    destinationFolder = Path('out')
    destinationFolder.mkdir(exist_ok=True, parents=True)
    
    TITLE = scraper.seed["title"] + ": " + table_name_lookup[tab.name[-1]]
    #OBS_ID = pathify(TITLE)
                
    df.to_csv(destinationFolder / 'observations.csv', index = False)

    #scraper.set_dataset_id(f'{pathify(environ.get("JOB_NAME", ""))}/{OBS_ID}')
    scraper.dataset.title = f'{TITLE}'
    
    scraper.dataset.theme = THEME['business-industry-trade-energy']
    scraper.dataset.family = 'Trade'

    with open(destinationFolder / 'observations.csv-metadata.trig', 'wb') as metadata:
        metadata.write(scraper.generate_trig())
            
    schema = CSVWMetadata('https://gss-cogs.github.io/family-trade/reference/')
    schema.create(destinationFolder / 'observations.csv', destinationFolder / 'observations.csv-schema.json')
    
    prov.output()


# %%