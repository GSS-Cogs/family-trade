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

def date_time(x):   
    time_string = str(x)
    time_len = len(time_string)
    if str(x)[-3] == '.':
        return 'day/' + datetime.datetime.strptime(str(x), '%d.%m.%y').strftime('%Y-%m-%d')
    elif str(x)[-4] == '.':
        x = x[:-1]
        return 'day/' + datetime.datetime.strptime(str(x), '%d.%m.%y').strftime('%Y-%m-%d') 
    elif time_len == 10:
        x = x[:-2]
        return 'day/' + datetime.datetime.strptime(str(x), '%d.%m.%y').strftime('%Y-%m-%d')


# -

# #### Spreadsheet title : Historic alcohol duty rates
# dividided up into the following sub-sections: 
# - Wine Duty (wine)
# - Wine Duty (made-wine)
# - Spirits Duty
# - Beer Duty
# - Cider Duty (historic)
# - Cider Duty (current)

for tab in tabs:               
            if (tab.name == 'R2'):
            #defining where each sub-section of duty reates starts / ends on the spreadsheet. 
                cell_wine_duty_wine = tab.filter('Wine Duty (wine)')
                cell_wine_duty_wine.assert_one()
                cell_wine_duty_made_wine = tab.filter('Wine Duty (made-wine)')
                cell_wine_duty_made_wine.assert_one()
                cell_spirits_duty = tab.filter('Spirits Duty')
                cell_spirits_duty.assert_one()
                cell_beer_duty = tab.filter('Beer Duty')
                cell_beer_duty.assert_one()
                cell_cider_duty_historic = tab.filter('Cider Duty (historic)')
                cell_cider_duty_historic.assert_one()
                cell_cider_duty_current = tab.filter('Cider Duty (current)')
                cell_cider_duty_current.assert_one()
            
                #general measure type and unit type shared across each sub-section.
                measure_type = 'rates-of-duty'
                unit = 'gbp-per-hl-product'
                
                
                # Wine Duty (WINE)
                period = cell_wine_duty_wine.shift(0,6).expand(DOWN).is_not_blank() - cell_wine_duty_made_wine.expand(DOWN)
                category = cell_wine_duty_wine.shift(0,3).expand(RIGHT).is_not_blank()
                alcohol_content_1 = cell_wine_duty_wine.shift(1,5).expand(RIGHT).is_not_blank()
                alcohol_content_2 = cell_wine_duty_wine.shift(1,6).expand(RIGHT).is_not_blank()
                alcohol_duty = cell_wine_duty_wine
                observations = alcohol_content_2.fill(DOWN).is_not_blank() - cell_wine_duty_made_wine.expand(RIGHT).expand(DOWN)
                dimensions = [
                    HDim(period, 'Period', DIRECTLY, LEFT),
                    HDim(category, 'Alcohol Category', CLOSEST, LEFT),
                    HDim(alcohol_content_1, 'Alcohol Content 1', DIRECTLY, ABOVE),
                    HDim(alcohol_content_2, 'Alcohol Content 2', DIRECTLY, ABOVE),
                    HDim(alcohol_duty, 'Alcohol Duty', CLOSEST, LEFT),
                    HDimConst('Revision', ''),
                    HDimConst('Measure Type', measure_type),
                    HDimConst('Unit', unit),
                ]
                tidy_sheet = ConversionSegment(tab, dimensions, observations)        
                savepreviewhtml(tidy_sheet, 'Wine Duty (WINE)' + " Preview.html")
                tidied_sheets.append(tidy_sheet.topandas())
                
                # Wine Duty (made-wine)
                period = cell_wine_duty_made_wine.shift(0,6).expand(DOWN).is_not_blank() - cell_spirits_duty.expand(DOWN)
                category = cell_wine_duty_made_wine.shift(0,3).expand(RIGHT).is_not_blank()
                alcohol_content_1 = cell_wine_duty_made_wine.shift(1,5).expand(RIGHT).is_not_blank()
                alcohol_content_2 = cell_wine_duty_made_wine.shift(1,6).expand(RIGHT).is_not_blank()
                alcohol_duty = cell_wine_duty_made_wine
                observations = alcohol_content_2.fill(DOWN).is_not_blank() - cell_spirits_duty.expand(RIGHT).expand(DOWN)
                dimensions = [
                    HDim(period, 'Period', DIRECTLY, LEFT),
                    HDim(category, 'Alcohol Category', CLOSEST, LEFT),
                    HDim(alcohol_content_1, 'Alcohol Content 1', DIRECTLY, ABOVE),
                    HDim(alcohol_content_2, 'Alcohol Content 2', DIRECTLY, ABOVE),
                    HDim(alcohol_duty, 'Alcohol Duty', CLOSEST, LEFT),
                    HDimConst('Revision', ''),
                    HDimConst('Measure Type', measure_type),
                    HDimConst('Unit', unit),
                ]
                tidy_sheet = ConversionSegment(tab, dimensions, observations)        
                savepreviewhtml(tidy_sheet, 'Wine Duty (made-wine)' + " Preview.html")
                tidied_sheets.append(tidy_sheet.topandas())
                
                
                # Spirits Duty
                period = cell_spirits_duty.shift(0,6).expand(DOWN).is_not_blank() - cell_beer_duty.expand(DOWN)
                category = cell_spirits_duty.shift(0,3).expand(RIGHT).is_not_blank()
                alcohol_content ='ABV 22%'
                alcohol_duty = cell_spirits_duty
                observations = category.fill(DOWN).is_not_blank() - cell_beer_duty.expand(RIGHT).expand(DOWN)
                dimensions = [
                    HDim(period, 'Period', DIRECTLY, LEFT),
                    HDim(category, 'Alcohol Category', CLOSEST, LEFT),
                    HDimConst('Alcohol Content 1', alcohol_content),
                    HDimConst('Alcohol Content 2', ''), #will be dropped 
                    HDim(alcohol_duty, 'Alcohol Duty', CLOSEST, LEFT),
                    HDimConst('Revision', ''),
                    HDimConst('Measure Type', measure_type),
                    HDimConst('Unit', unit),
                ]
                tidy_sheet = ConversionSegment(tab, dimensions, observations)        
                savepreviewhtml(tidy_sheet, 'Spirits Duty' + " Preview.html")
                tidied_sheets.append(tidy_sheet.topandas())
                
                # Beer Duty
                period = cell_beer_duty.shift(0,6).expand(DOWN).is_not_blank() - cell_cider_duty_historic.expand(DOWN)
                category = cell_beer_duty.shift(2,3).expand(RIGHT) - cell_beer_duty.shift(5,3) - cell_beer_duty.shift(6,3) - cell_beer_duty.shift(10,3).expand(RIGHT)
                alcohol_content = cell_beer_duty.shift(2,4).expand(RIGHT).is_not_blank()
                alcohol_duty = cell_beer_duty
                observations = category.shift(0,2).fill(DOWN).is_not_blank() - cell_cider_duty_historic.expand(RIGHT).expand(DOWN)
                dimensions = [
                    HDim(period, 'Period', DIRECTLY, LEFT),
                    HDim(category, 'Alcohol Category', CLOSEST, LEFT),
                    HDim(alcohol_content, 'Alcohol Content 1', CLOSEST, LEFT),
                    HDimConst('Alcohol Content 2', ''), #will be dropped 
                    HDim(alcohol_duty, 'Alcohol Duty', CLOSEST, LEFT),
                    HDimConst('Revision', ''),
                    HDimConst('Measure Type', measure_type),
                    HDimConst('Unit', unit),
                ]
                tidy_sheet = ConversionSegment(tab, dimensions, observations)        
                savepreviewhtml(tidy_sheet, 'Beer Duty' + " Preview.html")
                tidied_sheets.append(tidy_sheet.topandas())
                
                #Cider Duty (historic)
                period = cell_cider_duty_historic.shift(0,6).expand(DOWN).is_not_blank() - cell_cider_duty_current.expand(DOWN)
                category = cell_cider_duty_historic.shift(0,3).expand(RIGHT).is_not_blank()
                alcohol_content_1 = cell_cider_duty_historic.shift(1,5).expand(RIGHT).is_not_blank()
                alcohol_content_2 = cell_cider_duty_historic.shift(1,6).expand(RIGHT).is_not_blank()
                alcohol_duty = cell_cider_duty_historic
                observations = alcohol_content_2.fill(DOWN).is_not_blank() - cell_cider_duty_current.expand(RIGHT).expand(DOWN)
                dimensions = [
                    HDim(period, 'Period', DIRECTLY, LEFT),
                    HDim(category, 'Alcohol Category', CLOSEST, LEFT),
                    HDim(alcohol_content_1, 'Alcohol Content 1', DIRECTLY, ABOVE),
                    HDim(alcohol_content_2, 'Alcohol Content 2', DIRECTLY, ABOVE),
                    HDim(alcohol_duty, 'Alcohol Duty', CLOSEST, LEFT),
                    HDimConst('Revision', ''),
                    HDimConst('Measure Type', measure_type),
                    HDimConst('Unit', unit),
                ]
                #tidy_sheet = ConversionSegment(tab, dimensions, observations)        
                savepreviewhtml(tidy_sheet, 'Cider Duty (historic)' + " Preview.html")
                #tidied_sheets.append(tidy_sheet.topandas())
                
                #Cider Duty (current)
                period = cell_cider_duty_current.shift(0,6).expand(DOWN).is_not_blank()
                category = cell_cider_duty_current.shift(0,3).expand(RIGHT).is_not_blank()
                alcohol_content_1 = cell_cider_duty_current.shift(1,5).expand(RIGHT).is_not_blank()
                alcohol_content_2 = cell_cider_duty_current.shift(1,6).expand(RIGHT).is_not_blank()
                alcohol_duty = cell_cider_duty_current
                observations = alcohol_content_2.fill(DOWN).is_not_blank()
                dimensions = [
                    HDim(period, 'Period', DIRECTLY, LEFT),
                    HDim(category, 'Alcohol Category', CLOSEST, LEFT),
                    HDim(alcohol_content_1, 'Alcohol Content 1', DIRECTLY, ABOVE),
                    HDim(alcohol_content_2, 'Alcohol Content 2', DIRECTLY, ABOVE),
                    HDim(alcohol_duty, 'Alcohol Duty', CLOSEST, LEFT),
                    HDimConst('Revision', ''),
                    HDimConst('Measure Type', measure_type),
                    HDimConst('Unit', unit),
                ]
                tidy_sheet = ConversionSegment(tab, dimensions, observations)        
                savepreviewhtml(tidy_sheet, 'Cider Duty (current)' + " Preview.html")
                tidied_sheets.append(tidy_sheet.topandas())
                

