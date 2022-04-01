# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.7
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
from gssutils import *
import json
import numpy as np

df = pd.DataFrame()
info = json.load(open('info.json'))
metadata = Scraper(seed = 'info.json')
metadata


# +
#Format Date/Quarter
def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

def date_time(date):
    if len(date)  == 4:
        return 'year/' + date
    elif len(date) == 7:
        return 'quarter/' + left(date,4) + '-' + right(date,2)
    else:
        return "Date Formatting Error"


# -

distribution = metadata.distribution(latest = True)
distribution

datasetTitle = distribution.title
tabs = { tab.name: tab for tab in distribution.as_databaker() }
list(tabs)

total_tabs = {tab_name for tab_name in tabs}

tabs_name_to_process = ["Key Figures", "North East", "North West", "Yorkshire and The Humber",
"East Midlands", "West Midlands", "East of England", "London", "South East", "South West",
"England", "Wales", "Extra-Regio"]

if len(set(tabs_name_to_process)-(total_tabs)) != 0:
    raise ValueError(f"Aborting. A tab named{set(tabs_name_to_process)-(total_tabs)} required but not found")

tidied_sheets =[]

tab = tabs["Key Figures"]
footer = tab.filter(contains_string("1  Regional GDP is designated")).expand(DOWN)
indicies_or_percentage = tab.filter("Section").fill(DOWN).one_of(['Indices 2016=100', 'Percentage change, quarter on previous quarter']).is_not_blank().is_not_whitespace()-footer
unwanted = indicies_or_percentage|footer
period = tab.filter("Section").fill(DOWN).is_not_blank().is_not_whitespace() - unwanted
reference_area = tab.filter("Region").fill(RIGHT).is_not_blank().is_not_whitespace()
industry_section = tab.filter("Section").fill(RIGHT).is_not_blank().is_not_whitespace()
observations = period.waffle(industry_section)
dimensions = [
            HDim(period, "Period", DIRECTLY, LEFT),
            HDim(reference_area, "Reference Area", DIRECTLY, ABOVE),
            HDim(industry_section, "Industry Section", DIRECTLY, ABOVE),
            HDim(indicies_or_percentage, "Measure Type", CLOSEST, ABOVE),
            HDim(indicies_or_percentage, "Unit", CLOSEST, ABOVE),
]
tidy_sheet = ConversionSegment(tab, dimensions, observations)
# savepreviewhtml(tidy_sheet, fname= tab.name + "Preview.html")
tidied_sheets.append(tidy_sheet.topandas())


for name, tab in tabs.items():
    if 'Important information' in name or 'Contents' in name or 'Key Figures' in name:
        continue
    # print(tab.name)

    footer = tab.filter(contains_string("1  Regional GDP is designated")).expand(DOWN)
    indicies_or_percentage = tab.filter("Section").fill(DOWN).one_of(["Percentage change, quarter on previous quarter"]).is_not_blank().is_not_whitespace()-footer
    unwanted = indicies_or_percentage|footer
    period = tab.filter("Section").fill(DOWN).is_not_blank().is_not_whitespace()-unwanted
    reference_area = tab.name
    industry_section = tab.filter("Section").fill(RIGHT).is_not_blank().is_not_whitespace()
    observations = period.waffle(industry_section)
    # savepreviewhtml(observations, fname= tab.name + "Preview.html")
    dimensions = [
            HDim(period, "Period", DIRECTLY, LEFT),
            HDimConst("Reference Area", reference_area),
            HDim(industry_section, "Industry Section", DIRECTLY, ABOVE),
            HDim(indicies_or_percentage, "Measure Type", CLOSEST, ABOVE),
            HDim(indicies_or_percentage, "Unit", CLOSEST, ABOVE),
    ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    # savepreviewhtml(tidy_sheet, fname= tab.name + "Preview.html")
    tidied_sheets.append(tidy_sheet.topandas())    

df = pd.concat(tidied_sheets, sort = True).fillna('')
df

df['Reference Area'].unique()

map_regions = {
        "North East":"UKC",
        "North West":"UKD",
        "Yorkshire and The Humber":"UKE",
        "Yorkshire and The Humber":"UKE",
        "East Midlands":"UKF",
        "West Midlands":"UKG",
        "East of England":"UKH",
        "London":"UKI",
        "South East":"UKJ",
        "South West":"UKK",
        "England":"E92000001", # NUTS code for UK needs to be changed
        "Wales":"UKL",
        "Extra-Regio":"UKZ"
}

df["Reference Area"] = df["Reference Area"].map(lambda x: map_regions[x])

df['Reference Area'].unique()

df['Period'] = df['Period'].astype(str).replace('\.0', '', regex=True)
df["Period"] =  df["Period"].apply(date_time)

df["Period"]

df['Measure Type'].unique()

# 'Indices 2016=100'needs to be changed
df['Measure Type'] = df['Measure Type'].apply(lambda x: 'q-on-q-delta-gdp-from-gva' if 'Percentage change, quarter on previous quarter' in x else 'gdp-from-gva')

df['Measure Type'].unique()

df['Unit'].unique()

df['Unit']= df['Unit'].apply(lambda x: 'percentage' if 'Percentage' in x else 
                                      ('indices' if 'Indices' in x else x ))

df['Unit'].unique()

df.rename(columns={'OBS' : 'Value'}, inplace=True)

df = df[['Period', 'Reference Area', 'Industry Section', 'Measure Type', 'Unit', 'Value']]
df

#additional scraper info needed
comment = "Quarterly economic activity within Wales and the nine English regions (North East, North West, Yorkshire and The Humber, East Midlands, West Midlands, East of England, London, South East, South West) and Extra-Regio."
des = """
Regional GDP is designated as experimental statistics.
Indices reflect values measured at basic prices, which exclude taxes less subsidies on products.
Estimates cannot be regarded as accurate to the last digit shown.
Any apparent inconsistencies between the index numbers and the percentage change are due to rounding.
"""
metadata.dataset.description = comment + des
metadata.dataset.comment = comment
metadata.dataset.title = datasetTitle

df.columns

duplicate_df = df[df.duplicated(['Period', 'Reference Area', 'Industry Section', 'Measure Type', 'Unit',
       'Value'], keep = False)]
duplicate_df

df.drop_duplicates(subset = df.columns.difference(['Value']), inplace = True)

duplicate_df = df[df.duplicated(['Period', 'Reference Area', 'Industry Section', 'Measure Type', 'Unit',
       'Value'], keep = False)]
duplicate_df

df.to_csv("observations.csv", index = False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')
