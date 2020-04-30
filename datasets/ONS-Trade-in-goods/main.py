# ---
# jupyter:
#   jupytext:
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

observations = pd.concat(
    run_script(s) for s in ['exports', 'imports']
).drop_duplicates()

# +
observations.rename(columns={'Flow':'Flow Directions'}, inplace=True)

#Flow has been changed to Flow Direction to differentiate from Migration Flow dimension
# -

out = Path('out')
out.mkdir(exist_ok=True)
observations.to_csv(out / 'observations.csv', index = False)

# +
from gssutils.metadata import THEME
scraper.dataset.family = 'Trade'
scraper.dataset.theme = THEME['business-industry-trade-energy']
import os

dataset_path = pathify(os.environ.get('JOB_NAME', 'gss_data/trade/' + Path(os.getcwd()).name))

scraper.dataset.title = scraper.dataset.title.replace('imports', 'imports and exports')
scraper.dataset.comment = scraper.dataset.comment.replace('import', 'import and export')

lp1 = scraper.dataset.landingPage
lp2 = 'exports'.join(lp1.rsplit('imports', 1))
scraper.dataset.landingPage = [lp1, lp2]

with open(out / 'observations.csv-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())

csvw = CSVWMetadata('https://gss-cogs.github.io/family-trade/reference/')
csvw.create(
    out / 'observations.csv', out / 'observations.csv-metadata.json', with_transform=True,
    base_url='http://gss-data.org.uk/data/', base_path=dataset_path,
    dataset_metadata=scraper.dataset.as_quads(), with_external=False
)
# -

scraper.dataset.landingPage


