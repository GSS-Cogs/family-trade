# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
from gssutils import *

scraper = Scraper("https://www.gov.uk/government/collections/uk-regional-trade-in-goods-statistics-disaggregated-by-smaller-geographical-areas")
scraper
# -

scraper.select_dataset(latest=True)
scraper

tabs = {tab.name: tab for tab in scraper.distribution(title=lambda t: 'Data Tables' in t).as_databaker()}

#tab = tabs['T3 NUTS2 SITC Section'] #Old tab name from 2017
tab = tabs['T3 NUTS3'] #Current releases 

tidy = pd.DataFrame()

flow = tab.filter('Flow').fill(DOWN).is_not_blank().is_not_whitespace()
EuNonEu = tab.filter('EU / Non-EU').fill(DOWN).is_not_blank().is_not_whitespace()
geography = tab.filter('EU / Non-EU').fill(DOWN).is_not_blank().is_not_whitespace() 
nut = tab.filter('NUTS2').fill(DOWN).is_not_blank().is_not_whitespace() 
#sitc = tab.filter('SITC Section').fill(DOWN).is_not_blank().is_not_whitespace()
nut = tab.filter('NUTS3').fill(DOWN).is_not_blank().is_not_whitespace() 
observations = tab.filter('Statistical Value (£ million)').fill(DOWN).is_not_blank().is_not_whitespace()
observations = observations.filter(lambda x: type(x.value) != str or 'HMRC' not in x.value)
Dimensions = [
            HDim(flow,'Flow',DIRECTLY,LEFT),
            HDim(EuNonEu,'EU / Non EU',DIRECTLY,LEFT),
            HDim(geography,'HMRC Partner Geography',DIRECTLY,LEFT),
            HDim(nut,'Geography',DIRECTLY,LEFT),
            HDimConst('SITC 4', 'all'),
            HDimConst('Measure Type', 'GBP Total'),
            HDimConst('Unit', 'gbp-million'),
            HDimConst('Year', '2018')
            ]
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
table1 = c1.topandas()
tidy = pd.concat([tidy, table1])

# +
#savepreviewhtml(c1)
# -

observations1 = tab.filter('Business Count').fill(DOWN).is_not_blank().is_not_whitespace()
observations1 = observations1.filter(lambda x: type(x.value) != str or 'HMRC' not in x.value)
Dimensions = [
            HDim(flow,'Flow',DIRECTLY,LEFT),
            HDim(EuNonEu,'EU / Non EU',DIRECTLY,LEFT),
            HDim(geography,'HMRC Partner Geography',DIRECTLY,LEFT),
            HDim(nut,'Geography',DIRECTLY,LEFT),
            HDimConst('SITC 4', 'all'),
            HDimConst('Measure Type', 'Count of Businesses'),
            HDimConst('Unit', 'businesses'),
            HDimConst('Year', '2018')
            ]
c2 = ConversionSegment(observations1, Dimensions, processTIMEUNIT=True)
table2 = c2.topandas()
tidy = pd.concat([tidy, table2], sort=True)

tidy['Marker'] = tidy['DATAMARKER'].map(lambda x:'not-applicable'
                                  if (x == 'N/A')
                                  else (x))

import numpy as np
tidy['OBS'].replace('', np.nan, inplace=True)
# tidy.dropna(subset=['OBS'], inplace=True)
# tidy.drop(columns=['Marker'], inplace=True)
tidy.rename(columns={'OBS': 'Value'}, inplace=True)
# tidy['Value'] = tidy['Value'].astype(int)
tidy['Value'] = tidy['Value'].map(lambda x:''
                                  if (x == ':') | (x == 'xx') | (x == '..') | (x == 'N/A')
                                  else (x))

# +
#tidy['SITC 4'] = tidy['SITC 4'].map(lambda cell: cell.replace('.0',''))
#tidy['SITC 4'] = tidy['SITC 4'].map(
#    lambda x: {
#        'Below Threshold Traders':'below-threshold-traders', 
#        'Residual Trade - no SITC Section displayed' : 'residual-trade'}.get(x, x))
# -

for col in tidy.columns:
    if col not in ['Value', 'Year']:
        tidy[col] = tidy[col].astype('category')
        display(col)
        display(tidy[col].cat.categories)

