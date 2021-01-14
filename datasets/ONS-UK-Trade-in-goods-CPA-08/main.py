# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.6.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
# #!/usr/bin/env python
# coding: utf-8
# %%

import string
import pandas as pd
from gssutils import *
from databaker.framework import *

pd.options.mode.chained_assignment = None #check if it's required
# -

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
scraper

distribution = scraper.distribution(latest=True)
distribution

tabs = distribution.as_databaker()

# +
trace = TransformTrace()
title = distribution.title
columns = ['Period', 'Flow Directions','Product Department','Product Category','Product','CDID', 'Value','Measure Type','Unit']

for tab in tabs:  
    if tab.name in ['Index', 'Contact']:
        continue   
    print(tab.name)

    trace.start(title, tab, columns, scraper.distributions[0].downloadURL)
#     trace.start(title, tab, columns, distribution.downloadURL)
  
    cell = tab.excel_ref("A5").expand(DOWN).is_not_blank()
    
    flow_direction = tab.name
    period = tab.excel_ref("C4").expand(RIGHT).is_not_blank()
    
    trace.Product_Department("Selected as cells A5 & A194 and as other cells from 'A' as industry or sector")
    prod_dep = cell.regex('[^0-9]+')
    
    trace.Product_Category("Selected from cells A as sub-sectors or sub-industry")
    prod_cat = cell.regex('[0-9]{2}\s{1}[^\.]')
    
    trace.Product("Selected from cells A as all items excluding: sectors and sub-sectors")
    product = cell - prod_dep - prod_cat
        
    cdid_code = tab.excel_ref('B5').expand(DOWN).is_not_blank() | tab.excel_ref("B194") # Adding a blank value  
    
    observations = tab.excel_ref('C5').expand(DOWN).expand(RIGHT).is_not_blank()
    
    dimensions = [
        HDimConst('Flow Directions', flow_direction),
        HDimConst('Measure Type', 'GBP Total'),
        HDimConst('Unit', 'GBP-million'),
        
        HDim(period, 'Period', DIRECTLY, ABOVE), #directly, left
        
        HDim(prod_dep, 'Product Department', CLOSEST, ABOVE),
        HDim(prod_cat, 'Product Category', CLOSEST, ABOVE), ### ClosestRight
        HDim(product, 'Product', CLOSEST, ABOVE), ### ClosestBelow and DirectLeft
        
        HDim(cdid_code, 'CDID', CLOSEST, ABOVE)   
        ]
   
    cs = ConversionSegment(tab, dimensions, observations)
    tidy_sheet = cs.topandas()
    trace.store("combined_dataframe", tidy_sheet)    
# -

pd.set_option('display.float_format', lambda x: '%.0f' % x) #check if req

df = trace.combine_and_trace(title, "combined_dataframe").fillna('')

indexNames = df[ df['Product Department'] == 'Residual seasonal adjustment' ].index
df.drop(indexNames, inplace = True)

df['Period'] = df['Period'].map(lambda x: 'year/' + left(x,4) if 'Q' not in x else 'quarter/' + left(x,4) + '-' + right(x,2))

df['Flow Directions'] = df['Flow Directions'].map(lambda x: right(x, len(x) - 2))

df['Product Department'] = df['Product Department'].map(lambda x: right(x, len(x) - 2) if 'Total' not in x else x)

df['Product Category'] = df['Product Category'].map(lambda x: 'All' if x == '' else x)
df['Product Category'] = df['Product Category'].map(lambda x: right(x, len(x) - 3) if left(x, 2).isnumeric() == True else x)

df['Product'] = df['Product'].map(lambda x: '' if ('.' not in left(x, 5) and mid(x, 2, 1) == ' ') else x)
df['Product'] = df['Product'].map(lambda x: 'All' if x == '' else x)
df['Product'] = df['Product'].map(lambda x: right(x, len(x) - 8) if mid(x, 2, 5) == 'OTHER' else x)
df['Product'] = df['Product'].map(lambda x: right(x, len(x) - 5).strip() if '.' in x else (right(x, len(x) - 4) if left(x, 2).isnumeric() == True else x))

df['Product'] = [x.lstrip('-') for x in df['Product']]
df['Product'] = df['Product'].str.lstrip(string.digits)

df.rename(columns={'OBS' : 'Value'}, inplace=True)

# +
for column in df:
    if column in ('Flow Directions','Product Department','Product Category','Product','Unit'):
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
        
df['Product'].unique().tolist()
# -

cubes.add_cube(scraper, df, title)
cubes.output_all()

trace.render("spec_v1.html")

