# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.1.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

from gssutils import *

# ONS "UK trade in services by partner country experimental data" is available via https://www.ons.gov.uk/businessindustryandtrade/internationaltrade/bulletins/exportsandimportsstatisticsbycountryforuktradeinservices/apriltojune2018/relateddata.
#
# Todo: figure out whether/how to scrape this page directly and how to model it so that the latest data is always fetched. N.B. This is an "experimental" dataset.

# +
tables = []

# %run "Trade in Services by Country.py"
tables.append(new_table)

# %run "UK trade in services by partner country.py"
tables.append(new_table)
# -

# We just combine these two into the same table for now.

from pathlib import Path
out = Path('out')
out.mkdir(exist_ok=True)
tidy = pd.concat(tables).drop_duplicates()
tidy.to_csv(out / 'observations.csv', index = False)

# The metadata is more problematic; for now we just use the latter dataset's metadata.
#
# Todo: review titles, etc.

from gssutils.metadata import THEME
scraper.dataset.theme = THEME['business-industry-trade-energy']
scraper.dataset.family = 'Trade'
with open(out / 'dataset.trig', 'wb') as metadata:
     metadata.write(scraper.generate_trig())
csvw = CSVWMetadata('https://gss-cogs.github.io/ref_trade/')
csvw.create(out / 'observations.csv', out / 'observations.csv-schema.json')

# Generate alternative output for direct CSVW transformation. Note that these files won't be included in the upload to PMD.

tidy['Measure Type'] = tidy['Measure Type'].astype('category')
tidy['Measure Type'].cat.categories = tidy['Measure Type'].cat.categories.map(
    lambda x: pathify(x).replace('-', '_'))
tidy.to_csv(out / 'observations-alt.csv', index = False)
csvw.create(out / 'observations-alt.csv', out / 'observations-alt.csv-metadata.json', with_transform=True,
            base_url='http://gss-data.org.uk/data/', base_path='gss_data/trade/ons-uk-trade-in-services',
            dataset_metadata=scraper.dataset.as_quads())



