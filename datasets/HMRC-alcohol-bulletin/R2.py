# -*- coding: utf-8 -*-
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

# +
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
                measure_type = 'GBP per Hectolitre of Product'
                unit = 'GBP'
                
                # Wine Duty (WINE)
                period = cell_wine_duty_wine.shift(0,6).expand(DOWN).is_not_blank() - cell_wine_duty_made_wine.expand(DOWN)
                alcohol_origin = cell_wine_duty_wine.shift(0,3).expand(RIGHT).is_not_blank()
                alcohol_by_volume_1 = cell_wine_duty_wine.shift(1,5).expand(RIGHT).is_not_blank()
                alcohol_by_volume_2 = cell_wine_duty_wine.shift(1,6).expand(RIGHT).is_not_blank()
                observations = alcohol_by_volume_2.fill(DOWN).is_not_blank() - cell_wine_duty_made_wine.expand(RIGHT).expand(DOWN)
                dimensions = [
                    HDim(period, 'Period', DIRECTLY, LEFT),
                    HDim(alcohol_origin, 'Alcohol Origin', CLOSEST, LEFT),
                    HDim(alcohol_by_volume_1, 'Alcohol by vol 1', DIRECTLY, ABOVE), 
                    HDim(alcohol_by_volume_2, 'Alcohol by vol 2', DIRECTLY, ABOVE),
                    HDimConst('Alcohol Type', 'Wine'),
                    HDimConst('Measure Type', measure_type),
                    HDimConst('Unit', unit),
                ]
                tidy_sheet = ConversionSegment(tab, dimensions, observations)        
                savepreviewhtml(tidy_sheet, 'Wine Duty (WINE)' + " Preview.html")
                tidied_sheets.append(tidy_sheet.topandas())
                
                # Wine Duty (made-wine)
                period = cell_wine_duty_made_wine.shift(0,6).expand(DOWN).is_not_blank() - cell_spirits_duty.expand(DOWN)
                alcohol_origin = cell_wine_duty_made_wine.shift(0,3).expand(RIGHT).is_not_blank()
                alcohol_by_volume_1 = cell_wine_duty_made_wine.shift(1,5).expand(RIGHT).is_not_blank()
                alcohol_by_volume_2 = cell_wine_duty_made_wine.shift(1,6).expand(RIGHT).is_not_blank()
                observations = alcohol_by_volume_2.fill(DOWN).is_not_blank() - cell_spirits_duty.expand(RIGHT).expand(DOWN)
                dimensions = [
                    HDim(period, 'Period', DIRECTLY, LEFT),
                    HDim(alcohol_origin, 'Alcohol Origin', CLOSEST, LEFT),
                    HDim(alcohol_by_volume_1, 'Alcohol by vol 1', DIRECTLY, ABOVE),
                    HDim(alcohol_by_volume_2, 'Alcohol by vol 2', DIRECTLY, ABOVE),
                    HDimConst('Alcohol Type', 'Made-Wine'),
                    HDimConst('Measure Type', measure_type),
                    HDimConst('Unit', unit),
                ]
                tidy_sheet = ConversionSegment(tab, dimensions, observations)        
                savepreviewhtml(tidy_sheet, 'Wine Duty (made-wine)' + " Preview.html")
                tidied_sheets.append(tidy_sheet.topandas())
                
                
                # Spirits Duty
                period = cell_spirits_duty.shift(0,6).expand(DOWN).is_not_blank() - cell_beer_duty.expand(DOWN)
                alcohol_origin = cell_spirits_duty.shift(0,3).expand(RIGHT).is_not_blank()
                observations = alcohol_origin.fill(DOWN).is_not_blank() - cell_beer_duty.expand(RIGHT).expand(DOWN)
                dimensions = [
                    HDim(period, 'Period', DIRECTLY, LEFT),
                    HDim(alcohol_origin, 'Alcohol Origin', CLOSEST, LEFT),
                    HDimConst('Alcohol by vol 1', 'All'),
                    HDimConst('Alcohol by vol 2', ''), #will be dropped 
                    HDimConst('Alcohol Type', 'Spirits'),
                    HDimConst('Measure Type', measure_type),
                    HDimConst('Unit', unit),
                ]
                tidy_sheet = ConversionSegment(tab, dimensions, observations)        
                savepreviewhtml(tidy_sheet, 'Spirits Duty' + " Preview.html")
                tidied_sheets.append(tidy_sheet.topandas())
                
                # Beer Duty
                period = cell_beer_duty.shift(0,6).expand(DOWN).is_not_blank() - cell_cider_duty_historic.expand(DOWN)
                alcohol_origin_1 = cell_beer_duty.shift(2,3).expand(RIGHT) - cell_beer_duty.shift(5,3) - cell_beer_duty.shift(6,3) - cell_beer_duty.shift(10,3).expand(RIGHT)
                alcohol_origin_2 = cell_beer_duty.shift(2,4).expand(RIGHT) - cell_beer_duty.shift(5,3) - cell_beer_duty.shift(6,4) - cell_beer_duty.shift(10,4).expand(RIGHT)
                observations = alcohol_origin_1.shift(0,2).fill(DOWN).is_not_blank() - cell_cider_duty_historic.expand(RIGHT).expand(DOWN)
                dimensions = [
                    HDim(period, 'Period', DIRECTLY, LEFT),
                    HDim(alcohol_origin_1, 'Alcohol Origin 1', CLOSEST, LEFT),
                    HDim(alcohol_origin_2, 'Alcohol Origin 2', CLOSEST, LEFT),
                    HDimConst('Alcohol by vol 1', 'All'),
                    HDimConst('Alcohol by vol 2', ''), #will be dropped 
                    HDimConst('Alcohol Type', 'Beer'),
                    HDimConst('Measure Type', 'GBP per 1 percent ABV per hectolitre'),
                    HDimConst('Unit', unit),
                ]
                tidy_sheet = ConversionSegment(tab, dimensions, observations)        
                savepreviewhtml(tidy_sheet, 'Beer Duty' + " Preview.html")
                tidied_sheets.append(tidy_sheet.topandas())
                
                #Cider Duty (historic)
                period = cell_cider_duty_historic.shift(0,6).expand(DOWN).is_not_blank() - cell_cider_duty_current.expand(DOWN)
                alcohol_origin = cell_cider_duty_historic.shift(0,3).expand(RIGHT).is_not_blank()
                alcohol_by_volume_1 = cell_cider_duty_historic.shift(1,5).expand(RIGHT).is_not_blank()
                alcohol_by_volume_2 = cell_cider_duty_historic.shift(1,6).expand(RIGHT).is_not_blank()
                observations = alcohol_by_volume_2.fill(DOWN).is_not_blank() - cell_cider_duty_current.expand(RIGHT).expand(DOWN)
                dimensions = [
                    HDim(period, 'Period', DIRECTLY, LEFT),
                    HDim(alcohol_origin, 'Alcohol Origin', CLOSEST, LEFT),
                    HDim(alcohol_by_volume_1, 'Alcohol by vol 1', DIRECTLY, ABOVE),
                    HDim(alcohol_by_volume_2, 'Alcohol by vol 2', DIRECTLY, ABOVE),
                    HDimConst('Alcohol Type', 'Cider Historic'),
                    HDimConst('Measure Type', measure_type),
                    HDimConst('Unit', unit),
                ]
                tidy_sheet = ConversionSegment(tab, dimensions, observations)        
                savepreviewhtml(tidy_sheet, 'Cider Duty (historic)' + " Preview.html")
                tidied_sheets.append(tidy_sheet.topandas())
                
                #Cider Duty (current)
                period = cell_cider_duty_current.shift(0,6).expand(DOWN).is_not_blank()
                alcohol_origin = cell_cider_duty_current.shift(0,3).expand(RIGHT).is_not_blank()
                alcohol_by_volume_1 = cell_cider_duty_current.shift(1,5).expand(RIGHT).is_not_blank()
                alcohol_by_volume_2 = cell_cider_duty_current.shift(1,6).expand(RIGHT).is_not_blank()
                observations = alcohol_by_volume_2.fill(DOWN).is_not_blank()
                dimensions = [
                    HDim(period, 'Period', DIRECTLY, LEFT),
                    HDim(alcohol_origin, 'Alcohol Origin', CLOSEST, LEFT),
                    HDim(alcohol_by_volume_1, 'Alcohol by vol 1', DIRECTLY, ABOVE),
                    HDim(alcohol_by_volume_2, 'Alcohol by vol 2', DIRECTLY, ABOVE),
                    HDimConst('Alcohol Type', 'Cider Current'),
                    HDimConst('Measure Type', measure_type),
                    HDimConst('Unit', unit),
                ]
                tidy_sheet = ConversionSegment(tab, dimensions, observations)        
                savepreviewhtml(tidy_sheet, 'Cider Duty (current)' + " Preview.html")
                tidied_sheets.append(tidy_sheet.topandas())
                
               


