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

# ###  MRET xlsx to Tidy Data
#
# Take the Trade in goods MRETS (all BOP - EU2013): time series dataset and convert to Tidy Data in CSV.

# +
from gssutils import *

scraper = Scraper('https://www.ons.gov.uk/economy/nationalaccounts/balanceofpayments/datasets/'
                  'tradeingoodsmretsallbopeu2013timeseriesspreadsheet')
scraper
# -

# Read in the spreadsheet as a table, naming the columns after the CDID (second row).

tab = scraper.distribution().as_pandas(header=None, na_values=[], keep_default_na=False)
tab.rename(columns=tab.iloc[1], inplace=True)
tab.rename(columns={'CDID': 'Period'}, inplace=True)
tab

# The observations are in rows 7 on.

observations = tab[7:].rename(columns={'CDID': 'Period'})
observations.head()

# Each CDID corresponds to a unique time-series slice. Unpivot the table so we have one row per observation and drop any rows with no value for the observation.

observations = pd.melt(observations, id_vars=['Period'], var_name='CDID', value_name='Value')
observations['Value'] = pd.to_numeric(observations['Value'])
observations.dropna(inplace=True)
#observations['Value'] = observations['Value'].astype('int64')
observations.reset_index(drop=True, inplace=True)
print(len(observations))
observations.tail(5)

# The date/time values need to be in a format that can be used to create URIs for British calendar intervals,
# see https://github.com/epimorphics/IntervalServer/blob/master/interval-uris.md#british-calendar-intervals

observations['Period'].unique()

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
    for k in ['tig_sitc', 'tig_cpa', 'tig_country', 'codelist']), sort=False)

for col in cdids:
    cdids[col] = cdids[col].astype('category')

cdids
# -

# __TODO: need to check whether the CDID period length matches the MRETS period length.__

# This (above) list seems to be missing some values. E.g. looking up `BOQM` on https://www.ons.gov.uk/timeseriestool finds `BOP:Exports:Tons:SA:Crude oil: SITC 333`.
#
# Check that all CDIDs used in MRETS are defined in these tables.

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

# Inspect the unique values for these dimensions.

for col in cdids:
    display(HTML('<b>' + col + '</b>'))
    display(cdids[col].unique())

# __TODO: Still not sure what to make of the titles provided for the CDIDs in the MRETS table.__
#
# __TODO: PERIOD doesn't seem to correspond to usage.__
#
# __TODO: Currently outputting only BOP; need to figure out what to do with all other data points.__

# +
bop_series = cdids[cdids['BASIS'] == 'BOP'].copy()
bop_cdids = set(v[0] for v in bop_series.index.values)

def area_country(row):
    if pd.isnull(row['AREA']) or row['AREA'] == '':
        if pd.isnull(row['COUNTRY']) or row['COUNTRY'] == '':
            return None
        assert row['COUNTRY'] != ''
        return 'cord/' + row['COUNTRY']
    else:
        assert pd.isnull(row['COUNTRY']) or row['COUNTRY'] == ''
        return 'legacy/' + row['AREA']

bop_series['ONS Partner Geography'] = bop_series.apply(area_country, axis=1)

def product_commodity(row):
    if pd.isnull(row['PRODUCT']) or row['PRODUCT'] == '':
        if pd.isnull(row['COMMODITY']) or row['COMMODITY'] == '':
            return None
        assert not pd.isnull(row['COMMODITY']) and row['COMMODITY'] != ''
        return row['COMMODITY']
    else:
        assert pd.isnull(row['COMMODITY']) or row['COMMODITY'] == ''
        return row['PRODUCT']

bop_series['CORD SITC'] = bop_series.apply(product_commodity, axis=1)

bop_series.drop(columns=['PERIOD', 'AREA', 'COUNTRY', 'PRODUCT', 'COMMODITY', 'BASIS'], inplace=True)
bop_series.rename(columns={'DIRECTION': 'Flow',
                           'PRICE': 'Price Classification',
                           'SEASADJ': 'Seasonal Adjustment'}, inplace=True)
bop_series.replace({'Flow': {'BAL': 'balance', 'IM': 'imports', 'EX': 'exports'}}, inplace=True)
bop_series['Measure Type'] = 'GBP Total'
bop_series['Unit'] = 'gbp-million'

bop_observations = observations[observations['CDID'].isin(bop_cdids)]
bop_observations = bop_observations.merge(
    bop_series, how = 'left', left_on = ['CDID', 'Periodicity'], right_index=True)
bop_observations.dropna(how='any', inplace=True)
bop_observations = bop_observations[['ONS Partner Geography', 'Period', 'CDID', 'Flow', 'CORD SITC',
                                     'Price Classification', 'Seasonal Adjustment',
                                     'Measure Type', 'Value', 'Unit']].drop_duplicates()
bop_observations

# +
destinationFolder = Path('out')
destinationFolder.mkdir(exist_ok=True, parents=True)

bop_observations.to_csv(destinationFolder / ('bop_observations.csv'), index = False)
# -

# Update dataset metadata

with open(destinationFolder / 'dataset.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())

# Since we're using CDIDs as attributes / slice keys in the resulting data cube, they need to be defined as such and given labels.

used_cdids = pd.DataFrame({'CDID': list(map(lambda x: x[0], used_cdid_periods))})
used_cdids['Title'] = tab.iloc[0][used_cdids['CDID']].values
used_cdids

# +
from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef, RDFS, OWL, XSD
from rdflib.namespace import SKOS
from rdflib.collection import Collection

CDID = Namespace('http://gss-data.org.uk/def/cdid/')
QB = Namespace('http://purl.org/linked-data/cube#')

g = Graph()
g.bind('skos', SKOS)
g.bind('rdfs', RDFS)
g.bind('cdid', CDID)
g.bind('qb', QB)

for i, cdid, title in used_cdids.itertuples():
    term = CDID.term(cdid)
    g.add((term, RDF.type, QB.Slice))
    g.add((term, SKOS.notation, Literal(cdid)))
    g.add((term, RDFS.label, Literal(title)))

print(g.serialize(format='n3').decode('utf-8')[:1000])
# -

with open(destinationFolder / 'cdids.ttl', 'wb') as f:
    g.serialize(f, format='n3')


