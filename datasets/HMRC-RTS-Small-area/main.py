# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     cell_metadata_json: true
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.4.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
from gssutils import *
import json
import copy 

info = json.load(open('info.json'))
scraper = Scraper(seed='info.json')  
cubes = Cubes('info.json')
scraper 
# -

scraper.select_dataset(latest=True)

tabs = {tab.name: tab for tab in scraper.distribution(title=lambda t: 'Data Tables' in t).as_databaker()}

year_cell = tabs['Title'].filter('Detailed Data Tables').shift(UP)
year_cell.assert_one()
dataset_year = int(year_cell.value)
#dataset_year

# #%%capture
from T1 import tidy
tidy1 = tidy
from T2 import tidy
tidy2 = tidy
from T3 import tidy
tidy3 = tidy
from T4 import tidy
tidy4 = tidy
from T5 import tidy
tidy5 = tidy
print(tidy1['Value'].count())
print(tidy2['Value'].count())
print(tidy3['Value'].count())
print(tidy4['Value'].count())
print(tidy5['Value'].count())
table = pd.concat([tidy1,tidy2,tidy3,tidy4,tidy5])
print(table['Value'].count())
#def process_tab(t):
#    # %run "$t"
#    return tidy
#table = pd.concat(process_tab(f'{t}.py') for t in ['T1','T2','T3','T4','T5'])
#table.count()
# # +
import numpy
table['HMRC Partner Geography'] = numpy.where(table['HMRC Partner Geography'] == 'EU', 'C', table['HMRC Partner Geography'])
table['HMRC Partner Geography'] = numpy.where(table['HMRC Partner Geography'] == 'Non-EU', 'non-eu', table['HMRC Partner Geography'])
sorted(table)
#table = table[(table['Marker'] != 'residual-trade')]
#table = table[(table['Marker'] != 'below-threshold-traders')]
table["Measure Type"] = table["Measure Type"].apply(pathify)
table = table.drop_duplicates()
#Flow has been changed to Flow Direction to differentiate from Migration Flow dimension
table.rename(columns={'Flow':'Flow Directions'}, inplace=True)
table.loc[table['HMRC Partner Geography'] == 'europe', 'HMRC Partner Geography'] = 'C'
table.head(5)

# +
#table.to_csv('table.csv')
# -

#table = pd.read_csv('table.csv')
table['nanTest'] = table['Value']
table.loc[table['Value'].isna(), 'nanTest'] = '--'
table.loc[table['nanTest'] == '--', 'Value'] = 0
table['Value'] = table['Value'].astype(int)
table.loc[table['nanTest'] == '--', 'Value'] = ''
table.drop('nanTest', inplace=True, axis=1)
#table[table['Value'] == '']

# +
businessCount = table[table['Measure Type'] == 'businesses']
businessStats = table[table['Measure Type'] == 'statistical-value']
businessCount = businessCount[businessCount['HMRC Partner Geography'] != 'below-threshold-traders']
businessStats = businessStats[businessStats['HMRC Partner Geography'] != 'below-threshold-traders']

#del table
del businessCount['Measure Type']
del businessCount['Unit']
del businessStats['Measure Type']
del businessStats['Unit']


