# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.2.4
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
tab = dist.as_pandas(header = None)

tab.rename(columns=tab.iloc[0], inplace=True)
tab = tab.iloc[1:, :]
tab = tab.drop(tab.columns[[2,4]], axis = 1)
tab
# -

tab.columns.values[0] = 'Flow'
tab.columns.values[1] = 'Pink Book Services'
tab.columns.values[2] = 'ONS Partner Geography'

new_table = pd.melt(tab, id_vars=['Flow','Pink Book Services','ONS Partner Geography'], var_name='Period', value_name='Value')

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

new_table = new_table[['ONS Partner Geography', 'Period','Flow','Pink Book Services', 'Seasonal Adjustment', 'Measure Type','Value','Unit','Marker' ]]

new_table



# +



# -


