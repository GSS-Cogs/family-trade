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

# +
from gssutils import *

if is_interactive():
    scraper = Scraper('https://www.uktradeinfo.com/Statistics/Pages/TaxAndDutyBulletins.aspx')
    scraper.select_dataset(title='Alcohol Duty')
    tabs = scraper.distribution(title=lambda t: t.startswith('Alcohol Duty')).as_pandas(sheet_name=None)
    tab = tabs['8']
# -

tab

observations = tab.iloc[7:284, :20]

observations

list(observations)

temp = observations.drop(['Unnamed: 1','Unnamed: 2','Unnamed: 4',                            
                          'Unnamed: 6', 'Unnamed: 8', 'Unnamed: 9',
                         'Unnamed: 10', 'Unnamed: 13', 'Unnamed: 14',
                         'Unnamed: 15', 'Unnamed: 16', 'Unnamed: 17'], axis = 1)

temp.head()

temp.rename(columns= temp.iloc[0], inplace=True)

list(temp)

data = temp.iloc[3:]

data

data.columns.values[0] = 'Period'

list(data)

data

Final_table = pd.melt(data, id_vars=['Period'], var_name='Category', value_name='Value')

Final_table

Final_table.count()

Final_table.dropna(how='any',axis=0, inplace =True)

Final_table.count()

Final_table.dtypes

Final_table['Value'] = pd.to_numeric(Final_table['Value'], errors='coerce')

Final_table.count()

Final_table['Category'].unique()

Final_table['Category'] = Final_table['Category'].map(
    lambda x: {
        'Above 1.2% but not exceeding 5.5% ABV ' : 'Above 1.2% but not exceeding 5.5% ABV',
        'Imported \nex-ship' : 'Imported ex-ship',
        'Total wine1 ': 'Total Wine'
        }.get(x, x))


# +
def user_perc2(x):
    
    if ((str(x) ==  'Still')) | ((str(x) == 'Sparkling')): 
        
        return 'Above 5.5% ABV but not exceeding 15%'
    else:
        return 'Composition by Origin above 5.5% ABV'
    
Final_table['Alcohol Content'] = Final_table.apply(lambda row: user_perc2(row['Category']), axis = 1)


# +
def user_perc3(x,y):    
    if x.strip() == 'Above 1.2% but not exceeding 5.5% ABV':
        return 'Above 1.2% but not exceeding 5.5% ABV'
    else:
        return y        
    
Final_table['Alcohol Content'] = Final_table.apply(lambda row: user_perc3(row['Category'], row['Alcohol Content']), axis = 1)


# +
def user_perc4(x,y):
    
    if ((str(x) ==  'Total made wine')) | ((str(x) == 'Total Wine'))| ((str(x) == 'Total Alcohol')): 
        
        return 'Total'
    else:
        return y
    
Final_table['Alcohol Content'] = Final_table.apply(lambda row: user_perc4(row['Category'], row['Alcohol Content']), axis = 1)


# +
def user_perc5(x):
    
    if ((str(x) == 'Total Wine'))| ((str(x) == 'Total Alcohol')): 
        
        return 'gbp-million'
    else:
        return 'hectolitres'
    
Final_table['Unit'] = Final_table.apply(lambda row: user_perc5(row['Category']), axis = 1)


# +
def user_perc6(x):
    
    if ((str(x) == 'Total Wine'))| ((str(x) == 'Total Alcohol')): 
        
        return 'revenue'
    else:
        return 'quantities-consumption'
    
Final_table['Measure Type'] = Final_table.apply(lambda row: user_perc6(row['Category']), axis = 1)


# +
def user_perc7(x):
    
    if ((str(x) ==  '2018-05-01 00:00:00')) | ((str(x) == '2018-06-01 00:00:00')) | ((str(x) == '2018-07-01 00:00:00')): 
        
        return 'provisional'
    else:
        return ''
    
Final_table['Revision'] = Final_table.apply(lambda row: user_perc7(row['Period']), axis = 1)
# -

Final_table['Alcohol Duty'] = 'made-wine'

Final_table = Final_table[['Period','Alcohol Duty','Category','Alcohol Content','Measure Type','Value','Unit','Revision']]

Final_table.tail()

# +
# destinationFolder = Path('out')
# destinationFolder.mkdir(exist_ok=True, parents=True)

# Final_table.to_csv(destinationFolder / ('hmrcalcohol_8.csv'), index = False)
# -


