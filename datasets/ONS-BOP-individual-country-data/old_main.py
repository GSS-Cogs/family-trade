# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     cell_metadata_json: true
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.6.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# ###  Individual country data (goods) on a monthly basis to Tidy Data

# +
from databaker.framework import *
import pandas as pd

# we're only using CSVWMetadata from gssutils (for now), remember to change when we update this recipe
from gssutils import CSVWMetadata
# -

# This scrape will be a bit nasty as the data source is an adhoc, so url conventions appear to change between publications.
#
# To get around this, we're going to hit the ons website search page and parse out the most recent version of the adhoc
# from there.
#
# To help explain the following code, this is an example of a single search result from this page.
#
# -----
# ```
# <a href="/redir/eyJhbGciOiJIUzI1NiJ9.eyJpbmRleCI6MSwicGFnZVNpemUiOjEwLCJ0ZXJtIjoiaW5kaXZpZHVhbCBjb3VudHJ5IGRhdGEgb24gYSBtb250aGx5IGJhc2lzIGZyb20gamFudWFyeS9kYXRhIiwicGFnZSI6MSwidXJpIjoiL2Vjb25vbXkvbmF0aW9uYWxhY2NvdW50cy9iYWxhbmNlb2ZwYXltZW50cy9hZGhvY3MvMDA2Njc1aW5kaXZpZHVhbGNvdW50cnlkYXRhb25hbW9udGhseWJhc2lzZnJvbWphbnVhcnkyMDE2dG9qYW51YXJ5MjAxNyIsImxpc3RUeXBlIjoic2VhcmNoIn0.Gdw3U8ZGrtT85SftZUcHMEVqem3KmGpWRyRjS_ow77Y" data-gtm-uri="/economy/nationalaccounts/balanceofpayments/adhocs/006675individualcountrydataonamonthlybasisfromjanuary2016tojanuary2017"><strong>Individual</strong> <strong>Country</strong> <strong>data</strong> on a <strong>monthly</strong> <strong>basis</strong> <strong>from</strong> <strong>January</strong> 2016 to <strong>January</strong> 2017 </a>```

# +
import requests
search_for = "https://www.ons.gov.uk/search?q=individual+country+data+on+a+monthly+basis+from+january/data"

# get the page
r = requests.get(search_for)
if r.status_code != 200:
    raise ValueError("Aborting operation. Failed to get 1st (of 2) scrapes of ONS website.")

# We're going to look for the words: country, data, monthly and individual
# since there're loose conventions, we'll look for in any order and case
find = ["individual", "country", "data", "monthly", "tojanuary"]
found_urls = []
for html_line in r.text.split("\n"): # for every line of html

    # if all have matched and if its a redirect (they're all redirects) and has a data url
    matched = [x for x in find if x in html_line.lower()]
    if len(matched) == len(find) and 'href="/redir' in html_line and 'data-gtm-uri=' in html_line:

        # prefix the boiler plate and store the new url in our list
        found_urls.append("http://www.ons.gov.uk" + html_line.split('data-gtm-uri="')[1].split("\"")[0])

found_urls
# -

# -----
#
# Now that we've found the right adhoc page, we need to get the xls url. The element we're grabbing looks like the below:
#
# -----
# ```
# <a href="/file?uri=/economy/nationalaccounts/balanceofpayments/adhocs/008182individualcountrydatagoodsonamonthlybasisfromjanuary1998tojanuary2018/01.allcountriesjanuary2018.xls">Individual country data (goods) on a monthly basis from January 1998 to January 2018</a>
# ```

# +
# get the most recent one
dates_to_urls = { int(x[-4:]):x for x in found_urls}
url = dates_to_urls[max(dates_to_urls.keys())]

# around we go again...
r = requests.get(url)
if r.status_code != 200:
    raise ValueError("Aborting operation. Failed to get 2nd (of 2) scrapes of ONS website.")

# It's an adhoc, the first xls link should always contain the spreadsheet we want
content = [x for x in r.text.split("\n") if ".xls" in x][0]
sourceUrl = content.split(" ")[-1].replace('"', '')

# +
import requests
from cachecontrol import CacheControl
from cachecontrol.caches.file_cache import FileCache
from cachecontrol.heuristics import LastModified
from pathlib import Path
from io import BytesIO

