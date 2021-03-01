# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.10.2
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
tabs = distribution.as_databaker()


# +
#Format Date
def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

def date_time(date):
    # Various ways they're representing a 4 digit year
    if isinstance(date, float) or len(date) == 6 and date.endswith(".0") or len(date) == 4:
        return f'year/{str(date).replace(".0", "")}'
    # Montha and year
    elif len(date) == 7:
        date = pd.to_datetime(date, format='%Y%b')
        return date.strftime('month/%Y-%m')
    else:
        raise Exception(f'Aborting, failing to convert value "{date}" to period')


# -

for tab in tabs:
    columns=["Period", "Geography", "Seasonal Adjustment", "Flow", "Marker"]
    trace.start(datasetTitle, tab, columns, distribution.downloadURL)
    
    flow = str(tab.name.split()[-1]).lower()
    trace.Flow("Taken from tab title")
    observations = tab.excel_ref('C7').expand(DOWN).expand(RIGHT).is_not_blank().is_not_whitespace()
    year = tab.excel_ref('C5').expand(RIGHT).is_not_blank().is_not_whitespace()
    trace.Period("Taken from cell c5 across")
    geo = tab.excel_ref('A7').expand(DOWN).is_not_blank().is_not_whitespace()
    trace.Geography("Taken from cell ref A7 across")
    
    trace.Seasonal_Adjustment("Hardcoded as SA")
    dimensions = [
        HDim(year,'Period',DIRECTLY,ABOVE),
        HDim(geo,'ONS Partner Geography',DIRECTLY,LEFT),
        HDimConst("Flow", flow),
        HDimConst("Seasonal Adjustment", "SA")
    ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    trace.with_preview(tidy_sheet)
    trace.store("combined_dataframe", tidy_sheet.topandas())

# +
#Post Processing 
df = trace.combine_and_trace(datasetTitle, "combined_dataframe")
df.rename(columns={'OBS' : 'Value', 'DATAMARKER': "Marker"}, inplace=True)
df["Period"] =  df["Period"].apply(date_time)
df = df.fillna('')

df = df[["Period", "ONS Partner Geography", "Seasonal Adjustment", "Flow", "Value", "Marker"]]

# +
scraper.dataset.family = 'trade'
scraper.dataset.description = scraper.dataset.description + """
These data are our best estimate of these bilateral UK trade flows. Users should note that alternative estimates are available, in some cases, via the statistical agencies for bilateral countries or through central databases such as 
UN Comtrade (https://comtrade.un.org/).

Some data for countries have been marked with N/A. This is because Trade in Goods do not collate data from these countries.
"""

df["Value"] = df["Value"].map(lambda x: int(x) if isinstance(x, float) else x)
df["Marker"] = df["Marker"].str.replace("N/A", "not-applicable")
# -

cubes.add_cube(scraper, df.drop_duplicates(), datasetTitle)
cubes.output_all()
trace.render("spec_v1.html")

df.head(10)


