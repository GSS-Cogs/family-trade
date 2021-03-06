#!/usr/bin/env python
# coding: utf-8
# %% [markdown]
# ### ONS Quarterly National Accounts
#

# %%
EXTRACT_PERCENTAGE_CHANGE = True

# %%

import re
import os
import json

from gssutils import *

from gssutils.metadata import THEME
from os import environ
import numpy as np

cubes = Cubes("info.json")
trace = TransformTrace()
scraper = Scraper(seed="info.json")
dataset_title_prefix = scraper.dataset.title  # for later
scraper


# %%
tabs = scraper.distribution(downloadURL=lambda x: "quarterlynationalaccounts" in x, latest=True).as_databaker()

# %% [markdown]
# ### Index
#
# We're going to create a dictionary from the index tab for use in building all the datacubes, this is so we can:
#
# - differentiate the estimate type using series description.

# %%

# TODO - might be easier to output this one tab as pandas for this

tab = [x for x in tabs if x.name == "Index"]
if len(tab) != 1:
    raise Exception("Extraction Aborted. The spreadheet should have 1 (and only 1) tab named 'Index'.")

# Select all values in columns A and B
a_cells = tab[0].excel_ref('A').is_not_blank().is_not_whitespace() - tab[0].excel_ref("A1")
b_cells = tab[0].excel_ref('B').is_not_blank().is_not_whitespace() - tab[0].excel_ref("B1")
d_cells = tab[0].excel_ref('D').is_not_blank().is_not_whitespace() - tab[0].excel_ref("D1")

