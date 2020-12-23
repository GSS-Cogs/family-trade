#!/usr/bin/env python
# coding: utf-8

# In[22]:


#!/usr/bin/env python
# coding: utf-8
# %%


# In[23]:


import pandas as pd
import numpy as np
from gssutils import *
import json
from gssutils.metadata import THEME
from gssutils.metadata import *
from databaker.framework import *


# In[24]:


cubes = Cubes("info.json")


# In[25]:


def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

def mid(s, offset, amount):
    return s[offset:offset+amount]


# In[26]:


with open ('info.json') as file:
    info = json.load(file)
    
landingPage = info['landingPage']
landingPage


# In[27]:


scraper = Scraper(landingPage)
scraper.dataset.family = info['families']
scraper


# %%

# In[28]:


# %%
distribution = scraper.distribution(latest=True)
distribution


# In[29]:


tabs = distribution.as_databaker()


# %%

# In[30]:


trace = TransformTrace()
datacube_name = info['title']
columns = ['Functional category', 'Area', 'Value', 'Unit', 'Measure Type', 'Flow', 'Year']

tidied_sheets = []

for tab in tabs:
    if 'NUTS1 by category' in tab.name:
        print (tab.name)
        
        trace.start(datacube_name, tab, columns, scraper.distributions[0].downloadURL)
        tab_df = distribution.as_pandas(sheet_name = tab.name)
        
        trace.obs("Values from the dataframe")
        observations = tab_df.iloc[2:17]
        observations.rename(columns = observations.iloc[0], inplace = True)
        observations.drop(observations.index[0], inplace = True)

        table = pd.melt(observations, id_vars = ['Functional category'], var_name = 'Area', value_name = 'Value')
        table.Value.dropna(inplace = True)
        table['Unit'] = 'gbp-million'
        table['Measure Type'] = 'GBP Total'
        table['Year']  = right(tab.name,4)
        table['Flow'] = 'exports'    

        tidied_sheets.append(table)
#         trace.with_preview(table)
        trace.store("combined_dataframe", table)
        
    elif tab.name == "Northern Ireland":
        print(tab.name)
        
        trace.start(datacube_name, tab, columns, scraper.distributions[0].downloadURL)
        tabNI = distribution.as_pandas(sheet_name = 'Northern Ireland')
        
        trace.obs("Values from the dataframe")
        observations = tabNI.iloc[3:18, :6]
        
        observations.rename(columns= observations.iloc[0], inplace=True)
        observations.drop(observations.index[0], inplace = True)
        observations.columns.values[0] = 1
        table = pd.melt(observations, id_vars=[1], var_name='Year', value_name='Value')
        table.Value.dropna(inplace =True)
        table.columns = ['Functional category' if x== 1 else x for x in table.columns]
        table['Unit'] = 'gbp-million'
        table['Measure Type'] = 'GBP Total'
        table['Area'] = 'Northern Ireland'
        table['Flow'] = 'exports'
        table['Year'] = table['Year'].apply(lambda x: pd.to_numeric(x, downcast='integer'))
        table['Year'] = table['Year'].astype(int)
        table['Functional category'] = table['Functional category'].map(lambda x: { 
                            'Total in all categories':'Total in all categories for NUTS1 area' }.get(x, x))
        tidied_sheets.append(table)
#         trace.with_preview(table)
        trace.store("combined_dataframe", table)
        
trace.combine_and_trace(datacube_name, "combined_dataframe")
trace.ALL("Remove all duplicate rows from dataframe.")


# In[31]:


tidy = pd.concat(tidied_sheets, ignore_index = True, sort = False).fillna('')
tidy


# %%

# In[32]:


tidy['Area'] = tidy['Area'].map(lambda x: { 'Yorkshire and the Humber':'Yorkshire and The Humber' }.get(x, x))


# %%

# In[33]:


for col in tidy.columns:
    if col not in ['Value', 'Year']:
        tidy[col] = tidy[col].astype('category')
        display(col)
        display(tidy[col].cat.categories)


# %%

# In[34]:


tidy['NUTS Geography'] = tidy['Area'].cat.rename_categories({
    'East Midlands' : 'nuts1/UKF', 
    'East of England': 'nuts1/UKH', 
    'London' : 'nuts1/UKI', 
    'North East' : 'nuts1/UKC',
    'North West' : 'nuts1/UKD', 
    'Scotland' : 'nuts1/UKM', 
    'South East' : 'nuts1/UKJ', 
    'South West' : 'nuts1/UKK',
     'Total for functional category' : 'nuts1/all', 
    'Wales' : 'nuts1/UKL', 
    'West Midlands' : 'nuts1/UKG',
    'Yorkshire and The Humber' : 'nuts1/UKE',
    'Northern Ireland' : 'nuts1/UKN'
})
tidy['ONS Functional Category'] = tidy['Functional category'].cat.rename_categories({
    'Administrative and support services' : 'administrative-support' , 
    'Construction' :'construction', 
    'Financial' : 'financial',
    'Information and communication' : 'information-communication', 
    'Insurance and pension services' : 'insurance-pension',
    'Manufacturing' : 'manufacturing', 
    'Other services' : 'other', 
    'Primary and utilities' :'primary-utilities',
    'Real estate, professional, scientific and technical' : 'real-estate',
    'Retail (excluding motor trades)' : 'retail',
    'Total in all categories for NUTS1 area' : 'all',
    'Transport' : 'transport', 
    'Travel' : 'travel',
    'Wholesale and motor trades' : 'wholesale-motor'            
})


# %%

# In[35]:


tidy['Value'] = tidy['Value'].map(lambda x:'' 
                            if (x == ':') | (x == 'xx') | (x == '..') 
                            else int(x))
tidy = tidy[tidy['Value'] != '']


# %%

# In[36]:


tidy = tidy[['NUTS Geography','Year','ONS Functional Category','Flow','Measure Type','Value','Unit']]


# %%

# In[37]:


tidy.rename(columns={'Flow':'Flow Directions'}, inplace=True)
tidy


# flow has been changed to Flow Direction to differentiate from Migration Flow dimension

# %%

# In[38]:


cubes.add_cube(scraper, tidy, info['title'])

cubes.output_all()


# In[39]:


trace.render("spec_v1.html")


# %%

# %%
