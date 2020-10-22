# +
from gssutils import * 
import json 

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
datasetTitle = 'DCMS Sectors Economic Estimates 2018: Trade in services : Imports'
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

observations = country.waffle(sector_tpe) 
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

observations = country.waffle(sector_tpe) 
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
tidy = tidy.replace({'Marker' : {'-' : 'n/a'}})
tidy.drop(tidy[(( tidy['Sector Type']  == "Empty column") | (tidy['Sector Type'] == "Empty column2") | (tidy['Sector Type'] == "Empty column3") | (tidy['Sector Type'] == "Empty column4") | (tidy['Sector Type'] == "Empty column5"))].index, inplace = True)

tidy['Unit'] = "millions (pounds)"
tidy['Measure Type'] = "count"


tidy = tidy[['Period', 'Country', 'Sector', 'Sector Type', 'Flow', 'Measure Type', 'Unit', 'Value', 'Marker']]

# -

#output stage one transform for DM 
csvName = 'stage_one_transform.csv'
out = Path('out')
out.mkdir(exist_ok=True)
tidy.drop_duplicates().to_csv(out / csvName, index = False)
tidy

trace.output()
