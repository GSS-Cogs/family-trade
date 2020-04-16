# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# ###  ABS to Tidydata

# +
from gssutils import *
import json

with open("info.json") as f:
    info = json.load(f)
    
scraper = Scraper(info["landingPage"])
scraper
# -

sheets = scraper.distributions[0].as_databaker()

# +
import re
tab_name_re = re.compile(r'^([0-9]{4}) (.*)$')
tidy = pd.DataFrame()

for sheet in sheets[1:-1]:
    name_match = tab_name_re.match(sheet.name)
    #print (sheet.name)
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
        classifiers = HDim(classifiers, breakdown, DIRECTLY, LEFT)
        classifiers.AddCellValueOverride('2 to9', '2 to 9')
        import_export = sheet.filter(starts_with(breakdown)).fill(RIGHT).is_not_blank()
        import_export = HDim(import_export, 'Import/Export', DIRECTLY, UP)
        import_export.AddCellValueOverride('Businesses 4', 'Businesses')
        import_export.AddCellValueOverride('Exporter and/or Importer 7', 'Exporter and/or Importer')
        measure = sheet.filter(starts_with(breakdown)).shift(UP).fill(RIGHT).is_not_blank()
        measure = HDim(measure, 'Measure Type', CLOSEST, LEFT)
        measure.AddCellValueOverride('Number of 5', 'Count')
        measure.AddCellValueOverride('% 6', 'Proportion of all Business')
        tidy = tidy.append(ConversionSegment(breakdown_obs, [classifiers, import_export, year, trade, measure]).topandas(), sort=True)
#         savepreviewhtml([breakdown_obs, classifiers, import_export, measure])
        #break
    #break

##tidy
# -

# Check for duplicate rows

assert tidy.duplicated().sum() == 0, 'duplicate rows'

# "Employment" is the parent of "Detailed employment".
#
# Also, the class "250 and over" is repeated in each, so we need to drop the duplicates. However, there appear to be some discrepancies.

# +
duplicate_label = '250 and over'
emp_250 = tidy[tidy['Employment'] == duplicate_label].drop(columns=['Employment', 'Detailed employment']).reset_index(drop=True)
detailed_emp_250 = tidy[tidy['Detailed employment'] == duplicate_label].drop(columns=['Employment', 'Detailed employment']).reset_index(drop=True)
assert emp_250.size > 0
assert detailed_emp_250.size > 0
#assert emp_250.equals(detailed_emp_250)
merged = emp_250.merge(detailed_emp_250, indicator=True, how='outer')

#display(merged[merged['_merge'] == 'right_only'])

tidy = tidy[tidy['Detailed employment'] != '250 and over'].reset_index(drop=True)
# -

# We need to merge them and also list their values so that we can create a codelist.

display(tidy['Employment'].unique())
display(tidy['Detailed employment'].unique())
tidy['employees'] = tidy.apply(lambda x: x['Employment'] if pd.notnull(x['Employment']) else x['Detailed employment'], axis=1)
tidy = tidy.drop(columns=['Employment', 'Detailed employment'])

# Fill NaN with top values.

tidy.fillna(value={'Age': 'Any', 'Ownership': 'Any', 'Turnover': 'Any', 'employees': 'Any' }, inplace=True)

# Show the range of the codes and check for duplicated rows.

from IPython.core.display import HTML
for col in tidy:
    if col not in ['OBS']:
        display(HTML(f'<h2>{col}</h2>'))
        display(tidy[col].unique())
dups = tidy.duplicated()
#display(dups.sum())
tidy[dups]

# We need to specify the units of the observations.

# +
tidy['Unit'] = tidy['Measure Type'].map(lambda x: 'Businesses' if x == 'Count' else 'Percent')


tidy = tidy.replace({'Import/Export' : {
    'both Exporter and Importer'   : 'Exporter and Importer',
    'either Exporter and/or Importer 7' : 'Exporter and/or Importer'}})
# -

# And rename some columns.

tidy.rename(columns={'Turnover': 'turnover',
                     'Ownership': 'Country of Ownership',
                     'OBS': 'Value',
                     'Trade': 'ONS ABS Trade'
                    }, inplace=True)

# Update labels as according to Ref_trade codelist

tidy['Country of Ownership'] = tidy['Country of Ownership'].str.lower()
tidy

# +

c=pd.read_csv("https://raw.githubusercontent.com/GSS-Cogs/ref_trade/master/codelists/age-of-business.csv")
tidy = pd.merge(tidy, c, how = 'left', left_on = 'Age', right_on = 'Label')
tidy.columns = ['Age of Business' if x=='Notation' else x for x in tidy.columns]

c=pd.read_csv("https://raw.githubusercontent.com/GSS-Cogs/ref_trade/master/codelists/exporter-and-importer-activity.csv")
tidy = pd.merge(tidy, c, how = 'left', left_on = 'Import/Export', right_on = 'Label')
tidy.columns = ['Export and Import Activity' if x=='Notation' else x for x in tidy.columns]

c=pd.read_csv("https://raw.githubusercontent.com/GSS-Cogs/family-trade/master/reference/codelists/turnover-size-bands.csv")
tidy = pd.merge(tidy, c, how = 'left', left_on = 'turnover', right_on = 'Label')
tidy.columns = ['Turnover' if x=='Notation' else x for x in tidy.columns]

c=pd.read_csv("https://raw.githubusercontent.com/GSS-Cogs/family-trade/master/reference/codelists/employment-size-bands.csv")
tidy = pd.merge(tidy, c, how = 'left', left_on = 'employees', right_on = 'Label')
tidy.columns = ['Employment' if x=='Notation' else x for x in tidy.columns]

tidy.head()
# -

tidy.head(2)

tidy.rename(columns={'Turnover': 'Turnover(GBP Thousands)',
                     'Age of Business': 'Age of Business(Years)'
                    }, inplace=True)

tidy = tidy[['Age of Business(Years)', 'Export and Import Activity','Measure Type','Value',
             'Country of Ownership','ONS ABS Trade','Turnover(GBP Thousands)','Year','Employment','Unit']]

# +
# Use pathify to match csv values as per new style
for col in ["ONS ABS Trade"]:
    tidy[col] = tidy[col].apply(pathify)

out = Path('out')
out.mkdir(exist_ok=True, parents=True)

tidy.to_csv(out / ('observations.csv'), index = False)

tidy

# +
scraper.dataset.family = 'trade'
scraper.dataset.comment = scraper.dataset.comment.replace('Importers and exporters of goods and services',
                                                          'Importers and exporters of trade goods and services')
from gssutils.metadata import THEME
scraper.dataset.theme = THEME['business-industry-trade-energy']

destinationFolder = Path('out')
destinationFolder.mkdir(exist_ok=True, parents=True)

with open(destinationFolder / f'observations.csv-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())
            
schema = CSVWMetadata('https://gss-cogs.github.io/family-trade/reference/')
schema.create(destinationFolder / f'observations.csv', destinationFolder / f'observations.csv-schema.json')
# -


