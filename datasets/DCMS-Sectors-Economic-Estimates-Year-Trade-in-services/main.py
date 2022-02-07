# -*- coding: utf-8 -*-
# +
from gssutils import * 
import json 
from urllib.parse import urljoin

df = pd.DataFrame()
# -

info = json.load(open('dcms_sectors_economic_estimates-info.json')) 
scraper = Scraper(seed="dcms_sectors_economic_estimates-info.json")   
scraper

# +
#Distribution 2: Imports and Exports of services by sector 
# tabs = { tab.name: tab for tab in scraper.distribution(title = lambda x: "Imports and Exports" in x).as_databaker() }
# list(tabs)
# -

distribution = scraper.distribution(title = lambda x: "Imports and Exports" in x)
distribution

path = distribution.downloadURL

df1 = pd.read_excel(path, "Imports")

df1

# +
# df1 = df1.drop(labels = 0, axis = 0)
# -

df1.head()

header_row = 1
df1.columns = df1.iloc[header_row]


df1 = df1.drop(header_row)
df1 = df1.reset_index(drop = True)

df1

df1.columns = pd.MultiIndex.from_arrays([df1.columns, df1.iloc[1].values])
df1 = df1.iloc[2:]

df1

df1.head(0)

df1.columns.nlevels
df1.index.nlevels

# +
# stop
# -

# df1.index.nlevels 
df1.columns.nlevels
isinstance(df1.index, pd.MultiIndex)
# isinstance(df1.keys(), pd.core.indexes.multi.MultiIndex)



df2 = df1.T

df2.head()

# +
# needed_vars = ["DCMS Sectors (exc Tourism and Civil Society)", 
# "Creative Industries sub-sectors", 
# "Digital Sector sub-sectors", 
# "Culture Sector sub-sector", "All UK service imports (2018 Pink Book estimate)"]
# df2.melt(id_vars=["Country"])

# +
# header_row = 0
# df2.columns = df2.iloc[header_row]
# -

df2.index.names = ['sector', "sub-sector"]

df2.head()

header_row = 0
df2.columns = df2.iloc[header_row]

import numpy as np
df3 = df2.drop((np.nan, 'Country'))

df3.head()

# +
# df3 = df3.to_frame()

# +
# df3 = df3.set_index((["sector", "sub-sector"])
# .stack()
# .reset_index(name="Value")
# .rename(columns={"level_2":"Country"}))
# -

df3 = df3.stack()

df3

df3.index.nlevels

df3 = df3.to_frame()

type(df3)

df3

df3.head()

# +
# print(df3)

# +
# df3 = df3.set_index("sector")
# -

df3.head()

df3.columns.nlevels

for col in df3.columns:
    if col == 0:
        print(col)

df3.head()

df3 = df3.reset_index()

df3

df3.head(0)

df3 = df3.rename(columns = {(np.nan, 'Country'):"country", 0:"value"})

list(df3)

df3

type(df3)

df3

df3.tail(100)

df3.head(0)

df3["sector"].unique()

df3["sub-sector"].unique()

for val in df3["sub-sector"]:
    df3["sector"]

# +
# df3 = df3.groupby(["sector", "sub-sector", "country"])["value"]

# +
# df3 = df3.reindex(df3.index, method = "ffill", limit = 1)
# -

df3.index.values

next(df3.iterrows())

df3.head(300)

df3.head(150)

for df3.column in df3:
    print(df3.column)


df3 = df3.fillna(method = "ffill")

df3.loc[df3["sub-sector"] == "All_Imports", "sector"]

df3.head(100)

# +
# df3.loc[df3["sub-sector"] == "Digital Sector", "DCMS total"]
# -

df3.head(200)

# +
# df3 = df3.set_index(["sector", "sub-sector"])
# -

df3.iloc[2065]

for col in df3.columns:
    print(col)

# +
# (df3.shape) 
# (df3.index.nlevels)
# (df3.columns.nlevels)
# type(reset_df3)
# df3.set_index(["sector", "sub-sector"]
type(df3)


# -

df3 = df3.to_frame()

type(df3)
df3.index.nlevels
df3.columns.nlevels

df3 = df3.set_index(["sector", "sub-sector"])

# +
# reset_df3 = df3.reset_index()
# reset_df3

# +
# for every_column in df3.columns:
#     print(every_column)

# +
# reset_df3 = df3.set_index(["sector", "sub-sector"]).stack()

# +
# reset_df3.columns.names = ["New"]
# reset_df3 = reset_df3.drop(np.nan, "Country", inplace=True, axis=1)
# df3 = df2.drop((np.nan, 'Country'))

