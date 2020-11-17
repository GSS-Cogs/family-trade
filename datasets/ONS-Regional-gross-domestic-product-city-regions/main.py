# +
from gssutils import * 
import json 
import numpy as np 
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

# - Tables 1 - 5 : how the calculation of GDP in current prices in tables
# - Tables 6 - 7 : calculate GDP per head 
# - Table 8 : shows the implied deflators from the GVA(B) dataset
# - Table 9 - 10 : table 8 is used to remove the effect of price inflation and derive volume measures of regional GDP shown in tables 9 and 10.
# - Table 11 : shows volume GDP per head
# - Table 12 - 13 - show the annual growth rates of volume GDP and volume GDP per head
#

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
        HDim(period, 'Year', DIRECTLY, ABOVE),
        HDim(area_type, 'Area Type', DIRECTLY, LEFT),
        HDim(geo_code, 'Geography Code', DIRECTLY, LEFT),
        HDim(area_name, 'Area Name', DIRECTLY, LEFT),
        HDim(unit, 'Unit', CLOSEST, ABOVE),
        HDim(unsure, 'GDP Estimate Type', CLOSEST, LEFT),
        ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    trace.with_preview(tidy_sheet)
    savepreviewhtml(tidy_sheet, fname= tab.name + "PREVIEW.html") 
    trace.store("combined_dataframe", tidy_sheet.topandas())


city_regions = trace.combine_and_trace(datasetTitle, "combined_dataframe")
#city_regions = city_regions.drop_duplicates()

# Transformation of Imports file to be joined to ONS-Regional-gross-domestic-product-enterprise-regions 

# +
""
#changing landing page to ONS-Regional-gross-domestic-product-enterprise-regions  URL
with open("info.json", "r") as read_file:
    data = json.load(read_file)
    print("URL: ", data["landingPage"] )
    data["landingPage"] = "https://www.ons.gov.uk/economy/grossdomesticproductgdp/datasets/regionalgrossdomesticproductenterpriseregions" 
    print("URL changed to: ", data["landingPage"] )

with open("info.json", "w") as jsonFile:
    json.dump(data, jsonFile)
# -

info = json.load(open('info.json')) 
scraper = Scraper(seed="info.json")   
scraper 

#Distribution 
tabs = { tab.name: tab for tab in scraper.distributions[0].as_databaker() }

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
        HDim(period, 'Year', DIRECTLY, ABOVE),
        HDim(area_type, 'Area Type', DIRECTLY, LEFT),
        HDim(geo_code, 'Geography Code', DIRECTLY, LEFT),
        HDim(area_name, 'Area Name', DIRECTLY, LEFT),
        HDim(unit, 'Unit', CLOSEST, ABOVE),
        HDim(unsure, 'GDP Estimate Type', CLOSEST, LEFT),
        ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    trace.with_preview(tidy_sheet)
    savepreviewhtml(tidy_sheet, fname= tab.name + "PREVIEW.html") 
    trace.store("combined_dataframe_2", tidy_sheet.topandas())

enterprise_regions = trace.combine_and_trace(datasetTitle, "combined_dataframe_2")
#enterprise_regions = enterprise_regions.drop_duplicates()

""
#concatenating all the distributions togther - Easy to output all data togther once multiple measure types can be handeld
merged_data = pd.concat([city_regions, enterprise_regions], ignore_index=True)

merged_data['Area Type'].unique()

# +
#post processing 
merged_data.rename(columns={'OBS' : 'Value', 'DATAMARKER' : 'Marker'}, inplace=True)
merged_data = merged_data.replace({'Year' : {'20183' : '2018',}})
merged_data['Year'] = merged_data['Year'].astype(str).replace('\.0', '', regex=True)
merged_data['Year'] = "year/" + merged_data['Year']

#Greater London Authority = E61000001
#### merged_data = merged_data.replace({'Geography Code' : {'Not available' : 'E61000001',}})
#city-region' and 'local-authority'
merged_data = merged_data.replace({'Area Type' : {'CR' : 'city-region', 'LA' : 'local-authority', 'LEP' : 'local-enterprise-partnerships', 'ER' : 'enterprise-region'}})
merged_data = merged_data.replace({'Marker' : {'-' : 'not-applicable',}})

del merged_data['Geography Code']

