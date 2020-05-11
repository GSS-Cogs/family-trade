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

# # HM Revenue and Customs Alcohol Bulletin

# +
from gssutils import *

scraper = Scraper('https://www.uktradeinfo.com/Statistics/Pages/TaxAndDutyBulletins.aspx')
scraper
# -

scraper.select_dataset(title='Alcohol Duty')
scraper

alcohol = scraper.distribution(title=lambda t: t.startswith('Alcohol Duty'))
tabs = alcohol.as_pandas(sheet_name=None)

# +
frames = []

tidy = pd.DataFrame()
for tab_name, script in [
    ('2', 'Alcohol HMRC(2).ipynb'),
    ('3', 'Alcohol HMRC(3).ipynb'),
    ('4', 'Alcohol HMRC(4).ipynb'),
    ('5', 'Alcohol HMRC(5).ipynb'),
    ('7', 'Alcohol HMRC(7).ipynb'),
    ('8', 'Alcohol HMRC(8).ipynb'),
    ('9', 'Alcohol HMRC(9).ipynb'),
    ('10', 'Alcohol HMRC(10).ipynb'),
    ('12', 'Alcohol HMRC(12).ipynb')]:
    tab = tabs[tab_name]
    %run "$script"
    frames.append(Final_table)
    tidy = pd.concat([tidy, Final_table])

# tidy = pd.concat(frames, ignore_index=True)
tidy.dropna(how='any',axis=0, inplace =True)
tidy
# -

tidy['Alcohol Content'].unique()

tidy['Alcohol Content'] = tidy['Alcohol Content'].map(
    lambda x: {
        'Not exceeding 15%' : 'not-exc-15', 
        'Over 15% ABV' : 'over-15',
        'Composition by Origin above 5.5% ABV': 'comp-by-origin-above-5-5' ,
        'Total': 'all',
        'Above 1.2% but not exceeding 5.5% ABV' : 'above-1-2-not-exc-5-5',
        'pure alcohol':'pure-alcohol',
        'Various': 'all',
        '' : 'all',
        'Above 5.5% ABV but not exceeding 15%' : 'above-5-5-not-exc-15',
        'ABV 7.5%' : 'abv-7-5',
        '1.2% to 2.8%' : '1-2-to-2-8',
        'Over 1.2%, up to and including 4.0%' : 'over-1-2-up-to-and-incl-4-0',
        'Over 4.0%, up to and including 5.5%' : 'over-4-0-up-to-and-incl-5-5',
        'Over 15.0%, up to and including 22.0%' : 'over-15-0-up-to-and-incl-22',
        'Over 5.5%, less than 8.5%': 'over-5-5-less-than-8-5',
        'From 8.5%, up to and including 15.0%': 'from-8-5-up-to-and-incl-15-0',
        'Over 5.5% but less than 8.5%' : 'over-5-5-less-than-8-5',
        'ABV 22%' : 'abv-22',
        'Over 1.2%, up to and including 7.5%': 'over-1-2-up-to-and-incl-7-5',
        'Over 7.5% but less than 8.5% ' : 'over-7-5-less-than-8-5',
        'Over 5.5% but less than 8.5%' : 'over-5-5-less-than-8-5',
        'Over 5.5%, up to and including 15.0%' : 'over-5-5-up-to-and-incl-15-0'
        
    }.get(x, x))

tidy['Alcohol Content'].unique()

import datetime


# +
def user_perc(x):    
    if str(x)[-3] == '/':
        return 'gregorian-interval/' + str(x)[:4] + '-04-01T00:00:00/P1Y'
    elif str(x)[-3] == ':':
        return 'month/' + str(x)[:7]
    elif str(x)[-3] == '.':
        return 'day/' + datetime.datetime.strptime(str(x), '%d.%m.%y').strftime('%Y-%m-%d')
    else:
        return 'year/'  + str(x)      
    
tidy['Period'] = tidy.apply(lambda row: user_perc(row['Period']), axis = 1)
# -

