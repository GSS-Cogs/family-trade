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
next_table

next_table['Service Origin Geography'] = next_table['Service Origin']#.apply(pathify)
next_table['Service Destination Geography'] = next_table['Service Destination'].apply(pathify)
next_table['Service Destination Geography'] = next_table['Service Destination Geography'].map(
    lambda x: { 'total' : 'all', 'row' :'rest-of-world'        
        }.get(x, x))
next_table

next_table['Marker'] = next_table['Marker'].map(
    lambda x: { '..' : 'suppressed'     
        }.get(x, x))

next_table = next_table[['Period','Product','Service Origin Geography','Service Destination Geography','Flow','Unit','Value','Measure Type', 'Marker']]

next_table['Flow'] = next_table['Flow'].map(pathify)

from pathlib import Path
import numpy as np
out = Path('out')
out.mkdir(exist_ok=True)

# +
from os import environ

title = 'ONS International exports of services from the UK by Industry and destination'
file_name = 'observations'


scraper.dataset.family = 'trade'
from gssutils.metadata import THEME
scraper.dataset.theme = THEME['business-industry-trade-energy']

next_table.drop_duplicates().to_csv(out / (file_name + '.csv'), index = False)

desc = """
    Experimental estimated value of exports of services for 2017 for NUTS1, NUTS2, NUTS3 and 15 joint authorities, 
    including industry and non-EU and EU split. 
    """

com = """
    The Nomenclature of Territorial Units for Statistics (NUTS) is a hierarchical classification of administrative 
    areas, used across the European Union (EU) for statistical purposes. 
    NUTS1 are major socio-economic regions, while NUTS2 and NUTS3 are progressively smaller regions. 
    In the context of the UK, the NUTS1 areas are Wales, Scotland, Northern Ireland and the nine regions of England.
    The Joint Authorities consist of the seven English Combined Authorities, the mayoral authorities 
    Sheffield City Region and Greater London (split into Inner and Outer London), three Scottish City Deals and 
    two Welsh City Deals. 
    The European Union consists of 28 member countries including the United Kingdom. For trade purposes, this includes 
    all 27 countries other than the UK as well as the European Central Bank and European Institutions.
    The industrial groups presented in this analysis are based on the UK Standard Industrial Classification 2007, 
    although some changes have been made.
    Primary and utilities represents SIC07 section A, B, D and E; section G has been split into two parts 
    (Wholesale and motor trades, and Retail); Other services comprises of O, P, Q, R, S and unknown/unallocated 
    industries
    """

scraper.dataset.comment = com
scraper.dataset.description = desc
scraper.dataset.title = 'International exports of services from subnational areas of the UK'

with open(out / (file_name + '.csv-metadata.trig'), 'wb') as metadata:metadata.write(scraper.generate_trig())
csvw = CSVWMetadata('https://gss-cogs.github.io/family-trade/reference/')
csvw.create(out / (file_name + '.csv'), out / ((file_name + '.csv') + '-schema.json'))



# +
#scraper.dataset.family = 'trade'
#from gssutils.metadata import THEME
#scraper.dataset.theme = THEME['business-industry-trade-energy']
#with open(out / 'observations.csv-metadata.trig', 'wb') as metadata:
#    metadata.write(scraper.generate_trig())

# +
#csvw = CSVWMetadata('https://gss-cogs.github.io/family-trade/reference/')
#csvw.create(out / 'observations.csv', out / 'observations.csv-schema.json')
