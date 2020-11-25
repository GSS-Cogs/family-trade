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

# UK trade in services: all countries, non-seasonally adjusted

# +
from gssutils import *
import json

info = json.load(open('info.json'))
landingPage = info['landingPage']
landingPage

scraper = Scraper(landingPage)
tabs = { tab.name: tab for tab in scraper.distributions[0].as_databaker() }
# -

output = pd.DataFrame()

# -

for name,tab in tabs.items():
    
    observations = tab.excel_ref('C7').expand(DOWN).expand(RIGHT).is_not_blank().is_not_whitespace()
    year = tab.excel_ref('C5').expand(RIGHT).is_not_blank().is_not_whitespace()
    geo = tab.excel_ref('A7').expand(DOWN).is_not_blank().is_not_whitespace()
    dimensions = [HDim(year,'Period',DIRECTLY,ABOVE),
                  HDim(geo,'ONS Partner Geography',DIRECTLY,LEFT),
                  HDimConst('Measure Type', 'GBP Total'),
                  HDimConst('Unit','gbp-million')]
    cs = ConversionSegment(observations, dimensions, processTIMEUNIT=True)
    df = cs.topandas()
    
    # Take the last word of the tab's name and convert it to lower case, assign as value in Flow column in df
    df['Flow'] = str(name.split()[-1]).lower()
    
    df.rename(columns={'OBS': 'Value'}, inplace=True)
    df['Period'] = df['Period'].astype(str)
    df = df[['ONS Partner Geography', 'Period','Flow','Measure Type','Value' ,'Unit', 'DATAMARKER']]
    output = pd.concat([output, df])

# +
import re
YEAR_RE = re.compile(r'[0-9]{4}')
YEAR_MONTH_RE = re.compile(r'([0-9]{4})(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)')
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
        month_num = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
                     'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}.get(month)
        return f"month/{year}-{month_num}"
    elif gre.fullmatch(YEAR_QUARTER_RE, t):
        year, quarter = gre.last_match.groups()
        return f"quarter/{year}-{quarter}"
    else:
        print(f"no match for {t}")

Final_table['Period'] = Final_table.Period.str.replace('\.0', '')
Final_table['Period'] = Final_table['Period'].apply(time2period)
Final_table.rename(columns={'DATAMARKER': 'Marker'}, inplace=True)
Final_table['Marker'].replace('N/A', 'not-applicable', inplace=True)

# +
Final_table.rename(columns={'Flow':'Flow Directions'}, inplace=True)

#Flow has been changed to Flow Direction to differentiate from Migration Flow dimension
# -

from pathlib import Path
import numpy as np
out = Path('out')
out.mkdir(exist_ok=True)
Final_table.drop_duplicates().to_csv(out / 'observations.csv', index = False)

scraper.dataset.family = 'trade'
from gssutils.metadata import THEME
scraper.dataset.theme = THEME['business-industry-trade-energy']
with open(out / 'observations.csv-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())

csvw = CSVWMetadata('https://gss-cogs.github.io/family-trade/reference/')
csvw.create(out / 'observations.csv', out / 'observations.csv-schema.json')

Final_table


