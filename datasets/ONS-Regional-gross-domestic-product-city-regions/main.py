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
#tabs = { tab for tab in scraper.distributions[0].as_databaker() }
tabs = { tab.name: tab for tab in scraper.distributions[0].as_databaker() }
list(tabs)

# - Tables 1 - 5 : how the calculation of GDP in current prices in tables
# - Tables 6 - 7 : calculate GDP per head 
# - Table 8 : shows the implied deflators from the GVA(B) dataset
# - Table 9 - 10 : table 8 is used to remove the effect of price inflation and derive volume measures of regional GDP shown in tables 9 and 10.
# - Table 11 : shows volume GDP per head
# - Table 12 - 13 - show the annual growth rates of volume GDP and volume GDP per head
#

# +
for name, tab in tabs.items():
    if 'Information' in name or 'ESRI_MAPINFO_SHEET' in name:
        continue

    datasetTitle = 'Regional gross domestic product city regions'
    columns=["Period", "Area Type", "Geo Code", "Area Name", "Dimension name unsure", "Marker", "Measure Type", "Unit"]
    trace.start(datasetTitle, tab, columns, scraper.distributions[0].downloadURL)
        
    area_type = tab.excel_ref('A3').expand(DOWN)
    trace.Area_Type("Values taken from cell A3 Down")
        
    geo_code = tab.excel_ref('B3').expand(DOWN)
    trace.Geo_Code("Values taken from cell B3 Down")
        
    area_name = tab.excel_ref('C3').expand(DOWN)
    trace.Area_Name("Values taken from cell C3 Down")
        
    period = tab.excel_ref('D2').expand(RIGHT)
    trace.Period("Values taken from cell D2 across")
        
    unsure = tab.excel_ref('A1')
    trace.Dimension_name_unsure("Values taken from cell A1")
        
    unit = tab.excel_ref('X1')
    trace.Unit("Value taken from cell X1")
        
    observations = period.fill(DOWN).is_not_blank() 
    dimensions = [
        HDim(period, 'Period', DIRECTLY, ABOVE),
        HDim(area_type, 'Area Type', DIRECTLY, LEFT),
        HDim(geo_code, 'Geo Code', DIRECTLY, LEFT),
        HDim(area_name, 'Area Name', DIRECTLY, LEFT),
        HDim(unit, 'Unit', CLOSEST, ABOVE),
        HDim(unsure, 'Dimension name unsure?', CLOSEST, LEFT),
        ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    #trace.with_preview(tidy_sheet)
    savepreviewhtml(tidy_sheet, fname= tab.name + "PREVIEW.html") 
    trace.store("combined_dataframe", tidy_sheet.topandas())
        
        
        
# -

#post processing 
df = trace.combine_and_trace(datasetTitle, "combined_dataframe")
df.rename(columns={'OBS' : 'Value', 'DATAMARKER' : 'Marker'}, inplace=True)
df = df.replace({'Period' : {'20183' : '2018',}})
df['Period'] = df['Period'].astype(str).replace('\.0', '', regex=True)
df['Period'] = "year/" + df['Period']
df = df.replace({'Marker' : {'-' : 'not-applicable',}})
df["Dimension name unsure?"] = df["Dimension name unsure?"].str.split(':').str[2]
df["Dimension name unsure?"] = df["Dimension name unsure?"].str.lstrip()

df['Dimension name unsure?'].unique()

df['Unit'].unique()

tidy = df[["Period", "Area Type", "Area Name", "Geo Code", "Dimension name unsure?", "Value", "Marker", "Unit"]]

#output stage one transform for DM 
csvName = 'stage_one_transform.csv'
out = Path('out')
out.mkdir(exist_ok=True)
tidy.drop_duplicates().to_csv(out / csvName, index = False)
tidy

trace.render()
