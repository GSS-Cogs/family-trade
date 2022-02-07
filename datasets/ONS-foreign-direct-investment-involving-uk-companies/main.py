# -*- coding: utf-8 -*-
# %%
# +
from gssutils import *
import pandas as pd
from IPython.display import display
import json
from csvcubed.models.cube.qb.catalog import CatalogMetadata
from datetime import datetime

metadata = Scraper(seed = 'foreign_direct_investment-info.json')
#display(metadata)
# -

inward_scraper = metadata.distribution(latest = True)
#inward_scraper
# %%
#change to outward landing page.
with open("foreign_direct_investment-info.json", "r") as jsonFile:
    data = json.load(jsonFile)
data["landingPage"] = "https://www.ons.gov.uk/businessindustryandtrade/business/businessinnovation/datasets/foreigndirectinvestmentinvolvingukcompaniesoutwardtables"
with open("foreign_direct_investment-info.json", "w") as jsonFile:
    json.dump(data, jsonFile, indent=2)
del data


metadata_1 = Scraper(seed = 'foreign_direct_investment-info.json')
#display(metadata_1)

outward_scraper = metadata_1.distribution(latest = True)
#outward_scraper

# %%
# Collect together all tabs in one list of `((tab name, direction), tab)`

tabs = {
    ** {(tab.name.strip(), 'inward'): tab for tab in inward_scraper.as_databaker()},
    ** {(tab.name.strip(), 'outward'): tab for tab in outward_scraper.as_databaker()}
}
#print(list(tabs.keys()))
# %%
# A common issue is where a dimension label is split over more than one cell.
# The following function does a rudimentary search for these splits in a bag, returns a list of
# pairs of cells and their replacement, along with a list of extraneous cells to remove
# from the bag.

def split_overrides(bag, splits):
    overrides = []
    to_remove = None
    for split in splits:
        for cell in bag:
            c = cell
            found = True
            remove_list = []
            for s in split:
                if c.value.strip() != s:
                    found = False
                    break
                try:
                    c = c.shift(DOWN)
                except:
                    found = False
                    break
                remove_list.append(c)
            if found:
                overrides.append((cell, ' '.join(split)))
                for c in remove_list:
                    if to_remove is None:
                        to_remove = c
                    else:
                        to_remove = to_remove | c
    return (overrides, to_remove)

