# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
from gssutils import *
import json
import numpy as np

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

trace = TransformTrace()
df = pd.DataFrame()
cubes = Cubes("info.json")
info = json.load(open('info.json'))
scraper = Scraper(seed = 'info.json')
scraper
# -

distribution = scraper.distribution(latest = True)
datasetTitle = distribution.title
tabs = { tab.name: tab for tab in distribution.as_databaker() }

for name, tab in tabs.items():
    columns=['Period','Reference Area','Sector', 'Industry Section', 'Change Type', 'Measure Type''Marker']
    trace.start(datasetTitle, tab, columns, distribution.downloadURL)
    if 'Contents' in name or 'NOTE' in name:
        continue   
    elif tab.name == "Key Figures":
        reference_area = tab.excel_ref("B5").expand(RIGHT).is_not_blank()
        trace.Reference_Area("Selected as all non-blank values from cell ref B5 going right/across.")
    else:
        reference_area = tab.name
        trace.Reference_Area("Selected as the tab name.")
        
        #sector = tab.excel_ref("B5").expand(RIGHT).is_not_blank()
        #trace.Sector("Selected as all non-blank values from cell ref B5 going right/across.")
        
    industry_section = tab.excel_ref("B6").expand(RIGHT).is_not_blank()
    trace.Industry_Section("Selected as all non-blank values from cell ref B6 going down")
    
    indicies_or_percentage = tab.excel_ref('A7').fill(DOWN).one_of(['Indices 2016=100','Percentage change, quarter on previous quarter', 'Percentage change, quarter on same quarter a year ago', 'Percentage change, year on year'])
    period = tab.excel_ref('A9').expand(DOWN).is_not_blank() - indicies_or_percentage
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
        # trace.with_preview(tidy_sheet)
        trace.store("combined_dataframe", tidy_sheet.topandas())
    else:                
        dimensions = [
            HDim(period, "Period", DIRECTLY, LEFT),
            HDimConst("Reference Area", reference_area),
            HDim(industry_section, "Industry Section", DIRECTLY, ABOVE),
            HDim(indicies_or_percentage, "Measure Type", CLOSEST, ABOVE),
            HDim(indicies_or_percentage, "Unit", CLOSEST, ABOVE),
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        # trace.with_preview(tidy_sheet)
        trace.store("combined_dataframe", tidy_sheet.topandas())

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
df = trace.combine_and_trace(datasetTitle, "combined_dataframe")
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

cubes.add_cube(scraper, df.drop_duplicates(), datasetTitle)
cubes.output_all()
trace.render("spec_v1.html")
