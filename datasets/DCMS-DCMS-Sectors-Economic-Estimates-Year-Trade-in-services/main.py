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

#Distribution 2: Imports and Exports of services by sector 
tabs = { tab.name: tab for tab in scraper.distributions[1].as_databaker() }
list(tabs)

# Sheet : Imports 

# +
tab = tabs["Imports"]
datasetTitle = 'dcms-sectors-economic-estimates-2018-trade-in-services'
columns=["Period", "Flow", "Country", "Sector", "Sector Type", "Marker", "Measure Type", "Unit"]
trace.start(datasetTitle, tab, columns, scraper.distributions[1].downloadURL)

flow = "imports"
trace.Flow("Hardcoded as Imports")

period = "year/2018" #TAKEN FROM SHEET TITLE
trace.Period("Hardcoded as year/2018")

country = tab.excel_ref("A5").expand(DOWN)
trace.Country("Values taken from cell A5 Down")

sector = tab.excel_ref("A3").expand(RIGHT).is_not_blank()
trace.Sector("Non blank values from cell A3 across")

sector_tpe = tab.excel_ref("B4").expand(RIGHT).is_not_blank()
trace.Sector_Type("Non blank values from cell B4 across ")

observations = country.waffle(sector_tpe).is_not_blank() 
dimensions = [
    HDimConst('Period', period),
    HDimConst('Flow', flow),
    HDim(country, 'Country', DIRECTLY, LEFT),
    HDim(sector, 'Sector', CLOSEST, LEFT),
    HDim(sector_tpe, 'Sector Type', DIRECTLY, ABOVE),
    ]
tidy_sheet = ConversionSegment(tab, dimensions, observations)
trace.with_preview(tidy_sheet)
trace.store("import_dataframe", tidy_sheet.topandas())
df_imports = trace.combine_and_trace(datasetTitle, "import_dataframe")
# -

# Sheet : Exports 

# +
tab = tabs["Exports"]
datasetTitle = 'DCMS Sectors Economic Estimates 2018: Trade in services : Exports'
columns=["Period", "Flow", "Country", "Sector", "Sector Type", "Marker", "Measure Type", "Unit"]
trace.start(datasetTitle, tab, columns, scraper.distributions[1].downloadURL)

flow = "exports"
trace.Flow("Hardcoded as Exports")

period = "year/2018" #TAKEN FROM SHEET TITLE
trace.Period("Hardcoded as year/2018")

country = tab.excel_ref("A5").expand(DOWN)
trace.Country("Values taken from cell A5 Down")

sector = tab.excel_ref("A3").expand(RIGHT).is_not_blank()
trace.Sector("Non blank values from cell A3 across")

sector_tpe = tab.excel_ref("B4").expand(RIGHT).is_not_blank()
trace.Sector_Type("Non blank values from cell B4 across ")

observations = country.waffle(sector_tpe).is_not_blank()  
dimensions = [
    HDimConst('Period', period),
    HDimConst('Flow', flow),
    HDim(country, 'Country', DIRECTLY, LEFT),
    HDim(sector, 'Sector', CLOSEST, LEFT),
    HDim(sector_tpe, 'Sector Type', DIRECTLY, ABOVE),
    ]
tidy_sheet = ConversionSegment(tab, dimensions, observations)
trace.with_preview(tidy_sheet)
trace.store("exports_dataframe", tidy_sheet.topandas())
df_exports = trace.combine_and_trace(datasetTitle, "exports_dataframe")

# +
tidy = pd.concat([df_exports, df_imports])

#Post Processing
tidy.rename(columns={'OBS' : 'Value', 'DATAMARKER' : 'Marker'}, inplace=True)
tidy = tidy.replace({'Marker' : {'-' : 'suppressed'}})
tidy['Value'] = tidy.apply(lambda x: 0 if x['Marker']== "suppressed" else x['Value'], axis=1)
tidy = tidy.replace({'Sector Type' : {'Crafts4' : 'Crafts'}})

