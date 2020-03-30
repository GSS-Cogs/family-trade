# -*- coding: utf-8 -*-
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

# The Pink Book 2019

# +
from gssutils import *

scraper = Scraper('https://www.ons.gov.uk/economy/nationalaccounts/balanceofpayments/datasets/3tradeinservicesthepinkbook2016')
tabs = { tab.name: tab for tab in scraper.distributions[0].as_databaker() }
# -

list(tabs)

next_table = pd.DataFrame()

# +
# %%capture

# %run "3.1.py"
next_table = pd.concat([next_table, new_table])
# %run "3.2.py"
next_table = pd.concat([next_table, new_table])
# %run "3.3.py"
next_table = pd.concat([next_table, new_table])
# %run "3.4.py"
next_table = pd.concat([next_table, new_table])
# %run "3.5.py"
next_table = pd.concat([next_table, new_table])
# %run "3.6.py"
next_table = pd.concat([next_table, new_table])
# %run "3.7.py"
next_table = pd.concat([next_table, new_table])
# %run "3.8.py"
next_table = pd.concat([next_table, new_table])
# %run "3.9.py"
next_table = pd.concat([next_table, new_table])
# %run "3.10.py"
next_table = pd.concat([next_table, new_table])
# -

next_table['Unit'] = next_table['Unit'].map(
    lambda x: { '£ Million' : 'gbp-million' 
        }.get(x, x))

next_table['Marker'] = next_table['DATAMARKER'].map(
    lambda x: { '..' : 'not-available' ,
               '-' : 'nil-or-less-than-a-million'
        }.get(x, x))

next_table['Flow'] = next_table['Flow'].map(pathify)

next_table = next_table[['Geography','Year','Pink Book Services','Flow','Measure Type','Value','Unit','Marker']]

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

csvw = CSVWMetadata('https://gss-cogs.github.io/family-trade/reference/')
csvw.create(out / 'observations.csv', out / 'observations.csv-schema.json')