# Match the vertical offset (.y) of the xyCells to make the dict
estimate_type = {}
for a_cell in a_cells:

    # Get {cdid: GDP Estimate}
    b_cell = [x for x in b_cells if x.y == a_cell.y][0]
    d_cell = [x for x in d_cells if x.y == a_cell.y][0]

    if " cvm " in b_cell.value.lower():
        estimate_type[a_cell.value] = "chained-volume-measure"
    elif " cp " in b_cell.value.lower():
        estimate_type[a_cell.value] = "current-price"
    elif " deflator " in b_cell.value.lower():
        estimate_type[a_cell.value] = "deflator"
    elif " population " in b_cell.value.lower():
        estimate_type[a_cell.value] = "population"
    elif "per cent" in b_cell.value.lower() or " percent " in b_cell.value.lower():
        estimate_type[a_cell.value] = "percentage"
    else:
        raise Exception(f'Cannot find estimate type for {b_cell.value}')


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
    A class for passing to pandas .apply() to get the measure type.

    TODO - this has changed so many times now that we probably need a rewrite to account for having both a measure column
    and a growth column. As an interim we're providing measures in the format <measure type item:growth item> so we can split
    the column in post.
    """

    def __init__(self, job, tab):
        self.job = job
        self.tab = tab
        self.title = [x.value for x in tab.excel_ref("B1")][0]
        self.all_cdids = [x for x in self.tab.filter(is_cdid)]

        self._1YGR = "Percent:year-on-year"
        self._1QGR = "Percent:quarter-on-quarter"
        self._4QGR = "Percent:quarter-on-quarter-a-year-ago"

        # Overrides per job where the pattern is non standard for whatever reason
        self.overrides = {
            "Inventories": self._inventories
        }

        # Default (i.e the non percentage change measures) depending on job & (optionally) tab
        self.defaults = {
            "National Accounts Aggregates: GDP, GVA  and GDP deflator indices": "Index:not-applicable",
            "National Accounts Aggregates: GDP and GVA in £ million": "GBP Million:not-applicable",
            "Output indicators": "Index:not-applicable",
            "Expenditure indicators": "GBP Million:not-applicable",
            "Income indicators": "GBP Million:not-applicable",
            "Household expenditure indicators": "GBP Million:not-applicable",
            "Gross fixed capital formation": "GBP Million:not-applicable",
            "Trade": "GBP Million:not-applicable",
            "GFCF": "GBP Million:not-applicable",
            "Income indicators": "GBP Million:not-applicable",
            "GDP per head": "GBP Million:not-applicable"   # note, we'll override some of these later for horizontal changes in measure
        }

    def _inventories(self, val):
        return "GBP Million:not-applicable" if "current prices" in self.title else "Index:not-applicable"

    def __call__(self, val):
        if self.job in self.overrides.keys():
            return self.overrides[self.job](val)
        else:
            if "seasonally adjusted" in val.lower():
                try:
                    default = self.defaults[self.job]
                    if isinstance(default, dict):
                        tab_id = self.tab.name.split(" ")[0]
                        try:
                            return self.defaults[self.job][tab_id]
                        except:
                            raise Exception("Cannot find tab start text '{}' in '{}'.".format(tab_id, self.tab.name))
                    return self.defaults[self.job]
                except Exception as e:
                    raise Exception("Failed to get default measure type for job '{}'' and tab '{}' from this dict '{}'."
                                    .format(self.job, self.tab.name, json.dumps(self.defaults))) from e
            elif "latest year on previous" in val.lower():
                return self._1YGR
            elif "latest quarter on previous" in val.lower():
                return self._1QGR
            elif "latest quarter on corresponding quarter" in val.lower():
                return self._4QGR
            else:
                raise Exception("Cannot calculate measure from value '{}', tab is {}"
                            .format(val, self.tab.name))

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
    For if you just want a lookup to the labels that are offset y (vertical index) rows from the cdid header row
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

    # TODO - wrap the following comprehensions somehow, looks nasty
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


def horizontal_measure_overrides(job_name, df):
    """
    On some tabs the measures types are altered by changes in both the vertical and horizontal axis.
    We're dealing with this by going with the vertical but modifying for the horizontal changes in post (this function)
    """
    if job_name == "GDP per head":
        df["Measure Type"][(df["Measure Type"] == "GBP Million") & (df["Estimate Type"] == "population")] = "Count"

    return df


def add_datamarkers_for_missing_measures(df):

    # Get the unique measure types in this dataframe
    measures = df["Measure Type"].unique().tolist()

    # Create a composite key
    df["CKEYS"] = ""
    for col in [x for x in df.columns.values if x not in ["Value", "Marker", "CDID", "Decimals", "Measure Type"]]:
        df["CKEYS"] = df["CKEYS"].astype(str) + df[col].astype(str)

    measures = df["Measure Type"].unique().tolist()
    ckeys = df["CKEYS"].unique().tolist()
    
    for ckey in ckeys:
        temp_df = df[df["CKEYS"] == ckey]    
        for missing_measure in [x for x in measures if x not in temp_df["Measure Type"].unique().tolist()]:

            one_line = temp_df[:1]
            one_line["Measure Type"] = missing_measure
            one_line["Value"] = ""
            one_line["Marker"] = "not-available"
            df = pd.concat([df, one_line])

    df = df.drop("CKEYS", axis=1)
    return df


# filters to pass to databaker
# a filter can be anything that takes an xyCell and return True or False

pattern_cdid = re.compile("^[A-Z0-9]{4}$")
def is_cdid(xyCell):
    return True if pattern_cdid.match(str(xyCell.value)) else False


pattern_time = re.compile("^[0-9]{4}(\.[0-9])?( Q[1-4])?")
def is_time(xyCell):
    return True if pattern_time.match(str(xyCell.value)) else False


def is_not_time_or_blank(xyCell):
    if is_time(xyCell):
        return False
    else:
        if xyCell.value is None or xyCell.value == "":
            return False
    return True



# %% [markdown]
# ### Jobs
#
# We're gonna use a dictionary of parameters so we can transform each dataset via the same loop.

# %%

jobs = {
    "National Accounts Aggregates: GDP, GVA  and GDP deflator indices": {
        "tabs": [x for x in tabs if x.name.startswith("A1") and "AGGREGATES" in x.name],
        "cdid_header_row": '4',
        "dimension_looked_up_from_cdid_row": [
            ("Aggregate", move_rows(-1))
        ],
        "clear_footnotes_from": ["Aggregate"],
        "pathify": ["Aggregate"]
    },
    "National Accounts Aggregates: GDP and GVA in £ million": {
        "tabs": [x for x in tabs if x.name.startswith("A2") and "AGGREGATES" in x.name],
        "cdid_header_row": '4',
        "dimension_looked_up_from_cdid_row": [
            ("Aggregate", move_rows(-1))
        ],
        "clear_footnotes_from": ["Aggregate"],
        "pathify": ["Aggregate"]
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
            ("Income Category", lookup_from_offset_range(vertical=-2, left=-3, right=1, default="not-specified"))
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
            ("Capital Formation", table_f_lookup),
            ("Analysis", lookup_from_offset_range(vertical=-3, left=-5, right=2)),
        ],
        "clear_footnotes_from": ["Capital Formation", "Analysis"],
        "pathify": ["Capital Formation", "Analysis"]
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
            ("Flow", lookup_from_offset_range(vertical=-3, left=-1, right=1)),
            ("Trade Type", move_rows(-2))
        ],
        "pathify": ["Trade Type", "Flow"],
        "clear_footnotes_from": ["Trade Type", "Flow"]
    }
}


# %% [markdown]
#
# # NOTE re jobs (above)
#
# I Dropped this from the above there's an out of place population series that plays hell with the measure types.
#
#     "GDP per head": {
#         "tabs": [x for x in tabs if x.name.startswith("P") and "GDP per head" in x.name],
#         "cdid_header_row": '4',
#         "dimension_looked_up_from_cdid_row": [
#             ("GDP Measure", move_rows(-1))
#         ],
#         "pathify": ["GDP Measure"],
#         "clear_footnotes_from": ["GDP Measure"]
#

# %% [markdown]
# ### Create all the datacubes

# %%
###### # Make a directroy so we can dump some previews
previewsFolder = Path('previews')
previewsFolder.mkdir(exist_ok=True, parents=True)
    

for job_name, job_details in jobs.items():

    try:

        for i, tab in enumerate(job_details["tabs"]):
            
            columns = ["Period", "CDID", "Geography", "Area", "Measure Type", "Decimals"]
            trace.start(job_name, tab, columns, scraper.distributions[0].downloadURL)

            # Get the CDID header row
            trace.CDID("Selected CDID codes from row(s) {}".format(job_details["cdid_header_row"]))
            cdid_header_row = tab.excel_ref(job_details["cdid_header_row"]).filter(is_cdid)
            all_cdids = cdid_header_row.expand(DOWN).filter(is_cdid)

            # Get time
            trace.Period("Get period value from column A")
            period = tab.excel_ref("A6").fill(DOWN).filter(is_time)

            trace.obs("Get observation values as the cells inline with both Period and CDID")
            observations = period.waffle(cdid_header_row).is_not_blank().is_not_whitespace()

            if not EXTRACT_PERCENTAGE_CHANGE:
                p = tab.excel_ref('A').filter(contains_string('ercentage')).expand(RIGHT).expand(DOWN)
                observations = observations - p

            trace.Area("Hard code area to K02000001")
            area = "K02000001"
            
            mtype = tab.excel_ref('A').filter(is_not_time_or_blank)
            trace.Measure_Type("Select non-blank cells from column A that are not blank")
                
            dimensions = [
                HDim(period, "Period", DIRECTLY, LEFT),
                HDimConst("Area", area),
                HDim(all_cdids, "CDID", DIRECTLY, ABOVE),
                HDim(mtype, "Measure Type", CLOSEST, ABOVE,
                    cellvalueoverride={"P":"Seasonally adjusted"}) # account for missing header
            ]

            # missing CDID's for estimate type ....
            if job_name == "Gross fixed capital formation" or job_name == "Inventories":
                trace.add_column("Estimate Type")
                trace.Estimate_Type("Get estimate type as either current-price or chained-volume-measure" \
                                   + " from top right of sheet.")
                dimensions.append(
                HDim(cdid_header_row.shift(0, -4).is_not_blank().is_not_whitespace(), "Estimate Type", CLOSEST, RIGHT,
                     cellvalueoverride={
                         "£ million": "current-price",
                         "Reference year 2016, £ million": "chained-volume-measure"
                     })
                )

            for lookup_job in job_details.get("dimension_looked_up_from_cdid_row", []):
                table_lookup = lookup_job[1](cdid_header_row)
                dimensions.append(HDim(cdid_header_row, lookup_job[0], DIRECTLY, ABOVE, cellvalueoverride=table_lookup))

            cs = ConversionSegment(tab, dimensions, observations)
            savepreviewhtml(cs, fname="previews/{}-{}.html".format(pathify(job_name), str(i)))
            df = cs.topandas()

            # Applicable to all jobs
            trace.Period("Format time to have a /quarter or /year prefix")
            df["Period"] = df["Period"].apply(format_time)

            # missing CDID's for estimate type ....
            if job_name == "Income indicators":
                df["Estimate Type"] = "current-price"
            elif job_name.startswith("Gross fixed capital formation") or job_name.startswith("Inventories"):
                pass # handled with a dimension
            else:
                df["Estimate Type"] = df["CDID"]
                df["Estimate Type"] = df["Estimate Type"].map(lambda x: estimate_type[x])

            trace.Measure_Type("Lookup the measure types based on the name of the tab")
            df["Measure Type"] = df["Measure Type"].apply(LookupMeasure(job_name, tab))

            df["Measure Type"] = df["Measure Type"].str.replace("('GBP Million',)", "GBP Million") # why?
            df = df.rename(columns={"OBS": "Value", "DATAMARKER": "Marker"})
            df.fillna("", inplace=True)

            # Split out the entries for measure type and growth
            # If there's only one value for growth (i.e na throughout) drop the column
            df["Growth"] = df["Measure Type"].map(lambda x: x.split(":")[1])
            df["Measure Type"] = df["Measure Type"].map(lambda x: x.split(":")[0])
            if len(df["Growth"].unique().tolist()) == 1:
                df = df.drop("Growth", axis=1)
            else:
                trace.add_column("Growth")
                trace.Growth("Create a growth column, values are dependent on the tab name")

            # account for horizontal changes in measure type
            df = horizontal_measure_overrides(job_name, df)

            trace.Decimals('Set to 1 unless we\'re extracting population and GDP per head, in which case set to 1000')
            if job_name == "GDP per head":
                df["Decimals"] = df["Estimate Type"].map(lambda x: 1000 if x == "population" else 1)
            else:
                df["Decimals"] = 1

            for col in job_details.get("clear_rogue_zeroes", []):
                df[col] = df[col].astype(str).str.replace(".0", "")

            for col in job_details.get("clear_line_breaks_from", []):
                df[col] = df[col].map(lambda x: str(x).replace("\n", " ").replace("  ", " "))

            for col in job_details.get("clear_footnotes_from", []):
                df[col] = df[col].map(lambda x: ''.join([i for i in x if not i.isdigit()]).strip())

            for col in job_details.get("pathify", []):
                df[col] = df[col].apply(pathify)

            # Last, we'll pull out any datamarkers
            try:
                df["Marker"][df["Measure Type"] != "Percent"] = df["Value"][df["Measure Type"] != "Percent"].map(lambda cell: "".join([x for x in str(cell) if not x.isdigit()]))
                df["Marker"][df["Measure Type"] != "Percent"] = df["Marker"][df["Measure Type"] != "Percent"].map(lambda x: "-" if x == "-." else "" if x == "." else x)
                df["Value"] = df["Value"].map(lambda cell: "".join([x.replace("..", ".") for x in str(cell) if x.isdigit() or x =="."]))

                # Now correct the notation of any data markers
                marker_lookup = {"..": "not-availible", "-": "nil-or-less-than-half-the-final-digit-shown"}
                df["Marker"] = df["Marker"].map(lambda x: marker_lookup.get(x, x))
                
                trace.add_column("Marker")
                trace.Marker('Set ".."" to "not-availible" and "-"" to "nil-or-less-than-half-the-final-digit-shown"')
            except KeyError:
                pass # expected, not all datasets have Markers

            trace.store(job_name, df)

        destinationFolder = Path('out')
        destinationFolder.mkdir(exist_ok=True, parents=True)

        TITLE = scraper.dataset.title + dataset_title_prefix + ": " + job_name

        df = trace.combine_and_trace(job_name, job_name)
        
        trace.all("Drop all duplicate rows")
        df = df.drop_duplicates()

        # Fill in missing measures
        df = df.fillna("")
        
        trace.Measure_Type("Where we have sparsity in the measures, add a data marker")
        df = add_datamarkers_for_missing_measures(df)
        
        scraper.family = "Trade"
        scraper.dataset.family = "Trade"
        cubes.add_cube(scraper, df.drop_duplicates(), TITLE)

    except Exception as e:
        raise Exception("Error encountered on tab '{}' of job '{}'. See earlier trace for specifics"
                        .format(tab.name, job_name)) from e


# %%
cubes.output_all()

# %%
