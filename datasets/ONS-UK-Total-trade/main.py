# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.4.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# UK trade in services: all countries, non-seasonally adjusted

# +
from gssutils import *
import json

scraper = Scraper(json.load(open('info.json'))['landingPage'])
scraper
# -

tabs = { tab.name: tab for tab in scraper.distribution(latest=True).as_databaker() }
list(tabs)

# +
Final_table = pd.DataFrame()

def product(name):
    if 'Total Trade' in name:
        return 'goods-and-services'
    elif 'TiG' in name:
        return 'goods'
    elif 'TiS' in name:
        return 'services'
    raise ValueError(f'Unknown product type ${name}')

for name, tab in tabs.items():
    if 'Index' in name or 'Contact Sheet' in name:
        continue
    observations = tab.excel_ref('C7').expand(DOWN).expand(RIGHT).is_not_blank().is_not_whitespace()
    Year = tab.excel_ref('C4').expand(RIGHT).is_not_blank().is_not_whitespace()
    Flow = tab.fill(DOWN).one_of(['Exports','Imports'])
    geo = tab.excel_ref('A7').expand(DOWN).is_not_blank().is_not_whitespace()
    Dimensions = [
        HDim(Year,'Period',DIRECTLY,ABOVE),
        HDim(geo,'ONS Partner Geography',DIRECTLY,LEFT),
        HDim(Flow, 'Flow',CLOSEST,ABOVE),
        HDimConst('Measure Type', 'GBP Total'),
        HDimConst('Unit','gbp-million')
    ]
    c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
    new_table = c1.topandas()
    import numpy as np
    new_table.rename(columns={'OBS': 'Value'}, inplace=True)
    new_table['Flow'] = new_table['Flow'].map(lambda s: s.lower().strip())
    new_table['ONS ABS Trade'] = product(name)
    new_table['Period'] = new_table['Period'].astype(str)
    new_table = new_table[['ONS Partner Geography', 'Period','Flow','ONS ABS Trade', 'Measure Type','Value','Unit' ]]
    Final_table = pd.concat([Final_table, new_table])

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

Final_table['Period'] = Final_table.Period.str.replace('\.0', '')
Final_table['Period'] = Final_table['Period'].apply(time2period)
# -

from pathlib import Path
import numpy as np
out = Path('out')
out.mkdir(exist_ok=True)
Final_table.drop_duplicates().to_csv(out / 'observations.csv', index = False)

# +
from gssutils.metadata import THEME
scraper.dataset.family = 'trade'
scraper.dataset.theme = THEME['business-industry-trade-energy']

with open(out / 'observations.csv-metadata.trig', 'wb') as metadata:
     metadata.write(scraper.generate_trig())
csvw = CSVWMetadata('https://gss-cogs.github.io/family-trade/reference/')
csvw.create(out / 'observations.csv', out / 'observations.csv-schema.json')
# -

Final_table


