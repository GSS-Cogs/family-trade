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

# UK trade in services: service type by partner country, non-seasonally adjusted

# +
from gssutils import *
import json

info = json.load(open("info.json"))
scraper = Scraper(seed="info.json")
scraper
trace = TransformTrace()
# -

tabs = {tab.name: tab for tab in scraper.distribution(latest=True, mediaType=Excel).as_databaker()}

tab = tabs['Time Series']

observations = tab.excel_ref("F2").expand(RIGHT).expand(DOWN).is_not_blank()

Period = tab.excel_ref("F1").expand(RIGHT).is_not_blank()

Flow = tab.excel_ref("A2").expand(DOWN).is_not_blank()

Trade_Services = tab.excel_ref("B2").expand(DOWN).is_not_blank()

Ons_Partner_Geography = tab.excel_ref("D2").expand(DOWN).is_not_blank()

dimensions =[
    HDim(Period, 'Period', DIRECTLY, ABOVE),
    HDim(Flow, 'Flow', DIRECTLY, LEFT),
    HDim(Trade_Services, 'Trade_Services', DIRECTLY, LEFT),
    HDim(Ons_Partner_Geography, 'Ons_Partner_Geography', DIRECTLY, LEFT),
]

c1 = ConversionSegment(tab, dimensions, observations)
# savepreviewhtml(c1, "PREVIEW.html")
new_table = c1.topandas()

new_table.rename(columns = {'OBS':'Value', 'DATAMARKER':'Marker'},inplace = True)

new_table['Value'] = pd.to_numeric(new_table['Value'], errors = 'coerce')

new_table = new_table.replace({'Marker' : {'-' : 'itis-nil', '..' : 'disclosive'}})


# +
def left(s, amount):
    return s[:amount]
def right(s, amount):
    return s[-amount:]
def date_time (date):
    if len(date)  == 5:
        return 'year/' + left(date, 4)
    #year/2019
    elif len(date) == 6:
        return 'quarter/' + left(date,4) + '-' + right(date,2)
    #quarter/2019-01
    else:
        return date

new_table['Period'] = new_table['Period'].astype(str).replace('\.', '', regex=True)
new_table['Period'] =  new_table["Period"].apply(date_time)
# -

new_table['Flow'] = new_table['Flow'].map(lambda s: s.lower().strip())

new_table['Seasonal Adjustment'] =  'NSA'


