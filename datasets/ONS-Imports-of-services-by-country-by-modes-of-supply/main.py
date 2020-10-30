# NOTE: This dataset has been joined onto Exports of services by country, by modes of supply and run directly inside that main. This is main.py is just a placeholder for what has been done to the dataset. 

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
tab = tabs["Sheet1"]
datasetTitle = 'Exports of services by country, by modes of supply'
columns=["Period", "Country", "Mode", "Direction", "Service Account", "Marker", "Measure Type", "Unit"]
trace.start(datasetTitle, tab, columns, scraper.distributions[0].downloadURL)

period = "year/2018" #TAKEN FROM SHEET 
trace.Period("Hardcoded as year/2018")

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
savepreviewhtml(tidy_sheet, fname= "tidy_sheet.html") 
trace.store("combined_dataframe", tidy_sheet.topandas())

# -

df = trace.combine_and_trace(datasetTitle, "combined_dataframe")
df.rename(columns={'OBS' : 'Value'}, inplace=True)
df = df.replace({'Direction' : {'IM' : 'imports'}})
df["Country"] = df["Country"].str.split(' ').str[0]
df["Service Account"] = df["Service Account"].str.split(' ').str[0]
df['Mode'] = df['Mode'].apply(pathify)
tidy_imports = df[["Period", "Country", "Mode", "Direction", "Service Account", "Value"]]

trace.render()