merged_data["Table Number for joining"] = merged_data["GDP Estimate Type"].str.split(':').str[0]
merged_data["GDP Estimate Type"] = merged_data["GDP Estimate Type"].str.split(':').str[2]
merged_data["GDP Estimate Type"] = merged_data["GDP Estimate Type"].str.lstrip()

merged_data = merged_data.replace({'GDP Estimate Type' : {'Gross Value Added (Balanced)1,2 at current basic prices' : 'Gross Value Added (Balanced) at current basic prices',
                                       'Value Added Tax (VAT) on products1,2' : 'Value Added Tax (VAT) on products',
                                        'Other taxes on products1,2' : 'Other taxes on products',
                                        'Subsidies on products1,2' : 'Subsidies on products',
                                        'Gross Domestic Product (GDP)1,2 at current market prices' : 'Gross Domestic Product (GDP) at current market prices',
                                        'Total resident population numbers1' : 'Total resident population numbers',
                                        'Gross Domestic Product (GDP)1 per head2 at current market prices' : 'Gross Domestic Product (GDP) per head at current market prices',
                                        'Whole economy GVA implied deflators1,2' : 'Whole economy GVA implied deflators',
                                        'Gross Domestic Product (GDP)1 chained volume measures (CVM)2 index' : 'Gross Domestic Product (GDP) chained volume measures (CVM) index',
                                        'Gross Domestic Product (GDP)1 chained volume measures (CVM)2 in 2016 money value' : 'Gross Domestic Product (GDP) chained volume measures (CVM) in 2016 money value',
                                        'Gross Domestic Product (GDP)1 chained volume measures (CVM) per head2' : 'Gross Domestic Product (GDP) chained volume measures (CVM) per head',
                                        'Gross Domestic Product (GDP)1 chained volume measures (CVM)2 annual growth rates' : 'Gross Domestic Product (GDP) chained volume measures (CVM) annual growth rates',
                                        'Gross Domestic Product (GDP)1 chained volume measures (CVM) per head2 annual growth rates' : 'Gross Domestic Product (GDP) chained volume measures (CVM) per head annual growth rates'
                                       }})
merged_data['GDP Estimate Type'] = merged_data['GDP Estimate Type'].map(lambda x: pathify(x))
merged_data['Area Name'] = merged_data['Area Name'].map(lambda x: pathify(x))
#2018 = provisional
f1=((merged_data['Year'] =='year/2018'))
merged_data.loc[f1,'Marker'] = 'provisional'
merged_data = merged_data.replace(np.nan, '', regex=True)
merged_data
# -



merged_data = merged_data.replace({'Table Number for joining' : { 'Table 1' : 'Join 1', 'Table 2' : 'Join 1', 'Table 3' : 'Join 1', 'Table 4' : 'Join 1', 'Table 5' : 'Join 1',
                                                     'Table 6' : 'Join 2',
                                                     'Table 7' : 'Join 3',
                                                     'Table 8' : 'Join 4',
                                                     'Table 9' : 'Join 5',
                                                     'Table 10' : 'Join 6',
                                                     'Table 11' : 'Join 7',
                                                     'Table 12' : 'Join 8', 'Table 13' : 'Join 8',  }})
merged_data['Table Number for joining'].unique()


merged_data['Marker'].unique()

#create unique list of Unit's (children, familes)
unique_joins = merged_data['Table Number for joining'].unique()
print(unique_joins)

#create a data frame dictionary to store data frames
DataFrameDict = {elem : pd.DataFrame for elem in unique_joins}

#creating the sperate datasets from the dict
for key in DataFrameDict.keys():
    DataFrameDict[key] = merged_data[:][merged_data['Table Number for joining'] == key]
join_1_df = DataFrameDict['Join 1']
join_2_df = DataFrameDict['Join 2']
join_3_df = DataFrameDict['Join 3']
join_4_df = DataFrameDict['Join 4']
join_5_df = DataFrameDict['Join 5']
join_6_df = DataFrameDict['Join 6']
join_7_df = DataFrameDict['Join 7']
join_8_df = DataFrameDict['Join 8']


# +
#checking each only has one unit and correct value datatype
print('Join 1 unit ', join_1_df['Unit'].unique())
join_1_df['Value'] = join_1_df['Value'].astype(int)
#join_1_df.dtypes

print('Join 2 unit ', join_2_df['Unit'].unique())
join_2_df['Value'] = join_2_df['Value'].astype(int)
#join_2_df.dtypes

