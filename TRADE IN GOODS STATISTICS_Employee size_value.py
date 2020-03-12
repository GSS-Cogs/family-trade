# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
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

# TRADE IN GOODS STATISTICS:Employee size_value

from gssutils import *
if is_interactive():
    scraper = Scraper('https://www.uktradeinfo.com/Statistics/OverseasTradeStatistics/AboutOverseastradeStatistics/Pages/OTSReports.aspx')
    display(scraper)
    scraper.select_dataset(title=lambda x: x.startswith('UK Trade in Goods by Business Characteristics'))
    display(scraper)
    idbrs = sorted(
        [dist for dist in scraper.distributions if dist.title.startswith('IDBR OTS tables')],
        key=lambda d: d.title, reverse=True)
    idbr = idbrs[0]
    display(idbr.title)
    tabs = {tab.name: tab for tab in idbr.as_databaker()}
    display(tabs.keys())

tab = tabs['Industry_EmployeeSize']

savepreviewhtml(tab)

observations = tab.excel_ref('D10').expand(DOWN).expand(RIGHT).is_not_blank() 

observations = observations - tab.excel_ref('E10').expand(DOWN).is_not_blank()

observations = observations - tab.excel_ref('I10').expand(DOWN).is_not_blank()

observations = observations - tab.excel_ref('F10').expand(DOWN).is_not_blank()

observations = observations - tab.excel_ref('J10').expand(DOWN).is_not_blank()

Industrygroup = tab.excel_ref('A10').expand(DOWN).is_not_blank()

employees = tab.excel_ref('B10').expand(DOWN)

Flow = tab.excel_ref('D6').expand(RIGHT).is_not_blank()

Dimensions = [
            HDimConst('Geography', 'K02000001'),
            HDimConst('Year','2015'),
            HDimConst('Unit', '£ Million'), 
            HDimConst('Measure Type','Total Turnover'),            
            HDim(Industrygroup, 'HMRC Industry', CLOSEST, ABOVE),
            HDim(Flow, 'Flow', CLOSEST, LEFT),
            HDim(employees, 'Employment', DIRECTLY, LEFT)
]

c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)

savepreviewhtml(c1)

new_table = c1.topandas()

new_table.rename(index= str, columns= {'OBS':'Value'}, inplace = True)

new_table['HMRC Industry'] = new_table['HMRC Industry'].map(lambda cell:cell.replace('Grand Total9', 'Total'))

# +
# new_table['HMRC Industry'] = new_table['HMRC Industry'].str.lstrip('Group 1234567890')

# +
# new_table['HMRC Industry'] = new_table['HMRC Industry'].map(lambda cell: cell.replace('and', ''))
# -

new_table = new_table[new_table['Value'] != '']

new_table = new_table[new_table['Value'] != 'S']

new_table['Flow'] = new_table['Flow'].str.rstrip('s')
new_table['Value'] = new_table['Value'].astype(int)

new_table['Employment'] = new_table['Employment'].map(
    lambda c: {
        '': 'Total',
        '0.0': 'No'
    }.get(c.strip(), c.strip()) + ' employees')

new_table['HMRC Industry'] = new_table['HMRC Industry'].map(lambda x: str(x)[0:8])

new_table['HMRC Industry'] = new_table['HMRC Industry'].map(lambda cell: cell.replace('Group ', 'group-'))

new_table['HMRC Industry'] = new_table['HMRC Industry'].str.strip()
# new_table['Product'] = new_table['Product'].str.strip()
new_table['Year'] = new_table['Year'].str.strip()
new_table['Flow'] = new_table['Flow'].str.strip()
new_table['Unit'] = new_table['Unit'].str.strip()
new_table['Measure Type'] = new_table['Measure Type'].str.strip()
new_table['Geography'] = new_table['Geography'].str.strip()
new_table['Employment'] = new_table['Employment'].str.strip()

new_table = new_table[['Geography','Year','HMRC Industry','Flow','Employment','Measure Type','Value','Unit']]

# +
# def user_perc(x):
    
#     if x.strip(' ') == '':
#         return 'NA'
#     else:
#         return x
    
# new_table['HMRC Industry'] = new_table.apply(lambda row: user_perc(row['HMRC Industry']), axis = 1)
# new_table['Employment'] = new_table.apply(lambda row: user_perc(row['Employment']), axis = 1)
# -

new_table
