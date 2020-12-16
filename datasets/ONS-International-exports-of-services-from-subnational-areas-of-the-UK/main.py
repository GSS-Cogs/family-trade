# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
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

# ONS-International-exports-of-services-from-subnational-areas-of-the-UK

# +
from gssutils import *

scraper = Scraper('https://www.ons.gov.uk/businessindustryandtrade/internationaltrade/datasets/internationalexportsofservicesfromsubnationalareasoftheuk')
tabs = { tab.name: tab for tab in scraper.distributions[0].as_databaker() }
cubes = Cubes("info.json")
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

next_table['Export Services'] = next_table['Product'].apply(pathify)
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

next_table = next_table[['Period','Export Services','Service Origin Geography','Service Destination Geography','Flow','Unit','Value','Measure Type', 'Marker']]

next_table['Flow'] = next_table['Flow'].map(pathify)

next_table["Service Origin Geography"] = next_table["Service Origin Geography"].apply(pathify)
next_table.rename(columns={'Flow':'Flow Directions'}, inplace=True)

cubes.add_cube(scraper, next_table, "ONS-International-exports-of-services-from-subnational-areas-of-the-UK" )

# +
# next_table['Export Services'].unique()
# -

cubes.output_all()
