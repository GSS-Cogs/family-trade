# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
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

# ONS-International-exports-of-services-from-subnational-areas-of-the-UK

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

next_table['Product'] = next_table['Product'].apply(pathify)

next_table['Service Origin Geography'] = next_table['Service Origin'].apply(pathify)
next_table['Service Destination Geography'] = next_table['Service Destination'].apply(pathify)
next_table['Service Destination Geography'] = next_table['Service Destination Geography'].map(
    lambda x: { 'total' : 'all', 'row' :'rest-of-world'        
        }.get(x, x))

next_table['Marker'] = next_table['Marker'].map(
    lambda x: { '..' : 'suppressed'     
        }.get(x, x))

next_table = next_table[['Period','Product','Service Origin Geography','Service Destination Geography','Flow','Unit','Value','Measure Type', 'Marker']]

next_table['Flow'] = next_table['Flow'].map(pathify)

nuts = next_table[next_table['Service Origin Geography'].str.contains('nuts')]
not_nuts = next_table[~next_table['Service Origin Geography'].str.contains('nuts')]
nuts = nuts.rename(columns={'Service Origin Geography':'NUTS Geography'})
nuts
not_nuts

from pathlib import Path
import numpy as np
out = Path('out')
out.mkdir(exist_ok=True)

# +
from os import environ

tit1 = 'ONS International exports of services from the UK by NUTS area, Industry and destination'
tit2 = 'ONS International exports of services from the UK by Joint Authority, Industry and destination'

fn1 = 'observationsNUTS.csv'
fn2 = 'observationsJointAuthority.csv'

scraper.dataset.family = 'trade'
from gssutils.metadata import THEME
scraper.dataset.theme = THEME['business-industry-trade-energy']

nuts.drop_duplicates().to_csv(out / fn1, index = False)
scraper.set_dataset_id(f'{pathify(environ.get("JOB_NAME", ""))}/{fn1}')

comDesc = """
    Experimental estimated value of exports of services for 2017 for NUTS1, NUTS2, NUTS3, 
    including industry and non-EU and EU split.
    """
scraper.dataset.comment = comDesc
scraper.dataset.description = comDesc

with open(out / (fn1 + '.csv-metadata.trig'), 'wb') as metadata:metadata.write(scraper.generate_trig())
csvw = CSVWMetadata('https://gss-cogs.github.io/family-trade/reference/')
csvw.create(out / (fn1), out / ((fn1) + '-schema.json'))


not_nuts.drop_duplicates().to_csv(out / fn2, index = False)
scraper.set_dataset_id(f'{pathify(environ.get("JOB_NAME", ""))}/{fn2}')

comDesc = """
    Experimental estimated value of exports of services for 2017 for 15 joint authorities, 
    including industry and EU and RoW split.
    """
scraper.dataset.comment = comDesc
scraper.dataset.description = comDesc

with open(out / (fn2 + '.csv-metadata.trig'), 'wb') as metadata:metadata.write(scraper.generate_trig())
csvw = CSVWMetadata('https://gss-cogs.github.io/family-trade/reference/')
csvw.create(out / (fn2), out / ((fn2) + '-schema.json'))


# +
#scraper.dataset.family = 'trade'
#from gssutils.metadata import THEME
#scraper.dataset.theme = THEME['business-industry-trade-energy']
#with open(out / 'observations.csv-metadata.trig', 'wb') as metadata:
#    metadata.write(scraper.generate_trig())

# +
#csvw = CSVWMetadata('https://gss-cogs.github.io/family-trade/reference/')
#csvw.create(out / 'observations.csv', out / 'observations.csv-schema.json')
