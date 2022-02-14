# -*- coding: utf-8 -*-
# +
import json 
import numpy as np

from gssutils import * 
# from urllib.parse import urljoin
#from csvcubed.models.cube.qb.catalog import CatalogMetadata
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

df1.columns = pd.MultiIndex.from_arrays([df1.columns, df1.iloc[1].values])
df1 = df1.iloc[2:]

df2 = df1.T

df2.index.names = ['sector', "subsector"]

header_row = 0
df2.columns = df2.iloc[header_row]

df3 = df2.drop((np.nan, 'Country'))

df3 = df3.stack()

df3 = df3.to_frame()

df3 = df3.reset_index()

df3.head(0)

df3 = df3.rename(columns = {(np.nan, 'Country'):"country", 0:"value"})

df3 = df3.fillna(method = "ffill")

df3.loc[df3["subsector"] == "Empty column", "sector"]

df3["Marker"] = np.nan

df3["Flow"] = "Imports"

df4 = pd.read_excel(path, "Exports")

header_row = 1
df4.columns = df4.iloc[header_row]

df4 = df4.drop(header_row)
df4 = df4.reset_index(drop = True)

df4.columns = pd.MultiIndex.from_arrays([df4.columns, df4.iloc[1].values])
df4 = df4.iloc[2:]

df5 = df4.T

df5.index.names = ['sector', 'subsector']

header_row = 0
df5.columns = df5.iloc[header_row]

df6 = df5.drop((np.nan, "Country"))

df6 = df6.stack()

df6 = df6.to_frame()

df6 = df6.reset_index()

df6.head(0)

df6 = df6.rename(columns = {(np.nan, 'Country'):"country", 0:"value"})

df6 = df6.fillna(method = "ffill")

df6["Marker"] = np.nan

df6["Flow"] = "Exports"

frames = [df3, df6]

tidy = pd.concat(frames).fillna('')

tidy['Marker'] = tidy.apply(lambda x: 'suppressed' if x['value'] == '-' else x['Marker'], axis = 1)

tidy["sector"] = tidy.apply(lambda x: "Gambling" if x["subsector"] == "Gambling" 
                                    else "Sport" if x["subsector"] == "Sport" 
                                        else "Telecoms"if x["subsector"] == "Telecoms" 
                                            else x["sector"], axis = 1)


tidy["subsector"] = tidy.apply(lambda x: 'N/A' if x["sector"] == "Gambling" 
                                else 'N/A' if  x["sector"] == "Sport" 
                                    else 'N/A' if  x["sector"] == "Telecoms"
                                        else "Cultural Crafts" if x["subsector"] == "Crafts4"
                                            else x["subsector"], axis =1)

tidy["sector"] = tidy.apply(lambda x: "Creative-industries" if x["sector"] == "Creative Industries sub-sectors"
                                else "Digital-sector" if x["sector"] == "Digital Sector sub-sectors"
                                    else "Cultural-sector" if x["sector"] == "Culture Sector sub-sector"
                                        else "All-uk-2018-pink-book-estimate" if x["sector"] == "All UK service imports (2018 Pink Book estimate)"
                                            else "All-uk-2018-pink-book-estimate" if x["sector"] == "All UK service exports (2018 Pink Book estimate)"
                                                else x['sector'], axis = 1)

tidy["subsector"] = tidy.apply(lambda x : "All-uk-2018-pink-book-estimate" if x["subsector"] == "All_Exports"
                                    else "All-uk-2018-pink-book-estimate" if x["subsector"] == "All_Imports"
                                        else "Dcms-sectors-exc-tourism-and-civil-society" if x["subsector"] =="DCMS total"
                                            else x["subsector"], axis = 1)

tidy["unit"] = "gbp-million"
tidy["measure type"] = "Current prices"
tidy["year"] = "year/2018"

tidy.columns = map(str.title, tidy.columns)

tidy = tidy[["Sector", "Subsector", "Country", "Year", "Flow", "Measure Type", "Unit", "Value", "Marker"]]

duplicate_tidy = tidy[tidy.duplicated(["Sector", "Subsector", "Country", "Year", "Flow", "Measure Type", "Unit", "Value", "Marker"])]

duplicate_tidy

tidy['Value'] = pd.to_numeric(tidy.Value, errors = 'coerce')
tidy = tidy.round({"Value":2})

tidy.to_csv("dcms_sectors_economic_estimates-observations.csv", index = False)

# +
metadata.set_description = f"""
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

metadata.comment = "Official Statistics used to provide an estimate of the contribution of DCMS Sectors to the UK economy, measured by imports and exports of services."
metadata.summary = f"""
Economic Estimates are Official Statistics used to provide an estimate of imports and exports of services by DCMS Sectors (excluding Tourism and Civil Society).
This release only covers trade in services, and aims to provide a timely summary of the key findings for 2018, the latest year for which data are available.

"""
# -

catalog_metadata = metadata.as_csvqb_catalog_metadata()

catalog_metadata.to_json_file('dcms_sectors_economic_estimates-catalog-metadata.json')

# +
# tidy
