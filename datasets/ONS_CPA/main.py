# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.1.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

from gssutils import *
import json 
import re

# # + tags=["outputPrepend"]
info = json.load(open('info.json'))
scraper = Scraper(seed='info.json')
cubes = Cubes('info.json')
scraper.dataset.family = info['families']
df = scraper.distribution(latest=True).as_pandas(header=None, na_values=[], keep_default_na=False, index_col=0)
# -

# Build the column multiindex to allow melting
df.columns = pd.MultiIndex.from_frame(df.iloc[0:7].T)
# Remove the records from the dataframe which are now the column headers
df = df.iloc[8:]
# Unstack turns the dataframe to a series, creating a complex multiindex for rows
series = df.unstack()
# Name the series in the dataset, which helps when converting back to a dataframe
series.name = 'Value'
# Convert the series to a dataframe, and move the row multiindex to column values
df = series.to_frame().reset_index()
# Rename the column named 0 to 'Period'
df.rename({0: 'Period'}, axis=1, inplace=True)
# Set period values to proper format
df['Period'].loc[df['Period'].str.len() == 7] = df['Period'].apply(lambda x:'quarter/{year}-{quarter}'.format(year=x[:4], quarter=x[-2:]))
df['Period'].loc[df['Period'].str.len() == 4] = df['Period'].apply(lambda x:'year/{year}'.format(year=x[:4]))
# Interprate the release dates and format
df['Next release'] = pd.to_datetime(df['Next release'], format='%d %B %Y').dt.strftime('/id/day/%Y-%m-%d')
df['Release Date'] = pd.to_datetime(df['Release Date'], format='%d-%m-%Y').dt.strftime('/id/day/%Y-%m-%d')
# We don't use the data within these cells
df.drop(labels=['Title', 'PreUnit', 'Unit', 'Important Notes'], axis=1, inplace=True)

df.rename(columns={'CDID' : 'cdid'}, inplace=True)

n = len(pd.unique(df['cdid'])) 
print("No.of.unique values :",  
      n)

from IPython.display import display, HTML
from io import BytesIO
def fetch_table(t):
    return BytesIO(scraper.session.get('https://github.com/ONS-OpenData/Ref_CDID/raw/master/lookup/' + t).content)
cdids = pd.concat((
    pd.read_csv(fetch_table(f'{k}.csv'),
                       na_values=[''], keep_default_na=False, index_col=[0,7],
                       dtype={'AREA': str, 'DIRECTION': str, 'BASIS': str,
                              'PRICE': str, 'SEASADJ': str,
                              'PRODUCT': str, 'COUNTRY': str},
                       converters={'COMMODITY': lambda x: str(x).strip()})
    #for k in ['tig_sitc', 'tig_cpa', 'tig_country', 'codelist', 'mrets_data' ]), sort=False)
    for k in ['tig_cpa']), sort=False)
for col in cdids:
    cdids[col] = cdids[col].astype('category')
cdids.index = cdids.index.get_level_values('cdid')

defined_cdid = set(cdids.index.values)
used_cdid = set(
    df[['cdid']].drop_duplicates().apply(
        lambda x: (x['cdid']), axis='columns'
    ).values)
remaining_cdid = used_cdid.difference(defined_cdid)
remaining_cdids = set(
    map(lambda x: x[0], remaining_cdid)
).difference(set(
    map(lambda x: x[0], defined_cdid)))
assert not remaining_cdids, 'Not all CDIDs defined: ' + str(remaining_cdids)


# +
class Re(object):
  def __init__(self):
    self.last_match = None
  def fullmatch(self,pattern,text):
    self.last_match = re.fullmatch(pattern,text)
    return self.last_match

cdids.rename(columns={
    'PRODUCT': 'CPA 2008',
    'AREA': 'ONS Partner Geography',
    'DIRECTION': 'Flow Directions',
    'PRICE': 'Price Classification',
    'SEASADJ': 'Seasonal Adjustment',
    'BASIS': 'International Trade Basis'
}, inplace=True)

SECTION_RE = re.compile(r'[A-S]')
DIVISION_RE = re.compile(r'[0-9]{1,2}')
GROUP_RE = re.compile(r'[0-9]{1,2}\.[0-9]')
CLASS_RE = re.compile(r'[0-9]{2}\.[0-9]{2}')
ONS_RE = re.compile(r'30.3[ABC]|TOTAL')
def product2cpa(p):
    gre = Re()
    if gre.fullmatch(SECTION_RE, p):
        return f"section/{p}"
    elif gre.fullmatch(DIVISION_RE, p):
        if len(p) == 1:
            return f"division/0{p}"
        else:
            return f"division/{p}"
    elif gre.fullmatch(GROUP_RE, p):
        if p[1] == '.':
            return f"group/0{p}"
        else:
            return f"group/{p}"
    elif gre.fullmatch(CLASS_RE, p):
        return f"class/{p}"
    elif gre.fullmatch(ONS_RE, p):
        return f"ons/{p}"
    else:
        assert False, f"no match for {p}"
    
cdids['CPA 2008'].cat.categories = cdids['CPA 2008'].cat.categories.map(product2cpa)
cdids['Flow Directions'].cat.categories = cdids['Flow Directions'].cat.categories.map(
    lambda x: 'balance' if x == 'BAL' else 'imports' if x == 'IM' else 'exports' if x == 'EX' else None
)
# -

merged = pd.merge(df, cdids, on='cdid', how='left').drop_duplicates()
merged.rename(columns={'cdid' : 'CDID'}, inplace=True)
merged = merged[['ONS Partner Geography', 'Period', 'CDID', 'International Trade Basis',
                             'Flow Directions', 'CPA 2008', 'Price Classification', 'Seasonal Adjustment','Value',]].drop_duplicates()
merged.head(10)

# Have set up the CPA codelist to just include the code, so removeing prefix
merged['CPA 2008'] = merged['CPA 2008'].str.replace('group/','')
merged['CPA 2008'] = merged['CPA 2008'].str.replace('division/','')
merged['CPA 2008'] = merged['CPA 2008'].str.replace('section/','')
merged['CPA 2008'] = merged['CPA 2008'].str.replace('class/','')
merged['CPA 2008'].unique()

# +
#d = merged[merged['CPA 2008'] == 'ons/TOTAL']
#d.head(60)
#d['Flow Directions'].unique()
# -

# Add dataframe is in the cube
cubes.add_cube(scraper, merged, scraper.distribution(latest=True).title)

# +
#print(scraper.dataset.family)
#print(scraper.dataset.title)
#print(scraper.dataset.comment)
#print(scraper.dataset.description)
# -

# Write cube
cubes.output_all()


