# -*- coding: utf-8 -*-
# +
from gssutils import *
import json
import numpy as np

""
#changing landing page back to Exports URL (First dataset to run)
with open("info.json", "r") as read_file:
    data = json.load(read_file)
    print("URL: ", data["landingPage"] )
    data["landingPage"] = "https://www.ons.gov.uk/businessindustryandtrade/internationaltrade/datasets/exportsofservicesbycountrybymodesofsupply" 
    print("URL changed to: ", data["landingPage"] )

with open("info.json", "w") as jsonFile:
    json.dump(data, jsonFile)
# -

trace = TransformTrace()
df = pd.DataFrame()
cubes = Cubes("info.json")
scraper = Scraper(json.load(open('info.json'))['landingPage'])
scraper

#Distribution 
tabs = { tab.name: tab for tab in scraper.distribution(latest=True).as_databaker() }
list(tabs)

for name, tab in tabs.items():
    datasetTitle = 'exportsofservicesbycountrybymodesofsupply'
    columns=["Period", "Country", "Mode", "Direction", "Service Account", "Marker", "Measure Type", "Unit"]
    trace.start(datasetTitle, tab, columns, scraper.distributions[0].downloadURL)

    if 'Index' in name:
        continue
    period = "year/2019" #TAKEN FROM SHEET : NOTE "2019 estimates"
    trace.Period("Hardcoded as year/2019, note these are estimates")

    country = tab.excel_ref("A2").expand(DOWN)
    trace.Country("Values taken from cell A2 Down")

    mode = tab.excel_ref("B2").expand(DOWN)
    trace.Mode("Values taken from cell B2 Down")

    direction = tab.excel_ref("C2").expand(DOWN)
    trace.Direction("Values taken from cell C2 Down")

    service_account = tab.excel_ref("D2").expand(DOWN)
    trace.Service_Account("Values taken from cell D2 Down")
    observations = tab.excel_ref("E2").expand(DOWN)
   
    dimensions = [
        HDimConst('Period', period),
        HDim(country, 'Country', DIRECTLY, LEFT),
        HDim(mode, 'Mode', DIRECTLY, LEFT),
        HDim(direction, 'Direction', DIRECTLY, LEFT),
        HDim(service_account, 'Service Account', DIRECTLY, LEFT),
    ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)   
    #savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
    trace.with_preview(tidy_sheet)
    trace.store("combined_dataframe", tidy_sheet.topandas())


df = trace.combine_and_trace(datasetTitle, "combined_dataframe")
df.rename(columns={'OBS' : 'Value'}, inplace=True)
df = df.replace({'Direction' : {'EX' : 'exports'}})
df["Country"] = df["Country"].str.split(' ').str[0]
df['Mode'] = df['Mode'].apply(pathify)
df["Service Account"] = df["Service Account"].str.split(' ').str[0]
tidy_exports = df[["Period", "Country", "Mode", "Direction", "Service Account", "Value"]]
tidy_exports

#
#
#
#
#
#
# \|Transformation of Imports file to be joined to esports transformation done above 

# +
""
#changing landing page to imports URL
with open("info.json", "r") as read_file:
    data = json.load(read_file)
    print("URL: ", data["landingPage"] )
    data["landingPage"] = "https://www.ons.gov.uk/businessindustryandtrade/internationaltrade/datasets/importsofservicesbycountrybymodesofsupply" 
    print("URL changed to: ", data["landingPage"] )

with open("info.json", "w") as jsonFile:
    json.dump(data, jsonFile)
# -

info = json.load(open('info.json')) 
scraper = Scraper(seed="info.json")   
scraper 

#Distribution 
tabs = { tab.name: tab for tab in scraper.distribution(latest=True).as_databaker() }
list(tabs)

# +
tab = tabs["Modes 1, 2 and 4"]
datasetTitle = 'importsofservicesbycountrybymodesofsupply'
columns=["Period", "Country", "Mode", "Direction", "Service Account", "Marker", "Measure Type", "Unit"]
trace.start(datasetTitle, tab, columns, scraper.distributions[0].downloadURL)