# +
# col = ["sector", "sub-sector"]
# reset_df3 = reset_df3.loc[:, df.columns != col]



# reset_df3.shape
# -



# +
# for every_name in reset_df3.columns:
#     if every_name != "New":
#         print(every_name)

# +
# reset_df3

# +
# columns = ['New']
# reset_df3.drop(columns, inplace=True, axis=1)
# # reset_df3 = reset_df3.drop("New", axis=1, inplace=True)

# +
# reset_df3

# +
# df3.melt(id_vars = ["sector", "sub-sector"], var_name= "location", value_name="Value")

# +
# df3

# +
# df2.columns = df2.columns.astype(str)

# +
# df2.columns.map(type)

# +
# header_row = 0
# df2.columns = df2.iloc[header_row]

# +
# df2

# +
# df2.head()

# +
# import numpy as np
# df2.drop(index = (np.nan, 'Country'))

# +
# df2 = df2.reset_index()

# +
# df2

# +
# df2.reset_index(drop=True, inplace=True)

# +
# df2

# +
# df2.head(0)

# +
# df2.set_index(["sector", "sub-sector"], inplace = True)

# +
# df2.head(0)

# +
# df2 = df2.reset_index(level = "World")

# +
# list(df2.columns)

# +
# df2

# +
# df2 = df2.drop(header_row)
# df2 = df2.reset_index(drop = True)

# +
# tabs = distribution.as_pandas()

# +
# tabs

# +
# tidied_sheets = []

# +
tab = tabs["Imports"]
anchor = tab.excel_ref("A4")


sector = tab.filter("DCMS Sectors (exc Tourism and Civil Society)").expand(RIGHT).is_not_blank().filter(lambda x: type(x.value) != "Audio Visual" not in x.value)
column_7 = anchor.shift(7,0).expand(RIGHT)

empty_delete = anchor.fill(RIGHT).filter(contains_string("Empty column"))

del_sector_1 = anchor.shift(4,0)
del_sector_2 = del_sector_1.shift(RIGHT)
del_sector_3 = del_sector_2.shift(RIGHT)
total_del_sector = del_sector_1 | del_sector_2 | del_sector_3 | empty_delete

sub_sector = anchor.fill(RIGHT).is_not_blank().is_not_whitespace() - total_del_sector

# country = anchor.fill(DOWN).is_not_blank().is_not_whitespace()

observations = sub_sector.fill(DOWN).is_not_blank().is_not_whitespace()


dimensions = [
    HDim(sector, "Sector", CLOSEST, LEFT),
    # HDim(country, "Country", DIRECTLY, LEFT),
    HDim(sub_sector, "Sub-sector", DIRECTLY, ABOVE)
]
tidy_sheet = ConversionSegment(tab, dimensions, observations)
# savepreviewhtml(tidy_sheet, fname=tab.name+"Preview.html")
tidied_sheets.append(tidy_sheet.topandas())
df = pd.concat(tidied_sheets, sort = True)
# -

df

df.loc[df["Sector"] == "All UK service imports (2018 Pink Book estimate)", "Sub-sector"].unique()

# Sheet : Imports 

# +
# tab = tabs["Imports"]
# # datasetTitle = 'dcms-sectors-economic-estimates-2018-trade-in-services'
# # columns=["Period", "Flow", "Country", "Sector", "Subsector", "Marker", "Measure Type", "Unit"]
# anchor = tab.excel_ref("A4")
# flow = "imports"


# period = "year/2018" #TAKEN FROM SHEET TITLE


# # country = tab.excel_ref("A5").expand(DOWN)
# country = tab.filter("Country").fill(DOWN).is_not_blank().is_not_whitespace()


# row_3 = tab.filter("DCMS Sectors (exc Tourism and Civil Society)").expand(RIGHT).filter(lambda x: type(x.value) != "Audio Visual" not in x.value)
# column_7 = anchor.shift(7,0).expand(RIGHT)
# row_4 = anchor.shift(4, 0).expand(RIGHT)-column_7
# sector = row_3 | row_4
# savepreviewhtml(sector, fname=tab.name+"Preview.html")


# sector_tpe = tab.excel_ref("B4").expand(RIGHT).is_not_blank()


# # observations = country.waffle(sector_tpe).is_not_blank() 

