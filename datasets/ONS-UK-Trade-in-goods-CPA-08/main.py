# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.9.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# UK trade in goods, CPA (08)

import json
import pandas as pd
from gssutils import *

cubes = Cubes('info.json')

pd.options.mode.chained_assignment = None 
pd.set_option('display.float_format', lambda x: '%.0f' % x)


# +
def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]


# -

scraper = Scraper(seed="info.json")
scraper

distribution = scraper.distribution(latest=True)
distribution

tabs = distribution.as_databaker()

# +
trace = TransformTrace()
title = distribution.title

scraper.dataset.title = 'UK trade in goods, CPA(08)'
columns = ['Period', 'Flow Direction', 'Product', 'CDID', 'Unit', 'Value']
for tab in tabs:
    if tab.name not in ['Index', 'Contact']:
        print(tab.name)
        trace.start(title, tab, columns, distribution.downloadURL)
        
        flow_direction = tab.name.split(' ', 1)[1]
        
        period = tab.excel_ref("C4").expand(RIGHT).is_not_blank()
        product = tab.excel_ref("A5").expand(DOWN).is_not_blank() 
        cdid = tab.excel_ref('B5').expand(DOWN).is_not_blank()
        observations = tab.excel_ref('C5').expand(DOWN).expand(RIGHT).is_not_blank() 

        dimensions = [
            HDim(period, 'Period', DIRECTLY, ABOVE),
            HDim(product, 'Product', DIRECTLY, LEFT),
            HDim(cdid, 'CDID', CLOSEST, ABOVE),  
            HDimConst('Flow Direction', flow_direction),
            HDimConst('Measure Type', 'gbp total'),
            HDimConst('Unit', 'gbp-million')
            ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)   
        trace.store("combined_dataframe", tidy_sheet.topandas())
# -

df = trace.combine_and_trace(title, "combined_dataframe")

# +
# df = df[df['CDID'] != ' '] 
# -

df = df[df['OBS'] != 0]

df.rename(columns={'OBS' : 'Value'}, inplace=True)
df['Value'] = df['Value'].astype(int)
df['Period'] = df['Period'].map(lambda x: 'year/' + left(x,4) if 'Q' not in x else 'quarter/' + left(x,4) + '-' + right(x,2))
df['Product'] = df['Product'].map(lambda x: x.split(' ', 1)[0])

df = df[['Period', 'Flow Direction', 'Product', 'CDID', 'Measure Type', 'Unit', 'Value']]
df['Flow Direction'] = df['Flow Direction'].apply(pathify)
df

cubes.add_cube(scraper, df, title)
cubes.output_all()

trace.render("spec_v1.html")


