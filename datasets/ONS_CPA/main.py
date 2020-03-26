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

# ###  CPA xlsx to Tidydata

# +
from gssutils import *

scraper = Scraper('https://www.ons.gov.uk/businessindustryandtrade/internationaltrade/datasets/' + \
                  'uktradeingoodsbyclassificationofproductbyactivity')
scraper
# -

tab = scraper.distributions[1].as_pandas(header=None, na_values=[], keep_default_na=False)

tab.rename(columns=tab.iloc[1], inplace=True)
tab.rename(columns={'CDID': 'Period'}, inplace=True)
tab

# The observations are in rows 7 on.
#
# Each CDID corresponds to a unique time-series slice. Unpivot the table so we have one row per observation and drop any rows with no value for the observation.

observations = tab[7:].rename(columns={'CDID': 'Period'})
observations = pd.melt(observations, id_vars=['Period'], var_name='CDID', value_name='Value')
observations['Value'] = pd.to_numeric(observations['Value'])
observations.dropna(inplace=True)
observations.reset_index(drop=True, inplace=True)
observations

# The date/time values need to be in a format that can be used to create URIs for British calendar intervals,
# see https://github.com/epimorphics/IntervalServer/blob/master/interval-uris.md#british-calendar-intervals

# +
import re
YEAR_RE = re.compile(r'[0-9]{4}')
YEAR_MONTH_RE = re.compile(r'([0-9]{4})\s+(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)')
YEAR_QUARTER_RE = re.compile(r'([0-9]{4})\s+(Q[1-4])')

# from https://stackoverflow.com/questions/597476/how-to-concisely-cascade-through-multiple-regex-statements-in-python
class Re(object):
  def __init__(self):
    self.last_match = None
  def fullmatch(self,pattern,text):
    self.last_match = re.fullmatch(pattern,text)
    return self.last_match

def time2period(t):
    gre = Re()
    if gre.fullmatch(YEAR_RE, t):
        return f"year/{t}"
    elif gre.fullmatch(YEAR_MONTH_RE, t):
        year, month = gre.last_match.groups()
        month_num = {'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04', 'MAY': '05', 'JUN': '06',
                     'JUL': '07', 'AUG': '08', 'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'}.get(month)
        return f"month/{year}-{month_num}"
    elif gre.fullmatch(YEAR_QUARTER_RE, t):
        year, quarter = gre.last_match.groups()
        return f"quarter/{year}-{quarter}"
    else:
        assert False, f"no match for {t}"

def period2periodicity(t):
    if t.startswith('year'):
        return 'A'
    elif t.startswith('month'):
        return 'M'
    else:
        return 'Q'

observations['Period'] = observations['Period'].apply(time2period)
observations['Periodicity'] = observations['Period'].apply(period2periodicity)
observations
# -

# CDID is an arbitrary/opaque 4 letter code registered by ONS and corresponds to a timeseries slice, so each CDID provides the value of a list of dimensions. These codes are elaborated in separate CSV files currently in https://github.com/ONS-OpenData/Ref_CDID/tree/master/lookup

# +
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
    #for k in ['tig_sitc', 'tig_cpa', 'tig_country', 'codelist']), sort=False)
    for k in ['tig_cpa']), sort=False)

for col in cdids:
    cdids[col] = cdids[col].astype('category')

cdids
# -

# Check that all CDIDs used in the source are defined in these tables.

defined_cdid_periods = set(cdids.index.values)
used_cdid_periods = set(
    observations[['CDID', 'Periodicity']].drop_duplicates().apply(
        lambda x: (x['CDID'], x['Periodicity']), axis='columns'
    ).values)
remaining_cdid_periods = used_cdid_periods.difference(defined_cdid_periods)
# assume all left over CDIDs are defined without periodicity
remaining_cdids = set(
    map(lambda x: x[0], remaining_cdid_periods)
).difference(set(
    map(lambda x: x[0], defined_cdid_periods)))
assert not remaining_cdids, 'Not all CDIDs defined: ' + str(remaining_cdids)

# +
cdids['AREA'].cat.categories = cdids['AREA'].cat.categories.map(
    lambda x: f'legacy/{x}'
)
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
    
cdids['PRODUCT'].cat.categories = cdids['PRODUCT'].cat.categories.map(product2cpa)
cdids['DIRECTION'].cat.categories = cdids['DIRECTION'].cat.categories.map(
    lambda x: 'balance' if x == 'BAL' else 'imports' if x == 'IM' else 'exports' if x == 'EX' else None
)
cdids.rename(columns={
    'PRODUCT': 'CPA 2008',
    'AREA': 'ONS Partner Geography',
    'DIRECTION': 'Flow',
    'PRICE': 'Price Classification',
    'SEASADJ': 'Seasonal Adjustment',
    'BASIS': 'International Trade Basis'
}, inplace=True)
# -

# Merge in the dimension values

observations = observations.merge(
    cdids, how = 'left', left_on = ['CDID', 'Periodicity'], right_index=True)
observations['Measure Type'] = pd.Series('GBP Total', index=observations.index, dtype='category')
observations['Unit'] = pd.Series('gbp-million', index=observations.index, dtype='category')
observations = observations[['ONS Partner Geography', 'Period', 'CDID', 'International Trade Basis',
                             'Flow', 'CPA 2008', 'Price Classification', 'Seasonal Adjustment',
                             'Measure Type', 'Value', 'Unit']].drop_duplicates()
observations

from pathlib import Path
out = Path('out')
out.mkdir(exist_ok=True)
observations.drop_duplicates().to_csv(out / 'observations.csv', index = False)

from gssutils.metadata import THEME
scraper.dataset.theme = THEME['business-industry-trade-energy']
scraper.dataset.family = 'Trade'
with open(out / 'observations.csv-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())
csvw = CSVWMetadata('https://gss-cogs.github.io/family-trade/reference/')
csvw.create(out / 'observations.csv', out / 'observations.csv-schema.json')