# # dimensions = [
# #     HDimConst('Period', period),
# #     HDimConst('Flow', flow),
# #     HDim(country, 'Country', DIRECTLY, LEFT),
# #     HDim(sector, 'Sector', CLOSEST, LEFT),
# #     HDim(sector_tpe, 'Subsector', DIRECTLY, ABOVE),
# #     ]
# # tidy_sheet = ConversionSegment(tab, dimensions, observations)
# # tidied_sheets.append(tidy_sheet.topandas())


# -

# Sheet : Exports 

# +
tab = tabs["Exports"]
datasetTitle = 'DCMS Sectors Economic Estimates 2018: Trade in services : Exports'
columns=["Period", "Flow", "Country", "Sector", "Subsector", "Marker", "Measure Type", "Unit"]


flow = "exports"


period = "year/2018" #TAKEN FROM SHEET TITLE


country = tab.excel_ref("A5").expand(DOWN)


sector = tab.excel_ref("A3").expand(RIGHT).is_not_blank()


sector_tpe = tab.excel_ref("B4").expand(RIGHT).is_not_blank()


observations = country.waffle(sector_tpe).is_not_blank() 
dimensions = [
    HDimConst('Period', period),
    HDimConst('Flow', flow),
    HDim(country, 'Country', DIRECTLY, LEFT),
    HDim(sector, 'Sector', CLOSEST, LEFT),
    HDim(sector_tpe, 'Subsector', DIRECTLY, ABOVE),
    ]
tidy_sheet = ConversionSegment(tab, dimensions, observations)
tidied_sheets.append(tidy_sheet.topandas())
# -

tidy = pd.concat(tidied_sheets, sort = True)

# +


#Post Processing
tidy.rename(columns={'OBS' : 'Value', 'DATAMARKER' : 'Marker'}, inplace=True)
tidy = tidy.replace({'Marker' : {'-' : 'suppressed'}})
tidy['Value'] = tidy.apply(lambda x: 0 if x['Marker']== "suppressed" else x['Value'], axis=1)
tidy = tidy.replace({'Subsector' : {'Crafts4' : 'Cultural Crafts'}})

tidy['Unit'] = "gbp-million"
tidy['Measure Type'] = "count"


# +
# tidy['Country'] = tidy['Country'].apply(pathify)
# -



tidy['Sector'] = tidy['Sector'].apply(pathify)
tidy['Sector'].replace({
    "creative-industries-sub-sectors": "creative-industries", 
    "digital-sector-sub-sectors": "digital-sector",
    "culture-sector-sub-sector": "cultural-sector",
    "all-uk-service-exports-2018-pink-book-estimate": "all-uk-2018-pink-book-estimate",
    "all-uk-service-imports-2018-pink-book-estimate": "all-uk-2018-pink-book-estimate"
    }, inplace=True)

tidy['Subsector'] = tidy['Subsector'].apply(pathify)
tidy['Subsector'].replace({
    "all_exports": "all-uk-2018-pink-book-estimate", 
    "all_imports": "all-uk-2018-pink-book-estimate",
    "dcms-total": "dcms-sectors-exc-tourism-and-civil-society"
    }, inplace=True)

tidy = tidy[['Period', 'Country', 'Sector', 'Subsector', 'Flow', 'Measure Type', 'Unit', 'Value', 'Marker']]


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

tidy

# +
# csvName = 'observations.csv'
# out = Path('out')
# out.mkdir(exist_ok=True)
# tidy.drop_duplicates().to_csv(out / csvName, index = False)

# scraper.dataset.family = 'trade'
# scraper.dataset.description = description
# scraper.dataset.comment = comment
# scraper.dataset.title = 'Sectors Economic Estimates 2018: Trade in services'

# #dataset_path = pathify(os.environ.get('JOB_NAME', f'gss_data/{scraper.dataset.family}/' + Path(os.getcwd()).name) + '/pcn').lower()
# dataset_path = pathify(f'gss_data/{scraper.dataset.family}/' + Path(os.getcwd()).name).lower()

# scraper.set_base_uri('http://gss-data.org.uk')
# scraper.set_dataset_id(dataset_path)

# csvw_transform = CSVWMapping()
# csvw_transform.set_csv(out / csvName)
# csvw_transform.set_mapping(json.load(open('dcms_sectors_economic_estimates-info.json')))
# csvw_transform.set_dataset_uri(urljoin(scraper._base_uri, f'data/{scraper._dataset_id}'))
# csvw_transform.write(out / f'{csvName}-metadata.json')

# with open(out / f'{csvName}-metadata.trig', 'wb') as metadata:
#     metadata.write(scraper.generate_trig())
# -

tidy

tidy['Sector'].unique()

tidy['Subsector'].unique()

tidy['Flow'].unique()


