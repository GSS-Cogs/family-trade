# %%
import pandas as pandas
from gssutils import *

metadata = Scraper(seed="info.json")
distribution = metadata.distribution(latest=True)
tabs = distribution.as_databaker()
tidied_sheets = []
# %%
for tab in tabs:
    if '.' in tab.name:
        flow = tab.name
        geo = tab.filter(contains_string("Country Code")).fill(
            DOWN).is_not_blank().is_not_whitespace()
        year = tab.filter(contains_string('Country Name')).shift(
            RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace()
        observations = geo.shift(2, 0).expand(
            RIGHT).is_not_blank().is_not_whitespace()
        dimensions = [
            HDim(year, 'Period', DIRECTLY, ABOVE),
            HDim(geo, 'ONS Partner Geography', DIRECTLY, LEFT),
            HDimConst("Flow", flow),
            HDimConst("Seasonal Adjustment", "SA")
        ]
        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        tidied_sheets.append(tidy_sheet.topandas())

# %%
df = pd.concat(tidied_sheets, sort=True)  # .fillna('')
df.rename(columns={'OBS': 'Value', 'DATAMARKER': 'Marker'}, inplace=True)
df["Marker"] = df["Marker"].str.replace("X", "data-not-collated")
df['Flow'] = df['Flow'].apply(lambda x: 'exports' if 'Exports' in x else
                              ('imports' if 'Imports' in x else x))
df['Period 2'] = df['Period'].map(lambda x: x[4:])
df['Period 3'] = df['Period'].map(lambda x: x[:4])
df = df.replace({'Period 2': {'Jan': '01',
                              'Feb': '02',
                              'Mar': '03',
                              'Apr': '04',
                              'May': '05',
                              'Jun': '06',
                              'Jul': '07',
                              'Aug': '08',
                              'Sep': '09',
                              'Oct': '10',
                              'Nov': '11',
                              'Dec': '12'}})
# %%
df['Period'] = df.apply(lambda x: 'quarter/' + x['Period 3'] + '-' + x['Period 2'] if 'Q' in x['Period 2'] else (
    'month/' + x['Period 3'] + '-' + x['Period 2'] if x['Period 2'].isnumeric() else 'year/' + x['Period']), axis=1)
df = df.drop(columns=['Period 2', 'Period 3'])
df = df[["Period", "ONS Partner Geography",
         "Seasonal Adjustment", "Flow", "Value", "Marker"]]

# %%
metadata.dataset.title = metadata.dataset.title + " 2021"
metadata.dataset.description = metadata.dataset.description + """
These data are our best estimate of these bilateral UK trade flows. Users should note that alternative estimates are available, in some cases, via the statistical agencies for bilateral countries or through central databases such as 
UN Comtrade (https://comtrade.un.org/).

Some data for countries have been marked with N/A. This is because Trade in Goods do not collate data from these countries.
"""
# %%
df.to_csv("observations.csv", index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')
