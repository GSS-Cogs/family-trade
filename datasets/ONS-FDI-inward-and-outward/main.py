# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
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

# +
from gssutils import *

inward_scraper = Scraper('https://www.ons.gov.uk/businessindustryandtrade/business/businessinnovation/datasets/' \
                  'foreigndirectinvestmentinvolvingukcompanies2013inwardtables')
outward_scraper = Scraper('https://www.ons.gov.uk/businessindustryandtrade/business/businessinnovation/datasets/' \
                  'foreigndirectinvestmentinvolvingukcompaniesoutwardtables')

display(inward_scraper)
display(outward_scraper)
# -

# Collect together all tabs in one list of `((tab name, direction), tab)`

sheets = {
    ** {(sheet.name.strip(), 'inward'): sheet for sheet in inward_scraper.distribution(latest=True).as_databaker()},
    ** {(sheet.name.strip(), 'outward'): sheet for sheet in outward_scraper.distribution(latest=True).as_databaker()}
}
print(list(sheets.keys()))


# A common issue is where a dimension label is split over more than one cell.
# The following function does a rudimentary search for these splits in a bag, returns a list of
# pairs of cells and their replacement, along with a list of extraneous cells to remove
# from the bag.

def split_overrides(bag, splits):
    overrides = []
    to_remove = None
    for split in splits:
        for cell in bag:
            c = cell
            found = True
            remove_list = []
            for s in split:
                if c.value.strip() != s:
                    found = False
                    break
                try:
                    c = c.shift(DOWN)
                except:
                    found = False
                    break
                remove_list.append(c)
            if found:
                overrides.append((cell, ' '.join(split)))
                for c in remove_list:
                    if to_remove is None:
                        to_remove = c
                    else:
                        to_remove = to_remove | c
    return (overrides, to_remove)