tidy['Unit'] = "gbp-million"
tidy['Measure Type'] = "count"

# -

tidy['Country'] = tidy['Country'].apply(pathify)
tidy['Sector'] = tidy['Sector'].apply(pathify)
tidy['Sector Type'] = tidy['Sector Type'].apply(pathify)
tidy = tidy[['Period', 'Country', 'Sector', 'Sector Type', 'Flow', 'Measure Type', 'Unit', 'Value', 'Marker']]


# +
description = f"""
DCMS Sector Economic Estimates 2018: Trade in Services is an official statistic and has been produced to the standards set out in the Code of Practice for Statistics.
DCMS Sectors Economic Estimates 2018: Trade in services report:
https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/863862/DCMS_Sectors_Economic_Estimates_2018_Trade_In_Services.pdf
This release provides estimates of exports and imports of services by businesses in DCMS Sectors excluding Tourism and Civil Society2) in current prices. Any changes between years may reflect changes in the absolute value of the £ (affected by the domestic rate of inflation and by exchange rates), as well as changes in actual trade volume. These statistics are further broken down by selected countries, regions and continents.The latest year for which these estimates are available is 2018. Estimates of trade in services have been constructed from ONS official statistics using international classifications (StandardIndustrial Classification (SIC) codes). For further information see Annex A and the quality assurance (QA) document accompanying this report.Data are available for each DCMS Sector (excluding Tourism and Civil Society) and sub-sectors within the Creative Industries, Digital Sector, and Cultural Sector. There is significant overlap between DCMS Sectors so users should be aware that the estimate for “DCMSSectors Total” is lower than the sum of the individual sectors.

The World totals are calculated on the same basis as previous years. However, the list of individual countries used in the calculation of the (world) regional and continental statistics (e.g. European Union, Latin America and Caribbean, Asia) is slightly different to the previous (August 2019) release. Therefore, these statistics in particular are not directly comparable with previous years. In particular: 
-The Bailiwick of Guernsey, the Bailiwick of Jersey and Timor-Leste form part of the Europe, Rest of Europe and    Asia totals for the first time.
-Gibraltar is included, and now forms part of the European Union total, in line with the Balance of Payments Vademecum. The EU Institutions total is also included on its own for the first time.     
-Latin America & Caribbean no longer includes America Unallocated as part of its calculation.
A revised backseries of calculations on the current basis is expected to be provided in the summer.

"""

comment = "Official Statistics used to provide an estimate of the contribution of DCMS Sectors to the UK economy, measured by imports and exports of services."
# -


del tidy['Measure Type']
del tidy['Unit']
tidy = tidy.fillna('')

# +
csvName = 'observations.csv'
out = Path('out')
out.mkdir(exist_ok=True)
tidy.drop_duplicates().to_csv(out / csvName, index = False)

scraper.dataset.family = 'trade'
scraper.dataset.description = description
scraper.dataset.comment = comment
scraper.dataset.title = 'Sectors Economic Estimates 2018: Trade in services'

#dataset_path = pathify(os.environ.get('JOB_NAME', f'gss_data/{scraper.dataset.family}/' + Path(os.getcwd()).name) + '/pcn').lower()
dataset_path = pathify(os.environ.get('JOB_NAME', f'gss_data/{scraper.dataset.family}/' + Path(os.getcwd()).name)).lower()

scraper.set_base_uri('http://gss-data.org.uk')
scraper.set_dataset_id(dataset_path)

csvw_transform = CSVWMapping()
csvw_transform.set_csv(out / csvName)
csvw_transform.set_mapping(json.load(open('info.json')))
csvw_transform.set_dataset_uri(urljoin(scraper._base_uri, f'data/{scraper._dataset_id}'))
csvw_transform.write(out / f'{csvName}-metadata.json')

with open(out / f'{csvName}-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())
# -

tidy

trace.render()


