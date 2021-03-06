# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# UK trade in services: service type by partner country, non-seasonally adjusted

# +
from gssutils import *

scraper = Scraper('https://www.ons.gov.uk/businessindustryandtrade/' + \
                  'internationaltrade/datasets/uktradeinservicesservicetypebypartnercountrynonseasonallyadjusted')
scraper

# +
dist = scraper.distribution(latest=True, mediaType = Excel)
tab = dist.as_pandas(sheet_name = 'Time Series')

#tab.rename(columns=tab.iloc[0], inplace=True)
tab = tab.iloc[1:, :]
tab = tab.drop(tab.columns[[2,4]], axis = 1)
tab
# -

tab.columns.values[0] = 'Flow'
tab.columns.values[1] = 'Trade Services'
tab.columns.values[2] = 'ONS Partner Geography'

new_table = pd.melt(tab, id_vars=['Flow','Trade Services','ONS Partner Geography'], var_name='Period', value_name='Value')

new_table['Period'] = new_table['Period'].astype(str)

# +
import re
YEAR_RE = re.compile(r'[0-9]{4}')
YEAR_MONTH_RE = re.compile(r'([0-9]{4})\s+(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)')
YEAR_QUARTER_RE = re.compile(r'([0-9]{4})(Q[1-4])')

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
# -

new_table['Flow'] = new_table['Flow'].map(lambda s: s.lower().strip())

new_table['Seasonal Adjustment'] =  'NSA'
new_table['Measure Type'] =  'GBP Total'
new_table['Unit'] =  'gbp-million'


# +
def user_perc(x):
    
    if (str(x) ==  '-') : 
        return 'itis-nil'
    elif ((str(x) == '..')):
        return 'disclosive'
    else:
        return None
    
new_table['Marker'] = new_table.apply(lambda row: user_perc(row['Value']), axis = 1)
# -

new_table['Value'] = pd.to_numeric(new_table['Value'], errors = 'coerce')

new_table = new_table[['ONS Partner Geography', 'Period','Flow','Trade Services', 'Seasonal Adjustment', 'Measure Type','Value','Unit','Marker' ]]

# +
indexNames = new_table[ new_table['Trade Services'].str.contains('NaN', na=True)].index
new_table.drop(indexNames, inplace = True)

#The 27 April 2020 release added Trade Services which dont have Type codes. This causes duplicates as all the various Services without numbers are classed as the same service.
#This will need further investigation upon review. I did look to see if the most recent pink book publications had any reference to them but I coulnd't find antyhing.

# +
new_table.rename(columns={'ONS Partner Geography':'CORD Geography',
                          'Flow':'Flow Directions'}, 
                 inplace=True)

#ONS Partner geography has been changed since certain codes are missing from Vademecum codelist that it points to, CORD codelists are editable by us
#Flow has been changed to Flow Direction to differentiate from Migration flow dimension - I believe
# -

new_table