# %%
tidied_sheets = []
tables = []
for (name, direction), tab in tabs.items():
    
    # Only process tabs starting .2, .3 and .4
    if '.' not in name:
        continue
    major, minor = name.split('.')
    if major not in ['2', '3', '4']:
        continue
    #display(f'Processing tab {name}: {direction}')
    
    # Set anchors for header row
    top_right = tab.filter('£ million')
    top_right.assert_one()
    left_top = tab.filter('EUROPE').by_index(1)
    
    top_row = (left_top.fill(UP).fill(RIGHT) & top_right.expand(LEFT).fill(DOWN)).is_not_blank().is_not_whitespace()
    dims = []
    dims.append(HDim(top_row, 'top', DIRECTLY, ABOVE))
    
    # Select all the footer info as "bottom_block"
    bottom = tab.filter('The sum of constituent items may not always agree exactly with the totals shown because of rounding.')
    bottom.assert_one()
    bottom_block = bottom.shift(UP).expand(RIGHT).expand(DOWN)
    
    left_col = (left_top | left_top.shift(RIGHT) | left_top.shift(RIGHT) \
                .shift(RIGHT)).expand(DOWN).is_not_blank().is_not_whitespace() - bottom_block
    left_col = left_col - left_col.filter('of which')
    
    # fix up cells that have been split
    overrides, to_remove = split_overrides(left_col, [
        ('OTHER', 'EUROPEAN', 'COUNTRIES'),
        ('OTHER EUROPEAN', 'COUNTRIES'),
        ('UK OFFSHORE', 'ISLANDS'),
        ('NEAR & MIDDLE EAST', 'COUNTRIES'),
        ('NEAR & MIDDLE', 'EAST COUNTRIES'),
        ('AUSTRALASIA &', 'OCEANIA'),
        ('AUSTRALASIA', '& OCEANIA'),
        ('CENTRAL & EASTERN', 'EUROPE'),
        ('CENTRAL &', 'EASTERN', 'EUROPE'),
        ('GULF ARABIAN', 'COUNTRIES'),
        ('OTHER ASIAN', 'COUNTRIES')
    ])
    
    if to_remove:
        left_col = left_col - to_remove

    left_dim = HDim(left_col, "FDI Area", CLOSEST, UP)
    
    for cell, replace in overrides:
        left_dim.AddCellValueOverride(cell, replace)
    # Also, "IRELAND" should be "IRISH REPUBLIC"
    left_dim.AddCellValueOverride('IRELAND', 'IRISH REPUBLIC')
    dims.append(left_dim)
    
    if minor == '1':
        year_col = tab.excel_ref('D5').expand(RIGHT).is_not_blank()
        dims.append(HDim(year_col, 'Year', DIRECTLY, ABOVE))
        obs = year_col.fill(DOWN).is_not_blank() - bottom_block
    if minor == '2':
        year_col = tab.excel_ref('D7').expand(DOWN).is_not_blank()
        dims.append(HDim(year_col, 'Year', DIRECTLY, LEFT))
        obs = year_col.fill(RIGHT).is_not_blank() - bottom_block
        
       # if major == "2" :
       #     obs = year_col.fill(RIGHT).is_not_blank() - top_right.fill(DOWN) - bottom_block
    
    if minor == '3':
        year_col = tab.excel_ref('E6').expand(DOWN).is_not_blank()
        dims.append(HDim(year_col, 'Year', DIRECTLY, LEFT))
        obs = year_col.fill(RIGHT).is_not_blank() - bottom_block

    cs = ConversionSegment(obs, dims, includecellxy=True)
    #savepreviewhtml(cs, fname= tab.name + "PREVIEW.html") 
    table = cs.topandas()
    
        # Post processing
    table['Year'] = table['Year'].map(lambda x: int(float(x)))
    table["FDI Area"] = table["FDI Area"].map(lambda x: pathify(x.strip()))
    table["FDI Area"] = table["FDI Area"].replace({"other-european", "other-european-countries"})

    if minor != '2':
        table['FDI Component'] = {
            '2': {'outward': 'total-net-fdi-abroad',
                  'inward': 'total-net-fdi-in-the-uk'},
            '3': {'outward': 'total-net-fdi-international-investment-position-abroad-at-end-period',
                  'inward': 'total-net-fdi-international-investment-position-in-the-uk-at-end-period'},
            '4': {'outward': 'total-net-fdi-earnings-abroad',
                  'inward': 'total-net-fdi-earnings-in-the-uk'}
        }.get(major).get(direction)
    else:
        table.rename(columns={'top': 'FDI Component'}, inplace=True)
        table['FDI Component'] = table['FDI Component'].map(pathify)
    if minor == '3':
        table.rename(columns={'top': 'FDI Industry'}, inplace=True)
        table['FDI Industry'] = table['FDI Industry'].map(
            lambda x: pathify(x) if x != 'Total' else 'all-activities')
    else:
        table['FDI Industry'] = 'all-activities'
    # Disambiguate FDI Component between tabs 2.2 and 4.2
    if name == '2.2':
        table['FDI Component'] = table['FDI Component'].map(
            lambda x: 'fdi-' + x if not x.startswith('total-net-foreign-direct-investment-') else
            'total-net-fdi-' + x[len('total-net-foreign-direct-investment-'):]
        )
    elif name == '4.2':

        table['FDI Component'] = table['FDI Component'].map(
            lambda x: 'earnings-fdi-' + x if not x.startswith('total-net-') else
            'total-net-' + x[len('total-net-'):].replace('foreign-direct-investment', 'fdi')
        )

    table['International Trade Basis'] = table['Year'].map(lambda year: 'BPM5' if year < 2012 else 'BPM6')
    table['Investment Direction'] = direction
    tidied_sheets.append(table)


# %%
df = pd.concat(tidied_sheets, sort = True)
df.rename(columns = {'OBS': 'Value', 'DATAMARKER':'Marker'}, inplace = True)
df = df.replace({'Marker' : {'..' : 'disclosive', '-' : 'itis-nil'}})
df['Value'] = pd.to_numeric(df['Value'], errors = 'coerce')
df.drop(columns=['__x', '__y', '__tablename','top'],axis = 1, inplace = True)
df.drop_duplicates(subset=df.columns.difference(['Value']), inplace =True)
df

