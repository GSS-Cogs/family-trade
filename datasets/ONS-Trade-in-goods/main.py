# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.4.2
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
#table['Value'] = table['Value'].astype(int)

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

#line not needed data does not need to be supressed
table['Marker'] = ' '
#table.loc[(table['Value'] == 0), 'Marker'] = 'suppressed'

table = table[['ONS Partner Geography','Period','Flow','Commodity','Seasonal Adjustment','Value','Marker']]
table['Flow'] = table['Flow'].map(lambda x: pathify(x))
table

info_json_dataset_id = info.get('id', Path.cwd().name)
years = table['Period'].map(lambda p: p[-7:-3])
for period in years.unique():
    
    if len(cubes.cubes) == 0:
        graph_uri = f"http://gss-data.org.uk/graph/gss_data/trade/ons-trade-in-goods"
        csv_name = 'ons-trade-in-goods'
        cubes.add_cube(scraper1, table[years == period], csv_name, graph=info_json_dataset_id)
    else:
        graph_uri = f"http://gss-data.org.uk/graph/gss_data/trade/ons-trade-in-goods/{period}"
        csv_name = f"ons-trade-in-goods-{period}"
        cubes.add_cube(scraper1, table[years == period], csv_name, graph=info_json_dataset_id, override_containing_graph=graph_uri, suppress_catalog_and_dsd_output=True)

cubes.output_all()

### zipping currenlty not needed as space issue is resloved ###
#from urllib.parse import urljoin
#import os
#scraper1.dataset.family = "trade"
#csvName = 'observations.csv'
#out = Path('out')
#out.mkdir(exist_ok=True)
# Create the temp csv
#tempdat = table.iloc[0:5]
#tempdat.to_csv(out / csvName, index = False)
#table.drop_duplicates().to_csv(out / (csvName + '.gz'), index = False, compression='gzip')
#dataset_path = pathify(os.environ.get('JOB_NAME', f'gss_data/{scraper1.dataset.family}/{Path(os.getcwd()).name}'))
#scraper1.set_base_uri('http://gss-data.org.uk')
#scraper1.set_dataset_id(dataset_path)
#csvw_transform = CSVWMapping()
#csvw_transform.set_csv(out / csvName)
#csvw_transform.set_mapping(json.load(open('info.json')))
#csvw_transform.set_dataset_uri(urljoin(scraper1._base_uri, f'data/{scraper1._dataset_id}'))
#csvw_transform.write(out / f'{csvName}-metadata.json')
# Delete the temp csv
#(out / csvName).unlink()
#with open(out / f'{csvName}-metadata.trig', 'wb') as metadata:
 #   metadata.write(scraper1.generate_trig())

# +
oldStr1 = """<http://gss-data.org.uk/data/gss_data/trade/ons-trade-in-goods-catalog-entry> a pmdcat:Dataset;
    rdfs:label "UK trade in goods: country-by-commodity, exports and imports"@en;
    gdp:family gdp:Trade;
    gdp:updateDueOn "2021-06-11T00:00:00"^^xsd:dateTime;
    pmdcat:datasetContents <http://gss-data.org.uk/data/gss_data/trade/ons-trade-in-goods#dataset>;
    pmdcat:graph ns1:ons-trade-in-goods;
    dct:creator gov:office-for-national-statistics;"""

oldStr2 = """ dct:issued "2021-05-12"^^xsd:date;
    dct:license <http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/>;
    dct:modified "2021-05-25T08:08:41.773229+00:00"^^xsd:dateTime;
    dct:publisher gov:office-for-national-statistics;
    dct:title "UK trade in goods: country-by-commodity, exports and imports"@en;
    void:sparqlEndpoint <http://gss-data.org.uk/sparql>;
    rdfs:comment "Monthly export country-by-commodity data on the UK's trade in goods, including trade by all countries and selected commodities, non-seasonally adjusted."@en;
    dcat:contactPoint <mailto:trade@ons.gov.uk>;
    dcat:landingPage <https://www.ons.gov.uk/economy/nationalaccounts/balanceofpayments/datasets/uktradecountrybycommodityexports>;
    dcat:theme <https://www.ons.gov.uk/economy/nationalaccounts/balanceofpayments> ."""

newStr1 = """<http://gss-data.org.uk/data/gss_data/trade/ons-trade-in-goods-catalog-entry> a pmdcat:Dataset;
    rdfs:label "UK trade in goods: country-by-commodity, exports and imports"@en;
    gdp:family gdp:Trade;
    pmdcat:datasetContents <http://gss-data.org.uk/data/gss_data/trade/ons-trade-in-goods#dataset>;
    pmdcat:graph ns1:ons-trade-in-goods;
    dct:creator gov:office-for-national-statistics;

    schema:datePublished "2021-05-12T09:30:00.000+00:00"^^xsd:dateTime ;
    schema:dateModified "2021-05-12T09:30:00.000+00:00"^^xsd:dateTime ;
    gdp:updateDueOn "2021-06-11T00:00:00"^^xsd:dateTime;
    schema:name "UK trade in goods: country-by-commodity, exports and imports" ;
    schema:publisher gov:office-for-national-statistics;
    schema:repeatFrequency <http://purl.org/linked-data/sdmx/2009/code#freq-M> ;
    schema:description "Monthly import/export country-by-commodity data on the UK's trade in goods, including trade by all countries and selected commodities, non-seasonally adjusted." ;

    dct:issued "2021-05-12T09:30:00.000+00:00"^^xsd:date;
    dct:modified "2021-05-12T09:30:00.000+00:00"^^xsd:dateTime;
    dct:title "UK trade in goods: country-by-commodity, exports and imports"@en;
    dct:publisher gov:office-for-national-statistics;
    dct:accrualPeriodicity <http://purl.org/linked-data/sdmx/2009/code#freq-M> ;"""

newStr2 = """dct:license <http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/>;
    void:sparqlEndpoint <http://gss-data.org.uk/sparql>;
    rdfs:comment "Monthly export country-by-commodity data on the UK's trade in goods, including trade by all countries and selected commodities, non-seasonally adjusted."@en;
    dcat:contactPoint <mailto:trade@ons.gov.uk>;
    dcat:landingPage <https://www.ons.gov.uk/economy/nationalaccounts/balanceofpayments/datasets/uktradecountrybycommodityexports>;
    dcat:theme <https://www.ons.gov.uk/economy/nationalaccounts/balanceofpayments> ."""

# +
f = open("out/ons-trade-in-goods.csv-metadata.trig", "r")
st = f.read()
f.close()

st = st.replace(oldStr1, newStr1)
st = st.replace(oldStr2, newStr2)

f = open("out/ons-trade-in-goods.csv-metadata.trig", "w")
f.write(st)
f.close()

# -






