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

# # ONS Trade in goods: country-by-commodity, imports and exports
#
# This data is split into two distributions, one for imports and the other for exports:
#
# https://www.ons.gov.uk/economy/nationalaccounts/balanceofpayments/datasets/uktradecountrybycommodityimports
#
# and
#
# https://www.ons.gov.uk/economy/nationalaccounts/balanceofpayments/datasets/uktradecountrybycommodityexports   

from gssutils import *


# +
def run_script(s):
    %run "$s"
    return table

#observations = pd.concat(
    #run_script(s) for s in ['exports', 'imports']
#    run_script(s) for s in ['imports']
#).drop_duplicates()

obsIMP = run_script('imports')
obsEXP = run_script('exports')

# +
observations = pd.concat([obsIMP, obsEXP])
#print(type(obsIMP))
#print(type(obsEXP))

#print(obsIMP.count())
#print(obsEXP.count())
#print(observations.count())

# +
from pathlib import Path
import numpy as np
out = Path('out')
out.mkdir(exist_ok=True)
slice_size = 100000

for i in np.arange(len(observations) // slice_size):
    dest_file = out / f'observations_{i:04}.csv'
    observations.iloc[i * slice_size : i * slice_size + slice_size - 1].to_csv(dest_file, index=False)
# -

# Fix up title and description as we're combining the data into one Data Cube dataset

# +
from gssutils.metadata import THEME
scraper.dataset.family = 'Trade'
scraper.dataset.theme = THEME['business-industry-trade-energy']
scraper.dataset.title = scraper.dataset.title.replace('imports', 'imports and exports')
scraper.dataset.comment = scraper.dataset.comment.replace('import', 'import and export')

scraper.dataset

# +
with open(out / 'dataset.trig', 'wb') as metadata:
     metadata.write(scraper.generate_trig())
        
csvw = CSVWMetadata('https://gss-cogs.github.io/ref_trade/')
csvw.create(out / 'observations_0000.csv', out / 'observations.csv-schema.json')
# -




