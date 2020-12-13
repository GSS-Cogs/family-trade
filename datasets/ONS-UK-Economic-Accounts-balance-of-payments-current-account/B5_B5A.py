#!/usr/bin/env python
# coding: utf-8

# In[73]:


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


# ## Balance of Payments Current Account: Secondary income B5

# +

# In[74]:


import pandas as pd
import numpy as np
from gssutils import *
import json
from gssutils.metadata import THEME
from gssutils.metadata import *
from databaker.framework import *


# In[75]:


cubes = Cubes("info.json")


# In[76]:


with open ('info.json') as f:
    info = json.load(f)


# In[77]:


landingPage = info['landingPage']
landingPage


# In[78]:


scraper = Scraper(landingPage)
scraper.dataset.family = info['families']
scraper


# +

# In[79]:


dist = scraper.distributions[0]
dist


# In[80]:


tabs = scraper.distributions[0].as_databaker()


# In[81]:


def left(s, amount):
    return s[:amount]


# In[82]:


def right(s, amount):
    return s[-amount:]


# -

# In[83]:


tidied_sheets = []

for tab in tabs:
    if (tab.name == 'B5') or (tab.name == 'B5A'):
        
        flow = tab.excel_ref('B').expand(DOWN).by_index([7,24,43]) - tab.excel_ref('B51').expand(DOWN)
        sector = tab.excel_ref('B').expand(DOWN).by_index([8,14,25,34,44,45]) - tab.excel_ref('B51').expand(DOWN)
        income = tab.excel_ref('B10').expand(DOWN).is_not_blank() - tab.excel_ref('B51').expand(DOWN)
        code = tab.excel_ref('C7').expand(DOWN).is_not_blank()
        year =  tab.excel_ref('D4').expand(RIGHT).is_not_blank()
        quarter = tab.excel_ref('D5').expand(RIGHT)
        seasonal_adjustment = tab.excel_ref('B2')
        income_type = tab.excel_ref('B1')
        observations = quarter.fill(DOWN).is_not_blank()
        #savepreviewhtml(income)
        
        dimensions = [
            HDim(flow, 'Flow Directions', CLOSEST, ABOVE),
            HDim(sector, 'Sector', CLOSEST, ABOVE),
            HDim(income, 'Income Description', DIRECTLY, LEFT),
            HDim(code, 'CDID', DIRECTLY, LEFT),
            HDim(year, 'Period', DIRECTLY, ABOVE),
            HDim(quarter, 'Quarter', DIRECTLY, ABOVE),        
            HDim(seasonal_adjustment, 'Seasonal Adjustment', CLOSEST, LEFT),
            HDim(income_type, 'Income', CLOSEST, LEFT),
            HDimConst('Account Type', 'Current Account'),
            HDimConst('Measure Type', 'GBP Total'),
            HDimConst('Unit', 'gbp-million'),
        ]
        tidy_sheet = ConversionSegment(tab, dimensions, observations)        
        #savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
        tidied_sheets.append(tidy_sheet.topandas())
        
        df = pd.concat(tidied_sheets, ignore_index = True, sort = False)


# In[84]:


df['Period'] = df.Period.str.replace('\.0', '')
df['Quarter'] = df["Quarter"].str.lstrip()
df['Period'] = df['Period'] + df['Quarter']
df['Period'] = df['Period'].map(lambda x: 'year/' + left(x,4) if 'Q' not in x else 'quarter/' + left(x,4) + '-' + right(x,2))
df.drop(['Quarter'], axis=1, inplace=True)


# In[85]:


df['Income Description'] = df['Income Description'].str.rstrip('2')
df['Income Description'] = df['Income Description'].str.rstrip('3')
df['Income Description'] = df['Income Description'].str.lstrip()

df['Income'] = df['Income'].str.rstrip('1')
df['Sector'] = df['Sector'].str.lstrip()

df = df.replace({'Seasonal Adjustment' : {' Seasonally adjusted' : 'SA', ' Not Seasonally adjusted': 'NSA' }})

df.rename(columns={'OBS' : 'Value','DATAMARKER' : 'Marker'}, inplace=True)
df['Marker'].replace(' -', 'unknown', inplace=True)


# +

# In[86]:


tidy = df[['Period','Flow Directions', 'Income', 'Income Description', 'Sector', 'Account Type', 'Seasonal Adjustment', 
           'CDID', 'Value', 'Marker', 'Measure Type', 'Unit']]
for column in tidy:
    if column in ('Flow Directions', 'Income', 'Income Description', 'Sector', 'Account Type'):
        tidy[column] = tidy[column].str.lstrip()
        tidy[column] = tidy[column].map(lambda x: pathify(x))
        
tidy


# In[87]:


cubes.add_cube(scraper, tidy, info['title'])

cubes.output_all()


# + endofcell="--"

# --
