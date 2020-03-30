# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.4.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# #UK trade in goods by industry, country and commodity
#
# This data is split into two distributions, one for imports and the other for exports:
# https://www.ons.gov.uk/economy/nationalaccounts/balanceofpayments/datasets/uktradeingoodsbyindustrycountryandcommodityimports
#
# https://www.ons.gov.uk/economy/nationalaccounts/balanceofpayments/datasets/uktradeingoodsbyindustrycountryandcommodityexports

from gssutils import *


# +
def run_script(s):
    %run "$s"
    return table

observations = pd.concat(
    run_script(s) for s in ['exports', 'imports']
).drop_duplicates()

observations["ONS Partner Geography"] = observations["ONS Partner Geography"].str.replace("RS", "XS")
# -

from pathlib import Path
import numpy as np
out = Path('out')
out.mkdir(exist_ok=True)
observations.drop_duplicates().to_csv(out / 'observations.csv', index = False)

# +
from gssutils.metadata import THEME
scraper.dataset.family = 'Trade'
scraper.dataset.theme = THEME['business-industry-trade-energy']
scraper.dataset.title = scraper.dataset.title.replace('imports', 'imports and exports')
scraper.dataset.comment = scraper.dataset.comment.replace('import', 'import and export')

scraper.dataset
# -

with open(out / 'observations.csv-metadata.trig', 'wb') as metadata:
     metadata.write(scraper.generate_trig())
csvw = CSVWMetadata('https://gss-cogs.github.io/family-trade/reference/')
csvw.create(out / 'observations.csv', out / 'observations.csv-schema.json')


