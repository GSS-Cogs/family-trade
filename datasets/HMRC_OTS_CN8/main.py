#!/usr/bin/env python
# coding: utf-8

# In[3]:


# # Prepare Sources
#
# The HMRC provide overseas trade statistics broken down by country and commoditiy code using the Combined Nomenclature "CN8" 8 digit codes.
#
# These statistics have been obtained as a series of CSV files as "Tidy Data".
#
# However, some preparation is necessary in order to process these files using the table2qb utility.
#
# Firstly, fetch the source data, in this case from a shared (open) Google drive.
#
# We also keep track of the processing and the provenance of the inputs and outputs using W3C Prov.


# In[4]:


from datetime import datetime
import json
from pytz import timezone
from os import environ
from gssutils import *

# + pixiedust={"displayParams": {}}
import requests
from pathlib import Path
from io import BytesIO
from cachecontrol import CacheControl
from cachecontrol.caches.file_cache import FileCache
from cachecontrol.heuristics import LastModified

session = CacheControl(requests.Session(),
                       cache=FileCache('.cache'),
                       heuristic=LastModified())

sources = [
    ('CN8_Non-EU_cod_2012.csv', '1P7YyFF6qXKXWVtR0Vt3kkvFPOjThMQH8'),
    ('CN8_Non-EU_cod_2013.csv', '1de-Le9ungrbdoGyvWI_RwmEhNpTmR-70'),
    ('CN8_Non-EU_cod_2014.csv', '1oC3jlItfsUshd54KOR7yn9NxpR83iCbC'),
    ('CN8_Non-EU_cod_2015.csv', '1H54-FYrCFa1DylCBg38RAPAeCtkGq4la'),
    ('CN8_Non-EU_cod_2016.csv', '11fLsnoiWzTcA1d3nSDWvyrKQEHwIf6Hz')
]

sourceUrls = []

for filename, google_id in sources:
    
    sourceUrl = f'https://drive.google.com/uc?export=download&id={google_id}'
    sourceUrls.append(sourceUrl)


# In[5]:


import pandas as pd

table = pd.concat([pd.read_csv(BytesIO(session.get(sourceUrl).content),
                                       dtype={'comcode': str},
                                       na_values=[], keep_default_na=False)
                       for sourceUrl in sourceUrls], ignore_index=True).rename(
    index = str,
    columns = {'year': 'Year', 'flow': 'Flow', 'comcode': 'CN8',
               'country': 'Foreign Country', 'svalue': 'Value'})
table


# In[9]:


# Countries are mandated by Eurostat to use the Geonomenclature (GEONOM), which gradually changes over the years. 
# HMRC keeps track of these changes to the country codes and numbers and their data for each year will use the latest GEONOM codes.
#
# For now, we'll just use a static list that's good enough, but will __need to revisit this__.

geonom_2018_excel = 'https://drive.google.com/uc?export=download&id=17Laouuze9gT04xV1Q5M-RZyEqGZUHZJ_'
geonom = pd.read_excel(BytesIO(session.get(geonom_2018_excel).content),
                       na_values=[], keep_default_na=False, dtypes=str)
geonom['codseq'] = geonom['codseq'].apply(
    lambda x: "%03d" % int(x))
geonom.drop(columns=['statsw', 'geogsw', 'dutysw'], inplace=True)
geonom


# In[6]:


# We'll ignore the miscellaneous codes (e.g. Stores & Provis: deliveries of ship/aircraft stores et seq.)

geonom = geonom[:geonom[geonom['country'] == 'Stores & Provis.'].index[0]]
geonom.tail()

table = pd.merge(table, geonom, how='inner', left_on='Foreign Country', right_on='country', validate="m:1")
table

# We're using a good-enough-for-now list of country codes based on the alpha codes above

table.rename(columns={'codalpha': 'HMRC Partner Geography'}, inplace=True)
table.drop(columns=['Foreign Country', 'codseq', 'country'], inplace=True)
table

# Need to include the year of the observation in the CN8 code, as the codes are updated for each year.

table['Combined Nomenclature'] = table.apply(lambda row: 'cn_%s-cn8_%s' % (row['Year'], row['CN8']), axis=1)
table.drop(columns=['CN8'], inplace=True)
table

table['Measure Type'] = 'GBP Total'
table['Unit'] = 'GBP'
table['Flow'] = table['Flow'].map(lambda x: {'i': 'imports', 'e': 'exports'}[x])
table = table[['Year', 'Flow', 'Combined Nomenclature', 'HMRC Partner Geography', 'Measure Type', 'Unit', 'Value']]

from pathlib import Path
out = Path('out')
out.mkdir(exist_ok=True)
table.drop_duplicates().to_csv(out / 'observations.csv', index = False)

# Create dataset metadata


# In[7]:


from gssutils import *
from gssutils.metadata import *
import json
from dateutil.parser import parse
from urllib.parse import urljoin

info = json.load(Path('info.json').open())
ds = PMDDataset()
ds.theme = THEME['business-industry-trade-energy']
ds.family = 'Trade'
ds.title = info['title']
ds.description = info['description']
ds.issued = parse(info['published']).date()
ds.landingPage = info['landingPage']
ds.contactPoint = 'mailto:uktradeinfo@hmrc.gsi.gov.uk'
ds.publisher = GOV['hm-revenue-customs']
ds.rights = "https://www.uktradeinfo.com/AboutUs/Pages/TermsAndConditions.aspx"
ds.license = "http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/"

ds_id = pathify(os.environ.get('JOB_NAME', 'GSS_data/Trade/HMRC_OTS_CN8'))
ds_base = 'http://gss-data.org.uk'

ds.uri = urljoin(ds_base, f'data/{ds_id}')
ds.graph = urljoin(ds_base, f'graph/{ds_id}/metadata')
ds.inGraph = urljoin(ds_base, f'graph/{ds_id}')
ds.sparqlEndpoint = urljoin(ds_base, '/sparql')
ds.modified = datetime.now()
display(ds)

with open(out / 'observations.csv-metadata.trig', 'wb') as metadata:
     metadata.write(ds.as_quads().serialize(format='trig'))


# In[8]:


csvw = CSVWMetadata('https://gss-cogs.github.io/family-trade/reference/')
csvw.create(out / 'observations.csv', out / 'observations.csv-schema.json')

