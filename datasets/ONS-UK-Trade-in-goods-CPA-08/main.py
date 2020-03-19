#!/usr/bin/env python
# coding: utf-8

# In[59]:


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


# In[60]:


dist = scraper.distributions[0]
dist


# In[61]:


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
    
        


# In[66]:


pd.set_option('display.float_format', lambda x: '%.0f' % x)

df = pd.concat(tidied_sheets, ignore_index = True, sort = False).fillna('')

indexNames = df[ df['Product Department'] == 'Residual seasonal adjustment' ].index
df.drop(indexNames, inplace = True)

df['Period'] = df['Period'].map(lambda x: 'year/' + left(x,4) if 'Q' not in x else 'quarter/' + left(x,4) + '-' + right(x,2))

df['Flow Directions'] = df['Flow Directions'].map(lambda x: right(x, len(x) - 2))
df['Product Department'] = df['Product Department'].map(lambda x: right(x, len(x) - 2) if 'Total' not in x else x)

df['Product'] = df['Product'].map(lambda x: '' if ('.' not in left(x, 5) and mid(x, 2, 1) == ' ') else x)
df['Product'] = df['Product'].map(lambda x: 'All' if x == '' else x)

df['Product Category'] = df['Product Category'].map(lambda x: 'All' if x == '' else x)
df['Product Category'] = df['Product Category'].map(lambda x: right(x, len(x) - 3) if left(x, 2).isnumeric() == True else x)
df['Product'] = df['Product'].map(lambda x: right(x, len(x) - 5).strip() if '.' in x else (right(x, len(x) - 4) if left(x, 2).isnumeric() == True else x))

df = df.replace({'Product' : {
    '3 Processed and preserved fish, crustaceans, molluscs, fruit and vegetables' : 'Processed and preserved fish, crustaceans, molluscs, fruit and vegetables', 
    '-6 Alcoholic beverages' : 'Alcoholic beverages', 
    '6 Manufacture of cement, lime, plaster and articles of concrete, cement and plaster' : 'Manufacture of cement, lime, plaster and articles of concrete, cement and plaster',
    '3 Basic iron and steel' : 'Basic iron and steel', 
    '5 Other basic metals and casting' : 'Other basic metals and casting'}})

df.rename(columns={'OBS' : 'Value'}, inplace=True)

df = df[['Period', 'Flow Directions','Product Department','Product Category','Product','Value','Measure Type','Unit']]

for column in df:
    if column in ('Flow Directions','Product Department','Product Category','Product','Unit'):
        df[column] = df[column].map(lambda x: pathify(x))

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
        
df.head(25)


# In[63]:


from IPython.core.display import HTML
for col in df:
    if col not in ['Value']:
        df[col] = df[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(df[col].cat.categories) 


# In[65]:


destinationFolder = Path('out')
destinationFolder.mkdir(exist_ok=True, parents=True)

TAB_NAME = 'observations'

df.drop_duplicates().to_csv(destinationFolder / f'{TAB_NAME}.csv', index = False)

scraper.dataset.family = 'trade'

with open(destinationFolder / f'{TAB_NAME}.csv-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())

csvw = CSVWMetadata('https://gss-cogs.github.io/family-trade/reference/')
csvw.create(destinationFolder / f'{TAB_NAME}.csv', destinationFolder / f'{TAB_NAME}.csv-schema.json')
df.head(25)


# In[ ]:




