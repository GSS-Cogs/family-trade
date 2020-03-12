# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.2.4
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# UK trade in goods by industry, country and commodity, imports

# +
from gssutils import *

scraper = Scraper('https://www.ons.gov.uk/economy/nationalaccounts/balanceofpayments/datasets/uktradeingoodsbyindustrycountryandcommodityimports')
scraper
# -

tabs = scraper.distributions[0].as_databaker()
for i in tabs:
    print(i.name)

tab = next(t for t in tabs if t.name =='tig_ind_im_publ')

country = tab.filter(contains_string('country')).fill(DOWN).is_not_blank().is_not_whitespace()

industry = tab.filter(contains_string('industry')).fill(DOWN).is_not_blank().is_not_whitespace()

commodity = tab.filter(contains_string('commodity')).fill(DOWN).is_not_blank().is_not_whitespace()

year = tab.excel_ref('A1').fill(RIGHT).is_not_blank().is_not_whitespace().is_number()

observations = year.fill(DOWN).is_not_blank().is_not_whitespace()

Dimensions = [
            HDim(year,'Period',DIRECTLY,ABOVE),
            HDim(country,'ONS Partner Geography',DIRECTLY,LEFT),
            HDim(commodity,'CORD SITC',DIRECTLY,LEFT),
            HDim(industry,'SIC 2007',DIRECTLY,LEFT),
            HDimConst('Measure Type', 'GBP Total'),
            HDimConst('Unit', 'gbp-million'),
            HDimConst('Flow', 'imports')
            ]
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
table = c1.topandas()

# +
# import numpy as np
# table['OBS'].replace('', np.nan, inplace=True)
# table.dropna(subset=['OBS'], inplace=True)
# if 'DATAMARKER' in table.columns:
#     table.drop(columns=['DATAMARKER'], inplace=True)
# table.rename(columns={'OBS': 'Value'}, inplace=True)
# table['Value'] = table['Value'].astype(int)
# table['Value'] = table['Value'].map(lambda x:'' if x == '...' else x )
# -

table['DATAMARKER'] = table['DATAMARKER'].map(lambda x:'suppressed' if x == '..' else x )

import numpy as np
table['OBS'].replace('', np.nan, inplace=True)
table.rename(columns={'OBS': 'Value','DATAMARKER' : 'Marker'}, inplace=True)
table['Value'] = pd.to_numeric(table['Value'], errors='coerce')

for col in table.columns:
    if col not in ['Value', 'Period']:
        table[col] = table[col].astype('category')
        display(col)
        display(table[col].cat.categories)

table['CORD SITC'].cat.categories = table['CORD SITC'].cat.categories.map(lambda x: x[:2])
table['ONS Partner Geography'].cat.categories = table['ONS Partner Geography'].cat.categories.map(lambda x: x[:2])
table['SIC 2007'].cat.categories = table['SIC 2007'].cat.categories.map(lambda x: x[:2])
display(table['CORD SITC'].cat.categories)
display(table['ONS Partner Geography'].cat.categories)
display(table['SIC 2007'].cat.categories)

table['Period'] = 'year/' + table['Period'].astype(str).str[0:4]

table = table[['ONS Partner Geography', 'Period','Flow','CORD SITC', 'SIC 2007', 'Measure Type','Value','Unit', 'Marker']]