# %%
# --- Force Consistant labels ---:
# The data producer is using different labels for the same thing within the same dataset
# We need to force them to same
fix = {
    "other-european": "other-european-countries",
    "other-europen-countries": "other-european-countries",
    "other": "other-european-countries",
    "uk-offshore":"uk-offshore-islands",
    "near-middle-east": "near-middle-east-countries",
    "near-middle": "near-middle-east-countries",
    "australasia": "australasia-oceania",
    "central-eastern": "central-eastern-europe",
    "central": "central-eastern-europe",
    "gulf-arabian": "gulf-arabian-countries",
    "other-asian": "other-asian-countries"
}
df['FDI Area'] = df['FDI Area'].map(lambda x: fix.get(x, x))
df

# %%
#tabs 2.1, 2.2 have duplicate data down for cell year2019, AUSTRALIA, under "Total net foreign direct investment abroad" 
#In tab 2.1 the value is 300 but in 2.2 is .. meaning Indicates value is disclosive. These tabs could of been colated in a differnet manner. as all the other values for that column match across the two tabs. 
#The same applies for tabs 4.1 and 4.2 for data relating to year2020, NEW ZEALAND, "Total net FDI earnings abroad"
#I made (shannon) an informed descion to drop the the 2 values that hold a marker and use the observation with an actual numerical value. 
df_dup = df[df.duplicated(['Investment Direction', 'Year', 'International Trade Basis',
                             'FDI Area', 'FDI Component', 'FDI Industry'
                              ],keep=False)]
filtered_df = df_dup[df_dup['Value'].isnull()]
filtered_df


# %%
def dataframe_difference(df1: df, df2: df, which=None):
    """Find rows which are different between two DataFrames."""
    comparison_df = df1.merge(
        df2,
        indicator=True,
        how='outer'
    )
    if which is None:
        diff_df = comparison_df[comparison_df['_merge'] != 'both']
    else:
        diff_df = comparison_df[comparison_df['_merge'] == which]
    diff_df.drop(columns=['_merge'],axis = 1, inplace = True)
    return diff_df

df = dataframe_difference(df, filtered_df)

# %%
#checking no duplicates
df_dup = df[df.duplicated(['Investment Direction', 'Year', 'International Trade Basis',
                             'FDI Area', 'FDI Component', 'FDI Industry'
                              ],keep=False)]
df_dup

# %%
# +
df.to_csv('foreign_direct_investment-observations.csv', index = False)

catalog_metadata: CatalogMetadata = CatalogMetadata(
    title = "Foreign direct investment involving UK companies (directional)",
    summary = "Annual statistics on the investment of foreign companies into the UK, including for investment flows, positions and earnings into the UK and of UK companies abroad.",
    description = "Inward and Outward reference table including data for flows, positions and earnings. \
The sum of constituent items may not always agree exactly with the totals shown due to rounding. \
A negative sign before values indicates a net disinvestment in the UK. \
Component breakdown excludes the activities of private property, public corporations and bank holding companies.These are included in the total.",
    identifier = "ons-foreign-direct-investment-involving-uk-companies",
    keywords = [
        "business investment",
        "stocks",
        "investment flows"
    ],
    theme_uris = [
        "https://www.ons.gov.uk/businessindustryandtrade/business/businessinnovation"
    ],
    landing_page_uris = [
        "https://www.ons.gov.uk/businessindustryandtrade/business/businessinnovation/datasets/foreigndirectinvestmentinvolvingukcompanies2013inwardtables",
        "https://www.ons.gov.uk/businessindustryandtrade/business/businessinnovation/datasets/foreigndirectinvestmentinvolvingukcompaniesoutwardtables"
    ],
    creator_uri = "https://www.gov.uk/government/organisations/office-for-national-statistics",
    publisher_uri = "https://www.gov.uk/government/organisations/office-for-national-statistics",
    license_uri = "http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
    dataset_issued = "2020-12-21",
    dataset_modified = "2022-01-25T12:53:20.941413+00:00",
    public_contact_point_uri = "mailto:fdi@ons.gov.uk"
)

catalog_metadata.to_json_file('foreign_direct_investment-catalog-metadata.json')