print('Join 3 unit ', join_3_df['Unit'].unique())
join_3_df['Value'] = join_3_df['Value'].astype(int)
#join_3_df.dtypes

print('Join 4 unit ', join_4_df['Unit'].unique())
join_4_df['Value'] = join_4_df['Value'].astype(float)
#join_4_df.dtypes

print('Join 5 unit ', join_5_df['Unit'].unique())
join_5_df['Value'] = join_5_df['Value'].astype(float)
#join_5_df.dtypes

print('Join 6 unit ', join_6_df['Unit'].unique())
join_6_df['Value'] = join_6_df['Value'].astype(int)
#join_6_df.dtypes

print('Join 7 unit ', join_7_df['Unit'].unique())
join_7_df['Value'] = join_7_df['Value'].astype(int)
#join_7_df.dtypes

print('Join 8 unit ', join_8_df['Unit'].unique())
join_8_df['Value']  = pd.to_numeric(join_8_df.Value, errors='coerce')
#join_8_df.dtypes

# +

# Output filenames
fn = ['cp-observations.csv','pop-observations.csv', 'cmp-observations.csv', 'deflate-observations.csv', 'cvmindex-observations.csv', 'cvmmoney-observations.csv', 'cvmhead-observations.csv', 'cvmrate-observations.csv']
# Comments
co = [
    'Annual estimates of balanced UK regional Gross Domestic Product (GDP). Current price estimates for combined authorities and city regions.',
    'Annual estimates of balanced UK regional Gross Domestic Product (GDP). Total resident population numbers for combined authorities and city regions.',
    'Annual estimates of balanced UK regional Gross Domestic Product (GDP). CGDP per Head at Current Market Prices for combined authorities and city regions..',
    'Annual estimates of balanced UK regional Gross Domestic Product (GDP). Whole Economy GVA Implied Deflators for combined authorities and city regions.',
    'Annual estimates of balanced UK regional Gross Domestic Product (GDP). Chained Volume Measures index for combined authorities and city regions.',
    'Annual estimates of balanced UK regional Gross Domestic Product (GDP). Chained Volume Measures in 2016 money value for combined authorities and city regions.',
    ' Annual estimates of balanced UK regional Gross Domestic Product (GDP). Chained Volume Measures per head for combined authorities and city regions.',
    'Annual estimates of balanced UK regional Gross Domestic Product (GDP). Chained Volume Measures annual growth rates for combined authorities and city regions.'
]
# Title
ti = [
    'Regional Gross Domestic Product city regions - GDP in Current Prices ',
    'Regional Gross Domestic Product city regions - Total resident Population numbers',
    'Regional Gross Domestic Product city regions - GDP per Head at Current Market Prices',
    'Regional Gross Domestic Product city regions - Whole Economy GVA Implied Deflators',
    'Regional Gross Domestic Product city regions - Chained Volume Measures index',
    'Regional Gross Domestic Product city regions - Chained Volume Measures in 2016 money value',
    'Regional Gross Domestic Product city regions - Chained Volume Measures per head',
    'Regional Gross Domestic Product city regions - Chained Volume Measures annual growth rates'
    
    
]
# Paths
pa = ['/cp', '/pop', '/cmp', '/deflate', '/cvmindex', '/cvmmoney', '/cvmhead', '/cvmrate']

# Description
de = """
These tables are part of the regional economic activity by Gross Domestic Product release

The data herein are based on the balanced measure of regional gross value added (GVA(B)), which combines estimates produced using the income and production approaches to create a single best estimate of GVA for each industry in each region.
We have now included the effects of taxes and subsidies on products to derive annual estimates of regional GDP for the first time. GDP is equivalent to GVA plus Value Added Tax (VAT) plus other taxes on products less subsidies on products.
This is part of several datasets that give the full picture of Gross Domestic Product
Current Price data
Regional Gross Domestic Product city regions - GDP in Current Prices
Gross Value Added (Balanced) at current basic prices
 Value Added Tax (VAT) on products
 Other taxes on products
 Subsidies on products
 Gross Domestic Product (GDP) at current market prices

Used to calculate GDP per head:
Regional Gross Domestic Product city regions - Total resident Population numbers
Regional Gross Domestic Product city regions - GDP per Head at Current Market Prices

The implied deflators from the GVA(B) dataset:
Regional Gross Domestic Product city regions - Whole Economy GVA Implied Deflators

The deflators are used to remove the effect of price inflation and derive volume measures of regional GDP:
Regional Gross Domestic Product city regions - Chained Volume Measures index
 Regional Gross Domestic Product city regions - Chained Volume Measures in 2016 money value

Volume GDP per head is given in:
Regional Gross Domestic Product city regions - Chained Volume Measures per head

And the annual growth rates of volume GDP and volume GDP per head are given in:
Regional Gross Domestic Product city regions - Chained Volume Measures annual growth rates
Snnual growth rates
Per head annual growth rates
 
All calculations are carried out using unrounded data.

Workplace-based estimates are allocated to the region in which the economic activity takes place. 
Components may not sum to totals as a result of rounding.
Implied deflators are derived from whole economy current price and chained volume measures of GVA. 
Use of implied deflators duplicates the effect of chain-linking, though technically this results in constant price volume measures.
Components will not sum to totals since chain-linking produces non-additive volume estimates.
"""
# -

