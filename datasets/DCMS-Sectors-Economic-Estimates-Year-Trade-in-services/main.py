# -*- coding: utf-8 -*-
# +
from gssutils import * 
import json 
from urllib.parse import urljoin
import numpy as np

df = pd.DataFrame()
# -

info = json.load(open('dcms_sectors_economic_estimates-info.json')) 
scraper = Scraper(seed="dcms_sectors_economic_estimates-info.json")   
scraper

distribution = scraper.distribution(title = lambda x: "Imports and Exports" in x)
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

df2.index.names = ['sector', "sub-sector"]

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

for val in df3["sub-sector"]:
    df3["sector"]

df3 = df3.fillna(method = "ffill")

# +
# def replace_values_in_sector(data_frame):

#     df3["sector"] = df3.apply(lambda x: "Gambling" if x["sub-sector"] == "Gambling" 
#                                     else "Sport" if x["sub-sector"] == "Sport" 
#                                         else "Telecoms"if x["sub-sector"] == "Telecoms" 
#                                                 else np.nan if x["sub-sector"] == "Audio Visual" 
#                                                 else x["sector"], axis = 1)


# +
# df3["sub-sector"] = df3.apply(lambda x: np.nan if x["sub-sector"] == "Gambling" 
#                                 else np.nan if  x["sub-sector"] == "Sport" 
#                                     else np.nan if  x["sub-sector"] == "Telecoms" 
#                                         else x["sub-sector"], axis =1)
# -

df3.loc[df3["sub-sector"] == "Empty column", "sector"]

df3.tail(10)

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
