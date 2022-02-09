# -*- coding: utf-8 -*-
# +
import json 
import numpy as np

from gssutils import * 
# from urllib.parse import urljoin
from csvcubed.models.cube.qb.catalog import CatalogMetadata
from datetime import datetime


df = pd.DataFrame()
# -

info = json.load(open('dcms_sectors_economic_estimates-info.json')) 
metadata = Scraper(seed="dcms_sectors_economic_estimates-info.json")   
metadata

distribution = metadata.distribution(title = lambda x: "Imports and Exports" in x)
distribution

path = distribution.downloadURL

df1 = pd.read_excel(path, "Imports")

header_row = 1
df1.columns = df1.iloc[header_row]


df1 = df1.drop(header_row)
df1 = df1.reset_index(drop = True)

df1

df1.columns = pd.MultiIndex.from_arrays([df1.columns, df1.iloc[1].values])
df1 = df1.iloc[2:]

df1

df2 = df1.T

df2.index.names = ['sector', "subsector"]

df2.head()

header_row = 0
df2.columns = df2.iloc[header_row]

df3 = df2.drop((np.nan, 'Country'))

df3.head()

df3 = df3.stack()

df3

df3 = df3.to_frame()

df3

df3 = df3.reset_index()

df3.head(0)

df3 = df3.rename(columns = {(np.nan, 'Country'):"country", 0:"value"})

df3.loc[df3["sector"] == "sheet", "value"]

for val in df3["subsector"]:
    df3["sector"]

df3 = df3.fillna(method = "ffill")

df3.loc[df3["subsector"] == "Empty column", "sector"]

df3.tail(10)

df3["Marker"] = np.nan

df3["Flow"] = "Imports"

df3

# +
# stop
# -

df4 = pd.read_excel(path, "Exports")

header_row = 1
df4.columns = df4.iloc[header_row]

df4 = df4.drop(header_row)
df4 = df4.reset_index(drop = True)

df4

df4.columns = pd.MultiIndex.from_arrays([df4.columns, df4.iloc[1].values])
df4 = df4.iloc[2:]

df4

df5 = df4.T

df5.index.names = ['sector', 'subsector']

df5.head()

header_row = 0
df5.columns = df5.iloc[header_row]

df6 = df5.drop((np.nan, "Country"))

df6.head()

df6 = df6.stack()

df6

df6 = df6.to_frame()

df6

df6 = df6.reset_index()

df6.head(0)

df6 = df6.rename(columns = {(np.nan, 'Country'):"country", 0:"value"})

df6.loc[df6["sector"] == "sheet", "value"]

for val in df6["subsector"]:
    df6["sector"]

df6 = df6.fillna(method = "ffill")

df6.tail(10)

df6["Marker"] = np.nan

df6["Flow"] = "Exports"

df6

# +
# stop
# -

frames = [df3, df6]

tidy = pd.concat(frames).fillna('')

tidy

tidy['Marker'] = tidy.apply(lambda x: 'suppressed' if x['value'] == '-' else x['Marker'], axis = 1)

# +
# tidy.loc[tidy['value'] == '-', 'Marker']
# -

tidy['Marker'].unique()

tidy['sector'].unique()

# +
# def replace_values_in_sector(data_frame):

tidy["sector"] = tidy.apply(lambda x: "Gambling" if x["subsector"] == "Gambling" 
                                    else "Sport" if x["subsector"] == "Sport" 
                                        else "Telecoms"if x["subsector"] == "Telecoms" 
                                            else x["sector"], axis = 1)

# -

tidy['sector'].unique()

tidy["subsector"] = tidy.apply(lambda x: 'N/A' if x["sector"] == "Gambling" 
                                else 'N/A' if  x["sector"] == "Sport" 
                                    else 'N/A' if  x["sector"] == "Telecoms"
                                        else "Cultural Crafts" if x["subsector"] == "Crafts4"
                                            else x["subsector"], axis =1)

# +
# tidy = tidy.replace({'Subsector' : {'Crafts4' : 'Cultural Crafts'}}
# -

tidy['subsector'].unique()

# +
# val_dict = {"creative-industries-sub-sectors": "creative-industries", 
#     "digital-sector-sub-sectors": "digital-sector",
#     "culture-sector-sub-sector": "cultural-sector",
#     "all-uk-service-exports-2018-pink-book-estimate": "all-uk-2018-pink-book-estimate",
#     "all-uk-service-imports-2018-pink-book-estimate": "all-uk-2018-pink-book-estimate"}
# -