# +
tables = []
for (name, direction), sheet in sheets.items():
    if '.' not in name:
        continue
    major, minor = name.split('.')
    if major not in ['2', '3', '4']:
        continue
    display(f'Processing tab {name}: {direction}')
    dims = []
    top_right = sheet.filter('£ million')
    top_right.assert_one()
    left_top = sheet.filter('EUROPE').by_index(1)
    top_row = (left_top.fill(UP).fill(RIGHT) & top_right.expand(LEFT).fill(DOWN)).is_not_blank().is_not_whitespace()
    dims.append(HDim(top_row, 'top', DIRECTLY, ABOVE))
    bottom = sheet.filter('The sum of constituent items may not always agree exactly with the totals shown due to rounding.')
    bottom.assert_one()
    bottom_block = bottom.shift(UP).expand(RIGHT).expand(DOWN)
    left_col = (left_top | left_top.shift(RIGHT) | left_top.shift(RIGHT) \
                .shift(RIGHT)).expand(DOWN).is_not_blank().is_not_whitespace() - bottom_block
    left_col = left_col - left_col.filter('of which')
    # fix up cells that have been split
    overrides, to_remove = split_overrides(left_col, [
        ('OTHER', 'EUROPEAN', 'COUNTRIES'),
        ('OTHER EUROPEAN', 'COUNTRIES'),
        ('UK OFFSHORE', 'ISLANDS'),
        ('NEAR & MIDDLE EAST', 'COUNTRIES'),
        ('NEAR & MIDDLE', 'EAST COUNTRIES'),
        ('AUSTRALASIA &', 'OCEANIA'),
        ('AUSTRALASIA', '& OCEANIA'),
        ('CENTRAL & EASTERN', 'EUROPE'),
        ('CENTRAL &', 'EASTERN', 'EUROPE'),
        ('GULF ARABIAN', 'COUNTRIES'),
        ('OTHER ASIAN', 'COUNTRIES')
    ])
    if to_remove:
        left_col = left_col - to_remove
    left_dim = HDim(left_col, 'ONS FDI Area', CLOSEST, UP)
    for cell, replace in overrides:
        left_dim.AddCellValueOverride(cell, replace)
    # Also, "IRELAND" should be "IRISH REPUBLIC"
    left_dim.AddCellValueOverride('IRELAND', 'IRISH REPUBLIC')
    dims.append(left_dim)
    if minor != '1':
        year_col = left_top.fill(RIGHT).is_number().filter(lambda x: x.value > 1900).by_index(1).expand(DOWN).is_number() - bottom_block
        dims.append(HDim(year_col, 'Year', DIRECTLY, LEFT))
        obs = year_col.fill(RIGHT) & top_row.fill(DOWN)
    else:
        obs = left_col.fill(RIGHT) & top_row.fill(DOWN)
    cs = ConversionSegment(obs, dims, includecellxy=True)
    table = cs.topandas()
    table.drop(table[table['DATAMARKER'].notna()].index, inplace=True)
    table.drop(columns=['DATAMARKER'], inplace=True)
    table.rename(columns={'OBS': 'Value'}, inplace=True)
    table['ONS FDI Area'] = table['ONS FDI Area'].map(lambda x: 'fdi/' + pathify(x.strip()))
    if minor == '1':
        # top header row is year
        table.rename(columns={'top': 'Year'}, inplace=True)
    table['Year'] = table['Year'].map(lambda x: int(float(x)))
    if minor != '2':
        table['FDI Component'] = {
            '2': {'outward': 'total-net-fdi-abroad',
                  'inward': 'total-net-fdi-in-the-uk'},
            '3': {'outward': 'total-net-fdi-international-investment-position-abroad-at-end-period',
                  'inward': 'total-net-fdi-international-investment-position-in-the-uk-at-end-period'},
            '4': {'outward': 'total-net-fdi-earnings-abroad',
                  'inward': 'total-net-fdi-earnings-in-the-uk'}
        }.get(major).get(direction)
    else:
        table.rename(columns={'top': 'FDI Component'}, inplace=True)
        table['FDI Component'] = table['FDI Component'].map(pathify)
    if minor == '3':
        table.rename(columns={'top': 'FDI Industry'}, inplace=True)
        table['FDI Industry'] = table['FDI Industry'].map(
            lambda x: pathify(x) if x != 'Total' else 'all-activities'
        )
    else:
        table['FDI Industry'] = 'all-activities'
    # Disambiguate FDI Component between tabs 2.2 and 4.2
    if name == '2.2':
        table['FDI Component'] = table['FDI Component'].map(
            lambda x: 'fdi-' + x if not x.startswith('total-net-foreign-direct-investment-') else
            'total-net-fdi-' + x[len('total-net-foreign-direct-investment-'):]
        )
    elif name == '4.2':
        table['FDI Component'] = table['FDI Component'].map(
            lambda x: 'earnings-fdi-' + x if not x.startswith('total-net-') else
            'total-net-' + x[len('total-net-'):].replace('foreign-direct-investment', 'fdi')
        )
    table['International Trade Basis'] = table['Year'].map(lambda year: 'BPM5' if year < 2012 else 'BPM6')
    table['Investment Direction'] = direction
    tables.append(table)

observations = pd.concat(tables, sort=False)
observations
# -

from IPython.core.display import HTML
for col in observations:
    if col != 'Value':
        observations[col] = observations[col].astype('category')
        display(HTML(f'<h3>{col}</h3'))
        display(observations[col].cat.categories)

observations['Unit'] = 'gbp-million'
observations['Measure Type'] = 'GBP Total'
observations = observations[['Investment Direction', 'Year', 'International Trade Basis',
                             'ONS FDI Area', 'FDI Component', 'FDI Industry',
                             'Value', 'Unit', 'Measure Type',
                             '__x', '__y', '__tablename']]

# +
out = Path('out')
out.mkdir(exist_ok=True, parents=True)

observations.drop(columns=['__x', '__y', '__tablename']).drop_duplicates(subset=observations.columns.difference(['Value','__x', '__y', '__tablename'])).to_csv(out / 'observations.csv', index=False)

# +
inward_scraper.dataset.title = inward_scraper.dataset.title.replace(': inward', '')
inward_scraper.dataset.comment = inward_scraper.dataset.comment.replace(
    'into the UK', 'into the UK and of UK companies abroad')

from gssutils.metadata import THEME
inward_scraper.dataset.theme = THEME['business-industry-trade-energy']
inward_scraper.dataset.family = 'trade'

with open(out / 'dataset.trig', 'wb') as metadata:
    metadata.write(inward_scraper.generate_trig())
csvw = CSVWMetadata('https://gss-cogs.github.io/ref_trade/')
csvw.create(out / 'observations.csv', out / 'observations.csv-schema.json')
# -


