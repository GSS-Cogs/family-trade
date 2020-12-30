#!/usr/bin/env python
# coding: utf-8

# In[1]:


#!/usr/bin/env python
# coding: utf-8
# %% [markdown]
# # Country by commodity imports


# %%

# In[2]:


import pandas as pd
import numpy as np
from gssutils import *
import json
from gssutils.metadata import THEME
from gssutils.metadata import *
from databaker.framework import *


# In[3]:


import datetime

cubes = Cubes("info.json")
title = "Trade in goods: country-by-commodity imports"


# In[4]:


with open ('info.json') as file:
    info = json.load(file)

# info = json.load(open('info.json'))


# In[5]:


landingPage = info['landingPage'][1]
landingPage


# In[6]:


# scraper = Scraper('imports'.join(landingPage.rsplit('exports', 1)))

scraper = Scraper(landingPage)
scraper.dataset.family = info['families']
scraper


# %%

# In[7]:


from zipfile import ZipFile
from io import BytesIO


# In[8]:


distribution = scraper.distribution(mediaType=lambda x: 'zip' in x, latest=True)
distribution


# In[9]:


with ZipFile(BytesIO(scraper.session.get(distribution.downloadURL).content)) as zip:
    assert(len(zip.namelist()) == 1)
    with zip.open(zip.namelist()[0]) as excelFile:
        buffered_fobj = BytesIO(excelFile.read())
        data = pd.read_excel(buffered_fobj,
                             sheet_name=1, dtype={
                                 'COMMODITY': 'category',
                                 'COUNTRY': 'category',
                                 'DIRECTION': 'category'
                             }, na_values=['','N/A'], keep_default_na=False)
data


# %%

# In[10]:


pd.set_option('display.float_format', lambda x: '%.0f' % x)


# In[11]:


table = data.drop(columns='DIRECTION')
table.rename(columns={
    'COMMODITY': 'CORD SITC',
    'COUNTRY': 'ONS Partner Geography'}, inplace=True)
table = pd.melt(table, id_vars=['CORD SITC','ONS Partner Geography'], var_name='Period', value_name='Value')
#table['Period'] = table['Period'].astype('category')
table['Period'] = table['Period'].astype(str)
table.dropna(subset=['Value'], inplace=True)
table['Value'] = table['Value'].astype(int)
table


# %%

# In[12]:


# Check cat.categories
table['CORD SITC'].cat.categories = table['CORD SITC'].cat.categories.map(lambda x: x.split(' ')[0])
table['ONS Partner Geography'].cat.categories = table['ONS Partner Geography'].cat.categories.map(lambda x: x[:2])


# %%

# In[13]:


table["Period"] = pd.to_datetime(table['Period'], format='%Y%b')


# In[14]:


table["Period"] = 'quarter/' + pd.PeriodIndex(table['Period'], freq='Q').astype(str).str.replace('Q', '-Q')


# %%

# In[15]:


table['Seasonal Adjustment'] = pd.Series('NSA', index=table.index, dtype='category')
table['Measure Type'] = pd.Series('gbp-total', index=table.index, dtype='category')
table['Unit'] = pd.Series('gbp', index=table.index, dtype='category')
table['Flow'] = pd.Series('imports', index=table.index, dtype='category')


# %%

# In[16]:


table = table[['ONS Partner Geography', 'Period','Flow','CORD SITC', 'Seasonal Adjustment', 'Measure Type','Value','Unit' ]]
table


# %%

# In[17]:


table.rename(columns={'Flow':'Flow Directions'}, inplace=True)


# flow has been changed to Flow Direction to differentiate from Migration Flow dimension

# In[18]:


# # # The cube output is commented as it is called up in the main.py

# cubes.add_cube(scraper, table, title)
# cubes.output_all()