# tidy['sector'] = tidy['sector'].str.lower()


tidy['sector'].unique()

# +
# stop
# -

tidy["sector"] = tidy.apply(lambda x: "creative-industries" if x["sector"] == "creative industries sub-sectors"
                                else "digital-sector" if x["sector"] == "digital sector sub-sectors"
                                    else "cultural-sector" if x["sector"] == "culture sector sub-sector"
                                        else "all-uk-2018-pink-book-estimate" if x["sector"] == "all uk service imports (2018 pink book estimate)"
                                            else "all-uk-2018-pink-book-estimate" if x["sector"] == "all uk service exports (2018 pink book estimate)"
                                                else x['sector'], axis = 1)

# +
# tidy['sector'] = tidy['sector'].replace({"creative industries sub-sectors": "creative-industries", 
#     "digital sector sub-sectors": "digital-sector",
#     "culture sector sub-sector": "cultural-sector",
#     "all uk service imports (2018 pink book estimate)": "all-uk-2018-pink-book-estimate",
#     "all uk service exports (2018 pink book estimate)": "all-uk-2018-pink-book-estimate"}, inplace=True)
# -

tidy['sector'].unique()

# +
# tidy["sub-sector"].unique()

# +
# tidy['subsector'] = tidy['subsector'].str.lower()
# -

tidy["subsector"].unique()

tidy["subsector"] = tidy.apply(lambda x : "all-uk-2018-pink-book-estimate" if x["subsector"] == "all_exports"
                                    else "all-uk-2018-pink-book-estimate" if x["subsector"] == "all_imports"
                                        else "dcms-sectors-exc-tourism-and-civil-society" if x["subsector"] =="dcms total"
                                            else x["subsector"], axis = 1)

tidy["unit"] = "gbp-million"
tidy["measure type"] = "count"
tidy["year"] = "year/2018"

tidy.columns = map(str.title, tidy.columns)

tidy

tidy = tidy[["Sector", "Subsector", "Country", "Year", "Flow", "Measure Type", "Unit", "Value", "Marker"]]

duplicate_tidy = tidy[tidy.duplicated(["Sector", "Subsector", "Country", "Year", "Flow", "Measure Type", "Unit", "Value", "Marker"])]

duplicate_tidy

tidy['Value'] = pd.to_numeric(tidy.Value, errors = 'coerce')
tidy = tidy.round({"Value":2})

print(np.nan in tidy['Subsector'].unique())

tidy.to_csv("dcms_sectors_economic_estimates-observations.csv", index = False)

# +
# metadata.description = f"""
# DCMS Sector Economic Estimates 2018: Trade in Services is an official statistic and has been produced to the standards set out in the Code of Practice for Statistics.
# DCMS Sectors Economic Estimates 2018: Trade in services report:
# https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/863862/DCMS_Sectors_Economic_Estimates_2018_Trade_In_Services.pdf
# This release provides estimates of exports and imports of services by businesses in DCMS Sectors excluding Tourism and Civil Society2) in current prices. Any changes between years may reflect changes in the absolute value of the £ (affected by the domestic rate of inflation and by exchange rates), as well as changes in actual trade volume. These statistics are further broken down by selected countries, regions and continents.The latest year for which these estimates are available is 2018. Estimates of trade in services have been constructed from ONS official statistics using international classifications (StandardIndustrial Classification (SIC) codes). For further information see Annex A and the quality assurance (QA) document accompanying this report.Data are available for each DCMS Sector (excluding Tourism and Civil Society) and sub-sectors within the Creative Industries, Digital Sector, and Cultural Sector. There is significant overlap between DCMS Sectors so users should be aware that the estimate for “DCMSSectors Total” is lower than the sum of the individual sectors.

# The World totals are calculated on the same basis as previous years. However, the list of individual countries used in the calculation of the (world) regional and continental statistics (e.g. European Union, Latin America and Caribbean, Asia) is slightly different to the previous (August 2019) release. Therefore, these statistics in particular are not directly comparable with previous years. In particular: 
# -The Bailiwick of Guernsey, the Bailiwick of Jersey and Timor-Leste form part of the Europe, Rest of Europe and    Asia totals for the first time.
# -Gibraltar is included, and now forms part of the European Union total, in line with the Balance of Payments Vademecum. The EU Institutions total is also included on its own for the first time.     
# -Latin America & Caribbean no longer includes America Unallocated as part of its calculation.
# A revised backseries of calculations on the current basis is expected to be provided in the summer.

# """