# +
df = pd.concat(tidied_sheets, ignore_index = True, sort = False)
df.rename(columns={'OBS' : 'Value','DATAMARKER' : 'Marker'}, inplace=True)
df["Period"] = df["Period"].apply(date_time)

if 'Marker' in df.columns:
    df['Marker'].replace('*', 'estimated', inplace=True)
    df['Marker'].replace('-', 'unknown', inplace=True)

df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
df['Value'] = df['Value'].round(decimals = 2)

# +
df['Alcohol by vol 1'] = df['Alcohol by vol 1'].str.rstrip() 
df['Alcohol by Volume'] = df['Alcohol by vol 1'] + ' ' + df['Alcohol by vol 2']

f1=(df['Alcohol Origin'].isnull())
df.loc[f1,'Alcohol Origin'] = df['Alcohol Origin 1'] + ' ' + df['Alcohol Origin 2']

df = df.drop(['Alcohol by vol 1', 'Alcohol by vol 2', 'Alcohol Origin 1', 'Alcohol Origin 2'], axis=1)

# -

df = df.replace({'Alcohol Origin' : {' Beer1' : 'Beer',
                                     'reweries Producing 5000 Hls Or Less2 ' : 'reweries Producing 5000 Hls Or Less',
                                     'High Strength Beers ABV > 7.5%5' : 'High Strength Beers ABV > 7.5%',
                                     'Low Strength Beers 1.2% < ABV < 2.8%5' : 'Low Strength Beers 1.2% < ABV < 2.8%',
                                     'Sparkling 2' : 'Sparkling',
                                     'Sparkling 7' : 'Sparkling'
                                    }})