""
#changing measure to cp,  unit to gbp-million and value dtype to integer for join1 output 
with open("info.json", "r") as read_file:
    data = json.load(read_file)
    print("Unit: ", data["transform"]["columns"]["Value"]["unit"] )
    data["transform"]["columns"]["Value"]["unit"] = "http://gss-data.org.uk/def/concept/measurement-units/gbp-million" 
    print("Unit changed to: ", data["transform"]["columns"]["Value"]["unit"] )
    
    print("Value measure type: ", data["transform"]["columns"]["Value"]["measure"] )
    data["transform"]["columns"]["Value"]["measure"] = "http://gss-data.org.uk/def/measure/current-prices"
    print("Value measure changed to: ", data["transform"]["columns"]["Value"]["measure"] )
    
    print("Value dtype: ", data["transform"]["columns"]["Value"]["datatype"] )
    data["transform"]["columns"]["Value"]["datatype"] = "integer"
    print("Value dtype changed to: ", data["transform"]["columns"]["Value"]["datatype"] )

#Join 1 : Measure: cp, Unit: gbp-million, Datatype: integer, dataset_path: dataset_path + /cp
join_1_df = join_1_df[["Year", "Area Type", 'Area Name', "GDP Estimate Type", "Value", "Marker"]]
try:
    i = 0
    csvName = fn[i]
    out = Path('out')
    out.mkdir(exist_ok=True)
    join_1_df.drop_duplicates().to_csv(out / csvName, index = False)
    #join_1_df.drop_duplicates().to_csv(out / (csvName + '.gz'), index = False, compression='gzip')
    
    scraper.dataset.family = 'trade'
    scraper.dataset.description = scraper.dataset.description + '\n' + de[i]
    scraper.dataset.comment = co[i]
    scraper.dataset.title = ti[i]

    dataset_path = pathify(os.environ.get('JOB_NAME', f'gss_data/{scraper.dataset.family}/' + Path(os.getcwd()).name)).lower() + pa[i]
    scraper.set_base_uri('http://gss-data.org.uk')
    scraper.set_dataset_id(dataset_path)

    csvw_transform = CSVWMapping()
    csvw_transform.set_csv(out / csvName)
    csvw_transform.set_mapping(data)
    csvw_transform.set_dataset_uri(urljoin(scraper._base_uri, f'data/{scraper._dataset_id}'))
    csvw_transform.write(out / f'{csvName}-metadata.json')

    with open(out / f'{csvName}-metadata.trig', 'wb') as metadata:
        metadata.write(scraper.generate_trig())
except Exception as s:
    print(str(s))

""
#changing measure to count, unit to persons and value dtype to integer for join2 output 
with open("info.json", "r") as read_file:
    data = json.load(read_file)
    print("Unit: ", data["transform"]["columns"]["Value"]["unit"] )
    data["transform"]["columns"]["Value"]["unit"] = "http://gss-data.org.uk/def/concept/measurement-units/persons" 
    print("Unit changed to: ", data["transform"]["columns"]["Value"]["unit"] )
    
    print("Value measure type: ", data["transform"]["columns"]["Value"]["measure"] )
    data["transform"]["columns"]["Value"]["measure"] = "http://gss-data.org.uk/def/measure/count"
    print("Value measure changed to: ", data["transform"]["columns"]["Value"]["measure"] )
    
    print("Value dtype: ", data["transform"]["columns"]["Value"]["datatype"] )
    data["transform"]["columns"]["Value"]["datatype"] = "integer"
    print("Value dtype changed to: ", data["transform"]["columns"]["Value"]["datatype"] )

