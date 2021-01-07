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

# # UK trade in goods by industry, country and commodity
#
# This data is split into two distributions, one for imports and the other for exports:
# https://www.ons.gov.uk/economy/nationalaccounts/balanceofpayments/datasets/uktradeingoodsbyindustrycountryandcommodityimports
#
# https://www.ons.gov.uk/economy/nationalaccounts/balanceofpayments/datasets/uktradeingoodsbyindustrycountryandcommodityexports

# +
from gssutils import *
import json

cubes = Cubes("info.json")
with open("info.json", "r") as f:
    landing_pages = json.load(f)["landingPage"]


# +
def run_script(page):
    if page.endswith('imports'):
        %run "imports" {page}
    else:
        %run "exports" {page}
    return table

observations = pd.concat(
    run_script(page) for page in landing_pages
).drop_duplicates()

# Temporary repacment of RS for XS code (EU do something odd with serbia for trade)
# observations["ONS Partner Geography"] = observations["ONS Partner Geography"].str.replace("RS", "XS")
# -

#Flow has been changed to Flow Direction to differentiate from Migration Flow dimension
observations.rename(columns={'Flow':'Flow Directions'}, inplace=True)
cubes.add_cube(scraper, observations, "UK trade in goods by industry,\
               country and commodity, exports and imports")


from gssutils.metadata import THEME
scraper.dataset.family = 'trade'
scraper.dataset.title = scraper.dataset.title.replace('imports', 'imports and exports')
scraper.dataset.comment = scraper.dataset.comment.replace('import', 'import and export')
scraper.dataset.landingPage = landing_pages

cubes.output_all()
