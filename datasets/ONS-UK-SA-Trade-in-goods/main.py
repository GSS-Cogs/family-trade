#!/usr/bin/env python
# coding: utf-8

# In[121]:


import json
import pandas as pandas
from gssutils import *

info = json.load(open('info.json'))
landingPage = info['landingPage']

metadata = Scraper(seed="info.json")
distribution = metadata.distribution(latest = True)

title = distribution.title
tabs = distribution.as_databaker()
tidied_sheets = []


# In[122]:


for i in tabs:
    print(i.name)


# In[123]:


for tab in tabs:

    if '.' in tab.name:

        print(tab.name)
        flow = tab.name
        geo = tab.filter(contains_string("Country Code")).fill(DOWN).is_not_blank().is_not_whitespace()
        year = tab.filter(contains_string('Country Name')).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace()
        observations = geo.shift(2, 0).expand(RIGHT).is_not_blank().is_not_whitespace()
        dimensions = [
            HDim(year,'Period',DIRECTLY,ABOVE),
            HDim(geo,'ONS Partner Geography',DIRECTLY,LEFT),
            HDimConst("Flow", flow),
            HDimConst("Seasonal Adjustment", "SA")
        ]
        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        savepreviewhtml(tidy_sheet, fname=tab.name+"Preview.html")
        table = tidy_sheet.topandas()
        tidied_sheets.append(table)
        


# In[124]:


df = pd.concat(tidied_sheets, sort=True).fillna('')

df['Period 2'] = df['Period'].map(lambda x: x[4:])

df['Period 3'] = df['Period'].map(lambda x: x[:4])

df = df.replace({'Flow' : {'1. Annual Exports' : 'exports', 
                          '2. Annual Imports' : 'imports', 
                          '3. Quarterly Exports' : 'exports', 
                          '4. Quarterly Imports' : 'imports', 
                          '5. Monthly Exports' : 'exports', 
                          '6. Monthly Imports' : 'imports'},
                 'Period 2' : {'Jan' : '01',
                               'Feb' : '02',
                               'Mar' : '03',
                               'Apr' : '04',
                               'May' : '05',
                               'Jun' : '06',
                               'Jul' : '07',
                               'Aug' : '08',
                               'Sep' : '09',
                               'Oct' : '10',
                               'Nov' : '11',
                               'Dec' : '12'}})

df['Period'] = df.apply(lambda x: 'quarter/' + x['Period 3'] + '-' + x['Period 2'] if 'Q' in x['Period 2'] else ('month/' + x['Period 3'] + '-' + x['Period 2'] if x['Period 2'].isnumeric() else 'year/' + x['Period']), axis = 1)

df = df.drop(columns=['Period 2', 'Period 3'])

df


# In[125]:


df.rename(columns={'OBS' : 'Value', 'DATAMARKER' : 'Marker'}, inplace=True)

df["Marker"] = df["Marker"].str.replace("X", "data-not-collated")
df = df[["Period", "ONS Partner Geography", "Seasonal Adjustment", "Flow", "Value", "Marker"]]

df = df.replace({"ONS Partner Geography": {"NA":"NAM"}})

df['Value'] = df.apply(lambda x: 0 if 'data-not-collated' in x['Marker'] else x['Value'], axis = 1)

df['Value'] = pd.to_numeric(df['Value'], errors="raise", downcast="float")
df["Value"] = df["Value"].astype(float).round(2)

#scraper.dataset.family = 'trade'
metadata.dataset.description = metadata.dataset.description + """
These data are our best estimate of these bilateral UK trade flows. Users should note that alternative estimates are available, in some cases, via the statistical agencies for bilateral countries or through central databases such as 
UN Comtrade (https://comtrade.un.org/).

Some data for countries have been marked with N/A. This is because Trade in Goods do not collate data from these countries.
"""


# In[126]:


df.to_csv("observations.csv", index = False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')


# In[128]:


from IPython.core.display import HTML
for col in df:
    if col not in ['Value']:
        df[col] = df[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(df[col].cat.categories)

