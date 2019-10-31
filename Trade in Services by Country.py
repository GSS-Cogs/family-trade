# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
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

# UK trade in services: all countries, non-seasonally adjusted

# +
from gssutils import *

scraper = Scraper('https://www.ons.gov.uk/businessindustryandtrade/' + \
                  'internationaltrade/datasets/uktradeinservicesallcountriesnonseasonallyadjusted')

tabs = {tab.name: tab for tab in scraper.distribution(latest=True, mediaType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet").as_databaker()} 
# -

tab = tabs['TiS by country']

observations = tab.excel_ref('C7').expand(DOWN).expand(RIGHT).is_not_blank()

Year = tab.excel_ref('C4').expand(RIGHT).is_not_whitespace()

Flow = tab.excel_ref('B').expand(DOWN).by_index([5,253])

geo1 = tab.excel_ref('A7').expand(DOWN).is_not_blank()

Dimensions = [
            HDim(Year,'Period',DIRECTLY,ABOVE),
            HDim(geo1,'ONS Partner Geography',DIRECTLY,LEFT),
            HDim(Flow, 'Flow',CLOSEST,ABOVE),
            HDimConst('Measure Type', 'GBP Total'),
            HDimConst('Unit','gbp-million'),
            HDimConst('Marker',''),
           ]

c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
if is_interactive():
    savepreviewhtml(c1)

new_table = c1.topandas()

new_table['Period'] = 'quarter/' + new_table['Period'].astype(str).str[0:4]+ '-' +   new_table['Period'].astype(str).str[-2:]              

new_table.head()

new_table.columns = ['Value' if x=='OBS' else x for x in new_table.columns]

new_table['Flow'] = new_table['Flow'].map(lambda s: s.lower().strip())

new_table['Seasonal Adjustment'] =  'NSA'

new_table['Value'] = new_table['Value'].astype(int)

new_table['Pink Book Services'] = '0'

# Duplicated observations of different countries in 

new_table = new_table.loc[new_table['ONS Partner Geography'].isin(['AD','AE','AF','AG','AI','AM','AO','AQ','AS','AW','AZ','BA','BB','BD','BF',	
                                                                'BH','BI','BJ','BM','BN','BO','BQ','BS','BT','BV','BW','BZ','CC','CD','CF',
                                                                'CG','CI','CK','CM','CR','CU','CV','CW','CX','D5','DJ','DM','DO','DZ','EC',
                                                                'ER','ET','FJ','FK','FM','FO','GA','GD','GE','GG','GH','GI','GL','GM','GN',
                                                                'GQ','GS','GT','GU','GW','GY','HM','HN','HT','IM','IO','IQ','JE','JM','JO',
                                                                'KE','KG','KH','KI','KM','KN','KP','KW','KY','KZ','LA',	'LB','LC','LK','LR',
                                                                'LS','LY','MD','MG','MH','MK','ML','MM','MN','MO','MP','MR','MS','MU','MV',
                                                                'MW','MZ','NA','NC','NE','NF','NG','NI','NP','NR','NU','OM','PA','PE','PF',
                                                                'PG','PN','PS','PW','PY','QA','RW','SB','SC','SD','SH','SL','SM','SN','SO',
                                                                'SR','SS','ST','SV','SX','SY','SZ','TC','TD','TF','TG','TJ','TK','TL','TM',
                                                                'TN','TO','TT','TV','TZ','UG','UM','UZ','VA','VC','VG','VI','VN','VU','WF',
                                                                'WS','XK','YE','ZM','ZW'])]

new_table = new_table[['ONS Partner Geography', 'Period','Flow','Pink Book Services', 'Seasonal Adjustment', 'Measure Type','Value','Unit','Marker' ]]