# +
tidy = df[['Period', 'Alcohol by Volume', 'Alcohol Origin', 'Alcohol Type', 'Measure Type', 'Unit', 'Marker', 'Value']]

for column in tidy:
    if column in ('Alcohol by Volume', 'Alcohol Type', 'Alcohol Origin'):
        tidy[column] = tidy[column].str.lstrip()
        tidy[column] = tidy[column].map(lambda x: pathify(x))


# + endofcell="--"
destinationFolder = Path('out')
destinationFolder.mkdir(exist_ok=True, parents=True)

TITLE = 'HMRC Alcohol Duty Rates'
OBS_ID = pathify(TITLE)
import os
GROUP_ID = pathify(os.environ.get('JOB_NAME', 'gss_data/trade/' + Path(os.getcwd()).name))

tidy.drop_duplicates().to_csv(destinationFolder / f'{OBS_ID}.csv', index = False)
# # +
from gssutils.metadata import THEME
scraper.set_base_uri('http://gss-data.org.uk')
scraper.set_dataset_id(f'{GROUP_ID}/{OBS_ID}')
scraper.dataset.title = TITLE

scraper.dataset.family = 'trade'
with open(destinationFolder / f'{OBS_ID}.csv-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())
# -

schema = CSVWMetadata('https://gss-cogs.github.io/family-trade/reference/')
schema.create(destinationFolder / f'{OBS_ID}.csv', destinationFolder / f'{OBS_ID}.csv-schema.json')

tidy

# --
