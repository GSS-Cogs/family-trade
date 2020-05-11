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

# Recent Clearances and Revenue

# +
from gssutils import *

if is_interactive():
    scraper = Scraper('https://www.uktradeinfo.com/Statistics/Pages/TaxAndDutyBulletins.aspx')
    scraper.select_dataset(title='Alcohol Duty')
    tabs = scraper.distribution(title=lambda t: t.startswith('Alcohol Duty')).as_pandas(sheet_name=None)
    tab = tabs['5']
# -

tab

observations = tab.iloc[6:44, :20]

observations

list(observations)

temp = observations.drop(['Unnamed: 1','Unnamed: 2','Unnamed: 5',                            
                          'Unnamed: 10', 'Unnamed: 12'], axis = 1)

temp.head()

temp.rename(columns= temp.iloc[1], inplace=True)

list(temp)

data = temp.iloc[6:]

data

data.columns.values[0] = 'Period'
data.columns.values[1] = 'UK Beer Production'
data.columns.values[2] = 'UK Alcohol Production'
data.columns.values[6] = 'Alcohol Clearances'
data.columns.values[7] = 'Cider Clearances'


list(data)

data

Final_table = pd.melt(data, id_vars=['Period'], var_name='Category', value_name='Value')

Final_table

Final_table.count()

Final_table.dropna(how='any',axis=0, inplace =True)

Final_table.count()

Final_table.dtypes


# +
def user_perc(x):
    
    if '*'in str(x)  :
        return 'estimated based on previous Periods'
    else:
        return ''
    
Final_table['Revision'] = Final_table.apply(lambda row: user_perc(row['Value']), axis = 1)
# -

Final_table['Value'] = Final_table['Value'].astype(str).map(lambda cell: cell.replace('*', ''))

Final_table['Value'] = pd.to_numeric(Final_table['Value'], errors='coerce')

Final_table.count()

Final_table['Category'].unique()

Final_table['Alcohol Content'] = 'Various'


# +
def user_perc5(x):
    
    if ((str(x) == 'Total Beer'))| ((str(x) == 'Total Cider')) | ((str(x) == 'Total Alcohol')): 
        
        return 'gbp-million'
    else:
        return 'hectolitres-thousands'
    
Final_table['Unit'] = Final_table.apply(lambda row: user_perc5(row['Category']), axis = 1)


# +
def user_perc6(x):
    
    if ((str(x) == 'Total Beer'))| ((str(x) == 'Total Cider')) | ((str(x) == 'Total Alcohol')) : 
        
        return 'revenue'
    else:
        return 'quantities-consumption'
    
Final_table['Measure Type'] = Final_table.apply(lambda row: user_perc6(row['Category']), axis = 1)


# +
def user_perc7(x,y):
    
    if ((str(x) ==  '2018-05-01 00:00:00')) | ((str(x) == '2018-06-01 00:00:00')) | ((str(x) == '2018-07-01 00:00:00')): 
        
        return 'provisional'
    else:
        return y
    
Final_table['Revision'] = Final_table.apply(lambda row: user_perc7(row['Period'],row['Revision']), axis = 1)


# +
def user_perc8(x,y):
    
    if ((str(x) == 'Total Alcohol')): 
        
        return 'all'
    else:
        return y
    
Final_table['Alcohol Content'] = Final_table.apply(lambda row: user_perc8(row['Category'], row['Alcohol Content']), axis = 1)
# -

Final_table['Alcohol Duty'] = 'beer-and-cider'

Final_table = Final_table[['Period','Alcohol Duty','Category','Alcohol Content','Measure Type','Value','Unit','Revision']]

Final_table.tail()

# +
# destinationFolder = Path('out')
# destinationFolder.mkdir(exist_ok=True, parents=True)

# Final_table.to_csv(destinationFolder / ('hmrcalcohol_5.csv'), index = False)
# -


