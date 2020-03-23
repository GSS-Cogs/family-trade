#!/usr/bin/env python
# coding: utf-8
# %% [markdown]
# ### ONS Quarterly National Accounts
#   

# %%

import re
import os
import json

from gssutils import *

from gssutils.metadata import THEME
from os import environ

with open("info.json") as f:
    info = json.load(f)
    
scraper = Scraper(info["landingPage"])
dataset_title_prefix = scraper.dataset.title  # for later
scraper


# %%
tabs = scraper.distribution(downloadURL=lambda x: "estimate" in x, latest=True).as_databaker()
scraper.dataset.title

# %% [markdown]
# ### Index
#
# We're going to create a dictionary from the index tab for use in building all the datacubes, this is so we can get the measure types based on CDID.

# %%

tab = [x for x in tabs if x.name == "Index"]
if len(tab) != 1:
    raise Exception("Extraction Aborted. The spreadheet should have 1 (and only 1) tab named 'Index'.")
    
# Select all values in columns A and D
a_cells = tab[0].excel_ref('A').is_not_blank().is_not_whitespace()
d_cells = tab[0].excel_ref('D').is_not_blank().is_not_whitespace()

# Match the vertical offset (.y) of the xyCells to make the dict
index_dict = {}
for a_cell in a_cells:
    d_cell = [x for x in d_cells if x.y == a_cell.y][0]
    d_val = "GBP Million" if "£ million" in d_cell.value else d_cell.value
    index_dict[a_cell.value] = d_val


# %% [markdown]
# ### Reusable Code
#
# Three types of helper in this cell:
#
# - 1. Pandas .apply() classes. You use a class rather than a function to persist parameters (e.g pass in a dictionary where you want a function to apply said dictionary to any cell values passed to it).
#
# - 2. There're some (read: LOTS) of nasty header lookups for these datasets. So I've approached this by creating cellvalueoverride "lookup" dictionaries on the fly, matching the values in the top cdid row (which is a constant to all tabs) to the required labels.
#
# - 3. Databaker filters, anything that takes an xyCell and return True or False can be passed to .filter()
#

# %%

class LookupMeasure(object):
    """
    A class for passing to pandas .apply() to get a measure using the provided index dict (which we made earlier) 
    for a given CDID code.
    """
    
    def __init__(self, job, tab):
        self.job = job
        self.tab = tab
        self.title = [x.value for x in tab.excel_ref("B1")][0]
        
        # Overrides per job
        self.overrides = {
            "Income indicators": self._return_million,
            "Inventories": self._inventories
        }
        
        # Unfortunetly, not all CDID codes for table F are included in the index (though they should be...)
        # Hopefully they'll be more consistent in the future, so for now we're going to have to build some 
        # fall back logic for identifying measure type on F tabs
        if tab.name.startswith("F"):
            
            # Percentage is referenced 3 times in column A, we'll use this to differentiate
            # the measure type, based on vertical (.y) cell position.
            percentage_break_points = [x for x in tab.excel_ref("A") if "percent" in str(x.value).lower()]
            self.f_fallback = {
                percentage_break_points[0].y: "GBP Million",
                percentage_break_points[1].y: "1Y GR",
                percentage_break_points[2].y: "1Q GR"
            }
        else:
            self.f_fallback = None
            
    def _return_million(self):
        return "GBP Million"
    
    def _inventories(self):
        return "GBP Million" if "current prices" in self.title else "Index"
              
    def __call__(self, cdid):
        if self.job in self.overrides.keys():
            return self.overrides[self.job]()
        else:
            try:
                return index_dict[cdid]
            except KeyError:
                
                # Use horrible tab f fallback if we have to
                if self.f_fallback is not None:
                    # TODO - horrifically slow!
                    cdid_y_offset = [x for x in tab.filter(cdid).assert_one()][0].y
                    for k, v in self.f_fallback.items():
                        if cdid_y_offset < k:
                            return v,
                        return "4Q GR"
                else:
                    raise Exception("CDID-{}-NOT-FOUND".format(cdid), "tab is", self.tab.name)