# +
mainTitle = scraper.dataset.title.replace(': 2019', '')
mainTitle = scraper.dataset.title.replace(': 2020', '')
descr = """General: 
This release uses the same allocation methodology as the Regional Trade Statistics.
Data is compiled by merging trade data collected by HMRC with employment data from the Interdepartmental Business Register (IDBR). A business’ trade is allocated to a region based on the proportion of its employees employed in that region. Where a trader is not matched with the IDBR, its trade is matched with Office for National Statistics postcode data to obtain the region in which the Head Office of the VAT registered business (importer or exporter) is based.
Not all trade can be assigned to a NUTS1 region or smaller areas. Where appropriate, this is referred to in the tables as the ‘Unallocated Trade’. This is included only in table 1 for completeness. Un-allocated Trade is split into:
i. ‘Unallocated – Known’: where we have virtually full details of the trade but it is not appropriate to allocate it to a region. This covers: 
    • trade going into or out of the Channel Islands or the Isle of Man; 
    • trade carried out by the UK Government;
    • trade carried out by overseas based traders who have a VAT presence in the UK; and
    • parcel post trade that is dealt with centrally (trade with non-EU countries only).
ii. ‘Unallocated – Unknown’: This includes:
    • Trade where business details submitted are invalid
    • Un-registered businesses (Non-EU only)
    • Private Individuals (non-EU only); and
    • Low Value Trade (non-EU only).
Certain allocations made in the RTS have not been allocated to areas smaller than NUTS1. These are Below Threshold Trade Allocations and Fixed Link Energy Allocations.
Like the RTS, this release does not include estimates for late-response. It also excludes trade in non-monetary gold, which is included in OTS data from 2005 onwards.
More information can be found in the RTS methodology document which includes additional information concerning this release. 

These are totals for all NUTS2 and NUTS3 in the UK. All values are rounded to nearest £million so there may be rounding errors when summing. See note (g) for accessing NUTS1 data if required.
The number of businesses for a high level region will be less than the sums of the business counts of their constituent smaller level regions.
The business counts at NUTS2 and NUTS3 total level include businesses under the Intrastat threshold (Below Threshold Traders)
In the RTS there are two methods used to allocate a business' trade to regions for multi-branch businesses. This release uses the 'Whole Number Method' where a business counts as 1 in each region they have a presence.
All Stores and Provisions data has been moved to residual 'Other' areas. 

Due to data availibility Below Threshold Trade is showed in two parts within the same table:
    • Number of businesses below the Intratat threshold is showed at NUTS2 and NUTS3 level. There is no value of trade associated with this nor can it be showed at partner country and type of good level;
    • Value of Below Threshold Trade is showed at NUTS1 level where it can be broken down to partner country and type of good level.
Energy Allocations refer only to trade allocated to a region where HMRC has no record of importing / exporting buisness i.e. Fixed pipelines, Exports directly from offshore oil rigs.
A very small number of cells have been removed from Tables 4 and 5 under our statistical disclosure policy. This may have led to removal of other cells to prevent calculation of removed cells by deduction.
    • The trade for that combination of variables is between 0 (i.e. no trade) and £499,999;
    • The trade has been suppressed under our statistical disclosure policy.
Users are therefore advised to consult other pubilished sources in order to access more aggregated data

Not all partner countries are showed in all breakdowns within Table 5:
    • In addition to the reasons under (o) only those partner countries published in the RTS are included. These are described in annex 2 (pages 20-25) in the published RTS Methodology;

For residual 'Other' Areas and trade not allocated to a NUTS1 region (Unallocated), disaggregation of partner country and product has been removed. This will mean that product and partner country totals may not equal those previously published in OTS and RTS.
"""

scraper.dataset.family = 'trade'
scraper.dataset.title = mainTitle + ': Business Count'
scraper.dataset.comment = scraper.dataset.title + ' - Detailed data tables'
scraper.dataset.description = descr
# -
with open("info.json", "r") as jsonFile:
    data = json.load(jsonFile)
    data["transform"]["columns"]["Value"]["measure"] = "http://gss-data.org.uk/def/measure/count"
    data["transform"]["columns"]["Value"]["unit"] = "http://gss-data.org.uk/def/concept/measurement-units/businesses"
    with open("info.json", "w") as jsonFile:
        json.dump(data, jsonFile)
cubes = Cubes("info.json")        
cubes.add_cube(copy.deepcopy(scraper), businessCount, "hmrc-rts-small-area-business-count", 'hmrc-rts-small-area-business-count', data)

# +
scraper.dataset.family = 'trade'
scraper.dataset.title = mainTitle + ': Statistical value (£ million)'
scraper.dataset.comment = scraper.dataset.title + ' - Detailed data tables'
scraper.dataset.description = descr

with open("info.json", "r") as jsonFile:
    data = json.load(jsonFile)
    data["transform"]["columns"]["Value"]["measure"] = "http://gss-data.org.uk/def/measure/gbp-million"
    data["transform"]["columns"]["Value"]["unit"] = "http://gss-data.org.uk/def/concept/measurement-units/businesses"
    with open("info.json", "w") as jsonFile:
        json.dump(data, jsonFile)
        
cubes.add_cube(copy.deepcopy(scraper), businessStats, "hmrc-rts-small-area-gbp-million", 'hmrc-rts-small-area-gbp-million', data)
# -

cubes.output_all()


