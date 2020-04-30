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

nuts = next_table[next_table['Service Origin Geography'].str.contains('nuts')]
not_nuts = next_table[~next_table['Service Origin Geography'].str.contains('nuts')]
nuts = nuts.rename(columns={'Service Origin Geography':'NUTS Geography'})
not_nuts['Service Origin Geography'] = not_nuts['Service Origin Geography'].apply(pathify)
nuts
#not_nuts

# +
nuts.rename(columns={'Flow':'Flow Directions'}, inplace=True)

#Flow has been changed to Flow Direction to differentiate from Migration Flow dimension

not_nuts.rename(columns={'Flow':'Flow Directions'}, inplace=True)

#Flow has been changed to Flow Direction to differentiate from Migration Flow dimension
# -

from pathlib import Path
import numpy as np
out = Path('out')
out.mkdir(exist_ok=True)

# +
from os import environ

tit1 = 'ONS International exports of services from the UK by NUTS area, Industry and destination'
tit2 = 'ONS International exports of services from the UK by Joint Authority, Industry and destination'

fn1 = 'observationsNUTS'
fn2 = 'observationsJointAuthority'

scraper.dataset.family = 'trade'
from gssutils.metadata import THEME
scraper.dataset.theme = THEME['business-industry-trade-energy']

nuts.drop_duplicates().to_csv(out / (fn1 + '.csv'), index = False)
scraper.set_dataset_id(f'{pathify(environ.get("JOB_NAME", ""))}/{fn1}')

comDesc = """
    Experimental estimated value of exports of services for 2017 for NUTS1, NUTS2, NUTS3, 
    including industry and non-EU and EU split. 
    The Nomenclature of Territorial Units for Statistics (NUTS) is a hierarchical classification of administrative 
    areas, used across the European Union (EU) for statistical purposes. 
    NUTS1 are major socio-economic regions, while NUTS2 and NUTS3 are progressively smaller regions. 
    In the context of the UK, the NUTS1 areas are Wales, Scotland, Northern Ireland and the nine regions of England. 
    The European Union consists of 28 member countries including the United Kingdom. For trade purposes, this includes 
    all 27 countries other than the UK as well as the European Central Bank and European Institutions.
    The industrial groups presented in this analysis are based on the UK Standard Industrial Classification 2007, 
    although some changes have been made.
    Primary and utilities represents SIC07 section A, B, D and E; section G has been split into two parts 
    (Wholesale and motor trades, and Retail); Other services comprises of O, P, Q, R, S and unknown/unallocated 
    industries
    """
scraper.dataset.comment = comDesc
scraper.dataset.description = comDesc
scraper.dataset.title = 'International exports of services from subnational areas of the UK'

with open(out / (fn1 + '.csv-metadata.trig'), 'wb') as metadata:metadata.write(scraper.generate_trig())
csvw = CSVWMetadata('https://gss-cogs.github.io/family-trade/reference/')
csvw.create(out / (fn1 + '.csv'), out / ((fn1 + '.csv') + '-schema.json'))


not_nuts.drop_duplicates().to_csv(out / (fn2 + '.csv'), index = False)
scraper.set_dataset_id(f'{pathify(environ.get("JOB_NAME", ""))}/{fn2}')

