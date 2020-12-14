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
trace = TransformTrace()
scraper
# -

tabs = {tab.name: tab for tab in scraper.distribution(latest=True, mediaType=Excel).as_databaker()}

tab = tabs['Time Series']

datasetTitle = 'UK trade in services by partner country'
columns=["Period", "Flow", "Trade Services", "ONS Partner Geography", "Marker", "Seasonal Adjustment"]
trace.start(datasetTitle, tab, columns, scraper.distributions[0].downloadURL)

observations = tab.excel_ref("F2").expand(RIGHT).expand(DOWN).is_not_blank()

period = tab.excel_ref("F1").expand(RIGHT).is_not_blank()
trace.Period("Values taken from cell ref F1 across. Contains Year and Quarter values")

flow = tab.excel_ref("A2").expand(DOWN).is_not_blank()
trace.Flow("Values taken from cell ref A2 across. Contains exports or imports")

trade_services = tab.excel_ref("B2").expand(DOWN).is_not_blank()
trace.Trade_Services("Values taken from cell ref B2 across")

ons_partner_geography = tab.excel_ref("D2").expand(DOWN).is_not_blank()
trace.ONS_Partner_Geography("Values taken from cell ref D2 down")

dimensions =[
    HDim(period, 'Period', DIRECTLY, ABOVE),
    HDim(flow, 'Flow', DIRECTLY, LEFT),
    HDim(trade_services, 'Trade_Services', DIRECTLY, LEFT),
    HDim(ons_partner_geography, 'Ons_Partner_Geography', DIRECTLY, LEFT),
]

c1 = ConversionSegment(tab, dimensions, observations)
# savepreviewhtml(c1, "PREVIEW.html")
trace.with_preview(c1)
trace.store("combined_dataframe", c1.topandas())

new_table = trace.combine_and_trace(datasetTitle, "combined_dataframe")
new_table.rename(columns = {'OBS':'Value', 'DATAMARKER':'Marker'},inplace = True)

new_table['Value'] = pd.to_numeric(new_table['Value'], errors = 'coerce')

new_table = new_table.replace({'Marker' : {'-' : 'itis-nil', '..' : 'disclosive'}})
trace.Marker("Replcaing - to mean itis-nil and .. to mean disclosive")


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
trace.Period("Formating to be year/0000 and quarter/2019-01 ")
# -

new_table['Flow'] = new_table['Flow'].map(lambda s: s.lower().strip())

new_table['Seasonal Adjustment'] =  'NSA'
trace.Seasonal_Adjustment("Adding in column Seasonal Adjustment with value NSA")

trace.render()