session = CacheControl(requests.Session(),
                       cache=FileCache('.cache'),
                       heuristic=LastModified())

# -

tab = pd.read_excel(BytesIO(session.get(sourceUrl).content), header = None, sheet_name = 1)
tab.iloc[2][0] = 'Dummy'
tab.columns=tab.iloc[2]
tab.rename(columns={'Dummy': 'Period'}, inplace = True)
tab

observations = tab[3:].rename(columns={'ONS Partner Geography': 'Period'})
observations.head()

new_table = pd.melt(observations, id_vars= ['Period'], var_name='ONS Partner Geography', value_name='OBS')
new_table.reset_index(drop=True, inplace=True)
print(len(new_table))
new_table.head(50)

new_table = new_table[new_table['OBS'] != 0]

new_table.count()

new_table['Period'].unique()

# +
# new_table['Period'] = 'month/' + new_table['Period'].astype(str).str[0:4]+ '-' + new_table['Period'].astype(str).str[-3:]
# new_table.head()

# +
import re
YEAR_RE = re.compile(r'[0-9]{4}')
YEAR_MONTH_RE = re.compile(r'([0-9]{4})\s+(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)')
YEAR_QUARTER_RE = re.compile(r'([0-9]{4})\s+(Q[1-4])')

# from https://stackoverflow.com/questions/597476/how-to-concisely-cascade-through-multiple-regex-statements-in-python
class Re(object):
  def __init__(self):
    self.last_match = None
  def fullmatch(self,pattern,text):
    self.last_match = re.fullmatch(pattern,text)
    return self.last_match

def time2period(t):
    gre = Re()
    if gre.fullmatch(YEAR_RE, t):
        return f"year/{t}"
    elif gre.fullmatch(YEAR_MONTH_RE, t):
        year, month = gre.last_match.groups()
        month_num = {'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04', 'MAY': '05', 'JUN': '06',
                     'JUL': '07', 'AUG': '08', 'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'}.get(month)
        return f"month/{year}-{month_num}"
    elif gre.fullmatch(YEAR_QUARTER_RE, t):
        year, quarter = gre.last_match.groups()
        return f"quarter/{year}-{quarter}"
    else:
        print(f"no match for {t}")

new_table['Period'] = new_table['Period'].apply(time2period)
new_table.head(10)
# -

new_table['Unit'] = '£ Million'
new_table['Measure Type'] = 'GBP Total'
new_table['Flow'] = 'exports'
new_table.tail(5)

new_table.rename(index= str, columns= {'OBS':'Value'}, inplace = True)

Final_table = pd.DataFrame()

new_table = new_table[['ONS Partner Geography','Period','Flow','Measure Type','Value','Unit']]

new_table.tail(5)

new_table['Value'] = new_table['Value'].astype(int)

new_table.dtypes

Final_table = pd.concat([Final_table, new_table])

tab = pd.read_excel(BytesIO(session.get(sourceUrl).content), header = None, sheet_name = 3)
tab.iloc[2][0] = 'Dummy'
tab.columns=tab.iloc[2]
tab.rename(columns={'Dummy': 'Period'}, inplace = True)
tab

observations = tab[3:].rename(columns={'ONS Partner Geography': 'Period'})
observations.head()

new_table = pd.melt(observations, id_vars= ['Period'], var_name='ONS Partner Geography', value_name='OBS')
new_table.reset_index(drop=True, inplace=True)
print(len(new_table))
new_table.head(50)

new_table = new_table[new_table['OBS'] != 0]

new_table.count()

new_table['Period'].unique()

# +
import re
YEAR_RE = re.compile(r'[0-9]{4}')
YEAR_MONTH_RE = re.compile(r'([0-9]{4})\s+(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)')
YEAR_QUARTER_RE = re.compile(r'([0-9]{4})\s+(Q[1-4])')

# from https://stackoverflow.com/questions/597476/how-to-concisely-cascade-through-multiple-regex-statements-in-python
class Re(object):
  def __init__(self):
    self.last_match = None
  def fullmatch(self,pattern,text):
    self.last_match = re.fullmatch(pattern,text)
    return self.last_match

