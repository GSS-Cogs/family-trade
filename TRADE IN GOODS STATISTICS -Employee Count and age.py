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

# TRADE IN GOODS STATISTICS:Employee Count and age

# + {"jupyter": {"outputs_hidden": true}}
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

# + {"jupyter": {"outputs_hidden": true}}
tab = tabs['EmployeeSize_Age']
# -

savepreviewhtml(tab)

# + {"jupyter": {"outputs_hidden": true}}
observations = tab.excel_ref('D10').expand(DOWN).expand(RIGHT).is_not_blank() 

# + {"jupyter": {"outputs_hidden": true}}
observations = observations - tab.excel_ref('E10').expand(DOWN).is_not_blank()

# + {"jupyter": {"outputs_hidden": true}}
observations = observations - tab.excel_ref('F10').expand(DOWN).is_not_blank()

# + {"jupyter": {"outputs_hidden": true}}
observations = observations - tab.excel_ref('J10').expand(DOWN).is_not_blank()

# + {"jupyter": {"outputs_hidden": true}}
observations = observations - tab.excel_ref('I10').expand(DOWN).is_not_blank()

# + {"jupyter": {"outputs_hidden": true}}
totalemployees = tab.excel_ref('A10').expand(DOWN).is_not_blank()

# + {"jupyter": {"outputs_hidden": true}}
age = tab.excel_ref('B10').expand(DOWN)

# + {"jupyter": {"outputs_hidden": true}}
Flow = tab.excel_ref('D6').expand(RIGHT).is_not_blank()

# + {"jupyter": {"outputs_hidden": true}}
Dimensions = [
            HDimConst('Geography', 'K02000001'),
            HDimConst('Year','2015'),
            HDimConst('Unit', '£ Million'), 
            HDimConst('Measure Type','Total Turnover'),            
            HDim(totalemployees, 'Employment', CLOSEST, ABOVE),
            HDim(Flow, 'Flow', CLOSEST, LEFT),
            HDim(age, 'Age of Business', DIRECTLY, LEFT)
]

# + {"jupyter": {"outputs_hidden": true}}
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
# -

savepreviewhtml(c1)

new_table = c1.topandas()

# + {"jupyter": {"outputs_hidden": true}}
new_table.rename(index= str, columns= {'OBS':'Value'}, inplace = True)

# + {"jupyter": {"outputs_hidden": true}}
new_table['Employment'] = new_table['Employment'].str.strip()
new_table['Year'] = new_table['Year'].str.strip()
new_table['Flow'] = new_table['Flow'].str.strip()
new_table['Unit'] = new_table['Unit'].str.strip()
new_table['Measure Type'] = new_table['Measure Type'].str.strip()
new_table['Geography'] = new_table['Geography'].str.strip()
new_table['Age of Business'] = new_table['Age of Business'].str.strip()

# + {"jupyter": {"outputs_hidden": true}}
new_table = new_table[['Geography','Year','Employment','Flow','Age of Business','Measure Type','Value','Unit']]

# + {"jupyter": {"outputs_hidden": true}}
new_table['Employment'] = new_table['Employment'].map(lambda cell:cell.replace('Grand Total9', 'Grand Total'))


# + {"jupyter": {"outputs_hidden": true}}
new_table = new_table[new_table['Value'] != '']

# + {"jupyter": {"outputs_hidden": true}}
new_table = new_table[new_table['Value'] != 'S']

# + {"jupyter": {"outputs_hidden": true}}
new_table['Flow'] = new_table['Flow'].str.rstrip('s')
new_table['Value'] = new_table['Value'].astype(int)

# + {"jupyter": {"outputs_hidden": true}}
new_table['Employment'] = new_table['Employment'].map(lambda cell: cell.replace('0.0', '0'))

# + {"jupyter": {"outputs_hidden": true}}
new_table['Age of Business'] = new_table['Age of Business'].map(str) + ' years'

# + {"jupyter": {"outputs_hidden": true}}
new_table['Employment'] = new_table['Employment'].map(str) + ' employees'

# + {"jupyter": {"outputs_hidden": true}}
# def user_perc(x):
    
#     if x.strip(' ') == '':
#         return 'NA'
#     else:
#         return x
    
# new_table['Age of Business'] = new_table.apply(lambda row: user_perc(row['Age of Business']), axis = 1)
# -

new_table.head(20)

new_table.tail(4)
