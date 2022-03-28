# %%
# +
from gssutils import *
import json
from csvcubed.models.cube.qb.catalog import CatalogMetadata

#TWO LANDING PAGES 
# https://www.ons.gov.uk/economy/grossdomesticproductgdp/datasets/regionalgrossdomesticproductenterpriseregions
# https://www.ons.gov.uk/economy/grossdomesticproductgdp/datasets/regionalgrossdomesticproductcityregions

scraper = Scraper(seed = 'info.json')
enterpriseregions_scraper = scraper.distribution(latest = True)

#change to outward landing page.
with open("info.json", "r") as jsonFile:
    data = json.load(jsonFile)
data["landingPage"] = "https://www.ons.gov.uk/economy/grossdomesticproductgdp/datasets/regionalgrossdomesticproductcityregions"
with open("info.json", "w") as jsonFile:
    json.dump(data, jsonFile, indent=2)
del data


scraper = Scraper(seed = 'info.json')
cityregions_scraper = scraper.distribution(latest = True)


# %%
# Collect together all tabs in one list of `((tab name, direction), tab)`
tabs = {
    ** {(tab.name.strip(), 'enterprise'): tab for tab in enterpriseregions_scraper.as_databaker()},
    ** {(tab.name.strip(), 'city'): tab for tab in cityregions_scraper.as_databaker()}
}
# %%
tidied_sheets = []
for (name, direction), tab in tabs.items():
    if 'Information' in name or 'ESRI_MAPINFO_SHEET' in name or 'Correction' in name: 
        continue
        
    measure = tab.excel_ref('A1')
    unit = tab.excel_ref('Y1')
    bottom_anchor = tab.filter(contains_string("Note 1"))
    area_type = bottom_anchor.fill(UP).is_not_blank() - measure - measure.shift(0,1)
    geo_code = bottom_anchor.shift(1,0).fill(UP).is_not_blank() - measure.shift(1,1)
    area_name = bottom_anchor.shift(2,0).fill(UP).is_not_blank() - measure.shift(2,1)
    period = tab.excel_ref('D2').expand(RIGHT)
    tab_name = tab.name.strip()
    observations = area_name.waffle(period).is_not_blank()
    
    dimensions = [
        HDim(period, 'Year', DIRECTLY, ABOVE),
        HDim(area_type, 'Area Type', DIRECTLY, LEFT),
        HDim(geo_code, 'Geography Code', DIRECTLY, LEFT),
        HDim(area_name, 'Area Name', DIRECTLY, LEFT),
        HDimConst('TAB NAME', tab_name),
        ]
    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    df = tidy_sheet.topandas()
    tidied_sheets.append(df)
# %%
df = pd.concat(tidied_sheets, sort = True)
df.rename(columns = {'OBS': 'Value', 'DATAMARKER':'Marker'}, inplace = True)
df
# %%
#Post Processing

#Marker Column
f1=((df['Year'].str.contains("note 3")))
df.loc[f1,'Marker'] = "provisional"
df = df.replace({'Marker' : {'-' : 'not-applicable',}})
#Year
df['Year'] = df['Year'].str[:4]
df['Year'] = "year/" + df['Year']
#Area Name 
df['Area Name'] = df['Area Name'].apply(pathify)
# Area Type
area_types = {"CR": "City Region",
      "ER": "Enterprise Region",
      "LA": "Local Authority",
      "LEP": "Local Enterprise Partnership"}
df['Area Type'] = df['Area Type'].map(area_types)
df['Area Type'] = df['Area Type'].apply(pathify)

#Measure 
measures = {"Table 1": "gva-at-cp",
      "Table 2": "vat-on-products",
      "Table 3": "other-taxes-on-products",
      "Table 4": "subsidies-on-products", 
      "Table 5": "gdp-at-cmp",
      "Table 6": "count",
      "Table 7": "gdp-per-capita-cp",
      "Table 8": "gva-implied-deflators",
      "Table 9": "gdp-at-cvm",
      "Table 10": "gdp-at-cvm-2018-money",
      "Table 11": "gdp-per-capita-cvm",
      "Table 12": "gdp-at-cvm-agr",
      "Table 13": "gdp-at-cvm-per-head-agr"}
df['Measure Type'] = df['TAB NAME'].map(measures)

#Units 
units = {"Table 1": "gbp-million",
      "Table 2": "gbp-million",
      "Table 3": "gbp-million",
      "Table 4": "gbp-million",
      "Table 5": "gbp-million",
      "Table 6": "persons",
      "Table 7": "gbp",
      "Table 8": "index",
      "Table 9": "index",
      "Table 10": "gbp-million",
      "Table 11": "gbp",
      "Table 12": "percentage-change",
      "Table 13": "percentage-change"}
df['Unit'] = df['TAB NAME'].map(units)
# -
# %%
del df['TAB NAME']
df = df[['Year', 'Area Name', 'Area Type', 'Geography Code','Value','Measure Type', 'Unit', 'Marker']]
# %%
df = df.drop_duplicates()
df.to_csv('observations.csv', index=False)
# %%
scraper.title = "Regional gross domestic product: city and enterprise regions"
catalog_metadata = scraper.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')

# %%
scraper.title

# %%
