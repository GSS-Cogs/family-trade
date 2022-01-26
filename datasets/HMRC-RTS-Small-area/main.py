#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from gssutils import *
import json

scraper = Scraper(seed='info.json')
scraper


# In[2]:


scraper.select_dataset(latest=True)

tabs = {tab.name: tab for tab in scraper.distribution(title=lambda t: 'Data Tables' in t).as_databaker()}

year_cell = tabs['Title'].filter('Detailed Data Tables').shift(UP)
year_cell.assert_one()
dataset_year = int(year_cell.value.replace(' data', ''))
dataset_year


# In[3]:


tidied_tabs = []


# In[4]:


tab = tabs['T1 ITL1 (Summary Data)']

tidy = pd.DataFrame()

flow = tab.filter('Flow').fill(DOWN).is_not_blank().is_not_whitespace()
#EuNonEu = tab.filter('EU / Non-EU').fill(DOWN).is_not_blank().is_not_whitespace()
geography = tab.filter('EU / Non-EU').fill(DOWN).is_not_blank().is_not_whitespace() | flow
itl1 = tab.filter('ITL1').fill(DOWN).is_not_blank().is_not_whitespace() | flow
observations = tab.filter('Statistical Value (£ million)').fill(DOWN).is_not_blank().is_not_whitespace()
observations = observations.filter(lambda x: type(x.value) != str or 'HMRC' not in x.value)
Dimensions = [
            HDim(flow,'Flow',DIRECTLY,LEFT),
            HDim(geography,'HMRC Partner Geography',DIRECTLY,LEFT),
            HDim(itl1,'ITL Geography',DIRECTLY,LEFT),
            HDimConst('SITC 4', 'all'),
            HDimConst('Measure Type', 'Statistical Value'),
            HDimConst('Unit', 'statistical-value'),
            HDimConst('Year', dataset_year)
            ]
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
table1 = c1.topandas()
tidy = pd.concat([tidy, table1])

savepreviewhtml(c1, fname=tab.name + "Preview.html")
#tidy

