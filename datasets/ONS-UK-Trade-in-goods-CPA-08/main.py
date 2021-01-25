#!/usr/bin/env python
# coding: utf-8

# In[1]:


#!/usr/bin/env python
# coding: utf-8
# %%
from gssutils import *
from databaker.framework import *
import pandas as pd
from gssutils.metadata import THEME
from gssutils.metadata import *
import datetime
#from gssutils.metadata import Distribution, GOV
pd.options.mode.chained_assignment = None
import json
import inspect
import re


# In[2]:


pd.options.mode.chained_assignment = None 
# -


cubes = Cubes("info.json")


# In[3]:


def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

def mid(s, offset, amount):
    return s[offset:offset+amount]


# In[4]:


with open ('info.json') as f:
    info = json.load(f)
    
landingPage = info['landingPage']
landingPage


# In[5]:


scraper = Scraper(landingPage)
scraper.dataset.family = info['families']
scraper


# %%

# %%

# In[6]:


tabs = scraper.distributions[0].as_databaker()


# In[8]:


tidied_sheets = []

for tab in tabs:  
    if tab.name in ['Index', 'Contact']:
        continue
        
    print(tab.name)


    trace.start(title, tab, columns, distribution.downloadURL)
  
    cell = tab.excel_ref("A5").expand(DOWN).is_not_blank()

    
    flow_direction = tab.name
    period = tab.excel_ref("C4").expand(RIGHT).is_not_blank()
    product = tab.excel_ref("A5").expand(DOWN).is_not_blank()
   
    prod_dep = product.regex('[^0-9]+')
    
    prod_cat = product.regex('[0-9]{2}\s{1}[^\.]')
    

    prod_cat = prod_dep | prod_cat
    
    trace.Product("Selected from cells A as all items excluding: sectors and sub-sectors")
    product = cell      
    
    prod_override = {}
    for xy_cell in product:
        if xy_cell in prod_cat & xy_cell in prod_dep:
            prod_override[xy_cell.value] = 'all'
        
    cdid_code = tab.excel_ref('B5').expand(DOWN).is_not_blank() | tab.excel_ref("B194") # Adding a blank value  
    
    observations = tab.excel_ref('C5').expand(DOWN).expand(RIGHT).is_not_blank()
    
    dimensions = [
        HDimConst('Flow Directions', flow_direction),
        HDimConst('Measure Type', 'GBP Total'),
        HDimConst('Unit', 'GBP-million'),
        

        HDim(period, 'Period', DIRECTLY, ABOVE), 
        
        HDim(prod_dep, 'Product Department', CLOSEST, ABOVE),
        HDim(prod_cat, 'Product Category', CLOSEST, ABOVE),
        HDim(product, 'Product', DIRECTLY, LEFT, cellvalueoverride = prod_override), 
        
        HDim(cdid_code, 'CDID', CLOSEST, ABOVE)   
        ]
   
    cs = ConversionSegment(tab, dimensions, observations)
    tidy_sheet = cs.topandas()
    

    
    tidy_sheet["Product Category"][tidy_sheet["Product Category"] == tidy_sheet["Product Department"]] = "all"  
    
    trace.store("combined_dataframe", tidy_sheet)  
print(prod_override)
# -


df = pd.concat(tidied_sheets, ignore_index = True, sort = False).fillna('')


# In[12]:


indexNames = df[ df['Product Department'] == 'Residual seasonal adjustment' ].index
df.drop(indexNames, inplace = True)


# In[13]:


df['Period'] = df['Period'].map(lambda x: 'year/' + left(x,4) if 'Q' not in x else 'quarter/' + left(x,4) + '-' + right(x,2))


# In[14]:


df['Flow Directions'] = df['Flow Directions'].map(lambda x: right(x, len(x) - 2))


# In[15]:


df['Product Department'] = df['Product Department'].map(lambda x: right(x, len(x) - 2) if 'Total' not in x else x)


# In[16]:


df['Product Category'] = df['Product Category'].map(lambda x: 'All' if x == '' else x)
df['Product Category'] = df['Product Category'].map(lambda x: right(x, len(x) - 3) if left(x, 2).isnumeric() == True else x)


# In[17]:


df['Product'] = df['Product'].map(lambda x: '' if ('.' not in left(x, 5) and mid(x, 2, 1) == ' ') else x)
df['Product'] = df['Product'].map(lambda x: 'All' if x == '' else x)
df['Product'] = df['Product'].map(lambda x: right(x, len(x) - 8) if mid(x, 2, 5) == 'OTHER' else x)
df['Product'] = df['Product'].map(lambda x: right(x, len(x) - 5).strip() if '.' in x else (right(x, len(x) - 4) if left(x, 2).isnumeric() == True else x))


# In[18]:


import string

df['Product'] = [x.lstrip('-') for x in df['Product']]
df['Product'] = df['Product'].str.lstrip(string.digits)


# In[21]:


df.rename(columns={'OBS' : 'Value'}, inplace=True)


# In[22]:


df = df[['Period', 'Flow Directions','Product Department','Product Category','Product','CDID', 'Value','Measure Type','Unit']]


# In[23]:


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
        
df['Product'].unique().tolist()


# %%

# In[24]:


cubes.add_cube(scraper, df, info['title'])
cubes.output_all()


# In[54]:


# from IPython.core.display import HTML
# for col in df:
#     if col not in ['Value']:
#         df[col] = df[col].astype('category')
#         display(HTML(f"<h2>{col}</h2>"))
#         display(df[col].cat.categories) 


# %%

# %%
