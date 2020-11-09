# -*- coding: utf-8 -*-
# +
from gssutils import * 
import json 
from urllib.parse import urljoin

trace = TransformTrace()
df = pd.DataFrame()
# -

info = json.load(open('info.json')) 
scraper = Scraper(seed="info.json")   
scraper 

#Distribution 
tabs = { tab.name: tab for tab in scraper.distributions[0].as_databaker() }
list(tabs)

# +
tab = tabs["tis_ind_ex"]
datasetTitle = 'uktradeinservicesbyindustrycountryandservicetypeexport'
columns=["Period", "Country", "Industry", "Direction", "Service Account", "Marker", "Measure Type", "Unit"]
trace.start(datasetTitle, tab, columns, scraper.distributions[0].downloadURL)

period =  tab.excel_ref("E1").expand(RIGHT).is_not_blank()
trace.Period("Values taken from cell E1 across")

country = tab.excel_ref("A2").expand(DOWN).is_not_blank()
trace.Country("Values taken from cell A2 across")

industry = tab.excel_ref("B2").expand(DOWN).is_not_blank()
trace.Industry("Values taken from cell B2 across")

direction = tab.excel_ref("C2").expand(DOWN).is_not_blank()
trace.Direction("Values taken from cell B2 across")

service_account = tab.excel_ref("D2").expand(DOWN).is_not_blank()
trace.Service_Account("Values taken from cell B2 across")

observations = period.fill(DOWN).is_not_blank()
dimensions = [
    HDim(period, 'Period', DIRECTLY, ABOVE),
    HDim(country, 'Country', DIRECTLY, LEFT),
    HDim(industry, 'Industry', DIRECTLY, LEFT),
    HDim(direction, 'Direction', DIRECTLY, LEFT),
    HDim(service_account, 'Service Account', DIRECTLY, LEFT),
    ]
tidy_sheet = ConversionSegment(tab, dimensions, observations)
trace.with_preview(tidy_sheet)
savepreviewhtml(tidy_sheet, fname= "tidy_sheet.html") 
trace.store("combined_dataframe", tidy_sheet.topandas())

# -

df = trace.combine_and_trace(datasetTitle, "combined_dataframe")
df.rename(columns={'OBS' : 'Value', 'DATAMARKER' : 'Marker'}, inplace=True)
df = df.replace({'Direction' : {'EX' : 'exports'}})
df = df.replace({'Marker' : {'..' : 'suppressed-data',}})
df['Period'] = df['Period'].astype(str).replace('\.0', '', regex=True)
df["Country"] = df["Country"].str.split(' ').str[0]
df['Period'] = "year/" + df['Period']
df["Service Account"] = df["Service Account"].str.split(' ').str[0]
df["Industry"] = df["Industry"].str.split(' ').str[0]
tidy_exports = df[["Period", "Country", "Industry", "Direction", "Service Account", "Value", "Marker"]]
tidy_exports

# Transformation of Imports file to be joined to exports transformation done above 

# +
""
#changing landing page to imports URL
with open("info.json", "r") as read_file:
    data = json.load(read_file)
    print("URL: ", data["landingPage"] )
    data["landingPage"] = "https://www.ons.gov.uk/economy/nationalaccounts/balanceofpayments/datasets/uktradeinservicesbyindustrycountryandservicetypeimports" 
    print("URL changed to: ", data["landingPage"] )

with open("info.json", "w") as jsonFile:
    json.dump(data, jsonFile)
# -

info = json.load(open('info.json')) 
scraper = Scraper(seed="info.json")   
scraper 

#Distribution 
tabs = { tab.name: tab for tab in scraper.distributions[0].as_databaker() }
list(tabs)

# +
tab = tabs["tis_ind_im"]
datasetTitle = 'uktradeinservicesbyindustrycountryandservicetypeimport'
columns=["Period", "Country", "Industry", "Direction", "Service Account", "Marker", "Measure Type", "Unit"]
trace.start(datasetTitle, tab, columns, scraper.distributions[0].downloadURL)

period =  tab.excel_ref("E1").expand(RIGHT).is_not_blank()
trace.Period("Values taken from cell E1 across")

country = tab.excel_ref("A2").expand(DOWN).is_not_blank()
trace.Country("Values taken from cell A2 across")

industry = tab.excel_ref("B2").expand(DOWN).is_not_blank()
trace.Industry("Values taken from cell B2 across")

direction = tab.excel_ref("C2").expand(DOWN).is_not_blank()
trace.Direction("Values taken from cell B2 across")

service_account = tab.excel_ref("D2").expand(DOWN).is_not_blank()
trace.Service_Account("Values taken from cell B2 across")

