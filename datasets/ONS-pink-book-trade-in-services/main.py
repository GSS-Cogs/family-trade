
# %%
from gssutils import *
import numpy as np
metadata = Scraper(seed="info.json")
# %%
tabs = {tab.name: tab for tab in metadata.distribution(latest=True).as_databaker()}
#list(tabs)
# %%
tidied_sheets = []
sheetname = ['3.2', '3.3', '3.4', '3.5', '3.6', '3.7', '3.8', '3.9', '3.10']

tabs = [x for x in metadata.distribution(
    latest=True).as_databaker() if x.name in sheetname]
for tab in tabs:
    print(tab.name)
    anchor = tab.excel_ref('B3')

    cdid = anchor.shift(1, 0).fill(DOWN).is_not_blank().is_not_whitespace()

    flow = anchor.fill(DOWN).one_of(
        ['Exports (Credits)', 'Imports (Debits)', 'Balances'])
    period = anchor.fill(RIGHT).is_not_blank().is_not_whitespace()

    observations = period.fill(DOWN).is_not_blank().is_not_whitespace()

    dimensions = [
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
    tidied_sheets.append(df)


# %%
df = pd.concat(tidied_sheets, sort = True).fillna('')
# %%
classifications_table = pd.read_csv(
    "https://raw.githubusercontent.com/GSS-Cogs/Ref_CDID/master/lookup/pinkbook_pbclassifications.csv")
classifications_table.loc[-1] = ['CWVK', 'EX', '10.3.N510', 'CP', 'NSA']
classifications_table.loc[-2] = ['CWVL', 'IM', '10.3.N510', 'CP', 'NSA']
df = pd.merge(df, classifications_table, how='left',
              left_on='CDID', right_on='cdid')
df = df.rename(columns={'BPM6': 'Pink Book Services'})
classifications_table.tail()

# Below codes don't have Pink book services codes
# %%
df[df.cdid.isnull() == True]['CDID'].unique()

# Belo codes need to upload in to PMD
# %%
df = df[(df['CDID'] != 'FJOW') &
        (df['CDID'] != 'FJQO') &
        (df['CDID'] != 'FJSI')]
# Temp remove CWVK & CWVL as we do not have a reference code for it, have asked BAs to look into it (appeared in 2019 publication)
#df = df[(df['CDID'] != 'CWVK') & (df['CDID'] != 'CWVL')]
# -
df = df[df['Pink Book Services'].isnull() == False]
# %%
df['Marker'] = df['DATAMARKER'].map(
    lambda x: {'NA': 'not-available',
               ' -': 'nil-or-less-than-a-million'
               }.get(x, x))
# Order columns
df = df[['Period', 'CDID', 'Pink Book Services', 'Flow Directions', 'Value', 'Marker']]
df['Pink Book Services'] = df['Pink Book Services'].astype(str)
df['Flow Directions'] = df['Flow Directions'].str.strip().map(
    lambda x: {
        'Exports (Credits)': 'exports',
        'Imports (Debits)': 'imports',
        'Balances': 'balance'}.get(x, x)
)

df['Period'] = 'year/' + df['Period'].astype(str)
#df['Value'] = df['Value'].astype(int)

metadata.dataset.title = 'The Pink Book, Trade in Services'
metadata.dataset.description = metadata.dataset.description + \
    '\n Non Seasonally Adjusted'

df.to_csv("observations.csv", index = False)
df
#%%
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')
