# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.7.1
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

tabs = { tab.name: tab for tab in scraper.distribution(latest=True).as_databaker() }
list(tabs)

sheetname = ['3.2','3.3','3.4','3.5','3.6','3.7','3.8','3.9','3.10']

# +

tabs = [x for x in scraper.distribution(latest=True).as_databaker() if x.name in sheetname]
for tab in tabs:
    
    columns=["Geography", "Period", "CDID", "Pink Book Services", "Flow Directions", "Value", "Marker"]
    trace.start(tab.name, tab, columns, scraper.distributions[0].downloadURL)
    
    anchor = tab.excel_ref('B3')
    
    cdid = anchor.shift(1,0).fill(DOWN).is_not_blank().is_not_whitespace()
    trace.CDID("Selected cdids from column B")
        
    flow = anchor.fill(DOWN).one_of(['Exports (Credits)', 'Imports (Debits)', 'Balances'])
    trace.Flow_Directions("Set as one of 'Exports (Credits)', 'Imports (Debits)', 'Balances'")
    period = anchor.fill(RIGHT).is_not_blank().is_not_whitespace()            
    
    observations = period.fill(DOWN).is_not_blank().is_not_whitespace() 
    
    trace.Geography('Hard code geography to "K02000001"')
    geography = "K02000001"
    
    dimensions = [
                HDimConst('Geography', geography),
                HDim(period,'Period', DIRECTLY,ABOVE),
                HDim(cdid,'CDID', DIRECTLY,LEFT),
                HDim(flow, 'Flow Directions', CLOSEST, ABOVE)           

    ]
    c1 = ConversionSegment(tab, dimensions, observations)
    
    df = c1.topandas()
    df['Period'] = df['Period'].map(lambda cell: cell.replace('.0', '').strip())
    df['CDID'] = df['CDID'].str.strip()
    df['OBS'].replace('', np.nan, inplace=True)
    df['Flow Directions'] = df['Flow Directions'].map(
        lambda x: {
            'Exports (Credits)': 'Exports',
            'Imports (Debits)': 'Imports',
            'Balances': 'Balance'}.get(x, x))
    
    df.rename(index= str, columns={'OBS': 'Value'}, inplace=True)
    trace.store("pinkbook combined dataframe", df)

df = trace.combine_and_trace("pinkbook combined dataframe", "pinkbook combined dataframe")
df
# -

PBclassification_table_url = 'https://drive.google.com/uc?export=download&id=1uNwmZHgq7ERqD5wcND4W2sGHXRJyP2CR'
classifications_table = pd.read_excel(PBclassification_table_url, sheet_name = 0)
df = pd.merge(df, classifications_table, how = 'left', left_on = 'CDID', right_on = 'cdid')
df = df.rename(columns={'BPM6':'Pink Book Services'})

classifications_table

# Below codes don't have Pink book services codes

df[df.cdid.isnull() == True]['CDID'].unique()

# Belo codes need to upload in to PMD

trace.CDID("Remove CDIDs FJOW, FJQO, FJSI")
df = df[(df['CDID'] != 'FJOW') &
                       (df['CDID'] != 'FJQO') &
                       (df['CDID'] != 'FJSI')]

# Order columns
df = df[['Geography','Period','CDID','Pink Book Services','Flow Directions','Value','DATAMARKER']]

print(df['Pink Book Services'].unique())
df = df[df['Pink Book Services'].isnull() == False]

df['Marker'] = df['DATAMARKER'].map(
    lambda x: { 'NA' : 'not-available' ,
               ' -' : 'nil-or-less-than-a-million'
        }.get(x, x))

df['Pink Book Services'] = df['Pink Book Services'].astype(str)
df["Flow Directions"].unique()

trace.Flow_Directions('Pathify the "Flow Directions" column')
df['Flow Directions'] = df['Flow Directions'].str.strip().map(
        lambda x: {
            'Exports (Credits)': 'exports',
            'Imports (Debits)': 'imports',
            'Balances': 'balance'}.get(x, x)
        )

df['Period'] = 'year/' + df['Period']

df = df[['Geography','Period','CDID','Pink Book Services','Flow Directions', 'Value','Marker']]

cubes.add_cube(scraper, df.drop_duplicates(), "03 Trade in services, The Pink Book")
cubes.output_all()
trace.render("spec_v1.html")


