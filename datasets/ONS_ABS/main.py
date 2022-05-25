# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.8
#   kernelspec:
#     display_name: Python 3.9.12 64-bit
#     language: python
#     name: python3
# ---

# ###  ABS to Tidydata

# +
from gssutils import *
import json
import copy 
import re

cubes = Cubes("info.json")
with open("info.json") as f:
    info = json.load(f)
    
metadata = Scraper(info["landingPage"])
metadata
# -

sheets = metadata.distribution(latest=True).as_databaker()
metadata.distribution(latest=True)

all_tidy = []

tab_name_re = re.compile(r'^([0-9]{4}) (.*)$')
print(tab_name_re)

for sheet in sheets[2:5]:
    try:
        name_match = tab_name_re.match(sheet.name)
        assert name_match, "sheet name doesn't match regex"
        for breakdown in ['Detailed employment', 'Employment', 'Turnover']:
            year = HDimConst('Year', name_match.group(1))
            trade = HDimConst('Trade', name_match.group(2).strip())
            breakdown_on_down = sheet.filter(starts_with(breakdown)).fill(DOWN).expand(RIGHT).is_not_blank()
            breakdown_obs = breakdown_on_down - \
                breakdown_on_down.filter(contains_string('Total')).expand(DOWN).expand(RIGHT) - \
                sheet.filter(starts_with(breakdown)).fill(DOWN)
            classifiers = sheet.filter(starts_with(breakdown)).fill(DOWN).is_not_blank()
            classifiers = classifiers - classifiers.filter(contains_string('Total')).expand(DOWN)
            classifiers = HDim(classifiers, breakdown, DIRECTLY, LEFT, cellvalueoverride={'2 to9': '2 to 9'})
            import_export = sheet.filter(starts_with(breakdown)).fill(RIGHT).is_not_blank()
            import_export = HDim(import_export, 'Import/Export', DIRECTLY, ABOVE, cellvalueoverride={'Businesses 4':'Businesses', 'Exporter and/or Importer 7':'Exporter and/or Importer'})
            measure = sheet.filter(starts_with(breakdown)).shift(UP).fill(RIGHT).is_not_blank()
            measure = HDim(measure, 'Measure Type', CLOSEST, LEFT, cellvalueoverride={'Number of 5':'Count', '% 6':'Proportion of all Business'})
            tidy_sheet = ConversionSegment(breakdown_obs, [classifiers, import_export, year, trade, measure])
            all_tidy.append(tidy_sheet.topandas()) 
    except Exception as err:
        raise Exception(f'Issue encountered on tab {sheet.name}') from err

for sheet in sheets[5:10]:
    try:
        name_match = tab_name_re.match(sheet.name)
        assert name_match, "sheet name doesn't match regex"
        for breakdown in ['Detailed employment', 'Employment', 'Ownership', 'Turnover', 'Age']:
            year = HDimConst('Year', name_match.group(1))
            trade = HDimConst('Trade', name_match.group(2).strip())
            breakdown_on_down = sheet.filter(starts_with(breakdown)).fill(DOWN).expand(RIGHT).is_not_blank()
            breakdown_obs = breakdown_on_down - \
                breakdown_on_down.filter(contains_string('Total')).expand(DOWN).expand(RIGHT) - \
                sheet.filter(starts_with(breakdown)).fill(DOWN)
            classifiers = sheet.filter(starts_with(breakdown)).fill(DOWN).is_not_blank()
            classifiers = classifiers - classifiers.filter(contains_string('Total')).expand(DOWN)
            classifiers = HDim(classifiers, breakdown, DIRECTLY, LEFT, cellvalueoverride={'2 to9': '2 to 9'})
            import_export = sheet.filter(starts_with(breakdown)).fill(RIGHT).is_not_blank()
            import_export = HDim(import_export, 'Import/Export', DIRECTLY, ABOVE, cellvalueoverride={'Businesses 4':'Businesses', 'Exporter and/or Importer 7':'Exporter and/or Importer'})
            measure = sheet.filter(starts_with(breakdown)).shift(UP).fill(RIGHT).is_not_blank()
            measure = HDim(measure, 'Measure Type', CLOSEST, LEFT, cellvalueoverride={'Number of 5':'Count', '% 6':'Proportion of all Business'})
            tidy_sheet = ConversionSegment(breakdown_obs, [classifiers, import_export, year, trade, measure])
            all_tidy.append(tidy_sheet.topandas())
    except Exception as err:
        raise Exception(f'Issue encountered on tab {sheet.name}') from err

for sheet in sheets[10:-1]:
    try:
        name_match = tab_name_re.match(sheet.name)
        assert name_match, "sheet name doesn't match regex"
        for breakdown in ['Detailed employment', 'Employment', 'Ownership', 'Turnover']:
            year = HDimConst('Year', name_match.group(1))
            trade = HDimConst('Trade', name_match.group(2).strip())
            breakdown_on_down = sheet.filter(starts_with(breakdown)).fill(DOWN).expand(RIGHT).is_not_blank()
            breakdown_obs = breakdown_on_down - \
                breakdown_on_down.filter(contains_string('Total')).expand(DOWN).expand(RIGHT) - \
                sheet.filter(starts_with(breakdown)).fill(DOWN)
            classifiers = sheet.filter(starts_with(breakdown)).fill(DOWN).is_not_blank()
            classifiers = classifiers - classifiers.filter(contains_string('Total')).expand(DOWN)
            classifiers = HDim(classifiers, breakdown, DIRECTLY, LEFT, cellvalueoverride={'2 to9': '2 to 9'})
            import_export = sheet.filter(starts_with(breakdown)).fill(RIGHT).is_not_blank()
            import_export = HDim(import_export, 'Import/Export', DIRECTLY, ABOVE, cellvalueoverride={'Businesses 4':'Businesses', 'Exporter and/or Importer 7':'Exporter and/or Importer'})
            measure = sheet.filter(starts_with(breakdown)).shift(UP).fill(RIGHT).is_not_blank()
            measure = HDim(measure, 'Measure Type', CLOSEST, LEFT, cellvalueoverride={'Number of 5':'Count', '% 6':'Proportion of all Business'})
            tidy_sheet = ConversionSegment(breakdown_obs, [classifiers, import_export, year, trade, measure])
            all_tidy.append(tidy_sheet.topandas())
    except Exception as err:
        raise Exception(f'Issue encountered on tab {sheet.name}') from err

