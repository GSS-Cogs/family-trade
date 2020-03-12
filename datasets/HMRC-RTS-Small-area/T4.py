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

#tab = tabs['T4 NUTS2 Partner Country'] #Old tab name from 2017
tab = tabs['T4 NUTS2 SITC Section'] #Current releases 

tidy = pd.DataFrame()

flow = tab.filter('Flow').fill(DOWN).is_not_blank().is_not_whitespace()
#geography = tab.filter('Partner Country').fill(DOWN).is_not_blank().is_not_whitespace() 
EuNonEu = tab.filter('EU / Non-EU').fill(DOWN).is_not_blank().is_not_whitespace()
geography = tab.filter('EU / Non-EU').fill(DOWN).is_not_blank().is_not_whitespace() 
nut = tab.filter('NUTS2').fill(DOWN).is_not_blank().is_not_whitespace() 
sitc = tab.filter('SITC Section').fill(DOWN).is_not_blank().is_not_whitespace()
observations = tab.filter('Statistical Value (£ million)').fill(DOWN).is_not_blank().is_not_whitespace()
observations = observations.filter(lambda x: type(x.value) != str or 'HMRC' not in x.value)
Dimensions = [
            HDim(flow,'Flow',DIRECTLY,LEFT),
            HDim(EuNonEu,'EU / Non EU',DIRECTLY,LEFT),
            HDim(geography,'HMRC Partner Geography',DIRECTLY,LEFT),
            HDim(nut,'NUTS Geography',DIRECTLY,LEFT),
            HDim(sitc,'SITC 4',DIRECTLY,LEFT),
            HDimConst('Measure Type', 'GBP Total'),
            HDimConst('Unit', 'gbp-million'),
            HDimConst('Year', '2018')
            ]
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
table1 = c1.topandas()
t1 = tidy
t2 = table1
tidy = pd.concat([tidy, table1])

savepreviewhtml(c1)

tidy

observations1 = tab.filter('Business Count').fill(DOWN).is_not_blank().is_not_whitespace()
observations1 = observations1.filter(lambda x: type(x.value) != str or 'HMRC' not in x.value)
Dimensions = [
            HDim(flow,'Flow',DIRECTLY,LEFT),
            HDim(EuNonEu,'EU / Non EU',DIRECTLY,LEFT),
            HDim(geography,'HMRC Partner Geography',DIRECTLY,LEFT),
            HDim(nut,'NUTS Geography',DIRECTLY,LEFT),
            HDim(sitc,'SITC 4',DIRECTLY,LEFT),
            HDimConst('Measure Type', 'Count of Businesses'),
            HDimConst('Unit', 'businesses'),
            HDimConst('Year', '2018')
            ]
c2 = ConversionSegment(observations1, Dimensions, processTIMEUNIT=True)
table2 = c2.topandas()

tidy = pd.concat([tidy, table2])

savepreviewhtml(c2)

tidy

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

tidy['SITC 4'] = tidy['SITC 4'].map(lambda cell: cell.replace('.0',''))
tidy['SITC 4'] = tidy['SITC 4'].map(
    lambda x: {
        'Below Threshold Traders':'below-threshold-traders', 
        'Residual Trade - no SITC Section displayed' : 'residual-trade'}.get(x, x))

for col in tidy.columns:
    if col not in ['Value', 'Year']:
        tidy[col] = tidy[col].astype('category')
        display(col)
        display(tidy[col].cat.categories)

