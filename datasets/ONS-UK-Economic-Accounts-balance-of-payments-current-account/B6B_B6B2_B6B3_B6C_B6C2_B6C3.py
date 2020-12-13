#!/usr/bin/env python
# coding: utf-8

# In[16]:


# -*- coding: utf-8 -*-
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


# ## Balance of Payments Current Account: Transactions with non-EU countries B6B, B6B2, B6B3, B6C, B6C2, B6C3

# +

# In[17]:


import pandas as pd
import numpy as np
from gssutils import *
import json
from gssutils.metadata import THEME
from gssutils.metadata import *
from databaker.framework import *


# In[18]:


cubes = Cubes("info.json")


# In[19]:


with open ('info.json') as f:
    info = json.load(f)


# In[20]:


landingPage = info['landingPage']
landingPage


# +

# In[21]:


scraper = Scraper(landingPage)
scraper.dataset.family = info['families']
scraper


# In[22]:


dist = scraper.distributions[0]
dist


# In[23]:


tabs = scraper.distributions[0].as_databaker()


# In[24]:


def left(s, amount):
    return s[:amount]


# In[25]:


def right(s, amount):
    return s[-amount:]


# -

# In[26]:


tidied_sheets = []

for tab in tabs:
    if (tab.name == 'B6B') or (tab.name == 'B6B_2') or (tab.name == 'B6B_3') or (tab.name == 'B6C') or (tab.name == 'B6C_2') or (tab.name == 'B6C_3'):
        
        account_Type = tab.excel_ref('B1')
        seasonal_adjustment = tab.excel_ref('B3')
        transaction_type = tab.excel_ref('B8')
        flow = tab.excel_ref('B').expand(DOWN).by_index([10]) - tab.excel_ref('B72').expand(DOWN)
        services = tab.excel_ref('B').expand(DOWN).by_index([11,21,31,41,51,62]) - tab.excel_ref('B72').expand(DOWN)
        country = tab.excel_ref('B10').expand(DOWN).is_not_blank()
        code = tab.excel_ref('C7').expand(DOWN).is_not_blank()
        year =  tab.excel_ref('D5').expand(RIGHT).is_not_blank()
        quarter = tab.excel_ref('D6').expand(RIGHT)
        #savepreviewhtml(observations)
        
        if (tab.name == 'B6B_2') or (tab.name == 'B6B_3') or (tab.name == 'B6C_2') or (tab.name == 'B6C_3'):
            transaction_type = tab.excel_ref('B9')
            flow = tab.excel_ref('B').expand(DOWN).by_index([11]) - tab.excel_ref('B72').expand(DOWN)
            services = tab.excel_ref('B').expand(DOWN).by_index([12,22,32,42,52,63]) - tab.excel_ref('B73').expand(DOWN)
            year =  tab.excel_ref('D6').expand(RIGHT).is_not_blank()
            quarter = tab.excel_ref('D7').expand(RIGHT)
        if (tab.name == 'B6B_3') or (tab.name == 'B6C_2') or (tab.name == 'B6C_3'):
            services = tab.excel_ref('B').expand(DOWN).by_index([12,22,32,42,52,63]) - tab.excel_ref('B73').expand(DOWN)
        
        observations = quarter.fill(DOWN).is_not_blank()   
        
        dimensions = [
            HDim(account_Type, 'Account Type', CLOSEST, LEFT),
            HDim(seasonal_adjustment, 'Seasonal Adjustment', CLOSEST, LEFT),
            HDim(transaction_type, 'Transaction Type', CLOSEST, LEFT),
            HDim(flow, 'Flow Directions', CLOSEST, ABOVE),
            HDim(services, 'Services', CLOSEST, ABOVE),
            HDim(country, 'Country Transaction', DIRECTLY, LEFT),
            HDim(code, 'CDID', DIRECTLY, LEFT),
            HDim(year, 'Period', DIRECTLY, ABOVE),
            HDim(quarter, 'Quarter', DIRECTLY, ABOVE),
            HDimConst('Measure Type', 'GBP Total'),
            HDimConst('Unit', 'gbp-million'),
        ]
        tidy_sheet = ConversionSegment(tab, dimensions, observations)        
       # savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
        tidied_sheets.append(tidy_sheet.topandas())
        
        df = pd.concat(tidied_sheets, ignore_index = True, sort = False)


# In[27]:


df['Period'] = df.Period.str.replace('\.0', '')
df['Quarter'] = df['Quarter'].map(lambda x: x.lstrip() if isinstance(x, str) else x)
df['Period'] = df['Period'] + df['Quarter']
df['Period'] = df['Period'].map(lambda x: 'year/' + left(x,4)                                if 'Q' not in x else 'quarter/' + left(x,4) + '-' +                                 right(x,2))
df.drop(['Quarter'], axis=1, inplace=True)


# In[28]:


df['Account Type'] = df['Account Type'].map(lambda x: x.split()[0]) + ' ' +  df['Account Type'].map(lambda x: x.split()[1])
df['Account Type'] = df['Account Type'].str.rstrip(':')
df['Transaction Type'] = df['Transaction Type'].str.rstrip('1')
df['Country Transaction'] = df['Country Transaction'].str.lstrip()
df = df.replace({'Seasonal Adjustment' : {' Seasonally adjusted' : 'SA', ' Not seasonally adjusted': 'NSA' }})

df.rename(columns={'OBS' : 'Value','DATAMARKER' : 'Marker'}, inplace=True)
df['Marker'].replace(' -', 'unknown', inplace=True)


# +

# In[29]:


tidy = df[['Period','Flow Directions', 'Services', 'Account Type', 'Transaction Type', 'Country Transaction', 'Seasonal Adjustment', 
           'CDID', 'Value', 'Marker', 'Measure Type', 'Unit']]
for column in tidy:
    if column in ('Flow Directions', 'Services', 'Account Type', 'Transaction Type', 'Country Transaction'):
        tidy[column] = tidy[column].str.lstrip()
        tidy[column] = tidy[column].map(lambda x: pathify(x))
        
tidy


# In[30]:


cubes.add_cube(scraper, tidy, info['title'])

cubes.output_all()


# + endofcell="--"

# --
