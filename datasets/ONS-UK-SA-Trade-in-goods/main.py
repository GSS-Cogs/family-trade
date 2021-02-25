# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
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

# UK trade in services: all countries, non-seasonally adjusted

# +
from gssutils import *
import json

trace = TransformTrace()
df = pd.DataFrame()
cubes = Cubes("info.json")
info = json.load(open('info.json'))
scraper = Scraper(seed = 'info.json')

distribution = scraper.distribution(latest = True)
datasetTitle = distribution.title
tabs = { tab.name: tab for tab in distribution.as_databaker() }


# +
#Format Date
def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

def date_time(date):
    if len(date)  == 4:
        return 'year/' + date
    elif len(date) == 7:
        date = pd.to_datetime(date, format='%Y%b')
        return date.strftime('month/%Y-%m')
    else:
        return "Date Formatting Error"


# -

for name, tab in tabs.items():
    columns=["Period", "Geography", "Seasonal Adjustment", "Flow", "Marker"]
    trace.start(datasetTitle, tab, columns, distribution.downloadURL)
    
    flow = str(name.split()[-1]).lower()
    trace.Flow("Taken from tab title")
    observations = tab.excel_ref('C7').expand(DOWN).expand(RIGHT).is_not_blank().is_not_whitespace()
    year = tab.excel_ref('C5').expand(RIGHT).is_not_blank().is_not_whitespace()
    trace.Period("Taken from cell c5 across")
    geo = tab.excel_ref('A7').expand(DOWN).is_not_blank().is_not_whitespace()
    trace.Geography("Taken from cell ref A7 across")
    dimensions = [
        HDim(year,'Period',DIRECTLY,ABOVE),
        HDim(geo,'ONS Partner Geography',DIRECTLY,LEFT),
        HDimConst("Flow", flow),
    ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    trace.with_preview(tidy_sheet)
    trace.store("combined_dataframe", tidy_sheet.topandas())

# +
#Post Processing 
df = trace.combine_and_trace(datasetTitle, "combined_dataframe")
df.rename(columns={'OBS' : 'Value'}, inplace=True)
df["Period"] =  df["Period"].apply(date_time)
trace.Seasonal_Adjustment("Hardcoded as SA")
df.insert(loc=2, column='Seasonal Adjustment', value="SA")
    
df = df[["Period", "ONS Partner Geography", "Seasonal Adjustment", "Flow", "Value"]]

# +
scraper.dataset.family = 'trade'
scraper.dataset.description = scraper.dataset.description + """
These data are our best estimate of these bilateral UK trade flows. Users should note that alternative estimates are available, in some cases, via the statistical agencies for bilateral countries or through central databases such as 
UN Comtrade (https://comtrade.un.org/).

Some data for countries have been marked with N/A. This is because Trade in Goods do not collate data from these countries.
"""

df['Value'] = df['Value'].astype(int)
# -

cubes.add_cube(scraper, df.drop_duplicates(), datasetTitle)
cubes.output_all()
trace.render("spec_v1.html")

df.head(10)


