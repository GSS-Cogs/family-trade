# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.7.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# UK trade in services: all countries, non-seasonally adjusted

# +
from gssutils import *
import json

scraper = Scraper('https://www.ons.gov.uk/businessindustryandtrade/' + \
                  'internationaltrade/datasets/uktradeinservicesallcountriesnonseasonallyadjusted')
scraper
trace = TransformTrace()
# -

tabs = {tab.name: tab for tab in scraper.distribution(latest=True, mediaType=Excel).as_databaker()} 

tab = tabs['TiS by country']

datasetTitle = "ONS-UK-trade-in-services"
columns = ["Year", "ONS Partner Geography", "Flow", "Measure Type", "Unit", "Marker", "Footer"]
trace.start(datasetTitle, tab, columns, scraper.distributions[0].downloadURL)

trace.obs("Taken from cell C7 across and down which are non blank")
observations = tab.excel_ref('C7').expand(DOWN).expand(RIGHT).is_not_blank()

trace.Year("Taken from cell C4 across")
year = tab.excel_ref('C4').expand(RIGHT).is_not_whitespace()

trace.Flow("Taken from cells B5 and B252")
Flow = tab.excel_ref('B').expand(DOWN).by_index([5,252])

trace.Footer("Taken from cells A500 across and down ")
footer = tab.excel_ref("A500").expand(RIGHT).expand(DOWN)

trace.ONS_Partner_Geography("Taken from cell A7 down")
ons_partner_geography = tab.excel_ref('A7').expand(DOWN).is_not_blank() - footer

dimensions = [
            HDim(year, 'Year', DIRECTLY,ABOVE),
            HDim(ons_partner_geography, 'ONS_Partner_Geography', DIRECTLY,LEFT),
            HDim(Flow, 'Flow', CLOSEST,ABOVE),
           ]

c1 = ConversionSegment(tab, dimensions, observations)
trace.with_preview(c1)

new_table = c1.topandas()
trace.store("combined_dataframe", new_table)

df = trace.combine_and_trace(datasetTitle, "combined_dataframe")
trace.Year("Adding quarter and - to values in Period column and converting into string datatype")
df['Year'] = 'quarter/' + df['Year'].astype(str).str[0:4]+ '-' +   df['Year'].astype(str).str[-2:]              

df.head()

trace.add_column("Renaming OBS column into Value")
df.columns = ['Value' if x=='OBS' else x for x in new_table.columns]

df['Value'] = df['Value'].astype(int)

trace.Flow("Converting all values in Flow column to lower case")
df['Flow'] = df['Flow'].map(lambda s: s.lower().strip())

trace.add_column("Adding a new column Seasonal Adjustment and value as NSA")
df['Seasonal Adjustment'] =  'NSA'

trace.add_column("Adding a new column Trade Services and value as 0")
df['Trade Services'] = '0'

df["Marker"] = " "

# Duplicated observations of different countries in 

df = df.loc[new_table['ONS_Partner_Geography'].isin(['AD','AE','AF','AG','AI','AM','AO','AQ','AS','AW','AZ','BA','BB','BD','BF',	
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

# trace.df("Defining the order of Columns")
df = df[['ONS_Partner_Geography', 'Year','Flow','Trade Services', 'Seasonal Adjustment', 'Value', 'Marker' ]]

# +
trace.multi(["ONS_Partner_Geography", "Flow"], "Renamed columns ONS Partner Geography and Flow into CORD Geography and Flow Directions")
df.rename(columns={'ONS Partner Geography':'CORD Geography',
                          'Flow':'Flow Directions'}, 
                 inplace=True)

#ONS Partner geography has been changed since certain codes are missing from Vademecum codelist that it points to, CORD codelists are editable by us
#Flow has been changed to Flow Direction to differentiate from Migration flow dimension - I believe
# -

trace.render()

df
