#!/usr/bin/env python
# coding: utf-8

# In[17]:


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


# ## Balance of Payments Current Account: Primary income B4

# +

# In[18]:


import pandas as pd
import numpy as np
from gssutils import *
import json
from gssutils.metadata import THEME
from gssutils.metadata import *
from databaker.framework import *


# In[19]:


cubes = Cubes("info.json")


# In[20]:


with open ('info.json') as file:
    info = json.load(file)


# In[21]:


landingPage = info['landingPage']
landingPage


# In[22]:


scraper = Scraper(landingPage)
scraper.dataset.family = info['families']
scraper


# +

# In[23]:


dist = scraper.distributions[0]
dist


# In[24]:


tabs = scraper.distributions[0].as_databaker()


# In[25]:


def left(s, amount):
    return s[:amount]


# In[26]:


def right(s, amount):
    return s[-amount:]


# -

# In[27]:


tidied_sheets = []

for tab in tabs:
    if (tab.name == 'B4') or (tab.name == 'B4A') or (tab.name == 'B4B'):
    
        income = tab.excel_ref('B10').expand(DOWN).is_not_blank()  
        code = tab.excel_ref('C7').expand(DOWN).is_not_blank()
        year =  tab.excel_ref('D4').expand(RIGHT).is_not_blank()
        quarter = tab.excel_ref('D5').expand(RIGHT)
        seasonal_adjustment = tab.excel_ref('B2')
        income_type = tab.excel_ref('B1')
        observations = quarter.fill(DOWN).is_not_blank()
        
        if (tab.name == 'B4B'):
            flow = tab.excel_ref('B').expand(DOWN).by_index([7,18,29]) - tab.excel_ref('B72').expand(DOWN)
            earning_type = tab.excel_ref('B').expand(DOWN).by_index([9,20,31]) - tab.excel_ref('B72').expand(DOWN)
        if tab.name == 'B4':
            earning_type = tab.excel_ref('B').expand(DOWN).by_index([9,31,52]) - tab.excel_ref('B72').expand(DOWN)
            flow = tab.excel_ref('B').expand(DOWN).by_index([7,29,50]) - tab.excel_ref('B72').expand(DOWN)
        if tab.name == 'B4A':
            earning_type = tab.excel_ref('B').expand(DOWN).by_index([9,31,51]) - tab.excel_ref('B72').expand(DOWN)
            flow = tab.excel_ref('B').expand(DOWN).by_index([7,29,50]) - tab.excel_ref('B72').expand(DOWN)
                
        dimensions = [
            HDim(year, 'Period', DIRECTLY, ABOVE),
            HDim(quarter, 'Quarter', DIRECTLY, ABOVE),
            HDim(code, 'CDID', DIRECTLY, LEFT),
            HDim(flow, 'Flow Directions', CLOSEST, ABOVE),
            HDim(income, 'Income Description', DIRECTLY, LEFT),
            HDim(seasonal_adjustment, 'Seasonal Adjustment', CLOSEST, LEFT),
            HDim(earning_type, 'Earnings', CLOSEST, ABOVE),
            HDim(income_type, 'Income', CLOSEST, LEFT),
            HDimConst('Account Type', 'Current Account'),
            HDimConst('Measure Type', 'GBP Total'),
            HDimConst('Unit', 'gbp-million'),
        ]
        
        tidy_sheet = ConversionSegment(tab, dimensions, observations)        
       # savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
        tidied_sheets.append(tidy_sheet.topandas())
        
        df = pd.concat(tidied_sheets, ignore_index = True, sort = False)


# In[28]:


df['Period'] = df.Period.str.replace('\.0', '')
df['Quarter'] = df['Quarter'].str.lstrip()

df['Period'] = df['Period'] + df['Quarter']
df['Period'] = df['Period'].map(lambda x: 'year/' + left(x,4) if 'Q' not in x else 'quarter/' + left(x,4) + '-' + right(x,2))
df.drop(['Quarter'], axis=1, inplace=True)


# In[29]:


df.rename(columns={'OBS' : 'Value','DATAMARKER' : 'Marker'}, inplace=True)
df['Marker'].replace(' -', 'unknown', inplace=True)

df['Income Description'] = df['Income Description'].str.lstrip()
df['Income Description'] = df['Income Description'].str.rstrip('1')

df = df.replace({'Seasonal Adjustment' : {' Seasonally adjusted' : 'SA', ' Not seasonally adjusted': 'NSA', ' Sector analysis': 'sector-analysis' }})
df = df.replace({'Earnings' : { '' : 'Net earnings', 
                                   ' (Net earnings)' : 'Net earnings',
                                   ' (Earnings of UK residents on investment abroad)' : 'Earnings of UK residents on investment abroad',
                                   ' (Foreign earnings on investment in UK)' : 'Foreign earnings on investment in the UK',
                                   ' (Foreign earnings on investment in the UK)' : 'Foreign earnings on investment in the UK'}})
# +
tidy = df[['Period','Flow Directions', 'Income', 'Income Description', 'Earnings', 'Account Type', 'Seasonal Adjustment', 
           'CDID', 'Value', 'Marker', 'Measure Type', 'Unit']]
for column in tidy:
    if column in ('Flow Directions', 'Income', 'Income Description', 'Earnings', 'Account Type'):
        tidy[column] = tidy[column].str.lstrip()
        tidy[column] = tidy[column].str.rstrip()
        tidy[column] = tidy[column].map(lambda x: pathify(x))
        
tidy


# In[30]:


cubes.add_cube(scraper, tidy, info['title'])

cubes.output_all()


# + endofcell="--"

# --
