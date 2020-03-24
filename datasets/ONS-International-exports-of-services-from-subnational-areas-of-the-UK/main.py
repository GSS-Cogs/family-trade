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

# UK trade in services: all countries, non-seasonally adjusted

# +
from gssutils import *

scraper = Scraper('https://www.ons.gov.uk/businessindustryandtrade/internationaltrade/datasets/internationalexportsofservicesfromsubnationalareasoftheuk')
tabs = { tab.name: tab for tab in scraper.distributions[0].as_databaker() }
# -

list(tabs)

next_table = pd.DataFrame()

# +
# %%capture

# %run "1a.py"
next_table = pd.concat([next_table, new_table])
# %run "1b.py"
next_table = pd.concat([next_table, new_table])
# %run "2a.py"
next_table = pd.concat([next_table, new_table])
# %run "2b.py"
next_table = pd.concat([next_table, new_table])
# %run "3.py"
next_table = pd.concat([next_table, new_table])
# %run "4a.py"
next_table = pd.concat([next_table, new_table])
# %run "4b.py"
next_table = pd.concat([next_table, new_table])
# -

next_table.head()

from pathlib import Path
import numpy as np
out = Path('out')
out.mkdir(exist_ok=True)
next_table.drop_duplicates().to_csv(out / 'observations.csv', index = False)

scraper.dataset.family = 'trade'
from gssutils.metadata import THEME
scraper.dataset.theme = THEME['business-industry-trade-energy']
with open(out / 'observations.csv-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())

csvw = CSVWMetadata('https://gss-cogs.github.io/ref_trade/')
csvw.create(out / 'observations.csv', out / 'observations.csv-schema.json')
