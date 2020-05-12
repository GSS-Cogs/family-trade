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

# +
from gssutils import *

scraper = Scraper("https://www.gov.uk/government/statistics/alcohol-bulletin")
scraper
# -

dist = scraper.distributions[1]
tabs = (t for t in dist.as_databaker())
tidied_sheets = []
dist


# +
def left(s, amount):
    return s[:amount]
def right(s, amount):
    return s[-amount:]

def date_time(time_value):
    time_string = str(time_value).replace(".0", "").strip()
    time_len = len(time_string)
    if time_len == 4:
        return "year/" + time_string
    elif time_len == 7:
        return 'government-year/' + time_string[:4] + '-20' + time_string[5:7]
    elif time_len == 10:       
        return 'gregorian-interval/' + time_string[:7] + '-01T00:00:00/P1M'


# -

# T1: Wine Duty (wine) statistics
# T2: Wine Duty (made-wine) statistics

for tab in tabs:
            if (tab.name == 'T1'):
                period = tab.excel_ref('B12').expand(DOWN).is_not_blank() 
                category = tab.excel_ref('B9').expand(RIGHT).is_not_blank()
                revision = tab.excel_ref('D10').expand(DOWN)
                alcohol_content = tab.excel_ref('C8').expand(RIGHT).is_not_blank() 
                alcohol_duty = 'wine-of-fresh-grape'
                measure_type = 'quantities-consumption'
                unit = 'hectolitres'
                observations = category.fill(DOWN).is_not_blank()
      
                dimensions = [
                    HDim(period, 'Period', DIRECTLY, LEFT),
                    HDim(revision, 'Revision', DIRECTLY, LEFT),
                    HDim(category, 'Alcohol Category', DIRECTLY, ABOVE),
                    HDim(alcohol_content, 'Alcohol Content', CLOSEST, LEFT),
                    HDimConst('Alcohol Duty', alcohol_duty),
                    HDimConst('Measure Type', measure_type),
                    HDimConst('Unit', unit),
                ]
                tidy_sheet = ConversionSegment(tab, dimensions, observations)        
                #savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
                tidied_sheets.append(tidy_sheet.topandas())
                
            if (tab.name == 'T2'):
                
                period = tab.excel_ref('B12').expand(DOWN).is_not_blank() 
                category = tab.excel_ref('B9').expand(RIGHT).is_not_blank()
                revision = tab.excel_ref('D10').expand(DOWN)
                alcohol_content = tab.excel_ref('C8').expand(RIGHT).is_not_blank() 
                alcohol_duty = 'made-wine'
                measure_type = 'quantities-consumption'
                unit = 'hectolitres'
                observations = category.fill(DOWN).is_not_blank()
                
                dimensions = [
                    HDim(period, 'Period', DIRECTLY, LEFT),
                    HDim(revision, 'Revision', DIRECTLY, LEFT),
                    HDim(category, 'Alcohol Category', DIRECTLY, ABOVE),
                    HDim(alcohol_content, 'Alcohol Content', CLOSEST, LEFT),
                    HDimConst('Alcohol Duty', alcohol_duty),
                    HDimConst('Measure Type', measure_type),
                    HDimConst('Unit', unit),
                ]
                
                tidy_sheet = ConversionSegment(tab, dimensions, observations)        
                #savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
                tidied_sheets.append(tidy_sheet.topandas())

# +
df = pd.concat(tidied_sheets, ignore_index = True, sort = False)
df.rename(columns={'OBS' : 'Value','DATAMARKER' : 'Marker'}, inplace=True)

if 'Marker' in df.columns:
    df['Marker'].replace('*', 'estimated', inplace=True)
else:
    df['Marker'] = ''

df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
# -

df


# +

def user_perc2(x):
    if ((str(x) ==  'Still')) | ((str(x) == 'Sparkling')):  
        return 'Not exceeding 15%'
    else:
        return 'Composition by Origin above 5.5% ABV'
    
df['Alcohol Content'] = df.apply(lambda row: user_perc2(row['Alcohol Category']), axis = 1)

def user_perc3(x,y):    
    if x.strip() == 'Over 15% ABV':
        return 'Over 15% ABV'
    else:
        return y        
    
df['Alcohol Content'] = df.apply(lambda row: user_perc3(row['Alcohol Category'], row['Alcohol Content']), axis = 1)

def user_perc4(x,y):
    if ((str(x) ==  'Total wine of fresh grape')) | ((str(x) == 'Total Wine'))| ((str(x) == 'Total Alcohol')): 
        return 'Total'
    else:
        return y
    
df['Alcohol Content'] = df.apply(lambda row: user_perc4(row['Alcohol Category'], row['Alcohol Content']), axis = 1)

def user_perc5(x):
    if ((str(x) == 'Total Wine'))| ((str(x) == 'Total Alcohol')): 
        return 'gbp-million'
    else:
        return 'hectolitres'
    
df['Unit'] = df.apply(lambda row: user_perc5(row['Alcohol Category']), axis = 1)

def user_perc6(x):
    if ((str(x) == 'Total Wine'))| ((str(x) == 'Total Alcohol')): 
        return 'revenue'
    else:
        return 'quantities-consumption'

#f1=(df['Revision'] =='P')
#df.loc[f1,'Marker'] = 'provisional'
    
df['Measure Type'] = df.apply(lambda row: user_perc6(row['Alcohol Category']), axis = 1)
df['Value'] = df['Value'].round(decimals=2)
df["Period"] = df["Period"].apply(date_time)
#df.drop(['Revision'], axis=1)

df = df.replace({'Alcohol Category' : {'Over 15% \nABV' : 'total',
                                       'Over 15% ABV': 'total',
                               'Total1 \nWine': 'Total Wine',
                               'Ex-\nwarehouse' : 'Ex-warehouse',
                               'Imported \nex-ship' : 'Imported ex-ship', 
                               'Above 1.2% but not exceeding 5.5% ABV ' : 'total',
                               'Total wine1 ': 'Total Wine',
                               'Total wine2 ': 'Total Wine',
                               'Still1 ': 'Still',
                               }})

df = df.replace({'Alcohol Content' : {'Not exceeding 15%' : 'not-exc-15',
                                      'Over 15% ABV' : 'over-15',
                                      'Composition by Origin above 5.5% ABV' : 'comp-by-origin-above-5-5',
                                      'Total': 'all',
                                      }})
                
# -

df

Final_table = df[['Period','Alcohol Duty','Alcohol Category','Alcohol Content','Revision', 'Measure Type','Value','Unit', 'Marker']]


Final_table['Revision'].unique()

Final_table