# +
tidy['NUTS Geography'] = tidy['NUTS Geography'].cat.rename_categories({
    'All NUTS2 areas': 'nuts2/all',
    'Bedfordshire and Hertfordshire': 'nuts2/UKH2',
    'Berkshire, Buckinghamshire and Oxfordshire': 'nuts2/UKJ1',
    'Cheshire':'nuts2/UKD6',
    'Cornwall and Isles of Scilly':'nuts2/UKK3',
    'Cumbria':'nuts2/UKD1',
    'Derbyshire and Nottinghamshire':'nuts2/UKF1',
    'Devon':'nuts2/UKK4',
    'Dorset and Somerset':'nuts2/UKK2',
    'East Anglia':'nuts2/UKH1',
    'EA BTTA': 'nuts2/ea-btta',
    'EA Energy':'nuts2/ea-energy',
    'EA Other':'nuts2/ea-other',
    'East Wales':'nuts2/UKL2',
    'East Yorkshire and Northern Lincolnshire':'nuts2/UKE1',
    'Eastern Scotland':'nuts2/UKM7',
    'EM BTTA':'nuts2/em-btta',
    'EM Energy':'nuts2/em-energy',
    'EM Other':'nuts2/em-other',
    'Essex':'nuts2/UKH3',
    'Gloucestershire, Wiltshire and Bath/Bristol area':'nuts2/UKK1',
    'Greater Manchester':'nuts2/UKD3',
    'Hampshire and Isle of Wight':'nuts2/UKJ3',
    'Herefordshire, Worcestershire and Warwickshire':'nuts2/UKG1',
    'Highlands and Islands':'nuts2/UKM6',
    'Inner London - East':'nuts2/UKI4',
    'Inner London - West':'nuts2/UKI3',
    'Kent':'nuts2/UKJ4',
    'Lancashire':'nuts2/UKD4',
    'Leicestershire, Rutland and Northamptonshire':	'nuts2/UKF2',
    'Lincolnshire':'nuts2/UKF3',
    'LO BTTA':'nuts2/lo-btta',
    'LO Other':'nuts2/lo-other',
    'Merseyside':'nuts2/UKD7',
    'NE BTTA':'nuts2/ne-btta',
    'NE Energy':'nuts2/ne-energy',
    'NE Other':'nuts2/ne-other',
    'North Eastern Scotland':'nuts2/UKM5',
    'North Yorkshire':'nuts2/UKE2',
    'Northern Ireland':'nuts2/UKN0',
    'Northumberland and Tyne and Wear':	'nuts2/UKC2',
    'NW BTTA':'nuts2/nw-btta',
    'NW Energy':'nuts2/nw-energy',
    'NW Other':'nuts2/nw-other',
    'Outer London - East and North East':'nuts2/UKI5',
    'Outer London - South':'nuts2/UKI6',
    'Outer London - West and North West':'nuts2/UKI7',
    'SC BTTA':'nuts2/sc-btta',
    'SC Energy':'nuts2/sc-energy',
    'SC Other':'nuts2/sc-other',
    'SE BTTA':'nuts2/se-btta',
    'SE Energy':'nuts2/se-energy',
    'SE Other':'nuts2/se-other',
    'Shropshire and Staffordshire':	'nuts2/UKG2',
    'South Western Scotland':'nuts2/swsc',
    'SW BTTA':'nuts2/sw-btta',
    'SW Other':'nuts2/sw-other',
    'South Yorkshire':'nuts2/UKE3',
    'Southern Scotland':'nuts2/UKM9',
    'Surrey, East and West Sussex':'nuts2/UKJ2',
    'Tees Valley and Durham':'nuts2/UKC1',
    'West Central Scotland':'nuts2/UKM8',
    'West Midlands':'nuts2/UKG3',
    'West Wales':'nuts2/UKL1',
    'West Wales and The Valleys' : 'nuts2/UKL1',
    'West Yorkshire':'nuts2/UKE4',
    'WA BTTA':'nuts2/wa-btta',
    'WA Energy':'nuts2/wa-energy',
    'WA Other':'nuts2/wa-other',
    'WM BTTA':'nuts2/wm-btta',
    'WM Other':'nuts2/wm-other',
    'YH BTTA':'nuts2/yh-btta',
    'YH Energy':'nuts2/yh-energy',
    'YH Other':'nuts2/yh-other'

})

tidy['HMRC Partner Geography'] = tidy['HMRC Partner Geography'].cat.rename_categories({
        'EU'   : 'C',
        'Non-EU' : 'non-eu'})

tidy['Flow'] = tidy['Flow'].cat.rename_categories({
        'Exp'   : 'exports',
        'Imp' : 'imports'})
# -

tidy = tidy.rename(columns={'EU / Non EU' : 'EU - Non-EU'})
import numpy
tidy['Marker'] = numpy.where(tidy['SITC 4'] == 'residual-trade', tidy['SITC 4'], tidy['Marker'])
tidy['Marker'] = numpy.where(tidy['SITC 4'] == 'below-threshold-traders', tidy['SITC 4'], tidy['Marker'])
tidy['SITC 4'] = numpy.where(tidy['SITC 4'] == 'residual-trade', 'all', tidy['SITC 4'])
tidy['SITC 4'] = numpy.where(tidy['SITC 4'] == 'below-threshold-traders', 'all', tidy['SITC 4'])
tidy['HMRC Partner Geography'] = numpy.where(tidy['HMRC Partner Geography'] == 'residual-trade', tidy['EU - Non-EU'], tidy['HMRC Partner Geography'])

tidy =tidy[['Year','NUTS Geography','HMRC Partner Geography','Flow','SITC 4','Measure Type', 'Value', 'Unit','Marker']]

#tidy2 = tidy[tidy['SITC 4'] == 'residual-trade'] 
tidy['SITC 4'].unique()

tidy

