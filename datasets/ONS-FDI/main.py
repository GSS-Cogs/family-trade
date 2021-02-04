# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.7.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
from gssutils import *
from IPython.display import display
import json

cubes = Cubes("info.json")
trace = TransformTrace()

info = json.load(open('info.json'))
landingPages = info['landingPage']

display(landingPages)

inward_scraper = Scraper(next(page for page in landingPages if 'inwardtables' in page))
outward_scraper = Scraper(next(page for page in landingPages if 'outwardtables' in page))

display(inward_scraper)
display(outward_scraper)
# -

# Collect together all tabs in one list of `((tab name, direction), tab)`

tabs = {
    ** {(tab.name.strip(), 'inward'): tab for tab in inward_scraper.distribution(latest=True).as_databaker()},
    ** {(tab.name.strip(), 'outward'): tab for tab in outward_scraper.distribution(latest=True).as_databaker()}
}
print(list(tabs.keys()))


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
for (name, direction), tab in tabs.items():
    
    # Only process tabs starting .2, .3 and .4
    if '.' not in name:
        continue
    major, minor = name.split('.')
    if major not in ['2', '3', '4']:
        continue
    display(f'Processing tab {name}: {direction}')
    
    # Add transformTrace
    columns = ["Investment Direction", "Year", "International Trade Basis", "FDI Area", "FDI Component", "FDI Industry"]
    trace.start("{}:{}".format(name, direction), tab, columns, inward_scraper.distribution(latest=True).downloadURL if direction == "inward" else outward_scraper.distribution(latest=True).downloadURL)
    
    # Set anchors for header row
    top_right = tab.filter('£ million')
    top_right.assert_one()
    left_top = tab.filter('EUROPE').by_index(1)
    
    top_row = (left_top.fill(UP).fill(RIGHT) & top_right.expand(LEFT).fill(DOWN)).is_not_blank().is_not_whitespace()
    
    dims = []
    dims.append(HDim(top_row, 'top', DIRECTLY, ABOVE))
    
    # Select all the footer info as "bottom_block"
    bottom = tab.filter('The sum of constituent items may not always agree exactly with the totals shown due to rounding.')
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
    
    trace.FDI_Area('Take from lefthand side of tab')
    if to_remove:
        left_col = left_col - to_remove
        trace.FDI_Area('Removing unwanted text')
    left_dim = HDim(left_col, 'FDI Area', CLOSEST, UP)
    
    for cell, replace in overrides:
        left_dim.AddCellValueOverride(cell, replace)
    # Also, "IRELAND" should be "IRISH REPUBLIC"
    trace.FDI_Area('Overrid any occurances of "IRELAND" to "IRISH REPUBLIC".')
    left_dim.AddCellValueOverride('IRELAND', 'IRISH REPUBLIC')
    dims.append(left_dim)
    
    if minor != '1':
        trace.Year("Take year values from the column of continuous numbers higher than 1900")
        year_col = left_top.fill(RIGHT).is_number().filter(lambda x: x.value > 1900).by_index(1).expand(DOWN).is_number() - bottom_block
        dims.append(HDim(year_col, 'Year', DIRECTLY, LEFT))
        obs = year_col.fill(RIGHT) & top_row.fill(DOWN)
    else:
        trace.Year("Take year values from the header row")
        obs = left_col.fill(RIGHT) & top_row.fill(DOWN)
    
    cs = ConversionSegment(obs, dims, includecellxy=True)
    table = cs.topandas()

    # Post processing
    table.rename(columns={'OBS': 'Value'}, inplace=True)
    trace.FDI_Area('Add "fdi/" prefix then pathify')
    table['FDI Area'] = table['FDI Area'].map(lambda x: 'fdi/' + pathify(x.strip()))
    if minor == '1':
        # top header row is year
        table.rename(columns={'top': 'Year'}, inplace=True)
    table['Year'] = table['Year'].map(lambda x: int(float(x)))
    if minor != '2':
        trace.FDI_Component("Set based on source tab primary number, 2.x, 3.x etc")
        table['FDI Component'] = {
            '2': {'outward': 'total-net-fdi-abroad',
                  'inward': 'total-net-fdi-in-the-uk'},
            '3': {'outward': 'total-net-fdi-international-investment-position-abroad-at-end-period',
                  'inward': 'total-net-fdi-international-investment-position-in-the-uk-at-end-period'},
            '4': {'outward': 'total-net-fdi-earnings-abroad',
                  'inward': 'total-net-fdi-earnings-in-the-uk'}
        }.get(major).get(direction)
    else:
        trace.FDI_Component("Pathify all values")
        table.rename(columns={'top': 'FDI Component'}, inplace=True)
        table['FDI Component'] = table['FDI Component'].map(pathify)
    if minor == '3':
        table.rename(columns={'top': 'FDI Industry'}, inplace=True)
        trace.FDI_Industry('Replace any occurance of "Total" with "all-activites".')
        table['FDI Industry'] = table['FDI Industry'].map(
            lambda x: pathify(x) if x != 'Total' else 'all-activities'
        )
    else:
        trace.FDI_Industry('Set all to "all-activities".')
        table['FDI Industry'] = 'all-activities'
    # Disambiguate FDI Component between tabs 2.2 and 4.2
    if name == '2.2':
        trace.FDI_Component('Add prefixes, either "fdi-"" or "total-net-fdi-".')
        table['FDI Component'] = table['FDI Component'].map(
            lambda x: 'fdi-' + x if not x.startswith('total-net-foreign-direct-investment-') else
            'total-net-fdi-' + x[len('total-net-foreign-direct-investment-'):]
        )
    elif name == '4.2':
        trace.FDI_Component('Add prefixes, either "earnings-fdi-"" or "total-net-".')
        table['FDI Component'] = table['FDI Component'].map(
            lambda x: 'earnings-fdi-' + x if not x.startswith('total-net-') else
            'total-net-' + x[len('total-net-'):].replace('foreign-direct-investment', 'fdi')
        )
    trace.International_Trade_Basis('Set as BPM5 for pre 2012, else BPM5')
    table['International Trade Basis'] = table['Year'].map(lambda year: 'BPM5' if year < 2012 else 'BPM6')
    
    trace.Investment_Direction('Set direction as "{}".'.format(direction))
    table['Investment Direction'] = direction
    trace.store("FDI", table)
                
