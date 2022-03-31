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
# list(tabs)

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


# +
# tidied_sheets
# -

stop

for name, tab in tabs.items():
    # columns=['Period','Reference Area','Sector', 'Industry Section', 'Change Type', 'Measure Type''Marker']

    if 'Contents' in name or 'NOTE' in name:
        print(tab.name)
        continue
        
    elif tab.name == "Key Figures":
        reference_area = tab.excel_ref("B5").expand(RIGHT).is_not_blank()
    else:
        reference_area = tab.name
        
        #sector = tab.excel_ref("B5").expand(RIGHT).is_not_blank()
        #trace.Sector("Selected as all non-blank values from cell ref B5 going right/across.")
        
    industry_section = tab.excel_ref("B6").expand(RIGHT).is_not_blank()
    
    indicies_or_percentage = tab.excel_ref('A7').fill(DOWN).one_of(['Indices 2016=100','Percentage change, quarter on previous quarter', 'Percentage change, quarter on same quarter a year ago', 'Percentage change, year on year'])
    period = tab.excel_ref('A9').expand(DOWN).is_not_blank() 
    # - indicies_or_percentage
    observations = industry_section.fill(DOWN).is_not_blank()
               
    if tab.name == "Key Figures":                
        dimensions = [
            HDim(period, "Period", DIRECTLY, LEFT),
            HDim(reference_area, "Reference Area", DIRECTLY, ABOVE),
            HDim(industry_section, "Industry Section", DIRECTLY, ABOVE),
            HDim(indicies_or_percentage, "Measure Type", CLOSEST, ABOVE),
            HDim(indicies_or_percentage, "Unit", CLOSEST, ABOVE),
        ]
        tidy_sheet = ConversionSegment(tab, dimensions, observations)

    else:                
        dimensions = [
            HDim(period, "Period", DIRECTLY, LEFT),
            HDimConst("Reference Area", reference_area),
            HDim(industry_section, "Industry Section", DIRECTLY, ABOVE),
            HDim(indicies_or_percentage, "Measure Type", CLOSEST, ABOVE),
            HDim(indicies_or_percentage, "Unit", CLOSEST, ABOVE),
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)

map_regions = {
        "North East":"http://data.europa.eu/nuts/code/UKC",
        "North West":"http://data.europa.eu/nuts/code/UKD",
        "Yorkshire and The Humber":"http://data.europa.eu/nuts/code/UKE",
        "Yorkshire and The Humber":"http://data.europa.eu/nuts/code/UKE",
        "East Midlands":"http://data.europa.eu/nuts/code/UKF",
        "West Midlands":"http://data.europa.eu/nuts/code/UKG",
        "East of England":"http://data.europa.eu/nuts/code/UKH",
        "London":"http://data.europa.eu/nuts/code/UKI",
        "South East":"http://data.europa.eu/nuts/code/UKJ",
        "South West":"http://data.europa.eu/nuts/code/UKK",
        "England":"http://statistics.data.gov.uk/id/statistical-geography/E92000001",
        "Wales":"http://data.europa.eu/nuts/code/UKL",
        "Extra-Regio":"http://data.europa.eu/nuts/code/UKZ"
}

#Post Processing 
df.rename(columns={'OBS' : 'Value'}, inplace=True)
df['Period'] = df['Period'].astype(str).replace('\.0', '', regex=True)
df["Reference Area"] = df["Reference Area"].map(lambda x: map_regions[x])
df['Industry Section'] = df['Industry Section'].map(lambda x: pathify(x))
df["Period"] =  df["Period"].apply(date_time)
df['Measure Type'] = df['Measure Type'].str.rstrip()
df['Measure Type'] = df['Measure Type'].apply(lambda x: 'y-on-y-delta-gdp-from-gva' if 'Percentage change, year on year' in x else 
                                      ('q-on-q-delta-gdp-from-gva' if 'Percentage change, quarter on previous quarter' in x else 
                                       ('q-on-last-year-q-delta-gdp-from-gva' if 'Percentage change, quarter on same quarter a year ago' in x else 'gdp-from-gva')))
df['Unit']= df['Unit'].str.split(" ", n = 1, expand = True) 
df['Unit']= df['Unit'].apply(lambda x: 'percentage' if 'Percentage' in x else 
                                      ('indices' if 'Indices' in x else x ))
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
scraper.dataset.description = comment + des
scraper.dataset.comment = comment
scraper.dataset.title = datasetTitle