class lookup_from_offset_range(object):
    """
    some tables use horrible centered headings we need to untangle. We'll do it by building a
    cellvalueoverride dictionary on the fly.
    
    We'll use some databaker trickery so we "search" the row in question (relative to the cdid row)
    From the left offset, to the right offset (offset being one horizontal/x space) until we get
    a non blank, non whitespace value - which is used to build the {CDID:value} lookup
    """
    def __init__(self, vertical=None, left=None, right=None, default=None):
        self.vertical = vertical
        self.left = left
        self.right = right
        self.default = default
        
    def __call__(self, cdid_header_row):
        
        lookup = {}
        target_row = cdid_header_row.shift(0, self.vertical)
        for cdid in cdid_header_row:
            found = False
            for x_offset in range(self.left, self.right+1):
                try:
                    target_cell_value = str([x.value for x in target_row if x.x == cdid.x+x_offset][0]).strip()
                    if target_cell_value not in ["nan", ""]:
                        lookup[cdid.value] = target_cell_value
                        found = True
                except IndexError:
                    # Expected, sometimes we "look" too far to the left or right of our selection
                    pass
            
            if found == False and self.default is not None:
                lookup[cdid.value] = self.default
                
        return lookup
    
    
def format_time(time_value):
    """ Does exactly what you'd think """
    time_string = str(time_value).replace(".0", "").strip()
    time_len = len(time_string)
    if time_len == 4:
        return "year/" + time_string
    elif time_len == 7:
        return "quarter/{}-{}".format(time_string[:4], time_string[5:7])
    else:
        raise Exception("Aborting. Time cells should either be 4 or 7 characters in length. We have: '{}'.".format(time_string))
    
    
class move_rows(object):
    """
    For if you just want a lookup to the labels that are offset y (vertical index) rows from the cdid row
    """
    def __init__(self, y_offset):
        self.y_offset = y_offset
        
    def __call__(self, cdid_header_row):
        lookup = {}
        for cdid_cell in cdid_header_row:
            new_label_cell = [x for x in tab if x.x == cdid_cell.x and x.y == cdid_cell.y+self.y_offset][0]
            lookup[cdid_cell.value] = new_label_cell.value
        return lookup
        
        
def table_e_national_or_domestic_lookup(cdid_header_row):
    """
    The first two columns are national, the rest are domestic
    """
    lookup = {}
    min_x = min([x.x for x in cdid_header_row])
    for cdid_cell in cdid_header_row:
        if cdid_cell.x == min_x or cdid_cell.x == min_x+1:
            lookup[cdid_cell.value] = "uk-national"
        else:
            lookup[cdid_cell.value] = "uk-domestic"
    return lookup
    

def table_e_totals_lookup(cdid_header_row):
    """
    Table E has a nasty habit of overusing the label "Total" (3 times on one tab!).
    
    This lookup will:
    - prefix "Domestic " to any Total to the right of "Net tourism"
    - postfix " goods" to any Total left of "Durable goods" (and lower case that D)
    """
    lookup = {}
    label_row = cdid_header_row.shift(0, -2)   # up 2
    
    # Create basic 1 to 1 lookup with labels as-is
    for cdid_cell in cdid_header_row:
        label_cell = [x for x in label_row if x.x == cdid_cell.x][0]
        lookup[cdid_cell.value] = label_cell.value
        
    # TODO - rap the following comporehensions somehow, looks nasty
    # TODO - assertion on assumed find of Total cells
    
    # Add domestic prefix
    try:
        net_tourism_cell_x = [x.x for x in label_row if x.value == "Net tourism"][0]
        one_to_the_right = [x for x in label_row if x.x == net_tourism_cell_x+1][0]
        cdid_label = [x for x in cdid_header_row if x.x == net_tourism_cell_x+1][0]
        lookup[cdid_label.value] = "Domestic " + one_to_the_right.value.lower().strip() 
    except:
        raise Exception("Cannot find a required cell 'to the right of Net tourism' for lookup function "
                       "'table_e_totals_lookup'.")
        
    # Add goods postfix
    try:
        durable_goods_cell_x = [x.x for x in label_row if x.value == "Durable goods"][0]
        one_to_the_left = [x for x in label_row if x.x == durable_goods_cell_x-1][0]
        cdid_label = [x for x in cdid_header_row if x.x == durable_goods_cell_x-1][0]
        lookup[cdid_label.value] = one_to_the_left.value.lower().strip() + " goods" 
    except IndexError:
        pass # 'Durable goods' only appears on 1 of 4 tabs, so this will happen
    except:
        raise Exception("Cannot find a required cell 'to the left of Durable goods' for lookup function "
                       "'table_e_totals_lookup'.")
    return lookup
    
    
