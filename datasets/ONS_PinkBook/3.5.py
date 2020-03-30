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

# ###  Pinkbook2017_3.5

# +
from gssutils import *

scraper = Scraper('https://www.ons.gov.uk/economy/nationalaccounts/balanceofpayments/datasets/3tradeinservicesthepinkbook2016')
tabs = { tab.name: tab for tab in scraper.distributions[0].as_databaker() }
tab = tabs['3.5']
# -

observations = tab.excel_ref('D8').expand(DOWN).expand(RIGHT).is_not_blank()

Code = tab.excel_ref('C8').expand(DOWN).is_not_blank()

Year = tab.excel_ref('D3').expand(RIGHT).is_not_blank()

Commerce = tab.excel_ref('B').expand(DOWN).by_index([5,38,57]) - tab.excel_ref('B72').expand(DOWN)

Financialservices = tab.excel_ref('B').expand(DOWN).by_index([7,28,37,41,50,57,61,68,70,71]) - tab.excel_ref('B72').expand(DOWN)

Revenue = tab.excel_ref('B').expand(DOWN).is_not_blank().is_not_whitespace() - Commerce - Financialservices - tab.excel_ref('B1').expand(UP)

Currency = tab.excel_ref('W2')

Dimensions = [
            HDimConst('Geography', 'K02000001'),
            HDim(Year,'Year', DIRECTLY,ABOVE),
            HDim(Code,'CDID',DIRECTLY,LEFT),
            HDimConst('Unit','£ Million'),
            HDimConst('Measure Type','GBP Total'),
            HDim(Revenue, 'Product', DIRECTLY, LEFT),
            HDim(Financialservices, 'Services', CLOSEST, ABOVE),
            HDim(Commerce,'Flow', CLOSEST, ABOVE)    
]

c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)

new_table = c1.topandas()

new_table['Services'] = new_table['Services'].map(lambda x: x.rstrip('123'))

new_table['Product'] = new_table['Product'].fillna('')

new_table['Product'] = new_table['Product'].map(lambda x: x.rstrip('1234'))

new_table['Flow'] = new_table['Flow'].map(lambda cell:cell.replace('Exports (Credits)', 'Exports'))

new_table['Flow'] = new_table['Flow'].map(lambda cell:cell.replace('Imports (Debits)', 'Imports'))
new_table['Flow'] = new_table['Flow'].map(lambda cell:cell.replace('Balances', 'Balance'))

new_table['Year'] = new_table['Year'].map(lambda cell:cell.replace('.0', ''))

new_table['Services'] = new_table['Services'].map(lambda cell:cell.replace
                                                  ('Explicitly charged and other financial services (non-FISIM2)',
                                                   'Non-FISIM'))

new_table['Services'] = new_table['Services'].map(lambda cell:cell.replace
                                                  ('Financial intermediation services indirectly measured (FISIM2)', 
                                                   'FISIM'))

new_table['Product'] = new_table['Product'].str.strip()
new_table['Year'] = new_table['Year'].str.strip()
new_table['Geography'] = new_table['Geography'].str.strip()
new_table['CDID'] = new_table['CDID'].str.strip()
new_table['Flow'] = new_table['Flow'].str.strip()
new_table['Unit'] = new_table['Unit'].str.strip()
new_table['Measure Type'] = new_table['Measure Type'].str.strip()
new_table['Services'] = new_table['Services'].str.strip()

new_table.rename(index= str, columns= {'OBS':'Value'}, inplace = True)

new_table.fillna('NA', inplace = True)

PBclassification_table_url = 'https://drive.google.com/uc?export=download&id=1uNwmZHgq7ERqD5wcND4W2sGHXRJyP2CR'
temp_table = pd.read_excel(PBclassification_table_url, sheet_name = 0)
new_table = pd.merge(new_table, temp_table, how = 'left', left_on = 'CDID', right_on = 'cdid')
new_table.rename(index= str, columns= {'BPM6':'Pink Book Services'}, inplace = True)

new_table[new_table.cdid.isnull() == True]['CDID'].unique()

new_table = new_table[['Geography','Year','CDID','Pink Book Services','Flow','Measure Type','Value','Unit']]

new_table['Value'] = new_table['Value'].astype(int)
