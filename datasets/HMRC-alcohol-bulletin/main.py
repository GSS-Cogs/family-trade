# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py
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

import glob
from gssutils import *
from gssutils.metadata import THEME
import pandas as pd
import pyexcel
import messytables
from io import BytesIO

# +
# scraper = Scraper("https://www.gov.uk/government/statistics/alcohol-bulletin")
# scraper

scraper = Scraper(seed="info.json")
scraper.distributions = [x for x in scraper.distributions if hasattr(x, "mediaType")]
scraper

# +
# dist = scraper.distribution(title=lambda x: x.startswith('Alcohol Bulletin tables'), mediaType=ODS)
# tabs = (t for t in dist.as_databaker())
# dist

original_tabs = scraper.distributions[0]

with original_tabs.open() as ods_obj:
    excel_obj = BytesIO()
    book = pyexcel.get_book(file_type = 'ods', file_content = ods_obj, library = 'pyexcel-ods3')
    old_tab_names = book.sheet_names()
    
    for old_tab in old_tab_names:
        if len(old_tab) > 31:
            new_tab_names = book.sheet_names()
            find_index = new_tab_names.index(old_tab)
            book.remove_sheet(book.sheet_names()[find_index])
            
    book.save_to_memory(file_type = 'xls', stream = excel_obj)
    tableset = messytables.excel.XLSTableSet(fileobj = excel_obj)
    tabs = list(xypath.loader.get_sheets(tableset, "*"))


tab = tabs[0]
print(tab)
# -

tab = tabs[1]

next_table = pd.DataFrame()

# +
# %%capture

# %run 'T1.py' 
next_table = pd.concat([next_table, tidy])

# %run 'T2.py'
next_table = pd.concat([next_table, tidy])

# %run 'T3.py'
next_table = pd.concat([next_table, tidy])

# %run 'T4.py'
next_table = pd.concat([next_table, tidy])

# %run 'R2.py'

# +
for column in next_table:
    if column in ('Alcohol by Volume', 'Alcohol Type', 'Alcohol Origin', 'Production and Clearance'):
        next_table[column] = next_table[column].str.lstrip()
        next_table[column] = next_table[column].map(lambda x: pathify(x))

next_table['Value'] = next_table['Value'].round(decimals = 2)

# + endofcell="--"
destinationFolder = Path('out')
destinationFolder.mkdir(exist_ok=True, parents=True)

TITLE = 'HMRC Alcohol Releases, Production and Clearances - NSA'
OBS_ID = pathify(TITLE)
import os
GROUP_ID = pathify(os.environ.get('JOB_NAME', 'gss_data/trade/' + Path(os.getcwd()).name))

next_table.drop_duplicates().to_csv(destinationFolder / f'{OBS_ID}.csv', index = False)
# # +
from gssutils.metadata import THEME
scraper.set_base_uri('http://gss-data.org.uk')
scraper.set_dataset_id(f'{GROUP_ID}/{OBS_ID}')
scraper.dataset.title = TITLE

scraper.dataset.family = 'trade'
with open(destinationFolder / f'{OBS_ID}.csv-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())
# -

schema = CSVWMetadata('https://gss-cogs.github.io/family-trade/reference/')
schema.create(destinationFolder / f'{OBS_ID}.csv', destinationFolder / f'{OBS_ID}.csv-schema.json')

next_table
# --
