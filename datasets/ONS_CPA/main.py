# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.9.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

from gssutils import *
import json 

# + tags=["outputPrepend"]
info = json.load(open('info.json'))
scraper = Scraper(seed='info.json')
cubes = Cubes('info.json')
scraper.dataset.family = info['families']

# -

df = scraper.distribution(latest=True).as_pandas(header=None, na_values=[], keep_default_na=False, index_col=0)


# +
# Build the column multiindex to allow melting
df.columns = pd.MultiIndex.from_frame(df.iloc[0:7].T)

# Remove the records from the dataframe which are now the column headers
df = df.iloc[8:]

# +
# Unstack turns the dataframe to a series, creating a complex multiindex for rows
series = df.unstack()

# Name the series in the dataset, which helps when converting back to a dataframe
series.name = 'Trade in Goods'


# +
# Convert the series to a dataframe, and move the row multiindex to column values
df = series.to_frame().reset_index()

# Rename the column named 0 to 'Period'
df.rename({0: 'Period'}, axis=1, inplace=True)
# -

# Set period values to proper format
df['Period'].loc[df['Period'].str.len() == 7] = df['Period'].apply(lambda x:'/id/quarter/{year}-{quarter}'.format(year=x[:4], quarter=x[-2:]))
df['Period'].loc[df['Period'].str.len() == 4] = df['Period'].apply(lambda x:'/id/year/{year}'.format(year=x[:4]))

# Interprate the release dates and format
df['Next release'] = pd.to_datetime(df['Next release'], format='%d %B %Y').dt.strftime('/id/day/%Y-%m-%d')
df['Release Date'] = pd.to_datetime(df['Release Date'], format='%d-%m-%Y').dt.strftime('/id/day/%Y-%m-%d')

df

# We don't use the data within these cells
df.drop(labels=['Title', 'PreUnit', 'Unit', 'Important Notes'], axis=1, inplace=True)

# Add dataframe is in the cube
cubes.add_cube(scraper, df, scraper.distribution(latest=True).title)

# Write cube
cubes.output_all()
