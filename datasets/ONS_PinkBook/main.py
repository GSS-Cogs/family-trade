# -*- coding: utf-8 -*-
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

# The Pink Book 2019

# +
from gssutils import *

scraper = Scraper('https://www.ons.gov.uk/economy/nationalaccounts/balanceofpayments/datasets/3tradeinservicesthepinkbook2016')
tabs = { tab.name: tab for tab in scraper.distributions[0].as_databaker() }
# -

list(tabs)

sheetname = ['3.2','3.3','3.4','3.5','3.6','3.7','3.8','3.9','3.10']

next_table = pd.DataFrame()
for sheet in sheetname:
    tab = tabs[sheet]
    cell = tab.excel_ref('B3')
    code = cell.shift(1,0).fill(DOWN).is_not_blank().is_not_whitespace()
    Year = cell.fill(RIGHT).is_not_blank().is_not_whitespace()            
    observations = Year.fill(DOWN).is_not_blank().is_not_whitespace() 
    Flow = cell.fill(DOWN).one_of(['Exports (Credits)', 'Imports (Debits)', 'Balances'])
    Dimensions = [
                HDimConst('Geography', 'K02000001'),
                HDim(Year,'Year', DIRECTLY,ABOVE),
                HDim(code,'CDID',DIRECTLY,LEFT),
                HDimConst('Unit', 'gbp-miilion'), 
                HDimConst('Measure Type','GBP Total'),
                HDim(Flow,'Flow',CLOSEST, ABOVE)           

    ]
    c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
    new_table = c1.topandas()
    new_table['Year'] = new_table['Year'].map(lambda cell:cell.replace('.0', ''))
    new_table['Year'] = new_table['Year'].str.strip()
    new_table['Geography'] = new_table['Geography'].str.strip()
    new_table['CDID'] = new_table['CDID'].str.strip()
    new_table['Flow'] = new_table['Flow'].str.strip()
    import numpy as np
    new_table['OBS'].replace('', np.nan, inplace=True)
    new_table.rename(index= str, columns={'OBS': 'Value'}, inplace=True)
    new_table['Flow'] = new_table['Flow'].map(
        lambda x: {
            'Exports (Credits)': 'Exports',
            'Imports (Debits)': 'Imports',
            'Balances': 'Balance'}.get(x, x))
    next_table = pd.concat([next_table, new_table])

PBclassification_table_url = 'https://drive.google.com/uc?export=download&id=1uNwmZHgq7ERqD5wcND4W2sGHXRJyP2CR'
temp_table = pd.read_excel(PBclassification_table_url, sheet_name = 0)
next_table = pd.merge(next_table, temp_table, how = 'left', left_on = 'CDID', right_on = 'cdid')
next_table.rename(index= str, columns= {'BPM6':'Pink Book Services'}, inplace = True)

next_table[next_table.cdid.isnull() == True]['CDID'].unique()

next_table = next_table[['Geography','Year','CDID','Pink Book Services','Flow','Measure Type','Value','Unit','DATAMARKER']]

next_table = next_table[next_table['Pink Book Services'].isnull() == False]

next_table['Marker'] = next_table['DATAMARKER'].map(
    lambda x: { 'NA' : 'not-available' ,
               ' -' : 'nil-or-less-than-a-million'
        }.get(x, x))

next_table['Pink Book Services'] = next_table['Pink Book Services'].astype(str)

next_table['Flow Directions'] = next_table['Flow'].map(pathify)

next_table['Period'] = 'year/' + next_table['Year']

next_table = next_table[['Geography','Period','CDID','Pink Book Services','Flow Directions','Measure Type','Value','Unit','Marker']]

from pathlib import Path
import numpy as np
out = Path('out')
out.mkdir(exist_ok=True)
next_table.drop_duplicates().to_csv(out / 'observations.csv', index = False)

scraper.dataset.family = 'trade'
from gssutils.metadata import THEME
scraper.dataset.theme = THEME['business-industry-trade-energy']
with open(out / 'observations.csv-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())

csvw = CSVWMetadata('https://gss-cogs.github.io/family-trade/reference/')
csvw.create(out / 'observations.csv', out / 'observations.csv-schema.json')
