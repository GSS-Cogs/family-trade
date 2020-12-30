#!/usr/bin/env python
# coding: utf-8
# %%
# Scraped first Landing page
from gssutils import *
import json


scraper = Scraper('https://www.ons.gov.uk/businessindustryandtrade/' + \
                  'internationaltrade/datasets/uktradeinservicesallcountriesnonseasonallyadjusted')
scraper
trace = TransformTrace()

# %%
# distribution of first landing page
dist_1 = scraper.distributions[0]
dist_1

# %%
# URL of first landing page
first_url = scraper.distributions[0].downloadURL
first_url

# %%
tabs = {tab.name: tab for tab in scraper.distribution(latest=True, mediaType=Excel).as_databaker()}

# %%
tab = tabs["TiS by country"]

# %%
tab = tabs['TiS by country']
datasetTitle = "ONS-UK-trade-in-services"
columns = ["Period", "ONS Partner Geography", "Flow", "Trade Services", "Measure Type", "Unit", "Marker"]

trace.start(datasetTitle, tab, columns, first_url)

# trace.obs("Taken from cell C7 across and down which are non blank")
observations = tab.excel_ref('C7').expand(DOWN).expand(RIGHT).is_not_blank()

trace.Period("Taken from cell C4 across")
period = tab.excel_ref('C4').expand(RIGHT).is_not_whitespace()

trace.Flow("Taken from cells B5 and B252")
flow = tab.excel_ref('B').expand(DOWN).by_index([5,252])

footer = tab.excel_ref("A500").expand(RIGHT).expand(DOWN)

trace.Trade_Services = ("Hardcoded as all")

trace.ONS_Partner_Geography("Taken from cell A7 down")
ons_partner_geography = tab.excel_ref('A7').expand(DOWN).is_not_blank() - footer

dimensions = [
            HDim(period, 'Period', DIRECTLY,ABOVE),
            HDim(ons_partner_geography, 'ONS Partner Geography', DIRECTLY,LEFT),
            HDim(flow, 'Flow', CLOSEST,ABOVE),
            HDimConst("Trade Services", "all"),
           ]
tidy_sheet = ConversionSegment(tab, dimensions, observations)
savepreviewhtml(tidy_sheet, fname = tab.name + "Preview.html")
trace.with_preview(tidy_sheet)
trace.store("combined_dataframe", tidy_sheet.topandas())

# %%
#scraped second landing page
from gssutils import *
import json

info = json.load(open("info.json"))
scraper_2 = Scraper(seed="info.json")
trace = TransformTrace()
scraper_2

# %%
dist_2 = scraper_2.distributions[0]
dist_2

# %%
second_url = scraper_2.distributions[0].downloadURL
second_url

# %%
tabs = {tab.name: tab for tab in scraper_2.distribution(latest=True, mediaType=Excel).as_databaker()}

# %%
tab = tabs['Time Series']

datasetTitle = 'UK trade in services by partner country'
columns=["Period", "Flow", "Trade Services", "ONS Partner Geography", "Marker", "Seasonal Adjustment"]
trace.start(datasetTitle, tab, columns, second_url)

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
    HDim(trade_services, 'Trade Services', DIRECTLY, LEFT),
    HDim(ons_partner_geography, 'Ons Partner Geography', DIRECTLY, LEFT),
]

tidy_sheet = ConversionSegment(tab, dimensions, observations)
savepreviewhtml(tidy_sheet, fname = tab.name +"PREVIEW.html")
trace.with_preview(tidy_sheet)
trace.store("combined_dataframe", tidy_sheet.topandas())

# %%
new_table = trace.combine_and_trace(datasetTitle, "combined_dataframe")

# %%
new_table