observations1 = tab.filter('Business Count').fill(DOWN).is_not_blank().is_not_whitespace()
observations1 = observations1.filter(lambda x: type(x.value) != str or 'HMRC' not in x.value)
Dimensions = [
            HDim(flow,'Flow',DIRECTLY,LEFT),
            HDim(geography,'HMRC Partner Geography',DIRECTLY,LEFT),
            HDim(itl1,'ITL Geography',DIRECTLY,LEFT),
            HDimConst('Measure Type', 'Businesses'),
            HDimConst('SITC 4', 'all'),
            HDimConst('Unit', 'businesses'),
            HDimConst('Year', dataset_year)
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

tidy['ITL Geography'] = tidy['ITL Geography'].map(
    lambda x: {
        'Exp' : 'itl1/all',
        'Imp': 'itl1/all'}.get(x, x))

tidy['HMRC Partner Geography'] = tidy['HMRC Partner Geography'].map(
    lambda x: {
        'Exp' : 'europe',
        'Imp': 'europe'}.get(x, x))

for col in tidy.columns:
    if col not in ['Value', 'Year']:
        tidy[col] = tidy[col].astype('category')
        display(col)
        display(tidy[col].cat.categories)

ITL1Table = pd.read_csv("ITL1.csv")

ITL1Table['ITL121NM'] = ITL1Table['ITL121NM'].map(lambda x: x.replace(' (England)', ''))

ITL1Table = ITL1Table.rename(columns = {'ITL121NM' : 'ITL Geography'})

tidy = tidy.replace({'ITL Geography' : {'Yorkshire and the Humber' : 'Yorkshire and The Humber'}})

tidy = tidy.merge(ITL1Table, on='ITL Geography', how='left')

tidy['ITL Geography'] = tidy.apply(lambda x: 'itl1/' + str(x['ITL121CD']).lower() if str(x['ITL121CD'])[:1] == 'T' else x['ITL Geography'], axis = 1)

tidy = tidy.replace({'ITL Geography' : {'Unallocated-Known' : 'itl1/UNK',
                    'Unallocated-Unknown' : 'itl1/UNU'}})

tidy['HMRC Partner Geography'] = tidy['HMRC Partner Geography'].cat.rename_categories({
        'EU'   : 'C',
        'Non-EU' : 'non-eu'})
tidy['Flow'] = tidy['Flow'].cat.rename_categories({
        'Exp'   : 'exports',
        'Imp' : 'imports'})

tidy = tidy[['Year', 'ITL Geography','HMRC Partner Geography','Flow','SITC 4','Measure Type', 'Value', 'Unit','Marker']]

tidied_tabs.append(tidy)


# In[5]:


tab = tabs['T2 ITL2']

tidy = pd.DataFrame()

flow = tab.filter('Flow').fill(DOWN).is_not_blank().is_not_whitespace()
EuNonEu = tab.filter('EU / Non-EU').fill(DOWN).is_not_blank().is_not_whitespace()
geography = tab.filter('EU / Non-EU').fill(DOWN).is_not_blank().is_not_whitespace()
itl2 = tab.filter('ITL2').fill(DOWN).is_not_blank().is_not_whitespace()
observations = tab.filter('Statistical Value (£ million)').fill(DOWN).is_not_blank().is_not_whitespace()
observations = observations.filter(lambda x: type(x.value) != str or 'HMRC' not in x.value)
Dimensions = [
            HDim(flow,'Flow',DIRECTLY,LEFT),
            HDim(EuNonEu,'EU / Non EU',DIRECTLY,LEFT),
            HDim(geography,'HMRC Partner Geography',DIRECTLY,LEFT),
            HDim(itl2,'ITL Geography',DIRECTLY,LEFT),
            HDimConst('SITC 4', 'all'),
            HDimConst('Measure Type', 'Statistical Value'),
            HDimConst('Unit', 'statistical-value'),
            HDimConst('Year', dataset_year)
            ]
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
table1 = c1.topandas()
tidy = pd.concat([tidy, table1])

savepreviewhtml(c1, fname=tab.name + "Preview.html")

observations1 = tab.filter('Business Count').fill(DOWN).is_not_blank().is_not_whitespace()
observations1 = observations1.filter(lambda x: type(x.value) != str or 'HMRC' not in x.value)
Dimensions = [
            HDim(flow,'Flow',DIRECTLY,LEFT),
            HDim(EuNonEu,'EU / Non EU',DIRECTLY,LEFT),
            HDim(geography,'HMRC Partner Geography',DIRECTLY,LEFT),
            HDim(itl2,'ITL Geography',DIRECTLY,LEFT),
            HDimConst('SITC 4', 'all'),
            HDimConst('Measure Type', 'Businesses'),
            HDimConst('Unit', 'businesses'),
            HDimConst('Year', dataset_year)
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
tidy.rename(columns={'OBS': 'Value', 'FLOW' :'Flow'}, inplace=True)
# tidy['Value'] = tidy['Value'].astype(int)
tidy['Value'] = tidy['Value'].map(lambda x:''
                                  if (x == ':') | (x == 'xx') | (x == '..') | (x == 'N/A')
                                  else (x))

for col in tidy.columns:
    if col not in ['Value', 'Year']:
        tidy[col] = tidy[col].astype('category')
        display(col)
        display(tidy[col].cat.categories)

ITL2Table = pd.read_csv("ITL2.csv")

ITL2Table = ITL2Table.rename(columns = {'ITL221NM' : 'ITL Geography'})

tidy['ITL Geography'] = tidy['ITL Geography'].str.replace('-', '—')

tidy = tidy.replace({'ITL Geography' : {'Gloucestershire, Wiltshire and Bath/Bristol area' : 'Gloucestershire, Wiltshire and Bristol/Bath area'}})

tidy = tidy.merge(ITL2Table, on='ITL Geography', how='left')

tidy['ITL Geography'] = tidy.apply(lambda x: 'itl2/' + str(x['ITL221CD']).lower() if str(x['ITL221CD'])[:1] == 'T' else x['ITL Geography'], axis = 1)

tidy['ITL Geography'] = tidy.apply(lambda x: 'itl2/' + pathify(x['ITL Geography']) if ' ' in x['ITL Geography'] else x['ITL Geography'], axis = 1)

tidy['HMRC Partner Geography'] = tidy['HMRC Partner Geography'].cat.rename_categories({
        'EU'   : 'C',
        'Non-EU' : 'non-eu'})
tidy['Flow'] = tidy['Flow'].cat.rename_categories({
        'Exp'   : 'exports',
        'Imp' : 'imports'})

tidy =tidy[['Year', 'ITL Geography','HMRC Partner Geography','Flow','SITC 4','Measure Type', 'Value', 'Unit','Marker']]

tidied_tabs.append(tidy)


# In[6]:


tab = tabs['T5 ITL3'] #Current releases

tidy = pd.DataFrame()

flow = tab.filter('Flow').fill(DOWN).is_not_blank().is_not_whitespace()
EuNonEu = tab.filter('EU / Non-EU').fill(DOWN).is_not_blank().is_not_whitespace()
geography = tab.filter('EU / Non-EU').fill(DOWN).is_not_blank().is_not_whitespace()
itl3 = tab.filter('ITL3').fill(DOWN).is_not_blank().is_not_whitespace()
observations = tab.filter('Statistical Value (£ million)').fill(DOWN).is_not_blank().is_not_whitespace()
observations = observations.filter(lambda x: type(x.value) != str or 'HMRC' not in x.value)
Dimensions = [
            HDim(flow,'Flow',DIRECTLY,LEFT),
            HDim(EuNonEu,'EU / Non EU',DIRECTLY,LEFT),
            HDim(geography,'HMRC Partner Geography',DIRECTLY,LEFT),
            HDim(itl3,'ITL Geography',DIRECTLY,LEFT),
            HDimConst('SITC 4', 'all'),
            HDimConst('Measure Type', 'Statistical Value'),
            HDimConst('Unit', 'statistical-value'),
            HDimConst('Year', dataset_year)
            ]
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
table1 = c1.topandas()
tidy = pd.concat([tidy, table1])

savepreviewhtml(c1, fname=tab.name + "Preview.html")

observations1 = tab.filter('Business Count').fill(DOWN).is_not_blank().is_not_whitespace()
observations1 = observations1.filter(lambda x: type(x.value) != str or 'HMRC' not in x.value)
Dimensions = [
            HDim(flow,'Flow',DIRECTLY,LEFT),
            HDim(EuNonEu,'EU / Non EU',DIRECTLY,LEFT),
            HDim(geography,'HMRC Partner Geography',DIRECTLY,LEFT),
            HDim(itl3,'ITL Geography',DIRECTLY,LEFT),
            HDimConst('SITC 4', 'all'),
            HDimConst('Measure Type', 'Businesses'),
            HDimConst('Unit', 'businesses'),
            HDimConst('Year', dataset_year)
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

for col in tidy.columns:
    if col not in ['Value', 'Year']:
        tidy[col] = tidy[col].astype('category')
        #display(col)
        #display(tidy[col].cat.categories)

tidy['Flow'] = tidy['Flow'].cat.rename_categories({
        'Exp'   : 'exports',
        'Imp' : 'imports'})
tidy['HMRC Partner Geography'] = tidy['HMRC Partner Geography'].cat.rename_categories({
        'EU'   : 'C',
        'Non-EU' : 'non-eu'})

ITL3Table = pd.read_excel("ITL3.xlsx")

ITL3Table = ITL3Table.rename(columns = {'ITL321NM' : 'ITL Geography'})

tidy = tidy.replace({'ITL Geography' : {'North and West Norfolk' : 'North and West Norfolk',
                                        'Ards and North Down' : 'Ards and North Down '}})

tidy = tidy.merge(ITL3Table, on='ITL Geography', how='left')

tidy['ITL Geography'] = tidy.apply(lambda x: 'itl3/' + str(x['ITL321CD']).lower() if str(x['ITL321CD'])[:1] == 'T' else x['ITL Geography'], axis = 1)

tidy['ITL Geography'] = tidy.apply(lambda x: 'itl2/' + pathify(x['ITL Geography']) if ' ' in x['ITL Geography'] else x['ITL Geography'], axis = 1)

tidy =tidy[['Year', 'ITL Geography','HMRC Partner Geography','Flow','SITC 4','Measure Type', 'Value', 'Unit','Marker']]

tidy = tidy[(tidy['Marker'] != 'below-threshold-traders') & (tidy['Value'].notna())]

tidied_tabs.append(tidy)


# In[7]:


tab = tabs['T3 ITL2 SITC Section'] #Current releases

tidy = pd.DataFrame()

flow = tab.filter('Flow').fill(DOWN).is_not_blank().is_not_whitespace()
#geography = tab.filter('Partner Country').fill(DOWN).is_not_blank().is_not_whitespace()
EuNonEu = tab.filter('EU / Non-EU').fill(DOWN).is_not_blank().is_not_whitespace()
geography = tab.filter('EU / Non-EU').fill(DOWN).is_not_blank().is_not_whitespace()
itl2 = tab.filter('ITL2').fill(DOWN).is_not_blank().is_not_whitespace()
sitc = tab.filter('SITC Section').fill(DOWN).is_not_blank().is_not_whitespace()
observations = tab.filter('Statistical Value (£ million)').fill(DOWN).is_not_blank().is_not_whitespace()
observations = observations.filter(lambda x: type(x.value) != str or 'HMRC' not in x.value)
Dimensions = [
            HDim(flow,'Flow',DIRECTLY,LEFT),
            HDim(EuNonEu,'EU / Non EU',DIRECTLY,LEFT),
            HDim(geography,'HMRC Partner Geography',DIRECTLY,LEFT),
            HDim(itl2,'ITL Geography',DIRECTLY,LEFT),
            HDim(sitc,'SITC 4',DIRECTLY,LEFT),
            HDimConst('Measure Type', 'Statistical Value'),
            HDimConst('Unit', 'statistical-value'),
            HDimConst('Year', dataset_year)
            ]
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
table1 = c1.topandas()
t1 = tidy
t2 = table1
tidy = pd.concat([tidy, table1])

savepreviewhtml(c1, fname=tab.name + "Preview.html")

tidy

observations1 = tab.filter('Business Count').fill(DOWN).is_not_blank().is_not_whitespace()
observations1 = observations1.filter(lambda x: type(x.value) != str or 'HMRC' not in x.value)
Dimensions = [
            HDim(flow,'Flow',DIRECTLY,LEFT),
            HDim(EuNonEu,'EU / Non EU',DIRECTLY,LEFT),
            HDim(geography,'HMRC Partner Geography',DIRECTLY,LEFT),
            HDim(itl2,'ITL Geography',DIRECTLY,LEFT),
            HDim(sitc,'SITC 4',DIRECTLY,LEFT),
            HDimConst('Measure Type', 'Businesses'),
            HDimConst('Unit', 'businesses'),
            HDimConst('Year', dataset_year)
            ]
c2 = ConversionSegment(observations1, Dimensions, processTIMEUNIT=True)
table2 = c2.topandas()

tidy = pd.concat([tidy, table2])

savepreviewhtml(c2, fname=tab.name + "Preview.html")

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

tidy['ITL Geography'] = tidy['ITL Geography'].str.replace('-', '—')

tidy = tidy.replace({'ITL Geography' : {'Gloucestershire, Wiltshire and Bath/Bristol area' : 'Gloucestershire, Wiltshire and Bristol/Bath area'}})

tidy = tidy.merge(ITL2Table, on='ITL Geography', how='left')

tidy['ITL Geography'] = tidy.apply(lambda x: 'itl2/' + str(x['ITL221CD']).lower() if str(x['ITL221CD'])[:1] == 'T' else x['ITL Geography'], axis = 1)

tidy['ITL Geography'] = tidy.apply(lambda x: 'itl2/' + pathify(x['ITL Geography']) if ' ' in x['ITL Geography'] else x['ITL Geography'], axis = 1)

tidy['HMRC Partner Geography'] = tidy['HMRC Partner Geography'].cat.rename_categories({
        'EU'   : 'C',
        'Non-EU' : 'non-eu'})

tidy['Flow'] = tidy['Flow'].cat.rename_categories({
        'Exp'   : 'exports',
        'Imp' : 'imports'})

tidy = tidy.rename(columns={'EU / Non EU' : 'EU - Non-EU'})
import numpy
tidy['Marker'] = numpy.where(tidy['SITC 4'] == 'residual-trade', tidy['SITC 4'], tidy['Marker'])
tidy['Marker'] = numpy.where(tidy['SITC 4'] == 'below-threshold-traders', tidy['SITC 4'], tidy['Marker'])
tidy['SITC 4'] = numpy.where(tidy['SITC 4'] == 'residual-trade', 'all', tidy['SITC 4'])
tidy['SITC 4'] = numpy.where(tidy['SITC 4'] == 'below-threshold-traders', 'all', tidy['SITC 4'])
tidy['HMRC Partner Geography'] = numpy.where(tidy['HMRC Partner Geography'] == 'residual-trade', tidy['EU - Non-EU'], tidy['HMRC Partner Geography'])

tidy =tidy[['Year','ITL Geography','HMRC Partner Geography','Flow','SITC 4','Measure Type', 'Value', 'Unit','Marker']]

tidy['SITC 4'].unique()

tidied_tabs.append(tidy)


# In[8]:


tab = tabs['T4 ITL2 Partner Country'] #Current releases

# Get the relevant year
year_cell = tabs['Title'].filter('Detailed Data Tables').shift(UP)
year_cell.assert_one()
dataset_year = int(year_cell.value.replace(' data', ''))

tidy = pd.DataFrame()

flow = tab.filter('Flow').fill(DOWN).is_not_blank().is_not_whitespace()
geography = tab.filter('Partner Country').fill(DOWN).is_not_blank().is_not_whitespace()
EuNonEu = tab.filter('EU / Non-EU').fill(DOWN).is_not_blank().is_not_whitespace()
itl2 = tab.filter('ITL2').fill(DOWN).is_not_blank().is_not_whitespace()
observations = tab.filter('Statistical Value (£ million)').fill(DOWN).is_not_blank().is_not_whitespace()
observations = observations.filter(lambda x: type(x.value) != str or 'HMRC' not in x.value)
Dimensions = [
            HDim(flow,'Flow',DIRECTLY,LEFT),
            HDim(EuNonEu,'EU / Non EU',DIRECTLY,LEFT),
            HDim(geography,'Geography',DIRECTLY,LEFT),
            HDim(itl2,'ITL Geography',DIRECTLY,LEFT),
            HDimConst('SITC 4', 'all'),
            HDimConst('Measure Type', 'Statistical Value'),
            HDimConst('Unit', 'statistical-value'),
            HDimConst('Year', dataset_year)
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
            HDim(geography,'Geography',DIRECTLY,LEFT),
            HDim(itl2,'ITL Geography',DIRECTLY,LEFT),
            HDimConst('SITC 4', 'all'),
            HDimConst('Measure Type', 'Businesses'),
            HDimConst('Unit', 'businesses'),
            HDimConst('Year', dataset_year)
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

for col in tidy.columns:
    if col not in ['Value', 'Year']:
        tidy[col] = tidy[col].astype('category')
        display(col)
        display(tidy[col].cat.categories)


tidy['Geography'] = tidy['Geography'].cat.rename_categories({
        'Congo (Republic)' : 'Congo (Democratic Republic of the)',
        'Dominican Rep' : 'Dominican Republic',
        'Equat Guinea' : 'Equatorial Guinea',
        'Falkland Islands' : 'Falklands Islands and dependencies',
        'Fyr Macedonia': 'Macedonia',
        'Irish Republic' : 'Republic of Ireland',
        'Russia' : 'Russian Federation',
        'Tanzania' : 'Tanzania (United Republic of)',
        'Trinidad:Tobago' : 'Trinidad and Tobago',
        'UAE' : 'United Arab Emirates',
        'USA' : 'United States',
        'Venezuela' : 'Venezuela, Bolivarian Republic of',
        'Residual Trade - no Partner Country displayed' : 'Residual Trade',
        'OtherLatin America and Caribbean' : 'Other Latin America and Caribbean',
        'Other Middle East and N Africa (excl EU)' : 'Other Middle East and North Africa',
        'Residual Trade - no SITC Section displayed': 'Residual Trade'

})


tidy['ITL Geography'] = tidy['ITL Geography'].str.replace('-', '—')

tidy = tidy.replace({'ITL Geography' : {'Gloucestershire, Wiltshire and Bath/Bristol area' : 'Gloucestershire, Wiltshire and Bristol/Bath area'}})

tidy = tidy.merge(ITL2Table, on='ITL Geography', how='left')

tidy['ITL Geography'] = tidy.apply(lambda x: 'itl2/' + str(x['ITL221CD']).lower() if str(x['ITL221CD'])[:1] == 'T' else x['ITL Geography'], axis = 1)

tidy['ITL Geography'] = tidy.apply(lambda x: 'itl2/' + pathify(x['ITL Geography']) if ' ' in x['ITL Geography'] else x['ITL Geography'], axis = 1)


tidy['Flow'] = tidy['Flow'].cat.rename_categories({
        'Exp'   : 'exports',
        'Imp' : 'imports'})
tidy['Geography'] = tidy['Geography'].cat.rename_categories({
        'EU'   : 'C',
        'Non-EU' : 'non-eu'})

# +
import urllib.request as request
import csv
import io
import requests

r = request.urlopen('https://raw.githubusercontent.com/ONS-OpenData/ref_trade/master/codelists/hmrc-geographies.csv').read().decode('utf8').split("\n")
reader = csv.reader(r)
url="https://raw.githubusercontent.com/ONS-OpenData/ref_trade/master/codelists/hmrc-geographies.csv"
s=requests.get(url).content
c=pd.read_csv(io.StringIO(s.decode('utf-8')))

tidy = pd.merge(tidy, c, how = 'left', left_on = 'Geography', right_on = 'Label')

tidy.columns = ['HMRC Partner Geography' if x=='Notation' else x for x in tidy.columns]
# -

#QQ if Stores & Provisions
tidy['HMRC Partner Geography'].loc[(tidy['Geography'] == 'Stores and Provisions')] = 'QQ'

tidy = tidy.rename(columns={'EU / Non EU' : 'EU - Non-EU'})
import numpy
tidy['HMRC Partner Geography'] = numpy.where(tidy['HMRC Partner Geography'] == 'residual-trade', tidy['EU - Non-EU'], tidy['HMRC Partner Geography'])

tidy =tidy[['Year','ITL Geography','HMRC Partner Geography','Flow','SITC 4','Measure Type', 'Value', 'Unit','Marker']]

tidied_tabs.append(tidy)


# In[9]:


table = pd.concat(tidied_tabs)
table.count()


# In[10]:


import numpy
table['HMRC Partner Geography'] = numpy.where(table['HMRC Partner Geography'] == 'EU', 'C', table['HMRC Partner Geography'])
table['HMRC Partner Geography'] = numpy.where(table['HMRC Partner Geography'] == 'Non-EU', 'non-eu', table['HMRC Partner Geography'])

sorted(table)
table = table[(table['Marker'] != 'residual-trade')]
table = table[(table['Marker'] != 'below-threshold-traders')]
table["Measure Type"] = table["Measure Type"].apply(pathify)
table = table.drop_duplicates()
table['Unit'] = 'gbp-million'
#unit is being changed to gbp million this is not technically correct but its the only way i can see to deal with the missing URI

#Flow has been changed to Flow Direction to differentiate from Migration Flow dimension
table.rename(columns={'Flow':'Flow Directions'}, inplace=True)


# In[11]:


table['HMRC Partner Geography'] = table.apply(lambda x: 'all' if x['HMRC Partner Geography'] == 'europe' else x['HMRC Partner Geography'], axis = 1)

table['ITL Geography'] = table.apply(lambda x: x['ITL Geography'].lower() if 'UN' in x['ITL Geography'] else x['ITL Geography'], axis = 1)

scraper.dataset.comment = """HMRC experimental statistics that subdivide the existing Regional Trade in Goods Statistics (RTS) into smaller UK geographic areas (ITL2 and ITL3)."""


# In[12]:



scraper.dataset.family = 'trade'

table.to_csv('observations.csv', index=False)

catalog_metadata = scraper.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')

