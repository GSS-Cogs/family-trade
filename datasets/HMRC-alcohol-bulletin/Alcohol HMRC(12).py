# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.1.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# https://www.uktradeinfo.com/Statistics/Pages/TaxAndDutybulletins.aspx

# Changes to Alcohol rates

# +
from gssutils import *

if is_interactive():
    scraper = Scraper('https://www.uktradeinfo.com/Statistics/Pages/TaxAndDutyBulletins.aspx')
    scraper.select_dataset(title='Alcohol Duty')
    tabs = scraper.distribution(title=lambda t: t.startswith('Alcohol Duty')).as_pandas(sheet_name=None)
    tab = tabs['12']
# -

tab

observations = tab.iloc[12:44, :10]

observations

list(observations)

temp = observations.drop(['Unnamed: 1','Unnamed: 4','Unnamed: 7',                            
                          ], axis = 1)

temp.head()

temp.rename(columns= temp.iloc[0], inplace=True)

list(temp)

data = temp.iloc[4:]

data.head()

data.columns.values[0] = 'Period'
data.columns.values[1] = 'Over 1.2%, up to and including 4.0%'
data.columns.values[2] = 'Over 4.0%, up to and including 5.5%'
data.columns.values[3] = 'Over 5.5%, up to and including 15.0%'
data.columns.values[4] = 'Over 15.0%, up to and including 22.0%'
data.columns.values[5] = 'Over 5.5%, less than 8.5%'
data.columns.values[6] = 'From 8.5%, up to and including 15.0%'

list(data)

data

new_table = pd.melt(data, id_vars=['Period'], var_name='Alcohol Content', value_name='Value')

new_table

new_table.count()

new_table.dropna(how='any',axis=0, inplace =True)

new_table.count()

# +
# new_table['Value'] = pd.to_numeric(new_table['Value'], errors='coerce')
# -

new_table['Alcohol Content'].unique()

new_table['Unit'] = 'gbp-per-hl-product'

new_table['Measure Type'] = 'rates-of-duty'


# +
def user_perc8(x):
    
    if ((str(x) == 'Over 5.5%, less than 8.5%')) | ((str(x) == 'From 8.5%, up to and including 15.0%')) : 
        
        return 'Sparkling Wine'
    else:
        return 'Still Wine'
    
new_table['Category'] = new_table.apply(lambda row: user_perc8(row['Alcohol Content']), axis = 1)
# -

new_table['Revision'] = ''

new_table['Alcohol Duty'] = 'wine-of-fresh-grape'

new_table = new_table[['Period','Alcohol Duty','Category','Alcohol Content','Measure Type','Value','Unit','Revision']]

new_table.tail()

new_table.dtypes

# +
# new_table['Value'] = new_table['Value'].astype(str)
# -

new_table = new_table[new_table['Value'] !=  '-' ]

Final_table = pd.DataFrame()

Final_table = pd.concat([Final_table,new_table])

observations = tab.iloc[55:84, :10]

observations

temp = observations.drop(['Unnamed: 1','Unnamed: 4','Unnamed: 7',                            
                          ], axis = 1)

temp

data = temp.iloc[2:]

data

data.columns.values[0] = 'Period'
data.columns.values[1] = 'Over 1.2%, up to and including 4.0%'
data.columns.values[2] = 'Over 4.0%, up to and including 5.5%'
data.columns.values[3] = 'Over 5.5%, up to and including 15.0%'
data.columns.values[4] = 'Over 15.0%, up to and including 22.0%'
data.columns.values[5] = 'Over 5.5%, less than 8.5%'
data.columns.values[6] = 'From 8.5%, up to and including 15.0%'

data

new_table = pd.melt(data, id_vars=['Period'], var_name='Alcohol Content', value_name='Value')

new_table.count()

new_table.dropna(how='any',axis=0, inplace =True)

new_table.count()

# +
# new_table['Value'] = pd.to_numeric(new_table['Value'], errors='coerce')
# -

new_table['Unit'] = 'gbp-per-hl-product'

new_table['Measure Type'] = 'rates-of-duty'


# +
def user_perc8(x):
    
    if ((str(x) == 'Over 5.5%, less than 8.5%')) | ((str(x) == 'From 8.5%, up to and including 15.0%')) : 
        
        return 'Sparkling Wine'
    else:
        return 'Still Wine'
    
new_table['Category'] = new_table.apply(lambda row: user_perc8(row['Alcohol Content']), axis = 1)
# -

new_table['Alcohol Content'].unique()


# +
def user_perc8(x,y):
    
    if ((str(x) == 'Over 1.2%, up to and including 4.0%')) | ((str(x) == 'Over 4.0%, up to and including 5.5%')) : 
        
        return 'Ready-to-Drink '
    else:
        return y
    
new_table['Category'] = new_table.apply(lambda row: user_perc8(row['Alcohol Content'],row['Category']), axis = 1)
# -

new_table['Revision'] = ''

new_table['Alcohol Duty'] = 'made-wine'

new_table = new_table[['Period','Alcohol Duty','Category','Alcohol Content','Measure Type','Value','Unit','Revision']]

new_table.tail()

new_table['Value'] = new_table['Value'].astype(str)

new_table = new_table[new_table['Value'] !=  '-' ]

Final_table = pd.concat([Final_table,new_table])

Final_table.count()

observations = tab.iloc[197:228, :6]

observations

list(observations)

data = observations.drop(['Unnamed: 1','Unnamed: 4'], axis = 1)

data.head()

data.columns.values[0] = 'Period'
data.columns.values[1] = 'Over 1.2%, up to and including 7.5%'
data.columns.values[2] = 'Over 7.5% but less than 8.5% '
data.columns.values[3] = 'Over 5.5% but less than 8.5%'