#Join 2 Measure: count, Unit: persons, Datatype: integer, dataset_path: dataset_path + /pop
join_2_df = join_2_df[["Year", "Area Type", "Area Name", "GDP Estimate Type", "Value", "Marker"]]
try:
    i = 1
    csvName = fn[i]
    out = Path('out')
    out.mkdir(exist_ok=True)
    join_2_df.drop_duplicates().to_csv(out / csvName, index = False)
    #join_2_df.drop_duplicates().to_csv(out / (csvName + '.gz'), index = False, compression='gzip')
    
    scraper.dataset.family = 'trade'
    scraper.dataset.description = scraper.dataset.description + '\n' + de[i]
    scraper.dataset.comment = co[i]
    scraper.dataset.title = ti[i]

    dataset_path = pathify(os.environ.get('JOB_NAME', f'gss_data/{scraper.dataset.family}/' + Path(os.getcwd()).name)).lower() + pa[i]
    scraper.set_base_uri('http://gss-data.org.uk')
    scraper.set_dataset_id(dataset_path)

    csvw_transform = CSVWMapping()
    csvw_transform.set_csv(out / csvName)
    csvw_transform.set_mapping(data)
    csvw_transform.set_dataset_uri(urljoin(scraper._base_uri, f'data/{scraper._dataset_id}'))
    csvw_transform.write(out / f'{csvName}-metadata.json')

    with open(out / f'{csvName}-metadata.trig', 'wb') as metadata:
        metadata.write(scraper.generate_trig())
except Exception as s:
    print(str(s))

""
#changing measure to amp, unit to gbp and value dtype to integer for join3 output 
with open("info.json", "r") as read_file:
    data = json.load(read_file)
    print("Unit: ", data["transform"]["columns"]["Value"]["unit"] )
    data["transform"]["columns"]["Value"]["unit"] = "http://gss-data.org.uk/def/concept/measurement-units/gbp" 
    print("Unit changed to: ", data["transform"]["columns"]["Value"]["unit"] )
    
    print("Value measure type: ", data["transform"]["columns"]["Value"]["measure"] )
    data["transform"]["columns"]["Value"]["measure"] = "http://gss-data.org.uk/def/measure/amp"
    print("Value measure changed to: ", data["transform"]["columns"]["Value"]["measure"] )
    
    print("Value dtype: ", data["transform"]["columns"]["Value"]["datatype"] )
    data["transform"]["columns"]["Value"]["datatype"] = "integer"
    print("Value dtype changed to: ", data["transform"]["columns"]["Value"]["datatype"] )

#Join 3 : Measure: amp, Unit: gbp, Datatype: integer, dataset_path: dataset_path + /cmp
join_3_df = join_3_df[["Year", "Area Type", "Area Name", "GDP Estimate Type", "Value", "Marker"]]
try:
    i = 2
    csvName = fn[i]
    out = Path('out')
    out.mkdir(exist_ok=True)
    join_3_df.drop_duplicates().to_csv(out / csvName, index = False)
    #join_3_df.drop_duplicates().to_csv(out / (csvName + '.gz'), index = False, compression='gzip')
    
    scraper.dataset.family = 'trade'
    scraper.dataset.description = scraper.dataset.description + '\n' + de[i]
    scraper.dataset.comment = co[i]
    scraper.dataset.title = ti[i]

    dataset_path = pathify(os.environ.get('JOB_NAME', f'gss_data/{scraper.dataset.family}/' + Path(os.getcwd()).name)).lower() + pa[i]
    scraper.set_base_uri('http://gss-data.org.uk')
    scraper.set_dataset_id(dataset_path)

    csvw_transform = CSVWMapping()
    csvw_transform.set_csv(out / csvName)
    csvw_transform.set_mapping(data)
    csvw_transform.set_dataset_uri(urljoin(scraper._base_uri, f'data/{scraper._dataset_id}'))
    csvw_transform.write(out / f'{csvName}-metadata.json')

    with open(out / f'{csvName}-metadata.trig', 'wb') as metadata:
        metadata.write(scraper.generate_trig())
except Exception as s:
    print(str(s))