def table_c_lookup(cdid_header_row):
    """
    Anything left of "Total exports" is "National expenditure on goods and services at market prices" else "Not specified"
    """
    lookup = {}
    total_export_x = [x for x in cdid_header_row.shift(UP) if x.value == "Total exports"]
    if len(total_export_x) != 1:
        raise Exception("Aborted. Cannot find expected header 'Total exports'.")
    
    for cdid in cdid_header_row:
        if cdid.x < total_export_x[0].x:
            lookup[cdid.value] = "National expenditure on goods and services at market prices"
        else:
            lookup[cdid.value] = "Not specified"
            
    return lookup
    
    
def table_f_lookup(cdid_header_row):
    """
    Table F has recurring sub headings for public and private sector that we need to integrate, into eg:
    "Public corporations Dwellings", "Private sector Dwellings"
    
    We're going to do this by creating an override dict between the CDID row value and the result of pivoting (databaking)
    that relationship.
    """
    pub_priv_and_blank = cdid_header_row.shift(0, -2).is_not_blank() | tab.excel_ref("A2") | cdid_header_row.shift(UP).filter("Total").shift(UP)
    dimensions = [
        HDim(cdid_header_row.shift(UP), "pre", DIRECTLY, ABOVE),
        HDim(pub_priv_and_blank, "post", CLOSEST, LEFT)
    ]
    df = ConversionSegment(tab, dimensions, cdid_header_row).topandas()
    df["post"] = df["post"].str.strip() + " " + df["pre"].str.lower()
    df["post"] = df["post"].map(lambda x: x.strip().replace("  ", " "))
    return pd.Series(df["post"].values,index=df["DATAMARKER"]).to_dict()

    
def table_b_lookup(cdid_header_row):
    """
    Everything is a service industry other than a small number of exceptions.
    We'll just override them as we find them.
    """
    lookup = {}
    for cdid in cdid_header_row:
        lookup[cdid.value] = "Service Industry"
            
    # If it's the tab with production on
    if len([x for x in cdid_header_row.shift(0, -3) if "Production" in x.value]) > 0:

        overrides = {
            "Not Specified":["Agriculture, forestry & fishing", "Construction", 
                         "Gross value added at basic prices", "Gross value added excluding oil & gas"],
            "Production": ["Mining & quarrying including oil and gas extraction", "Manufacturing",
                          "Electricity, gas, steam and air", "Water supply, sewerage, etc.", 
                           "Total production"]
        }
        for override, header_list in overrides.items():
            for cdid in cdid_header_row:
                label_cell = cdid.shift(0, -2)
                clean_val = "".join([x for x in label_cell.value if not x.isdigit()]).replace("\n", "").strip()
                if clean_val in header_list:
                    lookup[cdid.value] = override
    return lookup


# filters to pass to databaker
# a filter can be anything that takes an xyCell and return True or False