list(data)

new_table = pd.melt(data, id_vars=['Period'], var_name='Alcohol Content', value_name='Value')

new_table

new_table.count()

new_table.dropna(how='any',axis=0, inplace =True)

# +
# new_table['Value'] = pd.to_numeric(new_table['Value'], errors='coerce')
# -

new_table['Unit'] = 'gbp-per-hl-product'

new_table['Measure Type'] = 'rates-of-duty'

new_table['Alcohol Content'].unique()


# +
def user_perc8(x):
    
    if ((str(x) == 'Over 5.5% but less than 8.5%')) : 
        
        return 'Sparkling Cider'
    else:
        return 'Still Cider'
    
new_table['Category'] = new_table.apply(lambda row: user_perc8(row['Alcohol Content']), axis = 1)
# -

new_table['Revision'] = ''

new_table['Alcohol Duty'] = 'cider'

new_table['Value'] = new_table['Value'].astype(str)

new_table = new_table[new_table['Value'] !=  '-' ]

new_table = new_table[['Period','Alcohol Duty','Category','Alcohol Content','Measure Type','Value','Unit','Revision']]

Final_table = pd.concat([Final_table,new_table])

Final_table.count()

observations = tab.iloc[97:133, :4]

observations

data = observations.drop(['Unnamed: 1'], axis = 1)

data

data.columns.values[0] = 'Period'
data.columns.values[1] = 'Spirits-Based RTDs'
data.columns.values[2] = 'Spirits'

data

new_table = pd.melt(data, id_vars=['Period'], var_name='Category', value_name='Value')

new_table

new_table.count()

new_table.dropna(how='any',axis=0, inplace =True)

new_table.count()

# +
# new_table['Value'] = pd.to_numeric(new_table['Value'], errors='coerce')
# -

new_table['Unit'] = 'gbp-per-l-pure-alcohol'

new_table['Measure Type'] = 'rates-of-duty'

new_table['Alcohol Content'] = 'ABV 22%'

new_table['Revision'] = ''

new_table['Alcohol Duty'] = 'spirits'

new_table['Value'] = new_table['Value'].astype(str)

new_table = new_table[new_table['Value'] !=  '-' ]

new_table = new_table[['Period','Alcohol Duty','Category','Alcohol Content','Measure Type','Value','Unit','Revision']]

new_table.tail()

Final_table = pd.concat([Final_table,new_table])

Final_table.count()

observations = tab.iloc[146:175, :10]

observations

data = observations.drop(['Unnamed: 1','Unnamed: 4','Unnamed: 7', 'Unnamed: 5', 'Unnamed: 6'                          
                          ], axis = 1)

data.head(2)

data.columns.values[0] = 'Period'
data.columns.values[1] = 'Beer'
data.columns.values[2] = 'Breweries Producing 5000 Hls Or Less'
data.columns.values[3] = 'High Strength Beers'
data.columns.values[4] = 'Low Strength Beers'

# +
# data.columns.values[0] = 'Period'
# data.columns.values[1] = 'Beer'
# data.columns.values[2] = 'Breweries Producing 5000 Hls Or Less'
# data.columns.values[3] = 'Breweries Producing 5000 to 30000 Hls'
# data.columns.values[4] = 'Breweries Producing 30000 to 60000 Hls'
# data.columns.values[5] = 'High Strength Beers'
# data.columns.values[6] = 'Low Strength Beers'
# -

new_table = pd.melt(data, id_vars=['Period'], var_name='Category', value_name='Value')

new_table

new_table.count()

new_table.dropna(how='any',axis=0, inplace =True)

new_table.count()

new_table.dtypes

new_table['Unit'] = 'gbp-per-1-abv-per-hl'

new_table['Measure Type'] = 'rates-of-duty'

new_table['Revision'] = ''

new_table['Category'].unique()


# +
def user_perc8(x):
    
    if ((str(x) == 'Low Strength Beers')) : 
        
        return '1.2% to 2.8%'
    else:
        return 'Various'
    
new_table['Alcohol Content'] = new_table.apply(lambda row: user_perc8(row['Category']), axis = 1)


# +
def user_perc8(x,y):
    
    if ((str(x) == 'High Strength Beers')) : 
        
        return 'ABV 7.5%'
    else:
        return y
    
new_table['Alcohol Content'] = new_table.apply(lambda row: user_perc8(row['Category'], row['Alcohol Content']), axis = 1)
# -

new_table['Alcohol Duty'] = 'beer'

new_table = new_table[['Period','Alcohol Duty','Category','Alcohol Content','Measure Type','Value','Unit','Revision']]

new_table.tail()

new_table['Value'] = new_table['Value'].astype(str)

new_table = new_table[new_table['Value'] !=  '-' ]

Final_table = pd.concat([Final_table,new_table])

Final_table = Final_table[Final_table['Value'] !=  '-' ]

Final_table = Final_table[Final_table['Value'] !=  '' ]

Final_table['Period'] = [x.split(' ')[0] for x in Final_table['Period']]

Final_table['Value'] = Final_table['Value'].astype(str)

Final_table['Value'] = Final_table['Value'].map(lambda cell: cell.replace('to', '-'))

Final_table.dropna()

Final_table = Final_table[['Period','Category','Alcohol Duty','Alcohol Content','Measure Type','Value','Unit','Revision']]

# +
# destinationFolder = Path('out')
# destinationFolder.mkdir(exist_ok=True, parents=True)

# Final_table.to_csv(destinationFolder / ('hmrcalcohol_12.csv'), index = False)
# -

Final_table.head()