# +
df = pd.concat(tidied_sheets, ignore_index = True, sort = False)
df.rename(columns={'OBS' : 'Value','DATAMARKER' : 'Marker'}, inplace=True)

if 'Marker' in df.columns:
    df['Marker'].replace('*', 'estimated based on previous years', inplace=True)
    df['Marker'].replace('-', 'unknown', inplace=True)
else:
    df['Marker'] = ''

df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
# -

df['Alcohol Content 1'] = df['Alcohol Content 1'].str.rstrip() 
df['Alcohol Content'] = df['Alcohol Content 1'] + ' ' + df['Alcohol Content 2']


# +
df['Alcohol Category'] = df['Alcohol Category'].str.rstrip()

f1=(((df['Alcohol Duty'] =='Wine Duty (wine)') | (df['Alcohol Duty'] =='Wine Duty (made-wine)')) & ((df['Alcohol Category'] == 'Sparkling') | (df['Alcohol Category'] == 'Still')))
df.loc[f1,'Alcohol Category'] = df.loc[f1,'Alcohol Category'] + ' Wine'

f2=((df['Alcohol Duty'] =='Wine Duty (made-wine)') & (df['Alcohol Category'] == 'Wine'))
df.loc[f2,'Alcohol Category'] = 'Sparkling Wine'

