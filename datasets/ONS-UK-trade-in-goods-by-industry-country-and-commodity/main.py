# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.4.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
from gssutils import *
import json

with open("info.json", "r") as f:
    landing_pages = json.load(f)["landingPage"]


# +
def tidy(url):
    scraper = Scraper(url)
    display(scraper)
    tabs = scraper.distribution(latest=True).as_databaker()
    tab = next(t for t in tabs if t.name != 'Contents')

    header = tab.excel_ref('A1').expand(RIGHT)
    country = header.regex(r'(?i)country').fill(DOWN).is_not_blank()
    industry = header.regex(r'(?i)industry').fill(DOWN).is_not_blank()
    direction = header.regex(r'(?i)direction').fill(DOWN).is_not_blank()
    commodity = header.regex(r'(?i)commodity').fill(DOWN).is_not_blank()
    years = header.fill(RIGHT).is_number()
    observations = years.fill(DOWN).is_not_blank()
    cs = ConversionSegment(observations, [
        HDim(years, 'Year', DIRECTLY, ABOVE),
        HDim(country, 'Country', DIRECTLY, LEFT),
        HDim(industry, 'Industry', DIRECTLY, LEFT),
        HDim(direction, 'Direction', DIRECTLY, LEFT),
        HDim(commodity, 'Commodity', DIRECTLY, LEFT)
    ])
    return scraper, cs.topandas()

scrapers, dfs = zip(* (tidy(url) for url in landing_pages))
obs = pd.concat(dfs)
obs.rename(columns={'OBS': 'Value','DATAMARKER' : 'Marker'}, inplace=True)
obs

# +
import numpy as np
from IPython.core.display import HTML

obs['Year'] = pd.to_numeric(obs['Year'], downcast='integer')

for col in obs.columns:
    if col not in ['Value', 'Year']:
        obs[col] = obs[col].astype('category')
        display(HTML(f'<h2>{col}</h2>'))
        display(obs[col].cat.categories)

# +
from pathlib import Path
out = Path('out')
out.mkdir(exist_ok=True)
codelists = out / 'codelists'
codelists.mkdir(exist_ok=True)

for col in ['Industry', 'Country', 'Commodity']:
    codelist = pd.DataFrame.from_records(
        obs[col].cat.categories.map(lambda x: x.split(' ', 1)),
        columns=['Notation', 'Label']
    )
    codelist['Parent Notation'] = ''
    codelist['Sort Priority'] = codelist
    codelist['Description'] = ''
    display(HTML(f'<h2>{col}</h2>'))
    display(codelist)
    codelist.to_csv(codelists / f'{col.lower()}.csv', index = False)
    obs[col].cat.categories = obs[col].cat.categories.map(lambda x: x.split()[0])

# +
obs.drop_duplicates().to_csv(out / 'observations.csv', index = False)

scraper = scrapers[0]

from gssutils.metadata import THEME
scraper.dataset.family = 'Trade'
scraper.dataset.theme = THEME['business-industry-trade-energy']
scraper.dataset.title = scraper.dataset.title.replace('imports', 'imports and exports')
scraper.dataset.comment = scraper.dataset.comment.replace('import', 'import and export')
scraper.dataset.landingPage = landing_pages

scraper
# -

with open(out / 'observations.csv-metadata.trig', 'wb') as metadata:
     metadata.write(scraper.generate_trig())
csvw = CSVWMetadata('https://gss-cogs.github.io/family-trade/reference/')
csvw.create(out / 'observations.csv', out / 'observations.csv-schema.json')


