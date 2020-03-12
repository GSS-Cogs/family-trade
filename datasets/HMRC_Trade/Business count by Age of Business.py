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

# Business count by Age of Business

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

tab = tabs['Age Group']

savepreviewhtml(tab)

observations = tab.excel_ref('C25').expand(DOWN).expand(RIGHT).is_not_blank()-tab.excel_ref('C24').expand(UP)

observations = observations - tab.excel_ref('C34').expand(DOWN).expand(RIGHT)

Businessage = tab.excel_ref('A').expand(DOWN)

Flow = tab.excel_ref('C22').expand(RIGHT)

Dimensions = [
            HDimConst('Geography', 'K02000001'),
            HDimConst('Year','2015'),
            HDimConst('Unit', 'Businesses'), 
            HDimConst('Measure Type','Count'),            
            HDim(Businessage, 'Age of Business', DIRECTLY, LEFT),
            HDim(Flow, 'Flow', CLOSEST, LEFT)    
]

c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)

savepreviewhtml(c1)

new_table = c1.topandas()

new_table.rename(index= str, columns= {'OBS':'Value'}, inplace = True)

new_table['Value'] = new_table['Value'].astype('int', copy=False)

new_table['Age of Business'] = new_table['Age of Business'].str.strip()
new_table['Year'] = new_table['Year'].str.strip()
new_table['Flow'] = new_table['Flow'].str.strip()
new_table['Unit'] = new_table['Unit'].str.strip()
new_table['Measure Type'] = new_table['Measure Type'].str.strip()
new_table['Geography'] = new_table['Geography'].str.strip()

new_table['Flow'] = new_table['Flow'].str.rstrip('s')

new_table['Age of Business'] = new_table['Age of Business'].map(str) + ' years' 

new_table['Value'] = new_table['Value'].astype(int)

new_table = new_table[['Geography','Year','Age of Business','Flow','Measure Type','Value','Unit']]

new_table.head(4)

new_table.tail(4)


