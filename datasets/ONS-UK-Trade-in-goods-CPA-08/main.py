#!/usr/bin/env python
# coding: utf-8

# In[1]:


#!/usr/bin/env python
# coding: utf-8
# %%

import pandas as pd
import numpy as np
from gssutils import *
import json
from gssutils.metadata import THEME
from gssutils.metadata import *
from databaker.framework import *

#pd.options.mode.chained_assignment = None

import datetime
import inspect
import re
from os import environ

cubes = Cubes("info.json")


# In[2]:


def left(s, amount):
    return s[:amount]


# In[3]:


def right(s, amount):
    return s[-amount:]


# In[4]:


def mid(s, offset, amount):
    return s[offset:offset+amount]


# In[5]:


with open ('info.json') as f:
    info = json.load(f)
    
#info = json.load(open('info.json'))


# In[6]:


landingPage = info['landingPage']
scraper = Scraper(landingPage)

scraper.dataset.family = info['families']
scraper


# %%

# In[7]:


dist = scraper.distributions[0]
dist


# %%

# In[8]:


tabs = scraper.distributions[0].as_databaker()


# In[9]:


tidied_sheets =[]
for tab in tabs: 
    if tab.name in ['Index', 'Contact']:
        continue
        
    print(tab.name)
    
    cell = tab.filter('Total')
    
    flow_direction = tab.name
    #period = cell.shift(2,-1).expand(RIGHT).is_not_blank()
    period = tab.excel_ref("C4").expand(RIGHT).is_not_blank()
    
    #product = cell.expand(DOWN).is_not_blank() # This was problematic
    product = tab.excel_ref("A5").expand(DOWN).is_not_blank()
    
    prod_dep = product.regex('[^0-9]+')
    
    prod_cat = product.regex('[0-9]{2}\s{1}[^\.]')
    
    cdid_code = tab.excel_ref('B5').expand(DOWN).is_not_blank() | tab.excel_ref("B194") # Adding a blank value 
   
    observations = tab.excel_ref('C5').expand(DOWN).expand(RIGHT).is_not_blank()
    #observations = product.shift(RIGHT).fill(RIGHT).is_not_blank()
   
    dimensions = [
        HDimConst('Flow Directions', flow_direction),
        HDimConst('Measure Type', 'GBP Total'),
        HDimConst('Unit', 'GBP-million'),
        
        HDim(period, 'Period', DIRECTLY, ABOVE),
        HDim(product, 'Product',  CLOSEST, ABOVE),
        HDim(prod_dep, 'Product Department', CLOSEST, ABOVE), 
        HDim(prod_cat, 'Product Category', CLOSEST, ABOVE),
        HDim(cdid_code, 'CDID', CLOSEST, UP)   
        ]
   
    cs = ConversionSegment(tab, dimensions, observations)
    tidy_sheet = cs.topandas()
    #savepreviewhtml(tidy_sheet, fname="Preview.html")
    tidied_sheets.append(tidy_sheet) # datacube
    
    df = pd.concat(tidied_sheets, ignore_index = True, sort = False).fillna('')  

# %%
pd.set_option('display.float_format', lambda x: '%.0f' % x)
  
indexNames = df[ df['Product Department'] == 'Residual seasonal adjustment' ].index
df.drop(indexNames, inplace = True)

df['Period'] = df['Period'].map(lambda x: 'year/' + left(x,4) if 'Q' not in x else 'quarter/' + left(x,4) + '-' + right(x,2))

df['Flow Directions'] = df['Flow Directions'].map(lambda x: right(x, len(x) - 2))

df['Product'] = df['Product'].map(lambda x: '' if ('.' not in left(x, 5) and mid(x, 2, 1) == ' ') else x)
df['Product'] = df['Product'].map(lambda x: 'All' if x == '' else x)
df['Product'] = df['Product'].map(lambda x: right(x, len(x) - 8) if mid(x, 2, 5) == 'OTHER' else x)
df['Product'] = df['Product'].map(lambda x: right(x, len(x) - 5).strip() if '.' in x else (right(x, len(x) - 4) if left(x, 2).isnumeric() == True else x))

df['Product Department'] = df['Product Department'].map(lambda x: right(x, len(x) - 2) if 'Total' not in x else x)

df['Product Category'] = df['Product Category'].map(lambda x: 'All' if x == '' else x)
df['Product Category'] = df['Product Category'].map(lambda x: right(x, len(x) - 3) if left(x, 2).isnumeric() == True else x)

df = df.replace({'Product' : {
'3 Processed and preserved fish, crustaceans, molluscs, fruit and vegetables' : 'Processed and preserved fish, crustaceans, molluscs, fruit and vegetables', 
'-6 Alcoholic beverages' : 'Alcoholic beverages', 
'6 Manufacture of cement, lime, plaster and articles of concrete, cement and plaster' : 'Manufacture of cement, lime, plaster and articles of concrete, cement and plaster',
'3 Basic iron and steel' : 'Basic iron and steel', 
'5 Other basic metals and casting' : 'Other basic metals and casting'}})

df = df.replace({'Product' : {
'a-products-of-agriculture-forestry-fishing' : 'products-of-agriculture-forestry-fishing',
'b-mining-quarrying' : 'mining-quarrying',
'c-manufactured-products' : 'manufactured-products',
'd-electricity-gas-steam-air-conditioning' : 'electricity-gas-steam-air-conditioning',
'e-water-supply-sewerage-waste-management' : 'water-supply-sewerage-waste-management',
'j-information-communication-services' : 'information-communication-services',
'm-professional-scientific-technical-services' : 'professional-scientific-technical-services',
'r-arts-entertainment-recreation' : 'arts-entertainment-recreation',
's-other-services' : 'other-services'}})

df['Product'].unique().tolist()

df.rename(columns={'OBS' : 'Value'}, inplace=True)
df = df[['Period','Flow Directions','Product','Product Department','Product Category','CDID','Value','Measure Type','Unit']]

for column in df:
    if column in ['Flow Directions','Product','Product Department','Product Category','Unit']:
        df[column] = df[column].map(lambda x: pathify(x))

from IPython.core.display import HTML
for col in df:
    if col not in ['Value']:
        df[col] = df[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(df[col].cat.categories) 
        
    
cubes.add_cube(scraper, df, info['title'])

cubes.output_all()


# %%
