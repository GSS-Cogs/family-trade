#%%
from gssutils import * 
import json 
from urllib.parse import urljoin
import numpy as np
#%%
info = json.load(open('info.json')) 
metadata = Scraper(seed="info.json")   
metadata
#%%
distribution = metadata.distribution(title = lambda x: "Imports and Exports" in x)
distribution
#%%
tabs = {tab.name: tab for tab in metadata.distribution (title = lambda x: "Imports and Exports"in x).as_databaker()}
#%%
tidied_sheets =[]
for name, tab in tabs.items():
    if "Cover sheet" in name:
        continue
    
    if tab.name == "Imports":
        flow = "imports"
    else:
        flow = "exports"

    period = "year/2018" #TAKEN FROM SHEET TITLE

    country = tab.filter("Country").fill(DOWN).is_not_blank().is_not_whitespace()

    sector = tab.filter("DCMS Sectors (exc Tourism and Civil Society)").expand(RIGHT).filter(lambda x: type(x.value) != "Audio Visual" not in x.value).is_not_blank().is_not_whitespace()

    empty_column = tab.filter(contains_string("Empty column"))

    sub_sector = tab.filter("Creative Industries").expand(RIGHT).is_not_blank().is_not_whitespace()-empty_column

    observations = country.fill(RIGHT).is_not_blank().is_not_whitespace()

    dimensions = [
        HDimConst("Year", period),
        HDimConst("Flow", flow),
        HDim(country, "Country", DIRECTLY, LEFT),
        HDim(sector, "Sector", CLOSEST, LEFT),
        HDim(sub_sector, "Subsector", DIRECTLY, ABOVE)
    ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    # savepreviewhtml(tidy_sheet, fname= tab.name + "Preview.html")
    tidied_sheets.append(tidy_sheet.topandas())
#%%
tidy = pd.concat(tidied_sheets, sort = True).fillna('')
tidy.rename(columns={'OBS' : 'Value', 'DATAMARKER' : 'Marker'}, inplace=True)
tidy = tidy.replace({'Marker' : {'-' : 'suppressed'}})
tidy['Value'] = tidy.apply(lambda x: 0 if x['Marker']== "suppressed" else x['Value'], axis=1)
tidy = tidy.replace({'Subsector' : {'Crafts4' : 'Cultural Crafts'}})
#%%
tidy['Unit'] = "GBP Million"
tidy['Measure Type'] = "Count"

#%%
tidy['Sector'].replace({
    "Creative Industries sub-sectors": "creative-industries", 
    "Digital Sector sub-sectors": "digital-sector",
    "Culture Sector sub-sector": "cultural-sector",
    "All UK service imports (2018 Pink Book estimate)": "all-uk-2018-pink-book-estimate",
    "All UK service exports (2018 Pink Book estimate)": "all-uk-2018-pink-book-estimate"
    }, inplace=True)
#%%
tidy["Sector"] = tidy.apply(lambda x: "Gambling" if x["Subsector"] == "Gambling" 
                                    else "Sport" if x["Subsector"] == "Sport" 
                                        else "Telecoms"if x["Subsector"] == "Telecoms" 
                                            else x["Sector"], axis = 1)
#%%
tidy['Subsector'].replace({
    "All_Exports": "All-uk-2018-pink-book-estimate", 
    "All_Imports": "All-uk-2018-pink-book-estimate",
    "DCMS total": "Dcms-sectors-exc-tourism-and-civil-society"
    }, inplace=True)
#%%
tidy["Subsector"] = tidy.apply(lambda x: 'Not Applicable' if x["Sector"] == "Gambling" 
                                else 'Not Applicable' if  x["Sector"] == "Sport" 
                                    else 'Not Applicable' if  x["Sector"] == "Telecoms"
                                        else "Cultural Crafts" if x["Subsector"] == "Crafts4"
                                            else x["Subsector"], axis =1)
tidy["Subsector"].unique()
#%%
tidy = tidy[["Sector", "Subsector", "Country", "Year", "Flow", "Measure Type", "Unit", "Value", "Marker"]]
#%%
duplicate_tidy = tidy[tidy.duplicated(["Sector", "Subsector", "Country", "Year", "Flow", "Measure Type", "Unit", "Value", "Marker"])]
duplicate_tidy

#%%
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
#%%
tidy.to_csv("observations.csv", index = False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')