""
#changing measure to gva, unit to deflators and value dtype to double for join4 output 
with open("info.json", "r") as read_file:
    data = json.load(read_file)
    print("Unit: ", data["transform"]["columns"]["Value"]["unit"] )
    data["transform"]["columns"]["Value"]["unit"] = "http://gss-data.org.uk/def/concept/measurement-units/deflators" 
    print("Unit changed to: ", data["transform"]["columns"]["Value"]["unit"] )
    
    print("Value measure type: ", data["transform"]["columns"]["Value"]["measure"] )
    data["transform"]["columns"]["Value"]["measure"] = "http://gss-data.org.uk/def/measure/gva"
    print("Value measure changed to: ", data["transform"]["columns"]["Value"]["measure"] )
    
    print("Value dtype: ", data["transform"]["columns"]["Value"]["datatype"] )
    data["transform"]["columns"]["Value"]["datatype"] = "float"
    print("Value dtype changed to: ", data["transform"]["columns"]["Value"]["datatype"] )

# +
#Join 4 : Measure: gva, Unit: deflators, Datatype: double, dataset_path: dataset_path + /deflate

join_4_df = join_4_df[["Year", "Area Type", "Area Name", "GDP Estimate Type", "Value", "Marker"]]
try:
    i = 3
    csvName = fn[i]
    out = Path('out')
    out.mkdir(exist_ok=True)
    join_4_df.drop_duplicates().to_csv(out / csvName, index = False)
    #join_4_df.drop_duplicates().to_csv(out / (csvName + '.gz'), index = False, compression='gzip')
    
    scraper.dataset.family = 'trade'
    scraper.dataset.description = scraper.dataset.description + '\n' + de[i]
    scraper.dataset.comment = co[i]
    scraper.dataset.title = ti[i]

    dataset_path = pathify(os.environ.get('JOB_NAME', f'gss_data/{scraper.dataset.family}/' + Path(os.getcwd()).name)).lower() + pa[i]
    scraper.set_base_uri('http://gss-data.org.uk')
    scraper.set_dataset_id(dataset_path)

    csvw_transform = CSVWMapping()
    csvw_transform.set_csv(out / csvName)
    csvw_transform.set_mapping(data)
    csvw_transform.set_dataset_uri(urljoin(scraper._base_uri, f'data/{scraper._dataset_id}'))
    csvw_transform.write(out / f'{csvName}-metadata.json')

    with open(out / f'{csvName}-metadata.trig', 'wb') as metadata:
        metadata.write(scraper.generate_trig())
except Exception as s:
    print(str(s))
# -

""
#changing measure to cvm, unit to index and value dtype to double for join5 output 
with open("info.json", "r") as read_file:
    data = json.load(read_file)
    print("Unit: ", data["transform"]["columns"]["Value"]["unit"] )
    data["transform"]["columns"]["Value"]["unit"] = "http://gss-data.org.uk/def/concept/measurement-units/index" 
    print("Unit changed to: ", data["transform"]["columns"]["Value"]["unit"] )
    
    print("Value measure type: ", data["transform"]["columns"]["Value"]["measure"] )
    data["transform"]["columns"]["Value"]["measure"] = "http://gss-data.org.uk/def/measure/cvm"
    print("Value measure changed to: ", data["transform"]["columns"]["Value"]["measure"] )
    
    print("Value dtype: ", data["transform"]["columns"]["Value"]["datatype"] )
    data["transform"]["columns"]["Value"]["datatype"] = "float"
    print("Value dtype changed to: ", data["transform"]["columns"]["Value"]["datatype"] )

# +
#Join 5 : Measure: cvm, Unit: index, Datatype: double, dataset_path: dataset_path + /cvmindex

join_5_df = join_5_df[["Year", "Area Type", "Area Name", "GDP Estimate Type", "Value", "Marker"]]
try:
    i = 4
    csvName = fn[i]
    out = Path('out')
    out.mkdir(exist_ok=True)
    join_5_df.drop_duplicates().to_csv(out / csvName, index = False)
    #join_5_df.drop_duplicates().to_csv(out / (csvName + '.gz'), index = False, compression='gzip')
    
    scraper.dataset.family = 'trade'
    scraper.dataset.description = scraper.dataset.description + '\n' + de[i]
    scraper.dataset.comment = co[i]
    scraper.dataset.title = ti[i]

    dataset_path = pathify(os.environ.get('JOB_NAME', f'gss_data/{scraper.dataset.family}/' + Path(os.getcwd()).name)).lower() + pa[i]
    scraper.set_base_uri('http://gss-data.org.uk')
    scraper.set_dataset_id(dataset_path)

    csvw_transform = CSVWMapping()
    csvw_transform.set_csv(out / csvName)
    csvw_transform.set_mapping(data)
    csvw_transform.set_dataset_uri(urljoin(scraper._base_uri, f'data/{scraper._dataset_id}'))
    csvw_transform.write(out / f'{csvName}-metadata.json')

    with open(out / f'{csvName}-metadata.trig', 'wb') as metadata:
        metadata.write(scraper.generate_trig())
