# ---
# jupyter:
#   jupytext:
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

import string
import pandas as pd
from gssutils import *
pd.options.mode.chained_assignment = None 

cubes = Cubes("info.json")


# +
def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

def mid(s, offset, amount):
    return s[offset:offset+amount]


# -

scraper = Scraper(seed='info.json')
distribution = scraper.distribution(latest=True)
distribution

# +
tabs = (t for t in distribution.as_databaker())
trace = TransformTrace()
title = distribution.title
columns = ['Period', 'Flow Directions','Product Department','Product Category','Product','CDID', 'Value']

for tab in tabs:
    if tab.name in ('Index', 'Contact'):
        continue   
    
    trace.start(title, tab, columns, distribution.downloadURL)
    cell = tab.filter(contains_string('Total'))
    
    flow_direction = tab.name

    period = cell.shift(2,-1).expand(RIGHT).is_not_blank()
    
    product = cell.expand(DOWN).is_not_blank()
    
    cdid_code = tab.excel_ref('B5').expand(DOWN)
    
    observations = product.shift(RIGHT).fill(RIGHT).is_not_blank()

    dimensions = [
        HDim(period, 'Period', DIRECTLY, ABOVE),
        HDim(cdid_code, 'CDID', DIRECTLY, LEFT),  
        HDim(product, 'Product', DIRECTLY, LEFT),
        HDimConst('Flow Directions', flow_direction),
        ]

    tidy_sheet = ConversionSegment(tab, dimensions, observations)   
    savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
    trace.with_preview(tidy_sheet)
    trace.store("combined_dataframe", tidy_sheet.topandas())

# +
pd.set_option('display.float_format', lambda x: '%.0f' % x)
df = trace.combine_and_trace(title, "combined_dataframe").fillna('')
df.rename(columns={'OBS' : 'Value'}, inplace=True)
indexNames = df[ df['Product'] == 'Residual seasonal adjustment' ].index
df.drop(indexNames, inplace = True)
df['Period'] = df['Period'].map(lambda x: 'year/' + left(x,4) if 'Q' not in x else 'quarter/' + left(x,4) + '-' + right(x,2))
df['Flow Directions'] = df['Flow Directions'].map(lambda x: right(x, len(x) - 2))

df['Product'] = df['Product'].map(lambda x: '' if ('.' not in left(x, 5) and mid(x, 2, 1) == ' ') else x)
df['Product'] = df['Product'].map(lambda x: 'All' if x == '' else x)

df['Product'] = df['Product'].map(lambda x: right(x, len(x) - 8) if mid(x, 2, 5) == 'OTHER' else x)
df['Product'] = df['Product'].map(lambda x: right(x, len(x) - 5).strip() if '.' in x else (right(x, len(x) - 4) if left(x, 2).isnumeric() == True else x))

# +
#how it was previously done 
df = df.replace({'Product' : {
    '3 Processed and preserved fish, crustaceans, molluscs, fruit and vegetables' : 'Processed and preserved fish, crustaceans, molluscs, fruit and vegetables', 
    '-6 Alcoholic beverages' : 'Alcoholic beverages', 
    '6 Manufacture of cement, lime, plaster and articles of concrete, cement and plaster' : 'Manufacture of cement, lime, plaster and articles of concrete, cement and plaster',
    '3 Basic iron and steel' : 'Basic iron and steel', 
    '5 Other basic metals and casting' : 'Other basic metals and casting'}})

for column in df:
    if column in ('Flow Directions','Product Department','Product Category','Product'):
        df[column] = df[column].map(lambda x: pathify(x))
        
df = df.replace({'Product' : {
    'a-products-of-agriculture-forestry-fishing' : 'products-of-agriculture-forestry-fishing',
    'b-mining-quarrying' : 'mining-quarrying',
    'c-manufactured-products' : 'manufactured-products',
    'd-electricity-gas-steam-air-conditioning' : 'electricity-gas-steam-air-conditioning',
    'e-water-supply-sewerage-waste-management' : 'water-supply-sewerage-waste-management',
    'j-information-communication-services' : 'information-communication-services',
    'm-professional-scientific-technical-services' : 'professional-scientific-technical-services',
    'r-arts-entertainment-recreation' : 'arts-entertainment-recreation',
    's-other-services' : 'other-services'}})

# +
from IPython.display import display, HTML
from io import BytesIO
def fetch_table(t):
    return BytesIO(scraper.session.get('https://github.com/ONS-OpenData/Ref_CDID/raw/master/lookup/' + t).content)
cdids = pd.concat((
    pd.read_csv(fetch_table(f'{k}.csv'),
                       na_values=[''], keep_default_na=False, index_col=[0,7],
                       dtype={'AREA': str, 'DIRECTION': str, 'BASIS': str,
                              'PRICE': str, 'SEASADJ': str,
                              'PRODUCT': str, 'COUNTRY': str},
                       converters={'COMMODITY': lambda x: str(x).strip()})
    for k in ['tig_cpa']), sort=False)
for col in cdids:
    cdids[col] = cdids[col].astype('category')
cdids.index = cdids.index.get_level_values('cdid')

cdids.rename(columns={
    'AREA': 'ONS Partner Geography',
    'PRICE': 'Price Classification',
    'SEASADJ': 'Seasonal Adjustment',
    'BASIS': 'International Trade Basis'
}, inplace=True)
df = pd.merge(df, cdids, how = 'left', left_on = 'CDID', right_on = 'cdid')
df = df.drop(columns=['PRODUCT', 'DIRECTION'])

# -

df = df[[ 'Period', 'CDID', 'International Trade Basis', 'Flow Directions','Product', 'Price Classification', 'Seasonal Adjustment','Value',]].drop_duplicates()
df

cubes.add_cube(scraper, df.drop_duplicates(), title)
cubes.output_all()

trace.render("spec_v1.html")

