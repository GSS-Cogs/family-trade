#!/usr/bin/env python
# coding: utf-8
# %%
from gssutils import *
import json

#Landing page URL in info.json for UK trade in services: all countries, non-seasonally adjusted
with open("info.json", "r") as read_file:
    data = json.load(read_file)
    data["landingPage"] = "https://www.ons.gov.uk/businessindustryandtrade/internationaltrade/datasets/uktradeinservicesallcountriesnonseasonallyadjusted" 

with open("info.json", "w") as jsonFile:
    json.dump(data, jsonFile)


# %%
scraper = Scraper(seed="info.json")
distribution = scraper.distribution(latest=True)

trace = TransformTrace()
cubes = Cubes("info.json")

tabs = {tab.name: tab for tab in distribution.as_databaker()}

# %%
tab = tabs['TiS by country']
datasetTitle = distribution.title
columns = ["Period", "ONS Partner Geography", "Flow", "Trade Services", "Measure Type", "Unit", "Marker"]

# %%
trace.start(datasetTitle, tab, columns, distribution.downloadURL)

# trace.obs("Taken from cell C7 across and down which are non blank")
observations = tab.excel_ref('C7').expand(DOWN).expand(RIGHT).is_not_blank()

trace.Period("Taken from cell C4 across")
period = tab.excel_ref('C4').expand(RIGHT).is_not_whitespace()

trace.Flow("Taken from cells B5 and B252")
flow = tab.excel_ref('B').expand(DOWN).by_index([5,252])

footer = tab.excel_ref("A500").expand(RIGHT).expand(DOWN)

trace.Trade_Services("Hardcoded as all")

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
#Landing page URL in info.json for UK trade in services: service type by partner country, non-seasonally adjusted
with open("info.json", "r") as read_file:
    data = json.load(read_file)
    data["landingPage"] = "https://www.ons.gov.uk/businessindustryandtrade/internationaltrade/datasets/uktradeinservicesservicetypebypartnercountrynonseasonallyadjusted" 

with open("info.json", "w") as jsonFile:
    json.dump(data, jsonFile)

# %%
scraper = Scraper(seed="info.json")
distribution = scraper.distribution(latest=True)
tabs = {tab.name: tab for tab in distribution.as_databaker()}

# %%
tab = tabs['Time Series']

datasetTitle = distribution.title
columns=["Period", "Flow", "Trade Services", "ONS Partner Geography", "Marker", "Seasonal Adjustment"]
trace.start(datasetTitle, tab, columns, distribution.downloadURL)

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
    HDim(ons_partner_geography, 'ONS Partner Geography', DIRECTLY, LEFT),
]

tidy_sheet = ConversionSegment(tab, dimensions, observations)
savepreviewhtml(tidy_sheet, fname = tab.name +"PREVIEW.html")
trace.with_preview(tidy_sheet)
trace.store("combined_dataframe", tidy_sheet.topandas())

# %%
new_table = trace.combine_and_trace(datasetTitle, "combined_dataframe")

# %%
new_table

# %%
trace.add_column("Renaming OBS column into Value and DATAMARKER column into Marker")
new_table.rename(columns = {'OBS':'Value', 'DATAMARKER':'Marker'},inplace = True)
new_table

# %%
new_table['Value'] = pd.to_numeric(new_table['Value'], errors = 'coerce')


# %%
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


# %%
new_table['Period'] = new_table['Period'].astype(str).replace('\.', '', regex=True)
new_table['Period'] =  new_table["Period"].apply(date_time)
trace.Period("Formating to be year/0000 and quarter/2019-01 ")

# %%
new_table = new_table.replace({'Marker' : {'-' : 'itis-nil', '..' : 'disclosive'}})
trace.Marker("Replcaing - to mean itis-nil and .. to mean disclosive")

# %%
new_table['Seasonal Adjustment'] =  'NSA'
trace.Seasonal_Adjustment("Adding in column Seasonal Adjustment with value NSA")

# %%
new_table['Flow'] = new_table['Flow'].apply(pathify)

# %%
tidy = new_table[['ONS Partner Geography', 'Period','Flow','Trade Services', 'Seasonal Adjustment', 'Value', 'Marker' ]]

# %%
tidy.loc[(tidy['Marker'] == 'disclosive'),'Value'] = 0
tidy['Value'] = tidy['Value'].astype(int)
tidy['Marker'].fillna('', inplace=True)

# %%
tidy = tidy.drop_duplicates()
tidy.head(10)

# %%
cubes.add_cube(scraper, tidy, "ONS UK trade in services by country and partner country" )
cubes.output_all()

# %%
trace.render("spec_v1.html")

# %%
tidy.head(10)

# %%