observations = period.fill(DOWN).is_not_blank()
dimensions = [
    HDim(period, 'Period', DIRECTLY, ABOVE),
    HDim(country, 'Country', DIRECTLY, LEFT),
    HDim(industry, 'Industry', DIRECTLY, LEFT),
    HDim(direction, 'Direction', DIRECTLY, LEFT),
    HDim(service_account, 'Service Account', DIRECTLY, LEFT),
    ]
tidy_sheet = ConversionSegment(tab, dimensions, observations)
trace.with_preview(tidy_sheet)
savepreviewhtml(tidy_sheet, fname= "tidy_sheet.html") 
trace.store("combined_dataframe_imports", tidy_sheet.topandas())

# -

df = trace.combine_and_trace(datasetTitle, "combined_dataframe_imports")
df.rename(columns={'OBS' : 'Value', 'DATAMARKER' : 'Marker'}, inplace=True)
df = df.replace({'Direction' : {'IM' : 'imports'}})
df = df.replace({'Marker' : {'..' : 'suppressed-data',}})
df["Country"] = df["Country"].str.split(' ').str[0]
df['Period'] = df['Period'].astype(str).replace('\.0', '', regex=True)
df["Service Account"] = df["Service Account"].str.split(' ').str[0]
df["Industry"] = df["Industry"].str.split(' ').str[0]
df['Period'] = "year/" + df['Period']
tidy_imports = df[["Period", "Country", "Industry", "Direction", "Service Account", "Value", "Marker"]]
tidy_imports

tidy = pd.concat([tidy_exports, tidy_imports])
tidy

# +
description = f"""
Experimental dataset providing a breakdown of UK trade in services by industry, country and service type on a balance of payments basis. Data are subject to disclosure control, which means some data have been suppressed to protect confidentiality of individual traders.

Users should note the following:    
Industry data has been produced using Standard Industrial Classification 2007 (SIC07).

Service type data has been produced using Extended Balance of Payments (EBOPs).    
Due to risks around disclosing data releated to individual firms we are only able to provide data for certain combinations of the dimensions included, i.e. country, service type and industry. This dataset therefore provides the following two combinations:    
Industry (SIC07 2 digit), by service type (EBOPs 1 digit), by geographic region (world total, EU and non-EU)
Industry (SIC07 2 digit), by total service type, by individual country
Some data cells have been suppressed to protect confidentiality so that individual traders cannot be identified.

Data
All data is in £ million, current prices    

Rounding
Some of the totals within this release (e.g. EU, Non EU and world total) may not exactly match data published via other trade releases due to small rounding differences.

Trade Asymmetries 
These data are our best estimate of these bilateral UK trade flows. Users should note that alternative estimates are available, in some cases, via the statistical agencies for bilateral countries or through central databases such as UN Comtrade (https://comtrade.un.org/)

"""

comment = "Experimental dataset providing a breakdown of UK trade in services by industry, country and service type on a balance of payments basis. Data are subject to disclosure control, which means some data have been suppressed to protect confidentiality of individual traders."
# -

tidy['Country'] = tidy['Country'].apply(pathify)
tidy['Marker'][tidy['Marker'] == 'suppressed-data'] = 'suppressed'
tidy.head(20)

# +
csvName = 'observations.csv'
out = Path('out')
out.mkdir(exist_ok=True)
tidy.drop_duplicates().to_csv(out / csvName, index = False)

scraper.dataset.family = 'trade'
scraper.dataset.description = description
scraper.dataset.comment = comment
scraper.dataset.title = 'UK trade in services by industry, country and service type, Imports & Exports'

dataset_path = pathify(os.environ.get('JOB_NAME', f'gss_data/{scraper.dataset.family}/' + Path(os.getcwd()).name) + '/pcn').lower()
scraper.set_base_uri('http://gss-data.org.uk')
scraper.set_dataset_id(dataset_path)

csvw_transform = CSVWMapping()
csvw_transform.set_csv(out / csvName)
csvw_transform.set_mapping(json.load(open('info.json')))
csvw_transform.set_dataset_uri(urljoin(scraper._base_uri, f'data/{scraper._dataset_id}'))
csvw_transform.write(out / f'{csvName}-metadata.json')

with open(out / f'{csvName}-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())

# +
""
#changing landing page back to Exports URL
with open("info.json", "r") as read_file:
    data = json.load(read_file)
    print("URL: ", data["landingPage"] )
    data["landingPage"] = "https://www.ons.gov.uk/economy/nationalaccounts/balanceofpayments/datasets/uktradeinservicesbyindustrycountryandservicetypeexports" 
    print("URL changed to: ", data["landingPage"] )

with open("info.json", "w") as jsonFile:
    json.dump(data, jsonFile)
# -

trace.render()