comDesc = """
    Experimental estimated value of exports of services for 2017 for 15 joint authorities, 
    including industry and EU and RoW split. 
    The Joint Authorities consist of the seven English Combined Authorities, the mayoral authorities 
    Sheffield City Region and Greater London (split into Inner and Outer London), three Scottish City Deals and 
    two Welsh City Deals. 
    The European Union consists of 28 member countries including the United Kingdom. For trade purposes, 
    this includes all 27 countries other than the UK as well as the European Central Bank and European Institutions. 
    The industrial groups presented in this analysis are based on the UK Standard Industrial Classification 2007, 
    although some changes have been made.
    Non-manufacturing production services represents SIC07 section A, B, D, E and F; section G has been split into 
    two parts (Wholesale and motor trades, and Retail); Other services comprises of L, O, P, Q, R, S and 
    unknown/unallocated industries. 
    Joint authority - Constituent NUTS3 areas
    Aberdeen City Region - UKM50 (Aberdeen City and Aberdeenshire)
    Cambridgeshire and Peterborough Combined Authority - UKH11 (East Derbyshire), UKH12 (Cambridgeshire CC)
    Cardiff Capital Region - UKL15 (Central Valleys), UKL16 (Gwent Valleys), part of UKL17 (local authority Bridgend), UKL21 (Monmouthshire and Newport), UKL22 (Cardiff and Vale of Glamorgan)
    Edinburgh and South East Scotland City Region - Part of UKM72 (local authority Fife), UKM73 (East Lothian and Mid Lothian), UKM75 (City of Edinburgh), UKM78 (West Lothian), UKM91 (Scottish Borders)
    Glasgow City Region	Parts of UKM81 (local authorities West Dunbartonshire and East Dunbartonshire), UKM82 (Glasgow City), UKM83 (Inverclyde, East Renfrewshire, Renfrewshire), UKM84 (North Lanarkshire), UKM95 (South Lanarkshire)
    Greater Manchester Combined Authority - UKD33 (Manchester), UKD34 (Greater Manchester South West), UKD35 (Greater Manchester South East), UKD36 (Greater Manchester North West), UKD37 (Greater Manchester North East)
    Liverpool City Region Combined Authority - UKD71 (East Merseyside), UKD72 (Liverpool), UKD73 (Sefton), UKD74 (Wirral)
    North of Tyne Combined Authority - UKC21 (Northumberland), part of UKC22 (local authorities Newcastle upon Tyne and North Tyneside)
    Sheffield City Region1 - UKE31 (Barnsley, Doncaster, Rotherham), UKE32 (Sheffield)
    Swansea Bay City Region - Parts of UKL14 (local authorities Carmarthenshire and Pembrokeshire), part of UKL17 (local authority Neath Port Talbot), UKL18 (Swansea)
    Tees Valley Combined Authority - UKC11 (Hartlepool and Stockton-on-Tees), UKC12 (South Teesside), UKC13 (Darlington)
    West Midlands Combined Authority - UKG31 (Birmingham), UKG32 (Solihull), UKG33 (Coventry), UKG36 (Dudley), UKG37 (Sandwell), UKG38 (Walsall), UKG39 (Wolverhampton)
    West of England Combined Authority - UKK11 (Bristol), part of UKK12 (local authorities Bath and North East Somerset and South Gloucestershire)
    Inner London - UKI31 (Camden and City of London), UKI32 (Westminster), UKI33 (Kensington & Chelsea and Hammersmith & Fulham), UKI34 (Wandsworth), UKI41 (Hackney and Newham), UKI42 (Tower Hamlets), UKI43 (Haringey and Islington), UKI44 (Lewisham and Southwark), UKI45 (Lambeth)
    Outer London - UKI51 (Bexley and Greenwich), UKI52 (Barking & Dagenham and Havering), UKI53 (Redbridge and Waltham Forest), UKI54 (Enfield), UKI61 (Bromley), UKI62 (Croydon),UKI63 (Merton, Kingston upon Thames and Sutton), UKI71 (Barnet), UKI72 (Brent), UKI73 (Ealing), UKI74 (Harrow and Hillingdon), UKI75 (Hounslow and Richmond upon Thames)
    Notes - Sheffield City Region, Inner London, Outer London and the Greater London Authority are not legally classified as combined authorities. However, they have been included as they are defined geographical boundaries headed by a mayor for the purposes of this analysis.
    """
scraper.dataset.comment = comDesc
scraper.dataset.description = comDesc
scraper.dataset.title = 'International exports of services from joint authority areas of the UK'

with open(out / (fn2 + '.csv-metadata.trig'), 'wb') as metadata:metadata.write(scraper.generate_trig())
csvw = CSVWMetadata('https://gss-cogs.github.io/family-trade/reference/')
csvw.create(out / (fn2 + '.csv'), out / ((fn2 + '.csv') + '-schema.json'))


# +
#scraper.dataset.family = 'trade'
#from gssutils.metadata import THEME
#scraper.dataset.theme = THEME['business-industry-trade-energy']
#with open(out / 'observations.csv-metadata.trig', 'wb') as metadata:
#    metadata.write(scraper.generate_trig())

# +
#csvw = CSVWMetadata('https://gss-cogs.github.io/family-trade/reference/')
#csvw.create(out / 'observations.csv', out / 'observations.csv-schema.json')
