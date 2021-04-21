# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# UK Trade in goods: country-by-commodity, exports and imports

# +
import pandas as pd
import json
from gssutils import *

from zipfile import ZipFile
from io import BytesIO


# +
def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]


# -

cubes = Cubes("info.json")

pd.options.mode.chained_assignment = None 

info = json.load(open('info.json'))

landingPage = info['landingPage']
landingPage

scraper1 = Scraper(landingPage[0])
scraper1.dataset.family = info['families']
scraper1

scraper2 = Scraper(landingPage[1])
scraper2

distribution1 = scraper1.distribution(mediaType=lambda x: 'zip' in x, latest=True)
distribution1

distribution2 = scraper2.distribution(mediaType=lambda x: 'zip' in x, latest=True)
distribution2

descr = """ 
Monthly import country-by-commodity data on the UK's trade in goods, including trade by all countries and selected commodities, non-seasonally adjusted.

Users should note the following:
Industry data has been produced using Standard Industrial Classification 2007 (SIC07).
Commodity data has been produced using Standard International Trade Classification (SITC).	

Due to risks around disclosing data related to individual firms we are only able to provide data for certain combinations of the dimensions included, i.e. country, commodity and industry. This dataset therefore provides the following two combinations:	
    Industry (SIC07 2 digit), by Commodity (SITC 2 digit), by geographic region (worldwide, EU and non-EU)
    Industry (SIC07 2 digit), by Commodity total, by individual country

Methodology improvements
Within this latest experimental release improvements have been made to the methodology that has resulted in some revisions when compared to our previous release in April 2019.
These changes include; improvements to the data linking methodology and a targeted allocation of some of the Balance of Payments (BoP) adjustments to industry.
The data linking improvements were required due to subtleties in both the HMRC data and IDBR not previously recognised within Trade.

While we are happy with the quality of the data in this experimental release we have noticed some data movements, specifically in 2018.
We will continue to review the movements seen in both the HMRC microdata and the linking methodology and, where appropriate, will further develop the methodology for Trade in Goods by Industry for future releases. 

"""

title = "Trade in goods: country-by-commodity, exports and imports"
scraper1.dataset.title = 'UK trade in goods: country-by-commodity, exports and imports'
scraper2.dataset.title = 'UK trade in goods: country-by-commodity, exports and imports'
scraper1.dataset.description = descr
scraper2.dataset.description = descr


def yearSum(dataframe):
    '''
    sums up the observations for each respective year from Jan to Dec
        and returns the dataframe with summed year-observation columns 
    '''
    df = dataframe
    new_data = []
    new_data.append(df.iloc[:,0:3])

    startYear = int(list(df.columns)[3][:4])
    endYear = int(list(df.columns)[-1][:4])

    for year in range(startYear,endYear+1):
        year = str(year)
        df1 = df.loc[:, year +'JAN' : year +'DEC']
        df1[year] = df1.sum(axis=1)
        new_data.append(df1[year])
    year_sum = pd.concat(new_data, axis=1)
    return year_sum


def transform(dataframe):
    '''transforms the dataframe to a datacube
    ''' 
    df = dataframe
    df.rename(columns={
        'COMMODITY': 'Commodity',
        'COUNTRY': 'ONS Partner Geography',
        'DIRECTION': 'Flow'
        }, inplace=True)
    tidy = pd.melt(df, id_vars=['Commodity','ONS Partner Geography', 'Flow'], var_name='Period', value_name='Value')
    tidy_sheet = tidy.sort_values(['Commodity','ONS Partner Geography', 'Flow'])
    tidy_sheet = tidy_sheet[tidy_sheet['Value'] != 0]
    return tidy_sheet


'''Country by Commodity Export data'''
with ZipFile(BytesIO(scraper1.session.get(distribution1.downloadURL).content)) as zip:
    assert(len(zip.namelist()) == 1)
    with zip.open(zip.namelist()[0]) as excelFile:
        buffered_fobj = BytesIO(excelFile.read())
        data1 = pd.read_excel(buffered_fobj,
                             sheet_name=1, dtype={
                                 'COMMODITY': 'category',
                                 'COUNTRY': 'category',
                                 'DIRECTION': 'category'
                             }, na_values=['','N/A'], keep_default_na=False)

#tidyData1 = yearSum(data1)
table1 = transform(data1)

'''Country by Commodity Import data'''
with ZipFile(BytesIO(scraper2.session.get(distribution2.downloadURL).content)) as zip:
    assert(len(zip.namelist()) == 1)
    with zip.open(zip.namelist()[0]) as excelFile:
        buffered_fobj = BytesIO(excelFile.read())
        data2 = pd.read_excel(buffered_fobj,
                             sheet_name=1, dtype={
                                 'COMMODITY': 'category',
                                 'COUNTRY': 'category',
                                 'DIRECTION': 'category'
                             }, na_values=['','N/A'], keep_default_na=False)

#tidyData2 = yearSum(data2)
table2 = transform(data2)

table = pd.concat([table1, table2])

pd.set_option('display.float_format', lambda x: '%.0f' % x)

table.loc[table['Period'].str.len() == 7, 'Period'] = pd.to_datetime(table.loc[table['Period'].str.len() == 7, 'Period'], format='%Y%b').astype(str).map(lambda x: 'month/' + left(x,7))
#table['Period'] = table['Period'].astype(str)
table.dropna(subset=['Value'], inplace=True)
table['Value'] = table['Value'].astype(int)

table['Commodity'].cat.categories = table['Commodity'].cat.categories.map(lambda x: x.split(' ')[0])
table['ONS Partner Geography'].cat.categories = table['ONS Partner Geography'].cat.categories.map(lambda x: x[:2])
table['Flow'] = table['Flow'].map(lambda x: x.split(' ')[1])

# +
#table['Period'] = table['Period'].astype(str)
#table['Period'] = 'year/' + table['Period']
# -

table['Seasonal Adjustment'] = pd.Series('NSA', index=table.index, dtype='category')
#table['Measure Type'] = pd.Series('gbp-million', index=table.index, dtype='category') 
#table['Unit'] = pd.Series('gbp-million', index=table.index, dtype='category')

table['Marker'] = ' '
table.loc[(table['Value'] == 0), 'Marker'] = 'suppressed'

table = table[['ONS Partner Geography','Period','Flow','Commodity','Seasonal Adjustment','Value','Marker']]
table['Flow'] = table['Flow'].map(lambda x: pathify(x))
table

cubes.add_cube(scraper1, table, title)
cubes.output_all()