tidy['Alcohol Category'] = tidy['Category'].map(
    lambda x: {
        'Still': 'still', 
        'Sparkling': 'sparkling', 
        'Over 15% ABV': 'total', 
        'Imported ex-ship': 'imported-ex-ship',
        'Ex-warehouse' : 'ex-warehouse', 
        'UK registered premises': 'uk-registered-premises',
        'Total wine of fresh grape': 'total-wine-of-fresh-grape', 
        'Total Wine': 'total-wine', 
        'Total Alcohol' : 'total-alcohol',
        'Above 1.2% but not exceeding 5.5% ABV' : 'total', 
        'Still2 ' :'still', 
        'Sparkling ' : 'sparkling' ,
        'Total made wine' : 'total-made-wine' , 
        'Total wine3 ' : 'total-wine', 
        'Total alcohol' : 'total-alcohol',
        'Production of Potable Spirits' : 'spirits' , 
        'Malt': 'hpw-malt', 
        'Grain and Blended' : 'hpw-grain-blended',
        'Total Home Produced Whisky' : 'hpw-total', 
        'Spirit Based RTDs' : 'spirit-based-rtds',
        'Imported and Other Spirits' : 'imported-and-other-spirits',
        'Net Quantities of Spirits Charged with Duty' : 'total-spirits', 
        'Total Spirits' : 'total-spirits',
        'UK Beer Production' : 'total-beer', 
        'UK Alcohol Production' : 'total-alcohol-production',
        'Ex-warehouse and imports': 'ex-warehouse-and-imports', 
        'Total beer clearances': 'total-beer-clearances' ,
        'Alcohol Clearances' : 'total-alcohol-clearances',
        'Cider Clearances' : 'total-cider-clearances', 
        'Total Beer' : 'total-beer',
        'Total Cider' : 'total-cider', 
        'Above 1.2% but not exceeding 5.5% ABV 1': 'total',
        'Still Wine' : 'still', 
        'Sparkling Wine' : 'sparkling', 
        'Ready-to-Drink ' : 'rtd', 
        'Still Cider' : 'still',
        'Sparkling Cider' : 'sparkling', 
        'Spirits-Based RTDs' : 'spirit-based-rtds', 
        'Spirits' : 'spirits', 
        'Beer' : 'beer',
        'Breweries Producing 5000 Hls Or Less' : 'breweries-5000-less',
        'Breweries Producing 5000 to 30000 Hls': 'breweries-5000-30000',
        'Breweries Producing 30000 to 60000 Hls' : 'breweries-30000-60000', 
        'High Strength Beers': 'high-strength-beers',
        'Low Strength Beers' :'low-strength-beers'  
        
        }.get(x, x))

tidy['Measure Type'].unique()

tidy['Measure Type'] = tidy['Measure Type'].map(
    lambda x: {
        'quantities-consumption' : 'Quantities Released for Consumption', 
        'revenue' : 'Revenue',
        'potable-spirits':'Production of Potable Spirits',
        'net-quantities-spirits':'Net Quantities of Spirits Charged with Duty',
        'uk-beer':'UK Beer Production',
        'alcohol-clearences':'Alcohol Clearances',
        'beer-clearences':'Beer Clearances',
        'cider-clearences':'Cider Clearances',
        'rates-of-duty':'Rates of Duty'
        
       }.get(x, x))

tidy['Measure Type'].unique()

tidy['Unit'].unique()

tidy['Revision'].unique()

tidy['Revision'] = tidy['Revision'].map(
    lambda x: {
        'estimated based on previous Periods' : 'estimated', 
        'estimated based on previous years' : 'estimated',
        '': 'original-value' 
       }.get(x, x))


tidy.head()

tidy = tidy[tidy['Value'].isnull() == False]

tidy = tidy.drop_duplicates(subset=None, keep='first', inplace=False)

tidy['Value'] = tidy['Value'].astype(str)

tidy = tidy[['Period','Alcohol Category','Alcohol Duty','Alcohol Content','Measure Type','Value','Unit','Revision']]

# +
from pathlib import Path

out = Path('out')
out.mkdir(exist_ok=True)
tidy.to_csv(out / 'observations.csv', index = False)
# -

# Try to grab the metadata from the spreadsheet's 'Cover' tab.
#
# We already know the title and the comment.

# +
import numpy as np
from dateutil.parser import parse

heading = None
stats_contacts = []
contact_info = []
for v in tabs['Cover']['Unnamed: 2']:
    if (type(v) == str) and (v.strip() in ['Coverage:', 'Theme:', 'Released:',
                                           'Next release:', 'Frequency of release:',
                                           'Media contact:', 'Statistical contacts:', 'Website:']):
        heading = v
    elif heading:
        if type(v) == str:
            if heading == 'Coverage:':
                if v == 'United Kingdom':
                    scraper.dataset.spatial = 'http://statistics.data.gov.uk/id/statistical-geography/K02000001'
                else:
                    assert False, 'Expected spatial coverage to be UK'
            elif heading == 'Theme:':
                if v == 'The Economy':
                    scraper.dataset.theme = 'https://www.statisticsauthority.gov.uk/themes/economy/'
                else:
                    assert False, 'Expected theme to be "The Economy"'
            elif heading == 'Released:':
                scraper.dataset.issued = parse(v)
            elif heading == 'Next release:':
                scraper.dataset.nextUpdateDue = parse(v)
            elif heading == 'Frequency of release:':
                pass
            elif heading == 'Website':
                scraper.dataset.landingPage = v
            if heading in ['Statistical contacts:', 'Media contact:']:
                contact_info.append(v)
            print(f'{heading} {v}')
        elif heading == 'Statistical contacts:':
            stats_contacts.append(contact_info)
            contact_info = []
        else:
            heading = None
            
scraper.dataset.family = 'health'
scraper.dataset.comment = 'The Alcohol Bulletin provides monthly statistics on clearances of' \
    'beer, wine, spirits and cider and duty receipts for the UK.'

with open(out / 'dataset.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())

# -

tidy['Period'].unique()

tidy

tidy['Measure Type'].unique()


