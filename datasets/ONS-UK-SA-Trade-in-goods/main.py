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
cubes = Cubes('info.json')
landingPage = info['landingPage']
landingPage

scraper = Scraper(landingPage)
scraper.dataset.family = info['families']

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
    df['Flow Directions'] = str(name.split()[-1]).lower()
    
    df.rename(columns={'OBS': 'Value'}, inplace=True)
    if name.split()[0] == 'Annual':
        df['Period'] = pd.to_datetime(df['Period'].str[:4], format='%Y').dt.strftime('/id/year/%Y')
    elif name.split()[0] == 'Monthly':
        df['Period'] = pd.to_datetime(df['Period'], format='%Y%b').dt.strftime('/id/month/%Y-%m')
    else:
        raise ValueError('Unexpected period')

    output = pd.concat([output, df])

#-

output.rename(columns={'DATAMARKER': 'Marker'}, inplace=True)
output['Marker'].replace('N/A', 'not-applicable', inplace=True)

#-

cubes.add_cube(scraper, output, info['title'])

#-
cubes.output_all()