except Exception as s:
    print(str(s))
# -

""
#changing measure to cvm, unit to gbp-million and value dtype to integer for join6 output 
with open("info.json", "r") as read_file:
    data = json.load(read_file)
    print("Unit: ", data["transform"]["columns"]["Value"]["unit"] )
    data["transform"]["columns"]["Value"]["unit"] = "http://gss-data.org.uk/def/concept/measurement-units/gbp-million" 
    print("Unit changed to: ", data["transform"]["columns"]["Value"]["unit"] )
    
    print("Value measure type: ", data["transform"]["columns"]["Value"]["measure"] )
    data["transform"]["columns"]["Value"]["measure"] = "http://gss-data.org.uk/def/measure/cvm"
    print("Value measure changed to: ", data["transform"]["columns"]["Value"]["measure"] )
    
    print("Value dtype: ", data["transform"]["columns"]["Value"]["datatype"] )
    data["transform"]["columns"]["Value"]["datatype"] = "integer"
    print("Value dtype changed to: ", data["transform"]["columns"]["Value"]["datatype"] )

# +
#Join 6 : Measure: cvm, Unit: index, Datatype: double, dataset_path: dataset_path + /cvmindex

join_6_df = join_6_df[["Year", "Area Type", "Area Name", "GDP Estimate Type", "Value", "Marker"]]
try:
    i = 5
    csvName = fn[i]
    out = Path('out')
    out.mkdir(exist_ok=True)
    join_6_df.drop_duplicates().to_csv(out / csvName, index = False)
    #join_6_df.drop_duplicates().to_csv(out / (csvName + '.gz'), index = False, compression='gzip')
    
    scraper.dataset.family = 'trade'
    scraper.dataset.description = scraper.dataset.description + '\n' + de[i]
    scraper.dataset.comment = co[i]
    scraper.dataset.title = ti[i]

    dataset_path = pathify(os.environ.get('JOB_NAME', f'gss_data/{scraper.dataset.family}/' + Path(os.getcwd()).name)).lower() + pa[i]
    scraper.set_base_uri('http://gss-data.org.uk')
    scraper.set_dataset_id(dataset_path)

    csvw_transform = CSVWMapping()
    csvw_transform.set_csv(out / csvName)
    csvw_transform.set_mapping(data)
    csvw_transform.set_dataset_uri(urljoin(scraper._base_uri, f'data/{scraper._dataset_id}'))
    csvw_transform.write(out / f'{csvName}-metadata.json')

    with open(out / f'{csvName}-metadata.trig', 'wb') as metadata:
        metadata.write(scraper.generate_trig())
except Exception as s:
    print(str(s))
# -

""
#changing measure to cvm, unit to gbp and value dtype to integer for join7 output 
with open("info.json", "r") as read_file:
    data = json.load(read_file)
    print("Unit: ", data["transform"]["columns"]["Value"]["unit"] )
    data["transform"]["columns"]["Value"]["unit"] = "http://gss-data.org.uk/def/concept/measurement-units/gbp" 
    print("Unit changed to: ", data["transform"]["columns"]["Value"]["unit"] )
    
    print("Value measure type: ", data["transform"]["columns"]["Value"]["measure"] )
    data["transform"]["columns"]["Value"]["measure"] = "http://gss-data.org.uk/def/measure/cvm"
    print("Value measure changed to: ", data["transform"]["columns"]["Value"]["measure"] )
    
    print("Value dtype: ", data["transform"]["columns"]["Value"]["datatype"] )
    data["transform"]["columns"]["Value"]["datatype"] = "integer"
    print("Value dtype changed to: ", data["transform"]["columns"]["Value"]["datatype"] )

# +
#Join 7 : Measure: cvm, Unit: gbp, Datatype: integer, dataset_path: dataset_path + /cvmhead

