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
    tab_name = tab.name
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

df = pd.concat(tidied_sheets, sort = True)
df.rename(columns = {'OBS': 'Value', 'DATAMARKER':'Marker'}, inplace = True)

# %%
#Post Processing

#Marker Column
f1=((df['Year'].str.contains("note 3")))
df.loc[f1,'Marker'] = "provisional"
df = df.replace({'Marker' : {'-' : 'not-applicable',}})
#Year
df['Year'] = df['Year'].str[:4]
df['Year'] = "year/" + df['Year']


# Area Type
#Note update codelist with values 'LEP', 'LA', 'ER', 'CR'

#Measure 
measures = {"Table 1": "GVA at Current Prices",
      "Table 2": "VAT on Products",
      "Table 3": "Other Taxes on Products",
      "Table 4": "Subsidies on Products",
      "Table 5": "GDP at Current Market Prices",
      "Table 6": "Count",
      "Table 7": "GDP per Capita",
      "Table 8": "GVA Implied Deflators",
      "Table 9": "GDP at Chained Volume Measures",
      "Table 10": "GDP at Chained Volume Measures",
      "Table 11": "GDP per Capita",
      "Table 12": "GDP at Chained Volume Measures - Annual Growth Rates",
      "Table 13": "GDP at Chained Volume Measures - per Head Annual Growth Rates"}
df['Measure Type'] = df['TAB NAME'].map(measures)

#Units 
units = {"Table 1": "GBP Million",
      "Table 2": "GBP Million",
      "Table 3": "GBP Million",
      "Table 4": "GBP Million",
      "Table 5": "GBP Million",
      "Table 6": "Person",
      "Table 7": "GBP",
      "Table 8": "Index",
      "Table 9": "Index",
      "Table 10": "GBP Million",
      "Table 11": "GBP",
      "Table 12": "Percentage Change",
      "Table 13": "Percentage Change"}
df['Unit'] = df['TAB NAME'].map(units)
# -
# %%
del df['TAB NAME']
df = df[[ 'Year', 'Area Name', 'Area Type', 'Geography Code','Value','Measure Type', 'Unit', 'Marker']]
df
# %%
df.to_csv('observations.csv', index=False)
catalog_metadata = scraper.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')
