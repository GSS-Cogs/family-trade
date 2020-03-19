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

# TRADE IN GOODS STATISTICS:Employee Count and age_employee count

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

tab = tabs['EmployeeSize_Age']

savepreviewhtml(tab)

observations = tab.excel_ref('F10').expand(DOWN).expand(RIGHT).is_not_blank() 

observations = observations - tab.excel_ref('I10').expand(DOWN).is_not_blank()

observations = observations - tab.excel_ref('H10').expand(DOWN).is_not_blank()

totalemployees = tab.excel_ref('A10').expand(DOWN).is_not_blank()

age = tab.excel_ref('B10').expand(DOWN)

Flow = tab.excel_ref('D6').expand(RIGHT).is_not_blank()

Dimensions = [
            HDimConst('Geography', 'K02000001'),
            HDimConst('Year','2015'),
            HDimConst('Unit', 'Employees'), 
            HDimConst('Measure Type','Count'),            
            HDim(totalemployees, 'Employment', CLOSEST, ABOVE),
            HDim(Flow, 'Flow', CLOSEST, LEFT),
            HDim(age, 'Age of Business', DIRECTLY, LEFT)
]

c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)

savepreviewhtml(c1)

new_table = c1.topandas()

new_table.rename(index= str, columns= {'OBS':'Value'}, inplace = True)

new_table['Employment'] = new_table['Employment'].str.strip()
new_table['Year'] = new_table['Year'].str.strip()
new_table['Flow'] = new_table['Flow'].str.strip()
new_table['Unit'] = new_table['Unit'].str.strip()
new_table['Measure Type'] = new_table['Measure Type'].str.strip()
new_table['Geography'] = new_table['Geography'].str.strip()
new_table['Age of Business'] = new_table['Age of Business'].str.strip()

new_table['Flow'] = new_table['Flow'].str.rstrip('s')

new_table = new_table[['Geography','Year','Employment','Flow','Age of Business','Measure Type','Value','Unit']]

new_table['Employment'] = new_table['Employment'].map(lambda cell:cell.replace('Grand Total9', 'Grand Total'))


new_table = new_table[new_table['Value'] != '']

new_table = new_table[new_table['Value'] != 'S']

new_table = new_table[new_table['Value'] != 0 ]

new_table['Value'] = new_table['Value'].astype(int)

new_table['Age of Business'] = new_table['Age of Business'].map(str) + ' years'

new_table['Employment'] = new_table['Employment'].map(str) + ' employees'

# +
# def user_perc(x):
    
#     if x.strip(' ') == '':
#         return 'NA'
#     else:
#         return x
    
# new_table['Age of Business'] = new_table.apply(lambda row: user_perc(row['Age of Business']), axis = 1)
# -

new_table.head(4)

new_table.tail(4)
