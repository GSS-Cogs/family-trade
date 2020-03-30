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

# ###  Pinkbook2017_3.8

# +
from gssutils import *

scraper = Scraper('https://www.ons.gov.uk/economy/nationalaccounts/balanceofpayments/datasets/3tradeinservicesthepinkbook2016')
tabs = { tab.name: tab for tab in scraper.distributions[0].as_databaker() }
tab = tabs['3.8']
# -

observations = tab.excel_ref('D7').expand(DOWN).expand(RIGHT).is_not_blank()

Code = tab.excel_ref('C7').expand(DOWN).is_not_blank()

Year = tab.excel_ref('D3').expand(RIGHT).is_not_blank()

Commerce = tab.excel_ref('B').expand(DOWN).by_index([5,39,73]) - tab.excel_ref('B92').expand(DOWN)

Revenue = tab.excel_ref('B').expand(DOWN).is_not_blank().is_not_whitespace() - Commerce 

Currency = tab.excel_ref('W2')

Dimensions = [
            HDimConst('Geography', 'K02000001'),
            HDim(Year,'Year', DIRECTLY,ABOVE),
            HDim(Code,'CDID',DIRECTLY,LEFT),
            HDimConst('Unit','£ Million'),  
            HDimConst('Measure Type','GBP Total'),
            HDim(Revenue, 'Product', DIRECTLY, LEFT),
            HDim(Commerce,'Flow', CLOSEST, ABOVE)    
]

c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)

new_table = c1.topandas()

new_table['Product'] = new_table['Product'].map(lambda cell:cell.replace('of which:', ''))

new_table.rename(index= str, columns= {'OBS':'Value'}, inplace = True)

new_table['Year'] = new_table['Year'].map(lambda cell:cell.replace('.0', ''))

new_table['Flow'] = new_table['Flow'].map(lambda cell:cell.replace('Exports (Credits)', 'Exports'))

new_table['Flow'] = new_table['Flow'].map(lambda cell:cell.replace('Imports (Debits)', 'Imports'))
new_table['Flow'] = new_table['Flow'].map(lambda cell:cell.replace('Balances', 'Balance'))

new_table['Product'] = new_table['Product'].str.strip()
new_table['Year'] = new_table['Year'].str.strip()
new_table['Geography'] = new_table['Geography'].str.strip()
new_table['CDID'] = new_table['CDID'].str.strip()
new_table['Flow'] = new_table['Flow'].str.strip()
new_table['Unit'] = new_table['Unit'].str.strip()
new_table['Measure Type'] = new_table['Measure Type'].str.strip()

new_table = new_table[new_table['Value'] != '']

PBclassification_table_url = 'https://drive.google.com/uc?export=download&id=1uNwmZHgq7ERqD5wcND4W2sGHXRJyP2CR'
temp_table = pd.read_excel(PBclassification_table_url, sheet_name = 0)
new_table = pd.merge(new_table, temp_table, how = 'left', left_on = 'CDID', right_on = 'cdid')
new_table.rename(index= str, columns= {'BPM6':'Pink Book Services'}, inplace = True)

new_table[new_table.cdid.isnull() == True]['CDID'].unique()

new_table = new_table[['Geography','Year','CDID','Pink Book Services','Flow','Measure Type','Value','Unit','DATAMARKER']]

new_table['Value'] = new_table['Value'].astype(int)

new_table = new_table[new_table['Pink Book Services'].isnull() == False]
