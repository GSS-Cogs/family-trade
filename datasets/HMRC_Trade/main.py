# -*- coding: utf-8 -*-
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

scraper = Scraper('https://www.uktradeinfo.com/Statistics/OverseasTradeStatistics/AboutOverseastradeStatistics/Pages/OTSReports.aspx')
scraper
# -

scraper.select_dataset(title=lambda x: x.startswith('UK Trade in Goods by Business Characteristics'))
scraper

idbrs = sorted(
    [dist for dist in scraper.distributions if dist.title.startswith('IDBR OTS tables')],
    key=lambda d: d.title, reverse=True)
idbr = idbrs[0]
display(idbr.title)
tabs = {tab.name: tab for tab in idbr.as_databaker()}
tabs.keys()

# +
# %%capture

processors = [
    "Business count by Age of Business.py",
    "Business count by Employee Size.py",
    "Business count by Industry Group.py",
    "Employee count for Businesses by Age of Business.py",
    "Employee count for Businesses by Employee Size.py",
    "Employee count for Businesses by Industry Group.py",
    "Total value of UK trade by Age of Business.py",
    "Total value of UK trade by Employee Size.py",
    "Total value of UK trade by Industry Group.py",
    "TRADE IN GOODS STATISTICS -Business Count.py",
    "TRADE IN GOODS STATISTICS -Employee Count and age business.py",
    "TRADE IN GOODS STATISTICS -Employee Count and age employee count.py",
    "TRADE IN GOODS STATISTICS -Employee Count and age.py",
    "TRADE IN GOODS STATISTICS -Employee Count.py",
    "TRADE IN GOODS STATISTICS -total value of UK Trade.py",
    "TRADE IN GOODS STATISTICS_Employee size_Businesses.py",
    "TRADE IN GOODS STATISTICS_Employee size_Employee count.py",
    "TRADE IN GOODS STATISTICS_Employee size_value.py"
]

def create_table(proc):
    %run "$proc"
    return new_table

final_table = pd.concat(create_table(p) for p in processors)
# -

final_table.fillna('Total', inplace = True)
final_table

# Rationalise the codes used in each dimension

for d in final_table:
    if d not in ['Value']:
        display(d)
        display(final_table[d].unique())

# +
final_table['Employment'] = final_table['Employment'].map(pathify)
final_table['HMRC Industry'] = final_table['HMRC Industry'].map(pathify)
final_table.replace({
    'Employment': {
        'total': 'total-employees',
        'grand-total-employees': 'total-employees',
        'no-employees': '0-employees'
    },
    'Flow': {
        'Export': 'exports',
        'Import': 'imports'
    },
    'Unit': {
        '£ Million': 'GBP Million'
    },
    'Age of Business': {
        'Total years': 'Total',
        '20 + years': '20+ years',
        'Unknown years': 'Unknown',
        '6 to 9  years': '6 to 9 years',
        ' years': 'Total',
        'years': 'Total'
    }
}, inplace=True)

for d in final_table:
    if d not in ['Value']:
        display(d)
        display(final_table[d].unique())
# -

# Distinguish measure types for business and employee counts

final_table.loc[(final_table['Measure Type'] == 'Count') & (final_table['Unit'] == 'Businesses'),
               'Measure Type'] = 'Count of Businesses'
final_table.loc[(final_table['Measure Type'] == 'Count') & (final_table['Unit'] == 'Employees'),
               'Measure Type'] = 'Count of Employees'
final_table.reset_index(inplace=True)
final_table

final_table = final_table[['Geography','Year','Employment','Flow','Age of Business','HMRC Industry','Measure Type','Value','Unit']].copy()
final_table.drop_duplicates(inplace=True)
final_table

# The RDF Cube model (in [IC-17](https://www.w3.org/TR/vocab-data-cube/#wf-rules)) requires that, where an observation is present for a given set of dimensions, observations be provided for all of the measures.
#
# The data violates this integrity constraint (potentially due to filters in the upstream process) and so the Tidyish view in PMD is currently not rendering correctly.

key_dimensions = ['Geography','Year','Employment','Flow','Age of Business','HMRC Industry']
obs_counts = final_table.groupby(key_dimensions).size().reset_index(name='Observation Count')
obs_counts['Observation Count'].value_counts()

# We probably ought to resolve this with data markers. For now though, it should suffice to only emit observations from combinations of dimension-values where all three measures are present.

valid_dims = obs_counts[(obs_counts['Observation Count']==3)]
final_table = final_table.merge(valid_dims.drop('Observation Count',1), how='inner', on=key_dimensions)
final_table.shape

out = Path('out')
out.mkdir(exist_ok=True)
final_table.to_csv(out / 'observations.csv', index = False)

scraper.dataset.family = 'trade'
from gssutils.metadata import THEME
scraper.dataset.theme = THEME['business-industry-trade-energy']
with open(out / 'observations.csv-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())

csvw = CSVWMetadata('https://gss-cogs.github.io/ref_trade/')
csvw.create(out / 'observations.csv', out / 'observations.csv-schema.json')