pattern_cdid = re.compile("^[A-Z0-9]{4}$")
def is_cdid(xyCell):
    return True if pattern_cdid.match(str(xyCell.value)) else False


pattern_time = re.compile("^[0-9]{4}(\.[0-9])?( Q[1-4])?")
def is_time(xyCell):
    return True if pattern_time.match(str(xyCell.value)) else False
    


# %% [markdown]
# ### Jobs
#
# We're gonna use a dictionary of parameters so we can transform each dataset via the same loop.

# %%


jobs = {
    "National Accounts Aggregates": {
        "tabs": [x for x in tabs if x.name.startswith("A") and "AGGREGATES" in x.name],
        "cdid_header_row": '4',
        "dimension_looked_up_from_cdid_row": [
            ("Aggregate", move_rows(-1)),
            ("Category", lookup_from_offset_range(vertical=-2, left=-3, right=2))
        ],
        "clear_footnotes_from": ["Aggregate", "Category"],
        "pathify": ["Aggregate", "Category"]
    },  
    "Output indicators": {
        "tabs": [x for x in tabs if x.name.startswith("B") and "OUTPUT" in x.name],
        "cdid_header_row": '5',
        "dimension_looked_up_from_cdid_row": [
            ("Industry", move_rows(-2)),
            ("Industrial Sector", table_b_lookup),
            ("2016 Weights", move_rows(-1))
        ],
        "clear_footnotes_from": ["Industry", "Industrial Sector"],
        "pathify": ["Industry", "Industrial Sector", "2016 Weights"],
        "clear_rogue_zeroes": ["2016 Weights"]
    },
    "Expenditure indicators": {
        "tabs": [x for x in tabs if x.name.startswith("C") and "EXPENDITURE" in x.name],
        "cdid_header_row": '5',
        "dimension_looked_up_from_cdid_row": [
            ("Expenditure", move_rows(-1)),
            ("Expenditure Category", lookup_from_offset_range(vertical=-2, left=-2, right=2, default="not-specified")),
            ("Expenditure Type", table_c_lookup)
        ],
        "clear_footnotes_from": ["Expenditure", "Expenditure Category", "Expenditure Type"],
        "pathify": ["Expenditure", "Expenditure Category", "Expenditure Type"]
    },
    "Income indicators": {
        "tabs": [x for x in tabs if x.name.startswith("D") and "INCOME" in x.name],
        "cdid_header_row": '4',
        "dimension_looked_up_from_cdid_row": [
            ("Income Indicator", move_rows(-1)),
            ("Income Category", lookup_from_offset_range(vertical=-2, left=-3, right=3, default="not-specified"))
        ],
        "clear_footnotes_from": ["Income Indicator", "Income Category"],
        "pathify": ["Income Indicator", "Income Category"]
    },
    "Household expenditure indicators": {
        "tabs": [x for x in tabs if x.name.startswith("E") and "EXPENDITURE" in x.name],
        "cdid_header_row": "6:8",
         "dimension_looked_up_from_cdid_row": [
             ("Household Expenditure", table_e_totals_lookup),
             ("Expenditure Category", table_e_national_or_domestic_lookup)
         ],
        "pathify": ["Household Expenditure", "Expenditure Category"],
    },
    "Gross fixed capital formation": {
        "tabs": [x for x in tabs if x.name.startswith("F") and "GFCF" in x.name],
        "cdid_header_row": '5',
        "dimension_looked_up_from_cdid_row": [
            ("Capital formation", table_f_lookup)
        ],
        "clear_footnotes_from": ["Capital formation"],
        "pathify": ["Capital formation"]
    },
    "Inventories": {
        "tabs": [x for x in tabs if x.name.startswith("G") and "INVENTORIES" in x.name],
        "cdid_header_row": '5',
        "dimension_looked_up_from_cdid_row": [
            ("Inventory", move_rows(-2)),
        ],
        "clear_footnotes_from": ["Inventory"],
        "pathify": ["Inventory"]
    },
    "Trade": {
        "tabs": [x for x in tabs if x.name.startswith("H") and "TRADE" in x.name],
        "cdid_header_row": '5:6',
        "dimension_looked_up_from_cdid_row": [
            ("Trade Type", lookup_from_offset_range(vertical=-3, left=-1, right=1)),
            ("Flow Directions", move_rows(-2))
        ],
        "pathify": ["Trade Type", "Flow Directions"],
        "clear_footnotes_from": ["Trade Type", "Flow Directions"]
    }
}