tidy = pd.concat(all_tidy,sort = True)

# Check for duplicate rows

#assert tidy.duplicated().sum() == 0, 'duplicate rows'
tidy.head()
tidy["Measure Type"].unique()

# "Employment" is the parent of "Detailed employment".
#
# Also, the class "250 and over" is repeated in each, so we need to drop the duplicates. However, there appear to be some discrepancies.

# We need to merge them and also list their values so that we can create a codelist.

print(tidy.columns.values)
print(tidy['Employment'].unique())
print(tidy['Detailed employment'].unique())
tidy['employees'] = tidy.apply(lambda x: x['Employment'] if pd.notnull(x['Employment']) else x['Detailed employment'], axis=1)
tidy = tidy.drop(columns=['Employment', 'Detailed employment'])

# Fill NaN with top values.

tidy.fillna(value={'Age': 'All', 'Ownership': 'All', 'Turnover': 'All', 'employees': 'All' }, inplace=True)
tidy.head()

# Show the range of the codes and check for duplicated rows.

# We need to specify the units of the observations.

# +
tidy['Age'].loc[(tidy['Age'] == "<2")] = "0-2"
tidy['Age'] = tidy['Age'].str.replace("<","")
tidy['Age'] = tidy['Age'].str.replace("+","plus")

tidy['Unit'] = tidy['Measure Type'].map(lambda x: 'Businesses' if x == 'Count' else 'Percent')


tidy = tidy.replace({'Import/Export' : {
    'both Exporter and Importer'   : 'Exporter and Importer',
    'either Exporter and/or Importer 7' : 'Exporter and-or Importer'}})

tidy = tidy.replace({'Turnover' : {'<1000': '0-1000'}})
tidy['Turnover'] = tidy['Turnover'].str.replace(",","")
tidy['Turnover'] = tidy['Turnover'].apply(pathify)

tidy['employees'] = tidy['employees'].apply(pathify)
tidy["Year"] = "year/" + tidy["Year"].astype(str)
# tidy.head()
# -

# And rename some columns.

# +
tidy.rename(columns={
                     'Ownership': 'Country of Ownership',
                     'OBS': 'Value',
                     'Trade': 'Trade Group',
                     "Age": "Age of Business", 
                     "Import/Export": "Business Activity",
                     "employees": "Employees"
                    }, inplace=True)

tidy = tidy.replace({'Business Activity' : {'Businesses': 'all'}})
# tidy.head()
# -

# Update labels as according to Ref_trade codelist

for c in tidy.columns:
    if (c != "Value") & (c != "Year"):
        tidy[c] = tidy[c].apply(pathify)

tidy = tidy.replace({'Employees' : {'250-and-over': '250'}})
tidy = tidy[['Year','Age of Business', 'Business Activity','Country of Ownership','Trade Group','Turnover'
             ,'Employees','Unit','Measure Type', 'Value']]
tidy.head()

metadata.dataset.description = metadata.dataset.description + """
Users should note that an Annual Business Survey (ABS) sample re-optimisation has been included in the estimates from 2016 onwards. This was last carried out in 2016 and occurs every five years to improve the efficiency of the ABS sample, estimation and reduce sample variability as part of the regular process to improve estimates.
This re-optimisation has led to a discontinuity between 2015 and 2016 within small and medium sized businesses (those with fewer than 250 employment). Therefore users should not make year-on-year comparisons between 2015 and 2016.

The questions and methodology used to compute these statistics are in their infancy. At this stage the estimates should be considered 	
experimental official statistics - https://www.ons.gov.uk/methodology/methodologytopicsandstatisticalconcepts/guidetoexperimentalstatistics	
	
Notes	
	
1. This spreadsheet contains Annual Business Survey (ABS) revised final estimates on exporters and importers for 2017, revised final estimates for 2018 and final estimates for 2019.
	
2. More details on the methodology used to produce these estimates and the things to be aware of when using the data can be found in the:
	Exporters and Importers in Great Britain, 2014 Information Paper - https://webarchive.nationalarchives.gov.uk/ukgwa/20160105160709/http://www.ons.gov.uk/ons/guide-method/method-quality/specific/business-and-energy/annual-business-survey/quality-and-methods/information-paper--annual-business-survey--abs---exporters-and-importers-in-great-britain--2014.pdf
	
3. These estimates do not cover all businesses. They do not cover:
 
• Businesses in Northern Ireland, only those in Great Britain. 
• Businesses in the Insurance and reinsurance industries – Section K (65.1 and 65.2) 
• The majority of the agriculture sector. 
• Unregistered businesses (those not registered for PAYE or VAT). As coverage of the ABS estimates is not for all businesses it may be more appropriate for users to focus on the percentages rather than the levels. 

4. The export figures plus the import figures will not sum to the total proportion of businesses trading internationally as some businesses do both import and export. This overlap is provided in the tables (labelled both Exporter and Importer). Further, the goods figures plus the services figures do not sum to the goods and/or services figures as some businesses undertake trade in both goods and services. The Information Note provides more detail of how to interpret the data in these tables.

"""

tidy.to_csv("observations.csv", index = False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')
