# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.10.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# The Pink Book 2019

# +
from gssutils import *
import numpy as np

cubes = Cubes("info.json")
trace = TransformTrace()

scraper = Scraper(seed="info.json")
scraper
# -

tabs = {tab.name: tab for tab in scraper.distribution(
    latest=True).as_databaker()}
list(tabs)

sheetname = ['3.2', '3.3', '3.4', '3.5', '3.6', '3.7', '3.8', '3.9', '3.10']

# +

tabs = [x for x in scraper.distribution(
    latest=True).as_databaker() if x.name in sheetname]
for tab in tabs:

    columns = ["Geography", "Period", "CDID",
               "Pink Book Services", "Flow Directions", "Value", "Marker"]
    trace.start(tab.name, tab, columns, scraper.distributions[0].downloadURL)

    anchor = tab.excel_ref('B3')

    cdid = anchor.shift(1, 0).fill(DOWN).is_not_blank().is_not_whitespace()
    trace.CDID("Selected cdids from column B")

    flow = anchor.fill(DOWN).one_of(
        ['Exports (Credits)', 'Imports (Debits)', 'Balances'])
    trace.Flow_Directions(
        "Set as one of 'Exports (Credits)', 'Imports (Debits)', 'Balances'")
    period = anchor.fill(RIGHT).is_not_blank().is_not_whitespace()

    observations = period.fill(DOWN).is_not_blank().is_not_whitespace()

    trace.Geography('Hard code geography to "K02000001"')
    geography = "K02000001"

    dimensions = [
        HDimConst('Geography', geography),
        HDim(period, 'Period', DIRECTLY, ABOVE),
        HDim(cdid, 'CDID', DIRECTLY, LEFT),
        HDim(flow, 'Flow Directions', CLOSEST, ABOVE)

    ]
    c1 = ConversionSegment(tab, dimensions, observations)

    df = c1.topandas()
    df['Period'] = df['Period'].map(
        lambda cell: cell.replace('.0', '').strip())
    df['CDID'] = df['CDID'].str.strip()
    df['OBS'].replace('', np.nan, inplace=True)
    df['Flow Directions'] = df['Flow Directions'].map(
        lambda x: {
            'Exports (Credits)': 'Exports',
            'Imports (Debits)': 'Imports',
            'Balances': 'Balance'}.get(x, x))

    df.rename(index=str, columns={'OBS': 'Value'}, inplace=True)
    trace.store("pinkbook combined dataframe", df)

df = trace.combine_and_trace(
    "pinkbook combined dataframe", "pinkbook combined dataframe")
df.head(60)
# -

classifications_table = pd.read_csv(
    "https://raw.githubusercontent.com/GSS-Cogs/Ref_CDID/master/lookup/pinkbook_pbclassifications.csv")
classifications_table.loc[-1] = ['CWVK', 'EX', '10.3.N510', 'CP', 'NSA']
classifications_table.loc[-2] = ['CWVL', 'IM', '10.3.N510', 'CP', 'NSA']
df = pd.merge(df, classifications_table, how='left',
              left_on='CDID', right_on='cdid')
df = df.rename(columns={'BPM6': 'Pink Book Services'})

classifications_table.tail()

# Below codes don't have Pink book services codes

df[df.cdid.isnull() == True]['CDID'].unique()

# Belo codes need to upload in to PMD

trace.CDID("Remove CDIDs FJOW, FJQO, FJSI")
df = df[(df['CDID'] != 'FJOW') &
        (df['CDID'] != 'FJQO') &
        (df['CDID'] != 'FJSI')]
# Temp remove CWVK & CWVL as we do not have a reference code for it, have asked BAs to look into it (appeared in 2019 publication)
#df = df[(df['CDID'] != 'CWVK') & (df['CDID'] != 'CWVL')]

# Order columns
df = df[['Geography', 'Period', 'CDID', 'Pink Book Services',
         'Flow Directions', 'Value', 'DATAMARKER']]

#df['Pink Book Services'] = df['Pink Book Services'].astype(str).apply(pathify)
print(df['Pink Book Services'].unique())
#df = df[df['Pink Book Services'].isnull() == False]

df['Marker'] = df['DATAMARKER'].map(
    lambda x: {'NA': 'not-available',
               ' -': 'nil-or-less-than-a-million'
               }.get(x, x))
#df = df.rename(columns={'SEASADJ':'Seasonal Adjustment'})

df['Pink Book Services'] = df['Pink Book Services'].astype(str)
df["Flow Directions"].unique()

trace.Flow_Directions('Pathify the "Flow Directions" column')
df['Flow Directions'] = df['Flow Directions'].str.strip().map(
    lambda x: {
        'Exports (Credits)': 'exports',
        'Imports (Debits)': 'imports',
        'Balances': 'balance'}.get(x, x)
)

df['Period'] = 'year/' + df['Period'].astype(str)
#df['Value'] = df['Value'].astype(int)

#df = df[['Geography','Period','CDID','Pink Book Services','Flow Directions', 'Value','Marker']]
df = df[['Period', 'CDID', 'Pink Book Services',
         'Flow Directions', 'Value', 'Marker']]

scraper.dataset.title = 'The Pink Book, Trade in Services'
# scraper.dataset.comment
scraper.dataset.description = scraper.dataset.description + \
    '\n Non Seasonally Adjusted'

cubes.add_cube(scraper, df.drop_duplicates(), "ONS Pink Book")
cubes.output_all()
# trace.render("spec_v1.html")

"""
a = pd.DataFrame(pd.read_csv('cdid.csv'))
a = a['Label']
d = pd.DataFrame(df['CDID'].unique(), df['CDID'].unique())
d = d.rename(columns={0:'Label'})
d.reset_index(drop=True, inplace=True)
d = d['Label']
print('A Size: ' + str(a.count()))
print('D Size: ' + str(d.count()))
b = pd.DataFrame(pd.concat([a,d]))
print('B Size: ' + str(b.count()))
b = b.drop_duplicates()
print('B Size: ' + str(b.count()))
b.columns = ['Label']
b['Notation'] = b['Label']
b['Parent Notation'] = ''
b = b.assign(Sort=add('', np.arange(1, len(b) + 1).astype(str)))
b = b.rename(columns={'Sort':'Sort Priority'})
b.drop_duplicates().to_csv('cdidnew.csv', index = False)
b
"""
#p = pd.DataFrame(pd.read_csv('pink-book-services.csv'))
#p['Notation'] = p['Notation'].replace('-','.', regex=False)
#p['Parent Notation'] = ''
#p['Notation'] = p['Notation'].astype(str).apply(pathify)
#p['Parent Notation'] = p['Parent Notation'].astype(str).apply(pathify)
#p.drop_duplicates().to_csv('pink-book-services.csv', index = False)
# p
