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

# Historic Quantities Released For Consumption and Revenue

# +
from gssutils import *

if is_interactive():
    scraper = Scraper('https://www.uktradeinfo.com/Statistics/Pages/TaxAndDutyBulletins.aspx')
    scraper.select_dataset(title='Alcohol Duty')
    tabs = scraper.distribution(title=lambda t: t.startswith('Alcohol Duty')).as_pandas(sheet_name=None)
    tab = tabs['9']
# -

tab

observations = tab.iloc[7:284, :16]

observations.head(2)

list(observations)

temp = observations.drop(['Unnamed: 1','Unnamed: 2','Unnamed: 4',                            
                          'Unnamed: 8', 'Unnamed: 12'], axis = 1)

temp.head(10)

temp.rename(columns= temp.iloc[0], inplace=True)

list(temp)

data = temp.iloc[3:]

data.head()

data.columns.values[0] = 'Period'
data.columns.values[1] = 'Production of Potable Spirits'
data.columns.values[4] = 'Total Home Produced Whisky'
data.columns.values[7] = 'Net Quantities of Spirits Charged with Duty'
data.columns.values[3] = 'Grain and Blended'

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
        return 'estimated based on previous years'
    else:
        return ''
    
Final_table['Revision'] = Final_table.apply(lambda row: user_perc(row['Value']), axis = 1)

# -

Final_table['Value'] = Final_table['Value'].astype(str).map(lambda cell: cell.replace('*', ''))

Final_table

Final_table['Value'] = pd.to_numeric(Final_table['Value'], errors='coerce')

Final_table.count()

Final_table['Category'].unique()

Final_table['Alcohol Content'] = 'pure alcohol'


# +
def user_perc5(x):
    
    if ((str(x) == 'Total Spirits')) | ((str(x) == 'Total Alcohol')): 
        
        return 'gbp-million'
    else:
        return 'hectolitres'
    
Final_table['Unit'] = Final_table.apply(lambda row: user_perc5(row['Category']), axis = 1)


# +
def user_perc6(x):
    
    if ((str(x) == 'Total Spirits'))| ((str(x) == 'Total Alcohol')): 
        
        return 'revenue'
    
    elif ((str(x) == 'Production of Potable Spirits')):
        return 'potable-spirits'
    elif ((str(x) == 'Net Quantities of Spirits Charged with Duty')):
        return 'net-quantities-spirits'
    else:
        return 'quantities-consumption'
    
Final_table['Measure Type'] = Final_table.apply(lambda row: user_perc6(row['Category']), axis = 1)
# -

Final_table['Category'].unique()

str(Final_table['Period'].unique()[-1])


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
        
        return ''
    else:
        return y
    
Final_table['Alcohol Content'] = Final_table.apply(lambda row: user_perc8(row['Category'], row['Alcohol Content']), axis = 1)
# -

Final_table.head()

Final_table['Alcohol Duty'] = 'spirits'

Final_table = Final_table[['Period','Category','Alcohol Duty','Alcohol Content','Measure Type','Value','Unit','Revision']]

Final_table.tail()

# +
# destinationFolder = Path('out')
# destinationFolder.mkdir(exist_ok=True, parents=True)

# Final_table.to_csv(destinationFolder / ('hmrcalcohol_9.csv'), index = False)
# -