# metadata.comment = "Official Statistics used to provide an estimate of the contribution of DCMS Sectors to the UK economy, measured by imports and exports of services."
# metadata.summary = f"""
# Economic Estimates are Official Statistics used to provide an estimate of imports and exports of services by DCMS Sectors (excluding Tourism and Civil Society).
# This release only covers trade in services, and aims to provide a timely summary of the key findings for 2018, the latest year for which data are available.

# """
# -

# metadata.description = description
# metadata.comment = comment
catalog_metadata = metadata.as_csvqb_catalog_metadata()

catalog_metadata.to_json_file('dcms_sectors_economic_estimates-catalog-metadata.json')

# +


# #Post Processing
# tidy.rename(columns={'OBS' : 'Value', 'DATAMARKER' : 'Marker'}, inplace=True)
# tidy = tidy.replace({'Marker' : {'-' : 'suppressed'}})
# tidy['Value'] = tidy.apply(lambda x: 0 if x['Marker']== "suppressed" else x['Value'], axis=1)
# tidy = tidy.replace({'Subsector' : {'Crafts4' : 'Cultural Crafts'}})

# tidy['Unit'] = "gbp-million"
# tidy['Measure Type'] = "count"


# +
# tidy['Country'] = tidy['Country'].apply(pathify)

# +
# tidy['Sector'] = tidy['Sector'].apply(pathify)
# tidy['Sector'].replace({
#     "creative-industries-sub-sectors": "creative-industries", 
#     "digital-sector-sub-sectors": "digital-sector",
#     "culture-sector-sub-sector": "cultural-sector",
#     "all-uk-service-exports-2018-pink-book-estimate": "all-uk-2018-pink-book-estimate",
#     "all-uk-service-imports-2018-pink-book-estimate": "all-uk-2018-pink-book-estimate"
#     }, inplace=True)

# +
# tidy['Subsector'] = tidy['Subsector'].apply(pathify)
# tidy['Subsector'].replace({
#     "all_exports": "all-uk-2018-pink-book-estimate", 
#     "all_imports": "all-uk-2018-pink-book-estimate",
#     "dcms-total": "dcms-sectors-exc-tourism-and-civil-society"
#     }, inplace=True)

# +
# tidy = tidy[['Period', 'Country', 'Sector', 'Subsector', 'Flow', 'Measure Type', 'Unit', 'Value', 'Marker']]
# -




# +
# description = f"""
# DCMS Sector Economic Estimates 2018: Trade in Services is an official statistic and has been produced to the standards set out in the Code of Practice for Statistics.
# DCMS Sectors Economic Estimates 2018: Trade in services report:
# https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/863862/DCMS_Sectors_Economic_Estimates_2018_Trade_In_Services.pdf
# This release provides estimates of exports and imports of services by businesses in DCMS Sectors excluding Tourism and Civil Society2) in current prices. Any changes between years may reflect changes in the absolute value of the £ (affected by the domestic rate of inflation and by exchange rates), as well as changes in actual trade volume. These statistics are further broken down by selected countries, regions and continents.The latest year for which these estimates are available is 2018. Estimates of trade in services have been constructed from ONS official statistics using international classifications (StandardIndustrial Classification (SIC) codes). For further information see Annex A and the quality assurance (QA) document accompanying this report.Data are available for each DCMS Sector (excluding Tourism and Civil Society) and sub-sectors within the Creative Industries, Digital Sector, and Cultural Sector. There is significant overlap between DCMS Sectors so users should be aware that the estimate for “DCMSSectors Total” is lower than the sum of the individual sectors.

# The World totals are calculated on the same basis as previous years. However, the list of individual countries used in the calculation of the (world) regional and continental statistics (e.g. European Union, Latin America and Caribbean, Asia) is slightly different to the previous (August 2019) release. Therefore, these statistics in particular are not directly comparable with previous years. In particular: 
# -The Bailiwick of Guernsey, the Bailiwick of Jersey and Timor-Leste form part of the Europe, Rest of Europe and    Asia totals for the first time.
# -Gibraltar is included, and now forms part of the European Union total, in line with the Balance of Payments Vademecum. The EU Institutions total is also included on its own for the first time.     
# -Latin America & Caribbean no longer includes America Unallocated as part of its calculation.
# A revised backseries of calculations on the current basis is expected to be provided in the summer.

# """

# comment = "Official Statistics used to provide an estimate of the contribution of DCMS Sectors to the UK economy, measured by imports and exports of services."

# +
# del tidy['Measure Type']
# del tidy['Unit']
# tidy = tidy.fillna('')

# +
# tidy

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