def time2period(t):
    gre = Re()
    if gre.fullmatch(YEAR_RE, t):
        return f"year/{t}"
    elif gre.fullmatch(YEAR_MONTH_RE, t):
        year, month = gre.last_match.groups()
        month_num = {'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04', 'MAY': '05', 'JUN': '06',
                     'JUL': '07', 'AUG': '08', 'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'}.get(month)
        return f"month/{year}-{month_num}"
    elif gre.fullmatch(YEAR_QUARTER_RE, t):
        year, quarter = gre.last_match.groups()
        return f"quarter/{year}-{quarter}"
    else:
        print(f"no match for {t}")

new_table['Period'] = new_table['Period'].apply(time2period)
new_table.head(10)
# -

new_table['Unit'] = '£ Million'
new_table['Measure Type'] = 'GBP Total'
new_table['Flow'] = 'imports'
new_table.tail(5)

new_table.rename(index= str, columns= {'OBS':'Value'}, inplace = True)

new_table = new_table[['ONS Partner Geography','Period','Flow','Measure Type','Value','Unit']]

new_table['Value'] = new_table['Value'].astype(int)

Final_table = pd.concat([Final_table, new_table])

tab = pd.read_excel(BytesIO(session.get(sourceUrl).content), header = None, sheet_name = 2)
tab.iloc[2][0] = 'Dummy'
tab.columns=tab.iloc[2]
tab.rename(columns={'Dummy': 'Period'}, inplace = True)
tab

observations = tab[3:].rename(columns={'ONS Partner Geography': 'Period'})
observations.head()

new_table = pd.melt(observations, id_vars= ['Period'], var_name='ONS Partner Geography', value_name='OBS')
new_table.reset_index(drop=True, inplace=True)
print(len(new_table))
new_table.head(50)

new_table = new_table[new_table['OBS'] != 0]

new_table.count()

new_table['Period'].unique()

new_table['Period'] = new_table['Period'].astype(str).str[0:4]+ ' ' + new_table['Period'].astype(str).str[-3:]
new_table.head()

# +
import re
YEAR_RE = re.compile(r'[0-9]{4}')
YEAR_MONTH_RE = re.compile(r'([0-9]{4})\s+(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)')
YEAR_QUARTER_RE = re.compile(r'([0-9]{4})\s+(Q[1-4])')

# from https://stackoverflow.com/questions/597476/how-to-concisely-cascade-through-multiple-regex-statements-in-python
class Re(object):
  def __init__(self):
    self.last_match = None
  def fullmatch(self,pattern,text):
    self.last_match = re.fullmatch(pattern,text)
    return self.last_match

def time2period(t):
    gre = Re()
    if gre.fullmatch(YEAR_RE, t):
        return f"year/{t}"
    elif gre.fullmatch(YEAR_MONTH_RE, t):
        year, month = gre.last_match.groups()
        month_num = {'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04', 'MAY': '05', 'JUN': '06',
                     'JUL': '07', 'AUG': '08', 'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'}.get(month)
        return f"month/{year}-{month_num}"
    elif gre.fullmatch(YEAR_QUARTER_RE, t):
        year, quarter = gre.last_match.groups()
        return f"quarter/{year}-{quarter}"
    else:
        print(f"no match for {t}")

new_table['Period'] = new_table['Period'].apply(time2period)
new_table.head(10)
# -

new_table['Unit'] = '£ Million'
new_table['Measure Type'] = 'GBP Total'
new_table['Flow'] = 'exports'
new_table.tail(5)

new_table.rename(index= str, columns= {'OBS':'Value'}, inplace = True)

new_table = new_table[['ONS Partner Geography','Period','Flow','Measure Type','Value','Unit']]

new_table['Value'] = new_table['Value'].astype(int)

new_table.dtypes

Final_table = pd.concat([Final_table, new_table])

tab = pd.read_excel(BytesIO(session.get(sourceUrl).content), header = None, sheet_name = 4)
tab.iloc[2][0] = 'Dummy'
tab.columns=tab.iloc[2]
tab.rename(columns={'Dummy': 'Period'}, inplace = True)
tab

observations = tab[3:].rename(columns={'ONS Partner Geography': 'Period'})
observations.head()

new_table = pd.melt(observations, id_vars= ['Period'], var_name='ONS Partner Geography', value_name='OBS')
new_table.reset_index(drop=True, inplace=True)
print(len(new_table))
new_table.head()

new_table = new_table[new_table['OBS'] != 0]