period = "year/2019" #TAKEN FROM SHEET : NOTE "2019 estimates"
trace.Period("Hardcoded as year/2019")

country = tab.excel_ref("A2").expand(DOWN)
trace.Country("Values taken from cell A2 Down")

mode = tab.excel_ref("B2").expand(DOWN)
trace.Mode("Values taken from cell B2 Down")

direction = tab.excel_ref("C2").expand(DOWN)
trace.Direction("Values taken from cell C2 Down")

service_account = tab.excel_ref("D2").expand(DOWN)
trace.Service_Account("Values taken from cell D2 Down")

observations = tab.excel_ref("E2").expand(DOWN)
dimensions = [
    HDimConst('Period', period),
    HDim(country, 'Country', DIRECTLY, LEFT),
    HDim(mode, 'Mode', DIRECTLY, LEFT),
    HDim(direction, 'Direction', DIRECTLY, LEFT),
    HDim(service_account, 'Service Account', DIRECTLY, LEFT),
    ]
tidy_sheet = ConversionSegment(tab, dimensions, observations)
trace.with_preview(tidy_sheet)
#savepreviewhtml(tidy_sheet, fname= "tidy_sheet.html") 
trace.store("combined_dataframe_imports", tidy_sheet.topandas())

# -

df = trace.combine_and_trace(datasetTitle, "combined_dataframe_imports")
df.rename(columns={'OBS' : 'Value'}, inplace=True)
df = df.replace({'Direction' : {'IM' : 'imports'}})
df["Country"] = df["Country"].str.split(' ').str[0]
df["Service Account"] = df["Service Account"].str.split(' ').str[0]
df['Mode'] = df['Mode'].apply(pathify)
tidy_imports = df[["Period", "Country", "Mode", "Direction", "Service Account", "Value"]]

tidy_imports

tidy = pd.concat([tidy_exports, tidy_imports], ignore_index=True)
tidy['Marker'] = 'estimated'
tidy['Mode'].unique()

tidy["Country"] = tidy["Country"].apply(pathify)
tidy["Direction"][tidy["Direction"] == "EX"] = "exports"

tidy['Country'].unique()

tidy

# +
description = f"""

New statistics presented in this article have been achieved as part of our ambitious trade development plan to provide more detail than ever before about the UK’s trading relationships, using improved data sources and methods enabled by our new trade IT systems.

When thinking about trade, most people imagine lorries passing through ports. While this is true for trade in goods, this is not the case for trade in services, which are not physical. Trade in services statistics are by nature more challenging to measure, due largely to their intangible nature. While it is relatively straightforward to measure the number of cars that are imported and exported through UK ports, capturing the amount UK advertisers generate from providing services to overseas clients is much more challenging. Nevertheless, it is important that we continue to develop our trade in services statistics given the UK is an overwhelmingly services dominated economy.

While our trade in services statistics already record the type of products being traded (for example, financial services) and who it is being traded with (for example, Germany), policymakers are increasingly interested in how that trade is conducted. This type of information is critical for understanding what barriers businesses face when looking to trade, and to assist policymakers engaged in trade negotiations.

To increase the information available to users on how UK trade in services is conducted, we have been developing statistics on so-called “modes of supply”. The UK is one of the first countries to have developed such estimates.

See report and methodology here:
https://www.ons.gov.uk/businessindustryandtrade/internationaltrade/articles/modesofsupplyukexperimentalestimates/latest

"""

comment = "Country breakdown of trade in services values by mode of supply (imports/exports) for 2018. Countries include only total services data, while regions include top-level extended balance of payments (EBOPs) breakdown."
scraper.dataset.family = 'trade'
scraper.dataset.description = description
scraper.dataset.comment = comment
scraper.dataset.title = 'Imports and Exports of services by country, by modes of supply'

# -

cubes.add_cube(scraper, tidy.drop_duplicates(), "ons-exports-of-services-by-country-by-modes-of-supply")
cubes.output_all()
trace.render("spec_v1.html")


