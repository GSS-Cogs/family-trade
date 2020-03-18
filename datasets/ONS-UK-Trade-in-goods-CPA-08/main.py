#!/usr/bin/env python
# coding: utf-8

# In[15]:


from gssutils import *
from databaker.framework import *
import pandas as pd
from gssutils.metadata import THEME
from gssutils.metadata import *
import datetime
from gssutils.metadata import Distribution, GOV
pd.options.mode.chained_assignment = None
import json
import inspect
import re

def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

def mid(s, offset, amount):
    return s[offset:offset+amount]

scraper = Scraper('https://www.ons.gov.uk/economy/nationalaccounts/balanceofpayments/datasets/publicationtablesuktradecpa08')
scraper


# In[16]:


dist = scraper.distributions[0]
dist


# In[17]:


tabs = (t for t in dist.as_databaker())

tidied_sheets = []

for tab in tabs:
    
    if tab.name in ('Index', 'Contact'):
        continue
        
    print(tab.name)
    
    cell = tab.filter(contains_string('Total'))
    
    flow_direction = tab.name

    period = cell.shift(2,-1).expand(RIGHT).is_not_blank()
    
    product = cell.expand(DOWN).is_not_blank()
    
    prod_dep = product.regex('[^0-9]+')
    
    prod_cat = product.regex('[0-9]{2}\s{1}[^\.]')
    
    observations = product.shift(RIGHT).fill(RIGHT).is_not_blank()

    dimensions = [
        HDim(period, 'Period', DIRECTLY, ABOVE),
        HDimConst('Flow Directions', flow_direction),
        HDim(product, 'Product', CLOSEST, ABOVE),
        HDim(prod_dep, 'Product Department', CLOSEST, ABOVE),
        HDim(prod_cat, 'Product Category', CLOSEST, ABOVE),
        HDimConst('Measure Type', 'GBP Total'),
        HDimConst('Unit', 'gbp-million')
        ]

    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    savepreviewhtml(tidy_sheet, fname="Preview.html")

    tidied_sheets.append(tidy_sheet.topandas())
        


# In[18]:


pd.set_option('display.float_format', lambda x: '%.0f' % x)

df = pd.concat(tidied_sheets, ignore_index = True, sort = False).fillna('')

indexNames = df[ df['Product Department'] == 'Residual seasonal adjustment' ].index
df.drop(indexNames, inplace = True)

df['Period'] = df['Period'].map(lambda x: 'year/' + left(x,4) if 'Q' not in x else 'quarter/' + left(x,4) + '-' + right(x,2))

df['Flow Directions'] = df['Flow Directions'].map(lambda x: right(x, len(x) - 2))
df['Product Department'] = df['Product Department'].map(lambda x: right(x, len(x) - 2) if 'Total' not in x else x)

df['Product'] = df['Product'].map(lambda x: '' if '.' not in left(x, 5) else x)
df['Product'] = df['Product'].map(lambda x: 'All' if x == '' else x)

df['Product Category'] = df['Product Category'].map(lambda x: 'All' if x == '' else x)
df['Product Category'] = df['Product Category'].map(lambda x: right(x, len(x) - 3) if left(x, 2).isnumeric() == True else x)
df['Product'] = df['Product'].map(lambda x: right(x, len(x) - 5).strip() if left(x, 2).isnumeric() == True else x)

df = df.replace({'Product' : {
    '3 Processed and preserved fish, crustaceans, molluscs, fruit and vegetables' : 'Processed and preserved fish, crustaceans, molluscs, fruit and vegetables', 
    '-6 Alcoholic beverages' : 'Alcoholic beverages', 
    '6 Manufacture of cement, lime, plaster and articles of concrete, cement and plaster' : 'Manufacture of cement, lime, plaster and articles of concrete, cement and plaster',
    '3 Basic iron and steel' : 'Basic iron and steel', 
    '5 Other basic metals and casting' : 'Other basic metals and casting'}})

df.rename(columns={'OBS' : 'Value',
                   'Flow Directions' : 'Flow'}, inplace=True)

df = df[['Period', 'Flow','Product Department','Product Category','Product','Value','Measure Type','Unit']]

for column in df:
    if column in ('Period', 'Flow Directions','Product Department','Product Category','Product','Measure Type','Unit'):
        df[column] = df[column].map(lambda x: pathify(x))

df.head(25)


# In[19]:


from IPython.core.display import HTML
for col in df:
    if col not in ['Value']:
        df[col] = df[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(df[col].cat.categories) 


# In[20]:


from pathlib import Path
out = Path('out')
out.mkdir(exist_ok=True)
df.drop_duplicates().to_csv(out / 'observations.csv', index = False)


# In[21]:


scraper.dataset.family = 'trade'
scraper.dataset.theme = THEME['business-industry-trade-energy']
with open(out / 'dataset.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())
    
csvw = CSVWMetadata('https://gss-cogs.github.io/family-trade/reference/')
csvw.create(out / 'observations.csv', out / 'observations.csv-schema.json')


# In[ ]:




