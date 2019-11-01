# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.2.4
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
from gssutils import *

scraper = Scraper("https://www.gov.uk/government/collections/uk-regional-trade-in-goods-statistics-disaggregated-by-smaller-geographical-areas")
scraper
# -

scraper.select_dataset(latest=True)
scraper

tabs = {tab.name: tab for tab in scraper.distribution(title=lambda t: 'Data Tables' in t).as_databaker()}
#tabs.keys()

year_cell = tabs['Title'].filter('Detailed Data Tables').shift(UP)
year_cell.assert_one()
dataset_year = int(year_cell.value)
#dataset_year

# +
# %%capture

def process_tab(t):
    %run "$t"
    return tidy

table = pd.concat(process_tab(f'{t}.py') for t in ['T1', 'T2', 'T3', 'T4', 'T5'])
table.count()
# -
sorted(table)
table = table[(table['Marker'] != 'residual-trade')]
table = table.drop_duplicates()
tidy['HMRC Partner Geography'] = tidy['HMRC Partner Geography'].cat.rename_categories({
        'EU'   : 'C',
        'Non EU' : 'non eu'})
#table.count()
#t = table[(table['NUTS Geography'] == 'nuts2/ea-other') & (table['HMRC Partner Geography'] == 'C') & (table['Value'] == 127)]
#tidy =tidy[['Year', 'NUTS Geography','HMRC Partner Geography','Flow','SITC 4','Measure Type', 'Value', 'Unit','Marker']]


out = Path('out')
out.mkdir(exist_ok=True)
table.to_csv(out / 'observations.csv', index = False)

# +
from gssutils.metadata import THEME
scraper.dataset.family = 'Trade'
scraper.dataset.theme = THEME['business-industry-trade-energy']

with open(out / 'dataset.trig', 'wb') as metadata:
     metadata.write(scraper.generate_trig())
#csvw = CSVWMetadata('https://ons-opendata.github.io/ref_trade/')
csvw = CSVWMetadata('https://gss-cogs.github.io/ref_trade/')
csvw.create(out / 'observations.csv', out / 'observations.csv-schema.json')
# -


