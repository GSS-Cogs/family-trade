# NOTE: This dataset has been joined onto UK trade in services by industry, country and service type, Exports
#  and run directly inside that main. This is main.py is just a placeholder for what has been done to the dataset. 

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
tab = tabs["tis_ind_im"]
datasetTitle = 'UK trade in services by industry, country and service type, imports'
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
df = df.replace({'Direction' : {'IM' : 'imports'}})
df = df.replace({'Marker' : {'..' : 'suppressed-data',}})
df["Country"] = df["Country"].str.split(' ').str[0]
df['Period'] = df['Period'].astype(str).replace('\.0', '', regex=True)
df["Service Account"] = df["Service Account"].str.split(' ').str[0]
df["Industry"] = df["Industry"].str.split(' ').str[0]
df['Period'] = "year/" + df['Period']
tidy = df[["Period", "Country", "Industry", "Direction", "Service Account", "Value", "Marker"]]

#output stage one transform for DM 
csvName = 'stage_one_transform.csv'
out = Path('out')
out.mkdir(exist_ok=True)
tidy.drop_duplicates().to_csv(out / csvName, index = False)
tidy

trace.render()