f3=((df['Alcohol Content'] =='Beer1 ') & (df['Alcohol Category'] == ''))
df.loc[f3,'Alcohol Category'] = 'beer'

f4=(((df['Alcohol Duty'] =='Cider Duty (historic)') | (df['Alcohol Duty'] =='Cider Duty (current)') ) & ((df['Alcohol Category'] == 'Sparkling 2') | (df['Alcohol Category'] == 'Still') | (df['Alcohol Category'] == 'Sparkling 7')))
df.loc[f4,'Alcohol Category'] = df.loc[f4,'Alcohol Category'] + ' Cider'


df = df.replace({'Alcohol Content' : {'ABV > 7.5%5 ' : 'ABV 7.5%', 
                                   '1.2% < ABV < 2.8%5 ' : '1.2% to 2.8%',
                                   'Beer1 ': 'various',
                                   'Over 7.5% but less than 8.5% 1' : 'Over 7.5% but less than 8.5%',
                                   'Over 5.5% but less than 8.5% 2' : 'Over 5.5% but less than 8.5%'
                               }})

df = df.replace({'Alcohol Category' : {'Ready-to-Drink (RTD)' : 'Ready-to-Drink',
                                       'Sparkling 2 Cider': 'Sparkling Cider',
                                       'Sparkling 7 Cider': 'Sparkling Cider'
                              }})
df = df.replace({'Alcohol Duty' : {'Wine Duty (wine)' : 'made-wine', 
                                   'Wine Duty (made-wine)' : 'wine-of-fresh-grape',
                                   'Spirits Duty': 'spirits',
                                   'Beer Duty' : 'beer',
                                   'Cider Duty (historic)' : 'cider',
                                   'Cider Duty (current)' : 'cider'
                              }})

# -


df["Period"] = df["Period"].apply(date_time)

df = df[['Period','Alcohol Duty','Alcohol Category','Alcohol Content','Measure Type','Value', 'Marker', 'Unit','Revision']]

Final_table = df[['Period','Alcohol Duty','Alcohol Category','Alcohol Content','Measure Type','Value','Unit', 'Marker']]
Final_table['Alcohol Category'] = Final_table['Alcohol Category'].map(lambda x: pathify(x))
Final_table['Alcohol Content'] = Final_table['Alcohol Content'].map(lambda x: pathify(x))
Final_table
