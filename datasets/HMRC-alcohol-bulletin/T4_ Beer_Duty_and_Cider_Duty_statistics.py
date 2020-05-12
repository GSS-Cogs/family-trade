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
import datetime

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

# T4: Beer Duty and Cider Duty statistics

for tab in tabs:               
            if (tab.name == 'T4'):
                period = tab.excel_ref('B11').expand(DOWN).is_not_blank() 
                category = tab.excel_ref('C9').expand(RIGHT).is_not_blank()
                revision = tab.excel_ref('D10').expand(DOWN)
                alcohol_content = 'Various'
                alcohol_duty = 'beer-and-cider'
                measure_type = 'quantities-consumption'
                unit = 'hectolitres'
                observations = category.fill(DOWN).is_not_blank()
                
                dimensions = [
                    HDim(period, 'Period', DIRECTLY, LEFT),
                    HDim(revision, 'Revision', DIRECTLY, LEFT),
                    HDim(category, 'Alcohol Category', DIRECTLY, ABOVE),
                    HDimConst('Alcohol Content', alcohol_content),
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

df.count()

df.dtypes

df['Alcohol Category'].unique()


# +

def user_perc5(x):
    
    if ((str(x) == 'Total Beer'))| ((str(x) == 'Total Cider')) | ((str(x) == 'Total Alcohol')): 
        
        return 'gbp-million'
    else:
        return 'hectolitres-thousands'
    
df['Unit'] = df.apply(lambda row: user_perc5(row['Alcohol Category']), axis = 1)

def user_perc6(x):
    if ((str(x) == 'Total Beer'))| ((str(x) == 'Total Cider')) | ((str(x) == 'Total Alcohol')) : 
        return 'revenue'
    elif ((str(x) == 'UK Beer Production')):
        return 'uk-beer'
    elif ((str(x) == 'Total beer clearances')):
        return 'beer-clearences'
    elif ((str(x) == 'Cider Clearances')):
        return 'cider-clearences'
    else:
        return 'alcohol-clearences'
    
df['Measure Type'] = df.apply(lambda row: user_perc6(row['Alcohol Category']), axis = 1)

def user_perc8(x,y):
    if ((str(x) == 'Total Alcohol')): 
        return 'all'
    else:
        return y
df['Alcohol Content'] = df.apply(lambda row: user_perc8(row['Alcohol Category'], row['Alcohol Content']), axis = 1)

df = df.replace({'Alcohol Category' : {'Thousand hectolitres' : 'UK Beer Production',
                              'Thousand hectolitres of alcohol (production)': 'UK Alcohol Production',
                              'Thousand hectolitres of alcohol (clearances)' : 'Alcohol Clearances',
                               'Cider Thousand hectolitres' : 'Cider Clearances'
                              }})

df['Value'] = df['Value'].round(decimals=2)
df["Period"] = df["Period"].apply(date_time)
#f1=(df['Revision'] =='P')
#df.loc[f1,'Marker'] = 'provisional'
#df.drop(['Revision'], axis=1)

# -

df['Alcohol Category'].unique()

Final_table = df[['Period','Alcohol Duty','Alcohol Category','Alcohol Content', 'Revision', 'Measure Type','Value','Unit', 'Marker']]


Final_table['Revision'].unique()


Final_table