new_table.count()

new_table['Period'].unique()

new_table['Period'] = new_table['Period'].astype(str).str[0:4]+ ' ' + new_table['Period'].astype(str).str[-3:]
new_table.head()

# +
import re
YEAR_RE = re.compile(r'[0-9]{4}')
YEAR_MONTH_RE = re.compile(r'([0-9]{4})\s+(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)')
YEAR_QUARTER_RE = re.compile(r'([0-9]{4})\s+(Q[1-4])')

# from https://stackoverflow.com/questions/597476/how-to-concisely-cascade-through-multiple-regex-statements-in-python
class Re(object):
  def __init__(self):
    self.last_match = None
  def fullmatch(self,pattern,text):
    self.last_match = re.fullmatch(pattern,text)
    return self.last_match

def time2period(t):
    gre = Re()
    if gre.fullmatch(YEAR_RE, t):
        return f"year/{t}"
    elif gre.fullmatch(YEAR_MONTH_RE, t):
        year, month = gre.last_match.groups()
        month_num = {'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04', 'MAY': '05', 'JUN': '06',
                     'JUL': '07', 'AUG': '08', 'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'}.get(month)
        return f"month/{year}-{month_num}"
    elif gre.fullmatch(YEAR_QUARTER_RE, t):
        year, quarter = gre.last_match.groups()
        return f"quarter/{year}-{quarter}"
    else:
        print(f"no match for {t}")

new_table['Period'] = new_table['Period'].apply(time2period)
new_table.head(10)
# -

new_table['Unit'] = '£ Million'
new_table['Measure Type'] = 'GBP Total'
new_table['Flow'] = 'imports'
new_table.tail(5)

new_table.rename(index= str, columns= {'OBS':'Value'}, inplace = True)

new_table = new_table[['ONS Partner Geography','Period','Flow','Measure Type','Value','Unit']]

new_table['Value'] = new_table['Value'].astype(int)

new_table.dtypes

Final_table = pd.concat([Final_table, new_table])

Final_table.count()

Final_table['ONS Partner Geography'].unique()

Final_table['ONS Partner Geography'] = Final_table['ONS Partner Geography'].astype(str).str[0:2]

Final_table.head()

Final_table.tail()

# +
Final_table.rename(columns={'ONS Partner Geography':'CORD Geography',
                          'Flow':'Flow Directions'}, 
                 inplace=True)

#ONS Partner geography has been changed since certain codes are missing from Vademecum codelist that it points to, CORD codelists are editable by us
#Flow has been changed to Flow Direction to differentiate from Migration flow dimension - I believe

# + {"endofcell": "--"}
from gssutils import *
from gssutils.metadata import *
import json
from dateutil.parser import parse
from urllib.parse import urljoin

out = Path('out')
out.mkdir(exist_ok=True, parents=True)

Final_table.to_csv(out / ('observations.csv'), index = False)

info = json.load(Path('info.json').open())
ds = PMDDataset()
ds.theme = THEME['business-industry-trade-energy']
ds.family = 'Trade'
ds.title = info['title']
ds.description = info['description']
ds.issued = parse(info['published']).date()
ds.landingPage = info['landingPage']
ds.contactPoint = 'mailto:bop@ons.gsi.gov.uk'
ds.publisher = GOV['office-for-national-statistics']
ds.rights = "https://www.uktradeinfo.com/AboutUs/Pages/TermsAndConditions.aspx"
ds.license = "http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/"

ds_id = pathify(os.environ.get('JOB_NAME', 'ONS_BoP_individual_countries'))
ds_base = 'http://gss-data.org.uk'

ds.uri = urljoin(ds_base, f'data/{ds_id}')
ds.graph = urljoin(ds_base, f'graph/{ds_id}/metadata')
ds.inGraph = urljoin(ds_base, f'graph/{ds_id}')
ds.sparqlEndpoint = urljoin(ds_base, '/sparql')
ds.modified = datetime.now()
display(ds)

with open(out / 'observations.csv-metadata.trig', 'wb') as metadata:
     metadata.write(ds.as_quads().serialize(format='trig'))

# -

csvw = CSVWMetadata('https://gss-cogs.github.io/family-trade/reference/')
csvw.create(out / 'observations.csv', out / 'observations.csv-schema.json')

# --





