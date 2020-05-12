# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py
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

import glob
from gssutils import *
from gssutils.metadata import THEME
import pandas as pd

next_table = pd.DataFrame()

# +
# %%capture

# %run 'T1_T2_ Wine_Duty_wine_and_made_wine.py' 
next_table = pd.concat([next_table, Final_table])

# %run "T3_Spirits_Duty_statistics.py"
next_table = pd.concat([next_table, Final_table])

# %run 'T4_ Beer_Duty_and_Cider_Duty_statistics.py'
next_table = pd.concat([next_table, Final_table])

# %run 'R2_Historic_alcohol_duty_rates.py'
next_table = pd.concat([next_table, Final_table])

# +
next_table = next_table.replace({'Measure Type' : { 'quantities-consumption' : 'Quantities Released for Consumption','revenue' : 'Revenue',
                                    'potable-spirits':'Production of Potable Spirits','net-quantities-spirits':'Net Quantities of Spirits Charged with Duty',
                                    'uk-beer':'UK Beer Production', 'alcohol-clearences':'Alcohol Clearances',
                                    'beer-clearences':'Beer Clearances','cider-clearences':'Cider Clearances','rates-of-duty':'Rates of Duty'
                              }})

next_table = next_table.replace({'Alcohol Category' : { 'UK Beer Production' : 'total-beer', 'UK Alcohol Production' : 'total-alcohol-production',
                                                       'Alcohol Clearances' : 'total-alcohol-clearances', 'Cider Clearances' : 'total-cider-clearances', 
                                                       'Still Wine' : 'still', 'Sparkling Wine' : 'sparkling', 'Ready-to-Drink' : 'rtd', 'Spirits-Based RTDs' : 'spirit-based-rtds', 
                                                       'Breweries Producing 5000 Hls Or Less' : 'breweries-5000-less', 'Still Cider' : 'Still', 'Sparkling Cider' : 'Sparkling',
                                                       'Breweries Producing 5000 Hls Or Less2' : 'breweries-5000-less'
                              }})

next_table = next_table.replace({'Alcohol Content' : { 'Various': 'all', 'various': 'all','Over 1.2%, up to and including 4.0%' : 'over-1-2-up-to-and-incl-4-0',
                                                      'Over 4.0%, up to and including 5.5%' : 'over-4-0-up-to-and-incl-5-5',
                                                      'Over 5.5%, up to and including 15.0%' : 'over-5-5-up-to-and-incl-15-0',
                                                      'Over 15.0%, up to and including 22%' : 'over-15-0-up-to-and-incl-22',
                                                      'From 8.5%, up to and including 15.0%': 'from-8-5-up-to-and-incl-15-0',
                                                      'Exceeding 1.2% but less than 6.9% abv' : 'exceed-1-2-less-than-6-9-abv',
                                                      'At least 6.9% but not exceeding 7.5% abv' : 'at-least-6-9-not-exceed-7-5-abv',
                                                      'Exceeding 7.5% but less than 8.5% abv' : 'exceed-7-5-less-than-8-5-abv',
                                                      'Exceeding 5.5% but less than 8.5% abv' : 'exceed-5-5-less-than-8-5-abv'      
                                                      
                              }})



next_table['Revision'] = next_table['Revision'].map(
    lambda x: {
        'estimated based on previous Periods' : 'estimated', 
        'estimated based on previous years' : 'estimated',
        '': 'original-value',
        'P' : 'provisional',
        'R' : 'revised'
       }.get(x, x))


# -

next_table['Alcohol Content'].unique()

next_table['Revision'].unique()

next_table['Alcohol Category'] = next_table['Alcohol Category'].map(lambda x: pathify(x))
next_table['Alcohol Content'] = next_table['Alcohol Content'].map(lambda x: pathify(x))

# +
destinationFolder = Path('out')
destinationFolder.mkdir(exist_ok=True, parents=True)

next_table.to_csv(destinationFolder / ('observations.csv'), index = False)
# +
scraper.dataset.family = 'trade'
from gssutils.metadata import THEME

with open(destinationFolder / 'observations.csv-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())
# -

csvw = CSVWMetadata('https://gss-cogs.github.io/family-trade/reference/')
csvw.create(destinationFolder / 'observations.csv', destinationFolder / 'observations.csv-schema.json')

next_table


