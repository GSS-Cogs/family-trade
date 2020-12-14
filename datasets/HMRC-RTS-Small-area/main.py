# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     cell_metadata_json: true
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

# +
from gssutils import *
import json

info = json.load(open('info.json'))
scraper = Scraper(seed='info.json')  
cubes = Cubes('info.json')
scraper 
# -

tabs = {tab.name: tab for tab in scraper.catalog.dataset[0].distribution[1].as_databaker()}
# tabs = {tab.name: tab for tab in scraper.distribution(latest=True, mediaType=Excel).as_databaker()}
# excel_distro_list = [x for x in scraper.catalog.dataset[0].distribution if x.mediaType == ExcelOpenXML]
# excel_distro_list = [x for x in scraper.catalog.dataset[0].distribution if x.mediaType == Excel]

excel_distro_list = [x for x in scraper.catalog.dataset[0].distribution if x.mediaType == Excel]

year_cell = tabs['Title'].filter('Detailed Data Tables').shift(UP)
year_cell.assert_one()
dataset_year = int(year_cell.value)
#dataset_year

# +
# %%capture

def process_tab(t):
    %run "$t"
    return tidy

table = pd.concat(process_tab(f'{t}.py') for t in ['T1','T2','T3','T4','T5'])
table.count()
# +
import numpy
table['HMRC Partner Geography'] = numpy.where(table['HMRC Partner Geography'] == 'EU', 'C', table['HMRC Partner Geography'])
table['HMRC Partner Geography'] = numpy.where(table['HMRC Partner Geography'] == 'Non-EU', 'non-eu', table['HMRC Partner Geography'])

sorted(table)
table = table[(table['Marker'] != 'residual-trade')]
table = table[(table['Marker'] != 'below-threshold-traders')]
table = table.drop_duplicates()

#table.count()
#t = table[(table['NUTS Geography'] == 'nuts2/ea-other') & (table['HMRC Partner Geography'] == 'C') & (table['Value'] == 127)]
#t = table[(table['HMRC Partner Geography'] == 'EU')]

# -


table['HMRC Partner Geography'].unique()

# +
table.rename(columns={'Flow':'Flow Directions'}, inplace=True)

#Flow has been changed to Flow Direction to differentiate from Migration Flow dimension
# -

cubes.add_cube(scraper, table, info['title'])
scraper.dataset.family = info['families']
scraper.catalog.dataset[0].family = info['families']

cubes.output_all()