observations = trace.combine_and_trace("FDI", "FDI")
observations
# -

observations['Marker'] = observations['DATAMARKER'].map(
    lambda x: { '..' : 'disclosive',
               '-' : 'itis-nil'
        }.get(x, x))

from IPython.core.display import HTML
for col in observations:
    if col != 'Value':
        observations[col] = observations[col].astype('category')
        display(HTML(f'<h3>{col}</h3'))
        display(observations[col].cat.categories)

# +

observations = observations[['Investment Direction', 'Year', 'International Trade Basis',
                             'FDI Area', 'FDI Component', 'FDI Industry',
                             'Value', 'Marker',
                             '__x', '__y', '__tablename']]
# -

destinationFolder = Path('out')
destinationFolder.mkdir(exist_ok=True, parents=True)
observations.drop(columns=['__x', '__y', '__tablename'],axis = 1, inplace = True)
observations.drop_duplicates(subset=observations.columns.difference(['Value']), inplace =True)

# There are mutiple duplicate values due to empty cells from source data that makes error in Jenkins Those empty cells with no values are removed 

observation_duplicate = observations[observations.duplicated(['Investment Direction', 'Year', 'International Trade Basis',
                             'FDI Area', 'FDI Component', 'FDI Industry'
                              ],keep=False)]

observations_unique = observations.drop_duplicates(['Investment Direction', 'Year', 'International Trade Basis',
                             'FDI Area', 'FDI Component', 'FDI Industry'
                              ],keep=False)

observations.shape, observation_duplicate.shape, observations_unique.shape

observations = observation_duplicate[observation_duplicate['Value'] != '']

observations = pd.concat([observations_unique, observations])

observations.shape, observation_duplicate.shape, observations_unique.shape

# +

inward_scraper.dataset.title = inward_scraper.dataset.title.replace(': inward', '')
inward_scraper.dataset.comment = inward_scraper.dataset.comment.replace(
    'into the UK', 'into the UK and of UK companies abroad')
inward_scraper.dataset.landingPage = landingPages

from gssutils.metadata import THEME
inward_scraper.dataset.theme = THEME['business-industry-trade-energy']
inward_scraper.dataset.family = 'trade'

cubes.add_cube(inward_scraper, observations, inward_scraper.dataset.title)
cubes.output_all()

# -
trace.render("spec_v1.html")
