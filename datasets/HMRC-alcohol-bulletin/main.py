# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py
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

import glob
from gssutils import *
from gssutils.metadata import THEME
import pandas as pd

next_table = pd.DataFrame()

# +
# %%capture

# %run 'T1_T2_ Wine_Duty_wine_and_made_wine.py' 
next_table = pd.concat([next_table, Final_table])

# %run "T3_Spirits_Duty_statistics.py"
next_table = pd.concat([next_table, Final_table])

# %run 'T4_ Beer_Duty_and_Cider_Duty_statistics.py'
next_table = pd.concat([next_table, Final_table])

# %run 'R2_Historic_alcohol_duty_rates.py'
next_table = pd.concat([next_table, Final_table])
# -

next_table

# +
destinationFolder = Path('out')
destinationFolder.mkdir(exist_ok=True, parents=True)

next_table.to_csv(destinationFolder / ('observations.csv'), index = False)

# +
scraper.dataset.family = 'trade'
from gssutils.metadata import THEME

with open(destinationFolder / 'observations.csv-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())
# -

csvw = CSVWMetadata('https://gss-cogs.github.io/family-trade/reference/')
csvw.create(destinationFolder / 'observations.csv', destinationFolder / 'observations.csv-schema.json')