# %% [markdown]
# ### Create all the datacubes

# %%


for job_name, job_details in jobs.items():
    tidy_sheets = []
    
    try:
        
        # --- Initial Extraction ---
        
        for tab in job_details["tabs"]:

            # Get the CDID header row
            cdid_header_row = tab.excel_ref(job_details["cdid_header_row"]).filter(is_cdid)

            # Get time
            time = tab.excel_ref("A6").fill(DOWN).filter(is_time)

            dimensions = [
                HDim(time, "Date", DIRECTLY, LEFT),
                HDimConst("Geography", "K02000001"),
                HDim(cdid_header_row.expand(DOWN).filter(is_cdid), "Measure Type", DIRECTLY, ABOVE),
            ]
                
            for lookup_job in job_details.get("dimension_looked_up_from_cdid_row", []):
                table_lookup = lookup_job[1](cdid_header_row)
                dimensions.append(HDim(cdid_header_row, lookup_job[0], DIRECTLY, ABOVE, cellvalueoverride=table_lookup))
                
            # Waffle to get obs then create
            observations = time.waffle(cdid_header_row).is_not_blank().is_not_whitespace()
            df = ConversionSegment(tab, dimensions, observations).topandas()
                
            # Appliable to all jobs
            df["Date"] = df["Date"].apply(format_time)
            df["Measure Type"] = df["Measure Type"].apply(LookupMeasure(job_name, tab))
            df["Measure Type"] = df["Measure Type"].str.replace("('GBP Million',)", "GBP Million")
            df = df.rename(columns={"OBS": "Value", "DATAMARKER": "Marker"})
            df.fillna("", inplace=True)
            
            for col in job_details.get("clear_rogue_zeroes", []):
                df[col] = df[col].astype(str).str.replace(".0", "")
                    
            for col in job_details.get("clear_line_breaks_from", []):
                df[col] = df[col].map(lambda x: str(x).replace("\n", " ").replace("  ", " "))

            for col in job_details.get("clear_footnotes_from", []):
                df[col] = df[col].map(lambda x: ''.join([i for i in x if not i.isdigit()]).strip())
        
            for col in job_details.get("pathify", []):
                df[col] = df[col].apply(pathify) 
                
            tidy_sheets.append(df)
                
        destinationFolder = Path('out')
        destinationFolder.mkdir(exist_ok=True, parents=True)
        
        TITLE = info["title"] + ", " + dataset_title_prefix + ": " + job_name
        OBS_ID = pathify(TITLE)
        
        df = pd.concat(tidy_sheets)
        df.to_csv(destinationFolder / f'{OBS_ID}.csv', index = False)

        scraper.set_dataset_id(f'{pathify(environ.get("JOB_NAME", ""))}/{OBS_ID}')
        scraper.dataset.title = f'{TITLE}'
        scraper.dataset.family = 'trade'

        with open(destinationFolder / f'{OBS_ID}.csv-metadata.trig', 'wb') as metadata:
            metadata.write(scraper.generate_trig())
            
        schema = CSVWMetadata('https://gss-cogs.github.io/family-trade/reference/')
        schema.create(destinationFolder / f'{OBS_ID}.csv', destinationFolder / f'{OBS_ID}.csv-schema.json')
    
    except Exception as e:
        raise Exception("Error encountered on tab '{}' of job '{}'. See earlier trace for specifics"
                        .format(tab.name, job_name)) from e
        