# +
tidy['Geography'] = tidy['Geography'].map(
    lambda x: {
         'EA BTTA' : 'East Anglia (Below Threshold Trade Allocations)',
          'EA Energy' : 'East Anglia (Energy)',
          'EA Other' : 'East Anglia (Other)',
          'EM BTTA' : 'East Midlands (Below Threshold Trade Allocations)',
         'EM Energy' : 'East Midlands (Energy)',
         'EM Other' : 'East Midlands (Other)',
         'LO BTTA' : 'London (Below Threshold Trade Allocations)',
         'LO Other' : 'London (Other)',
         'NE BTTA' : 'North East (Below Threshold Trade Allocations)',
         'NE Energy' : 'North East (Energy)',
         'NE Other' : 'North East (Other)',
         'NW BTTA' : 'North West (Below Threshold Trade Allocations)',
         'NW Energy' : 'North West (Energy)',
         'NW Other' : 'North West (Other)',
         'SC BTTA' : 'Scotland (Below Threshold Trade Allocations)',
         'SC Energy' : 'Scotland (Energy)',
         'SC Other' : 'Scotland (Other)',
         'SE BTTA' : 'South East (Below Threshold Trade Allocations)',
         'SE Energy' : 'South East (Energy)',
         'SE Other' : 'South East (Other)',
         'SW BTTA' : 'South West (Below Threshold Trade Allocations)',
         'SW Other' : 'South West (Other)',
         'WA BTTA' : 'Wales (Below Threshold Trade Allocations)',
         'WA Energy' : 'Wales (Energy)',
         'WA Other' : 'Wales (Other)',
         'WM BTTA' : 'West Midlands (Below Threshold Trade Allocations)',
         'WM Other' : 'West Midlands (Other)',
         'YH BTTA' : 'Yorkshire and the Humber (Below Threshold Trade Allocations)',
         'YH Energy' : 'Yorkshire and the Humber (Energy)',
         'YH Other' : 'Yorkshire and the Humber (Other)',
        'NI BTTA' : 'Northern Ireland (Below Threshold Trade Allocations)',
        'NI Energy' : 'Northern Ireland (Energy)',
        'NI Other' : 'Northern Ireland (Other)',
        'Perth & Kinross and Stirling' : 'Perth and Kinross and Stirling',
        'Caithness & Sutherland and Ross & Cromarty' : 'Caithness and Sutherland and Ross and Cromarty',
        'Inverness & Nairn and Moray, Badenoch & Strathspey' : 'Inverness and Nairn and Moray, Badenoch and Strathspey',
        'Lochaber, Skye & Lochalsh, Arran & Cumbrae and Argyll & Bute' : 'Lochaber, Skye and Lochalsh, Arran and Cumbrae and Argyll and Bute',
        'Dumfries & Galloway' : 'Dumfries and Galloway',
        'East Dunbartonshire, West Dunbartonshire and Helensburgh & Lomond' : 'East Dunbartonshire, West Dunbartonshire and Helensburgh and Lomond',
        'City of Edinburgh' :'Edinburgh, City of',
}.get(x, x))

tidy['Flow'] = tidy['Flow'].cat.rename_categories({
        'Exp'   : 'exports',
        'Imp' : 'imports'})
tidy['HMRC Partner Geography'] = tidy['HMRC Partner Geography'].cat.rename_categories({
        'EU'   : 'C',
        'Non-EU' : 'non-eu'})

# +
import urllib.request as request
import csv
import io
import requests

r = request.urlopen('https://raw.githubusercontent.com/ONS-OpenData/ref_trade/master/codelists/nuts-geographies.csv').read().decode('utf8').split("\n")
reader = csv.reader(r)
url="https://raw.githubusercontent.com/ONS-OpenData/ref_trade/master/codelists/nuts-geographies.csv"
s=requests.get(url).content
c=pd.read_csv(io.StringIO(s.decode('utf-8')))

tidy = pd.merge(tidy, c, how = 'left', left_on = 'Geography', right_on = 'Label')

tidy.columns = ['NUTS Geography' if x=='Notation' else x for x in tidy.columns]

# +
#tidy = tidy.rename(columns={'EU / Non EU' : 'EU - Non-EU'})
# -

tidy =tidy[['Year', 'NUTS Geography','HMRC Partner Geography','Flow','SITC 4','Measure Type', 'Value', 'Unit','Marker']]

import numpy
#tidy['Marker'] = numpy.where(tidy['SITC 4'] == 'residual-trade', tidy['SITC 4'], tidy['Marker'])
#tidy['Marker'] = numpy.where(tidy['SITC 4'] == 'below-threshold-traders', tidy['SITC 4'], tidy['Marker'])
#tidy['SITC 4'] = numpy.where(tidy['SITC 4'] == 'residual-trade', 'all', tidy['SITC 4'])
#tidy['SITC 4'] = numpy.where(tidy['SITC 4'] == 'below-threshold-traders', 'all', tidy['SITC 4'])


#tidy[(tidy['Marker'] == 'below-threshold-traders') & (tidy['Value'].notna())].count()
tidy = tidy[(tidy['Marker'] != 'below-threshold-traders') & (tidy['Value'].notna())]


tidy
