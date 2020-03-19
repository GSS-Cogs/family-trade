# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
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

# Total value of UK trade by Employee Size

# +
from gssutils import *

scraper = Scraper('https://www.uktradeinfo.com/Statistics/OverseasTradeStatistics/AboutOverseastradeStatistics/Pages/OTSReports.aspx')
scraper.select_dataset(title=lambda x: x.startswith('UK Trade in Goods by Business Characteristics'))
idbrs = sorted(
    [dist for dist in scraper.distributions if dist.title.startswith('IDBR OTS tables')],
    key=lambda d: d.title, reverse=True)
idbr = idbrs[0]
display(idbr.title)
tabs = {tab.name: tab for tab in idbr.as_databaker()}
tabs.keys()
# -

tab = tabs['Employee Size']

savepreviewhtml(tab)

observations = tab.excel_ref('C9').expand(DOWN).expand(RIGHT).is_not_blank()-tab.excel_ref('C8').expand(UP)

observations = observations - tab.excel_ref('C17').expand(DOWN).expand(RIGHT)

Employeesize = tab.excel_ref('A').expand(DOWN)

Flow = tab.excel_ref('C6').expand(RIGHT)

Dimensions = [
            HDimConst('Geography', 'K02000001'),
            HDimConst('Year','2015'),
            HDimConst('Unit', '£ Million'), 
            HDimConst('Measure Type','Total Turnover'),            
            HDim(Employeesize, 'Employment', DIRECTLY, LEFT),
            HDim(Flow, 'Flow', CLOSEST, LEFT)    
]

c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)

savepreviewhtml(c1)

new_table = c1.topandas()

new_table.rename(index= str, columns= {'OBS':'Value'}, inplace = True)

new_table['Value'] = new_table['Value'].astype('int', copy=False)

new_table['Employment'] = new_table['Employment'].str.strip()
new_table['Year'] = new_table['Year'].str.strip()
new_table['Flow'] = new_table['Flow'].str.strip()
new_table['Unit'] = new_table['Unit'].str.strip()
new_table['Measure Type'] = new_table['Measure Type'].str.strip()
new_table['Geography'] = new_table['Geography'].str.strip()

new_table['Flow'] = new_table['Flow'].str.rstrip('s')
new_table['Value'] = new_table['Value'].astype(int)

new_table['Employment'] = new_table['Employment'].map(str) + ' employees'

new_table = new_table[['Geography','Year','Employment','Flow','Measure Type','Value','Unit']]

new_table['Employment'] = new_table['Employment'].map(lambda cell: cell.replace('0.0', '0'))

new_table