join_7_df = join_7_df[["Year", "Area Type", "Area Name", "GDP Estimate Type", "Value", "Marker"]]
try:
    i = 6
    csvName = fn[i]
    out = Path('out')
    out.mkdir(exist_ok=True)
    join_7_df.drop_duplicates().to_csv(out / csvName, index = False)
    #join_7_df.drop_duplicates().to_csv(out / (csvName + '.gz'), index = False, compression='gzip')
    
    scraper.dataset.family = 'trade'
    scraper.dataset.description = scraper.dataset.description + '\n' + de[i]
    scraper.dataset.comment = co[i]
    scraper.dataset.title = ti[i]

    dataset_path = pathify(os.environ.get('JOB_NAME', f'gss_data/{scraper.dataset.family}/' + Path(os.getcwd()).name)).lower() + pa[i]
    scraper.set_base_uri('http://gss-data.org.uk')
    scraper.set_dataset_id(dataset_path)

    csvw_transform = CSVWMapping()
    csvw_transform.set_csv(out / csvName)
    csvw_transform.set_mapping(data)
    csvw_transform.set_dataset_uri(urljoin(scraper._base_uri, f'data/{scraper._dataset_id}'))
    csvw_transform.write(out / f'{csvName}-metadata.json')

    with open(out / f'{csvName}-metadata.trig', 'wb') as metadata:
        metadata.write(scraper.generate_trig())
except Exception as s:
    print(str(s))
# -

""
#changing measure to cvm, unit to rate and value dtype to double for join8 output 
with open("info.json", "r") as read_file:
    data = json.load(read_file)
    print("Unit: ", data["transform"]["columns"]["Value"]["unit"] )
    data["transform"]["columns"]["Value"]["unit"] = "http://gss-data.org.uk/def/concept/measurement-units/rate" 
    print("Unit changed to: ", data["transform"]["columns"]["Value"]["unit"] )
    
    print("Value measure type: ", data["transform"]["columns"]["Value"]["measure"] )
    data["transform"]["columns"]["Value"]["measure"] = "http://gss-data.org.uk/def/measure/cvm"
    print("Value measure changed to: ", data["transform"]["columns"]["Value"]["measure"] )
    
    print("Value dtype: ", data["transform"]["columns"]["Value"]["datatype"] )
    data["transform"]["columns"]["Value"]["datatype"] = "float"
    print("Value dtype changed to: ", data["transform"]["columns"]["Value"]["datatype"] )

# +
#Join 8 : Measure: cvm, Unit: gbp, Datatype: integer, dataset_path: dataset_path + /cvmhead

join_8_df = join_8_df[["Year", "Area Type", "Area Name", "GDP Estimate Type", "Value", "Marker"]]
try:
    i = 7
    csvName = fn[i]
    out = Path('out')
    out.mkdir(exist_ok=True)
    join_8_df.drop_duplicates().to_csv(out / csvName, index = False)
    #join_8_df.drop_duplicates().to_csv(out / (csvName + '.gz'), index = False, compression='gzip')
    
    scraper.dataset.family = 'trade'
    scraper.dataset.description = scraper.dataset.description + '\n' + de[i]
    scraper.dataset.comment = co[i]
    scraper.dataset.title = ti[i]

    dataset_path = pathify(os.environ.get('JOB_NAME', f'gss_data/{scraper.dataset.family}/' + Path(os.getcwd()).name)).lower() + pa[i]
    scraper.set_base_uri('http://gss-data.org.uk')
    scraper.set_dataset_id(dataset_path)

    csvw_transform = CSVWMapping()
    csvw_transform.set_csv(out / csvName)
    csvw_transform.set_mapping(data)
    csvw_transform.set_dataset_uri(urljoin(scraper._base_uri, f'data/{scraper._dataset_id}'))
    csvw_transform.write(out / f'{csvName}-metadata.json')

    with open(out / f'{csvName}-metadata.trig', 'wb') as metadata:
        metadata.write(scraper.generate_trig())
except Exception as s:
    print(str(s))

# +
""
#changing landing page to ONS-Regional-gross-domestic-product-enterprise-regions  URL
with open("info.json", "r") as read_file:
    data = json.load(read_file)
    print("URL: ", data["landingPage"] )
    data["landingPage"] = "https://www.ons.gov.uk/economy/grossdomesticproductgdp/datasets/regionalgrossdomesticproductcityregions" 
    print("URL changed to: ", data["landingPage"] )

with open("info.json", "w") as jsonFile:
    json.dump(data, jsonFile)
# -
trace.render()
