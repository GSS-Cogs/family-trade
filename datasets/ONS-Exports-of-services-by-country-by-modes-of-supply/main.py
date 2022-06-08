#!/usr/bin/env python
# coding: utf-8

# In[191]:


from gssutils import *
import json
import numpy as np
import re


# In[192]:


#changing landing page back to Exports URL (First dataset to run)
with open("info.json", "r") as read_file:
    data = json.load(read_file)
    print("URL: ", data["landingPage"] )
    data["landingPage"] = "https://www.ons.gov.uk/businessindustryandtrade/internationaltrade/datasets/exportsofservicesbycountrybymodesofsupply" 
    print("URL changed to: ", data["landingPage"] )

with open("info.json", "w") as jsonFile:
    json.dump(data, jsonFile)


# In[193]:


df = pd.DataFrame()

scraper = Scraper(json.load(open('info.json'))['landingPage'])
scraper

#Distribution 
tabs = { tab.name: tab for tab in scraper.distribution(latest=True).as_databaker() }
list(tabs)

tidy_tabs = []

for name, tab in tabs.items():
    datasetTitle = 'exportsofservicesbycountrybymodesofsupply'

    if 'Index' in name:
        continue
    period = "year/"+str(re.findall(r"'([^']*)'", str(tab.filter(contains_string("estimate"))))[0]).split(" ")[0]

    country = tab.filter("Country").fill(DOWN)

    mode = tab.filter("Mode").fill(DOWN)

    direction = tab.filter("Direction").fill(DOWN)

    service_account = tab.filter("Service account").fill(DOWN)

    observations = tab.filter(contains_string("estimate")).fill(DOWN)
   
    dimensions = [
        HDimConst('Period', period),
        HDim(country, 'Country', DIRECTLY, LEFT),
        HDim(mode, 'Mode', DIRECTLY, LEFT),
        HDim(direction, 'Direction', DIRECTLY, LEFT),
        HDim(service_account, 'Service Account', DIRECTLY, LEFT),
    ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
    tidy_tabs.append(tidy_sheet.topandas())


df = pd.concat(tidy_tabs)

df.rename(columns={'OBS' : 'Value'}, inplace=True)
df = df.replace({'Direction' : {'EX' : 'exports'}})
df["Country"] = df["Country"].str.split(' ').str[0]
df['Mode'] = df['Mode'].apply(pathify)
df["Service Account"] = df["Service Account"].str.split(' ').str[0]

tidy_exports = df[["Period", "Country", "Mode", "Direction", "Service Account", "Value"]]
tidy_exports

# \|Transformation of Imports file to be joined to esports transformation done above 


# In[194]:


#changing landing page to imports URL
with open("info.json", "r") as read_file:
    data = json.load(read_file)
    print("URL: ", data["landingPage"] )
    data["landingPage"] = "https://www.ons.gov.uk/businessindustryandtrade/internationaltrade/datasets/importsofservicesbycountrybymodesofsupply" 
    print("URL changed to: ", data["landingPage"] )

with open("info.json", "w") as jsonFile:
    json.dump(data, jsonFile)


# In[195]:


info = json.load(open('info.json')) 
scraper = Scraper(seed="info.json")   
scraper 

#Distribution 
tabs = { tab.name: tab for tab in scraper.distribution(latest=True).as_databaker() }
list(tabs)


# In[196]:


tab = tabs["Modes 1, 2 and 4"]
datasetTitle = 'importsofservicesbycountrybymodesofsupply'

tidy_tabs = []

period = "year/"+str(re.findall(r"'([^']*)'", str(tab.filter(contains_string("estimate"))))[0]).split(" ")[0]

country = tab.filter("Country").fill(DOWN)

mode = tab.filter("Mode").fill(DOWN)

direction = tab.filter("Direction").fill(DOWN)

service_account = tab.filter("Service account").fill(DOWN)

observations = tab.filter(contains_string("estimate")).fill(DOWN)
dimensions = [
    HDimConst('Period', period),
    HDim(country, 'Country', DIRECTLY, LEFT),
    HDim(mode, 'Mode', DIRECTLY, LEFT),
    HDim(direction, 'Direction', DIRECTLY, LEFT),
    HDim(service_account, 'Service Account', DIRECTLY, LEFT),
    ]
tidy_sheet = ConversionSegment(tab, dimensions, observations)
savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
tidy_tabs.append(tidy_sheet.topandas())


# In[197]:


df = df = pd.concat(tidy_tabs)

df.rename(columns={'OBS' : 'Value'}, inplace=True)
df = df.replace({'Direction' : {'IM' : 'imports'}})
df["Country"] = df["Country"].str.split(' ').str[0]
df["Service Account"] = df["Service Account"].str.split(' ').str[0]
df['Mode'] = df['Mode'].apply(pathify)

tidy_imports = df[["Period", "Country", "Mode", "Direction", "Service Account", "Value"]]

tidy_imports

tidy = pd.concat([tidy_exports, tidy_imports], ignore_index=True)
tidy['Marker'] = 'estimated'
tidy['Mode'].unique()

tidy["Direction"][tidy["Direction"] == "EX"] = "exports"

tidy['Country'].unique()

tidy


# In[198]:


description = f"""

New statistics presented in this article have been achieved as part of our ambitious trade development plan to provide more detail than ever before about the UK’s trading relationships, using improved data sources and methods enabled by our new trade IT systems.

When thinking about trade, most people imagine lorries passing through ports. While this is true for trade in goods, this is not the case for trade in services, which are not physical. Trade in services statistics are by nature more challenging to measure, due largely to their intangible nature. While it is relatively straightforward to measure the number of cars that are imported and exported through UK ports, capturing the amount UK advertisers generate from providing services to overseas clients is much more challenging. Nevertheless, it is important that we continue to develop our trade in services statistics given the UK is an overwhelmingly services dominated economy.

While our trade in services statistics already record the type of products being traded (for example, financial services) and who it is being traded with (for example, Germany), policymakers are increasingly interested in how that trade is conducted. This type of information is critical for understanding what barriers businesses face when looking to trade, and to assist policymakers engaged in trade negotiations.

To increase the information available to users on how UK trade in services is conducted, we have been developing statistics on so-called “modes of supply”. The UK is one of the first countries to have developed such estimates.

See report and methodology here:
https://www.ons.gov.uk/businessindustryandtrade/internationaltrade/articles/modesofsupplyukexperimentalestimates/latest

"""

comment = "Country breakdown of trade in services values by mode of supply (imports/exports) for 2018. Countries include only total services data, while regions include top-level extended balance of payments (EBOPs) breakdown."
scraper.dataset.family = 'trade'
scraper.dataset.description = description
scraper.dataset.comment = comment
scraper.dataset.title = 'Imports and Exports of services by country, by modes of supply'


# In[199]:


tidy.to_csv('observations.csv', index=False)

catalog_metadata = scraper.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')


# In[200]:


from IPython.core.display import HTML
for col in tidy:
    if col not in ['Value']:
        tidy[col] = tidy[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(tidy[col].cat.categories)

