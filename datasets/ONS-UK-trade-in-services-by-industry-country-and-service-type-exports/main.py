# +
from gssutils import * 
import json 

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
datasetTitle = 'UK trade in services by industry, country and service type, exports'
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
df = df.replace({'Marker' : {'..' : 'suppressed-data',}})
df['Period'] = df['Period'].astype(str).replace('\.0', '', regex=True)
df['Period'] = "year/" + df['Period']
tidy = df[["Period", "Country", "Industry", "Direction", "Service Account", "Value", "Marker"]]

#output stage one transform for DM 
csvName = 'stage_one_transform.csv'
out = Path('out')
out.mkdir(exist_ok=True)
tidy.drop_duplicates().to_csv(out / csvName, index = False)
tidy

trace.render()
