#!/usr/bin/env python
# coding: utf-8

# In[10]:


from gssutils import *

scraper = Scraper('https://www.ons.gov.uk/businessindustryandtrade/internationaltrade/datasets/regionalisedestimatesofukserviceexports')
"""distribution = scraper.distribution(
    mediaType='application/vnd.ms-excel',
    title='Regionalised estimates of UK service exports')
display(distribution)
"""
distribution = scraper.distributions[0]


# In[11]:


tidy = pd.DataFrame()


# In[12]:


tab = distribution.as_pandas(sheet_name = 'NUTS1 by category 2011')
observations = tab.iloc[2:17, :13]
observations.rename(columns= observations.iloc[0], inplace=True)
observations.drop(observations.index[0], inplace = True)
table = pd.melt(observations, id_vars=['Functional category'], var_name='Area', value_name='Value')
table.Value.dropna(inplace =True)
table['Unit'] = 'gbp-million'
table['Measure Type'] = 'GBP Total'
table['Year'] = '2011'
table['Flow'] = 'exports'
tidy = pd.concat([tidy, table])


# In[13]:


tab = distribution.as_pandas(sheet_name = 'NUTS1 by category 2012')
observations = tab.iloc[2:17, :13]
observations.rename(columns= observations.iloc[0], inplace=True)
observations.drop(observations.index[0], inplace = True)
table = pd.melt(observations, id_vars=['Functional category'], var_name='Area', value_name='Value')
table.Value.dropna(inplace =True)
table['Unit'] = 'gbp-million'
table['Measure Type'] = 'GBP Total'
table['Year'] = '2012'
table['Flow'] = 'exports'
tidy = pd.concat([tidy, table])


# In[14]:


tab = distribution.as_pandas(sheet_name = 'NUTS1 by category 2013')
observations = tab.iloc[2:17, :13]
observations.rename(columns= observations.iloc[0], inplace=True)
observations.drop(observations.index[0], inplace = True)
table = pd.melt(observations, id_vars=['Functional category'], var_name='Area', value_name='Value')
table.Value.dropna(inplace =True)
table['Unit'] = 'gbp-million'
table['Measure Type'] = 'GBP Total'
table['Year'] = '2013'
table['Flow'] = 'exports'
tidy = pd.concat([tidy, table])


# In[15]:


tab = distribution.as_pandas(sheet_name = 'NUTS1 by category 2014')
observations = tab.iloc[2:17, :13]
observations.rename(columns= observations.iloc[0], inplace=True)
observations.drop(observations.index[0], inplace = True)
table = pd.melt(observations, id_vars=['Functional category'], var_name='Area', value_name='Value')
table.Value.dropna(inplace =True)
table['Unit'] = 'gbp-million'
table['Measure Type'] = 'GBP Total'
table['Year'] = '2014'
table['Flow'] = 'exports'
tidy = pd.concat([tidy, table])


# In[16]:


tab = distribution.as_pandas(sheet_name = 'NUTS1 by category 2015')
observations = tab.iloc[2:17, :13]
observations.rename(columns= observations.iloc[0], inplace=True)
observations.drop(observations.index[0], inplace = True)
table = pd.melt(observations, id_vars=['Functional category'], var_name='Area', value_name='Value')
table.Value.dropna(inplace =True)
table['Unit'] = 'gbp-million'
table['Measure Type'] = 'GBP Total'
table['Year'] = '2015'
table['Flow'] = 'exports'
tidy = pd.concat([tidy, table])


# In[17]:


tab = distribution.as_pandas(sheet_name = 'NUTS1 by category 2016')
observations = tab.iloc[2:17, :13]
observations.rename(columns= observations.iloc[0], inplace=True)
observations.drop(observations.index[0], inplace = True)
table = pd.melt(observations, id_vars=['Functional category'], var_name='Area', value_name='Value')
table.Value.dropna(inplace =True)
table['Unit'] = 'gbp-million'
table['Measure Type'] = 'GBP Total'
table['Year'] = '2016'
table['Flow'] = 'exports'
tidy = pd.concat([tidy, table])


# In[18]:


tab = distribution.as_pandas(sheet_name = 'Northern Ireland')
observations = tab.iloc[3:18, :6]
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
tidy = pd.concat([tidy, table], sort=False)


# In[19]:


tidy['Area'] = tidy['Area'].map(lambda x: { 'Yorkshire and the Humber':'Yorkshire and The Humber' }.get(x, x))


# In[20]:


for col in tidy.columns:
    if col not in ['Value', 'Year']:
        tidy[col] = tidy[col].astype('category')
        display(col)
        display(tidy[col].cat.categories)


# In[21]:


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


# In[22]:


tidy['Value'] = tidy['Value'].map(lambda x:'' 
                            if (x == ':') | (x == 'xx') | (x == '..') 
                            else int(x))
tidy = tidy[tidy['Value'] != '']


# In[23]:


tidy = tidy[['NUTS Geography','Year','ONS Functional Category','Flow','Measure Type','Value','Unit']]


# In[24]:


from pathlib import Path
out = Path('out')
out.mkdir(exist_ok=True)
tidy.drop_duplicates().to_csv(out / 'observations.csv', index = False)


# In[25]:


from gssutils.metadata import THEME

scraper.dataset.family = 'trade'
scraper.dataset.theme = THEME['business-industry-trade-energy']
with open(out / 'dataset.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())


# In[26]:


tidy


# In[27]:


from gssutils.metadata import THEME

with open(out / 'dataset.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())
    
csvw = CSVWMetadata('https://gss-cogs.github.io/ref_trade/')
csvw.create(out / 'observations.csv', out / 'observations.csv-schema.json')


# In[ ]:




