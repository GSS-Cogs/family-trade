#!/usr/bin/env python
# coding: utf-8

# In[5]:


from gssutils import *
import json

info = json.load(open('info.json'))
scraper = Scraper(seed='info.json')
cubes = Cubes('info.json')
scraper


# In[8]:


scraper.select_dataset(latest=True)

tabs = {tab.name: tab for tab in scraper.distribution(title=lambda t: 'Data Tables' in t).as_databaker()}

year_cell = tabs['Title'].filter('Detailed Data Tables').shift(UP)
year_cell.assert_one()
dataset_year = int(year_cell.value.replace(' data', ''))
dataset_year


# In[7]:


# %%capture

def process_tab(t):
    # %run "$t"
    return tidy

table = pd.concat(process_tab(f'{t}.py') for t in ['T1','T2','T3','T4','T5'])
table.count()


# In[ ]:


import numpy
table['HMRC Partner Geography'] = numpy.where(table['HMRC Partner Geography'] == 'EU', 'C', table['HMRC Partner Geography'])
table['HMRC Partner Geography'] = numpy.where(table['HMRC Partner Geography'] == 'Non-EU', 'non-eu', table['HMRC Partner Geography'])

sorted(table)
table = table[(table['Marker'] != 'residual-trade')]
table = table[(table['Marker'] != 'below-threshold-traders')]
table["Measure Type"] = table["Measure Type"].apply(pathify)
table = table.drop_duplicates()
table['Unit'] = 'gbp-million'
#unit is being changed to gbp million this is not technically correct but its the only way i can see to deal with the missing URI

#Flow has been changed to Flow Direction to differentiate from Migration Flow dimension
table.rename(columns={'Flow':'Flow Directions'}, inplace=True)


# In[ ]:


table['HMRC Partner Geography'] = table.apply(lambda x: 'Total' if x['HMRC Partner Geography'] == 'europe' else x['HMRC Partner Geography'], axis = 1)

scraper.dataset.comment = """HMRC experimental statistics that subdivide the existing Regional Trade in Goods Statistics (RTS) into smaller UK geographic areas (NUTS2 and NUTS3)."""


# In[ ]:



scraper.dataset.family = 'trade'
cubes.add_cube(scraper, table, "HMRC RTS Small area")
cubes.output_all()


