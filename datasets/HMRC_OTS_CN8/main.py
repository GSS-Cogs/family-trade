# -*- coding: utf-8 -*-
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

# +
from datetime import datetime
import json
from pytz import timezone
from os import environ
from gssutils import *

provActivity = {
    '@id': environ.get('BUILD_URL', 'unknown-build') + "#prepare_sources",
    '@type': 'activity',
    'startedAtTime': datetime.now(timezone('Europe/London')).isoformat(),
    'label': 'Prepare sources',
    'comment': 'Jupyter Python notebook as part of Jenkins job %s' % environ.get('JOB_NAME', 'unknown-job')
}

# +
import requests
from pathlib import Path
from io import BytesIO
from cachecontrol import CacheControl
from cachecontrol.caches.file_cache import FileCache
from cachecontrol.heuristics import LastModified

session = CacheControl(requests.Session(),
                       cache=FileCache('.cache'),
                       heuristic=LastModified())

provSources = []

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
    provSources.append({
        '@id': sourceUrl,
        '@type': 'entity',
        'label': filename,
        'wasUsedBy': provActivity['@id']
    })

# +
import pandas as pd

table = pd.concat([pd.read_csv(BytesIO(session.get(sourceUrl).content),
                                       dtype={'comcode': str},
                                       na_values=[], keep_default_na=False)
                       for sourceUrl in sourceUrls], ignore_index=True).rename(
    index = str,
    columns = {'year': 'Year', 'flow': 'Flow', 'comcode': 'CN8',
               'country': 'Foreign Country', 'svalue': 'Value'})
table
# -

# Countries are mandated by Eurostat to use the Geonomenclature (GEONOM), which gradually changes over the years. HMRC keeps track of these changes to the country codes and numbers and their data for each year will use the latest GEONOM codes.
#
# For now, we'll just use a static list that's good enough, but will __need to revisit this__.

geonom_2018_excel = 'https://drive.google.com/uc?export=download&id=17Laouuze9gT04xV1Q5M-RZyEqGZUHZJ_'
geonom = pd.read_excel(BytesIO(session.get(geonom_2018_excel).content),
                       na_values=[], keep_default_na=False, dtypes=str)
geonom['codseq'] = geonom['codseq'].apply(
    lambda x: "%03d" % int(x))
geonom.drop(columns=['statsw', 'geogsw', 'dutysw'], inplace=True)
geonom

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

table['Combined Nomenclature'] = table.apply(lambda row: 'cn_%s#cn8_%s' % (row['Year'], row['CN8']), axis=1)
table.drop(columns=['CN8'], inplace=True)
table

table['Measure Type'] = 'GBP Total'
table['Unit'] = '£'
table['Flow'] = table['Flow'].map(lambda x: {'i': 'imports', 'e': 'exports'}[x])
table = table[['Year', 'Flow', 'Combined Nomenclature', 'HMRC Partner Geography', 'Measure Type', 'Unit', 'Value']]

# +
import numpy as np
destFolder = Path('out')
destFolder.mkdir(exist_ok=True, parents=True)

provOutputs = []
output_file_names = []
sliceSize = 50000
for i in np.arange(len(table)//sliceSize):
    outfile_name = f'observations_{i:04}.csv'
    destFile = destFolder / outfile_name
    table.iloc[i*sliceSize:i*sliceSize+sliceSize-1].to_csv(destFile, index=False)
    provOutputs.append((destFile, 'observations table'))
    output_file_names.append(outfile_name)
# -

# Output the PROV metadata as JSON-LD. This goes to the 'out' folder.

# +
metadataDir = Path('metadata')
with open(metadataDir / 'prov_context.json') as contextFile:
    context = json.load(contextFile)

provActivity['endedAtTime'] = datetime.now(timezone('Europe/London')).isoformat()
prov = {
    '@context': context,
    '@graph': [ provActivity ] + provSources + [
        {
            '@id': environ.get('BUILD_URL', 'unknown-build') + 'artifact/' + str(filename),
            '@type': 'entity',
            'wasGeneratedBy': provActivity['@id'],
            'label': label
        } for (filename, label) in provOutputs
    ]
}

with open(destFolder / 'prov.jsonld', 'w') as provFile:
    json.dump(prov, provFile, indent=2)
# -

# Create dataset metadata

# +
modified_date = datetime.now(timezone('Europe/London')).isoformat()

from string import Template
with open(Path('metadata') / 'dataset.trig.template', 'r') as metadata_template_file:
    metadata_template = Template(metadata_template_file.read())
    for out_file in output_file_names:
        with open(destFolder / f'{out_file}-metadata.trig', 'w') as metadata_file:
            metadata_file.write(metadata_template.substitute(modified=modified_date))
# -

csvw = CSVWMetadata('https://gss-cogs.github.io/ref_trade/')
for out_file in output_file_names:
    csvw.create(destFolder / out_file, destFolder / f'{out_file}-schema.json')


