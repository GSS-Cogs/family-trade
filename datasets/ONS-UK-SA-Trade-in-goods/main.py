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

# UK trade in services: all countries, non-seasonally adjusted

# +
from gssutils import *
import json

info = json.load(open('info.json'))
cubes = Cubes('info.json')
landingPage = info['landingPage']
landingPage

scraper = Scraper(landingPage)
scraper.dataset.family = info['families']

tabs = { tab.name: tab for tab in scraper.distributions[0].as_databaker() }
# -

output = pd.DataFrame()

# -

for name,tab in tabs.items():
    
    observations = tab.excel_ref('C7').expand(DOWN).expand(RIGHT).is_not_blank().is_not_whitespace()
    year = tab.excel_ref('C5').expand(RIGHT).is_not_blank().is_not_whitespace()
    geo = tab.excel_ref('A7').expand(DOWN).is_not_blank().is_not_whitespace()
    if name.split()[0] == 'Annual':
        datamarker = ' '.join([tab.excel_ref('A248').value, tab.excel_ref('A249').value])
    elif name.split()[0] == 'Monthly':
        datamarker = ' '.join([tab.excel_ref('A249').value, tab.excel_ref('A250').value])
    dimensions = [HDim(year,'Period',DIRECTLY,ABOVE),
                  HDim(geo,'ONS Partner Geography',DIRECTLY,LEFT)
                  #HDimConst('Measure Type', 'GBP Total'),
                  #HDimConst('Unit','gbp-million'),
                  #HDimConst('DATAMARKER', datamarker)
                  ]
    cs = ConversionSegment(observations, dimensions, processTIMEUNIT=True)
    df = cs.topandas()
    
    
    # Take the last word of the tab's name and convert it to lower case, assign as value in Flow column in df
    df['Flow'] = str(name.split()[-1]).lower()
    
    df.rename(columns={'OBS': 'Value'}, inplace=True)
    if name.split()[0] == 'Annual':
        #df['Period'] = pd.to_datetime(df['Period'].str[:4], format='%Y').dt.strftime('/id/year/%Y')
        df['Period'] = pd.to_datetime(df['Period'].str[:4], format='%Y').dt.strftime('year/%Y')
    elif name.split()[0] == 'Monthly':
        #df['Period'] = pd.to_datetime(df['Period'], format='%Y%b').dt.strftime('/id/month/%Y-%m')
        df['Period'] = pd.to_datetime(df['Period'], format='%Y%b').dt.strftime('month/%Y-%m')
    else:
        raise ValueError('Unexpected period')

    output = pd.concat([output, df])
    #output['ONS Partner Geography'] = output['ONS Partner Geography'].apply(pathify)

# +
output.rename(columns={'DATAMARKER': 'Marker'}, inplace=True)
output['Marker'].fillna('', inplace=True)
output.loc[(output['Marker'] == 'N/A'),'Marker'] = 'not-applicable'
output.loc[(output['Marker'] == 'not-applicable'),'Value'] = 0

output.insert(loc=2, column='Seasonal Adjustment', value="SA")
output = output[["Period", "ONS Partner Geography", "Seasonal Adjustment", "Flow", "Marker", "Value"]]

# +
scraper.dataset.family = 'trade'
scraper.dataset.description = scraper.dataset.description + """
These data are our best estimate of these bilateral UK trade flows. Users should note that alternative estimates are available, in some cases, via the statistical agencies for bilateral countries or through central databases such as 
UN Comtrade (https://comtrade.un.org/).

Some data for countries have been marked with N/A. This is because Trade in Goods do not collate data from these countries.
"""

output['Value'] = output['Value'].astype(int)


# +
#cubes.add_cube(scraper, output, info['title'])

#cubes.output_all()
# -

import os
from urllib.parse import urljoin

csvName = 'observations.csv'
out = Path('out')
out.mkdir(exist_ok=True)
output.drop_duplicates().to_csv(out / csvName, index = False)
output.drop_duplicates().to_csv(out / (csvName + '.gz'), index = False, compression='gzip')

dataset_path = pathify(os.environ.get('JOB_NAME', f'gss_data/{scraper.dataset.family}/' + Path(os.getcwd()).name)).lower()
scraper.set_base_uri('http://gss-data.org.uk')
scraper.set_dataset_id(dataset_path)

csvw_transform = CSVWMapping()
csvw_transform.set_csv(out / csvName)
csvw_transform.set_mapping(json.load(open('info.json')))
csvw_transform.set_dataset_uri(urljoin(scraper._base_uri, f'data/{scraper._dataset_id}'))
csvw_transform.write(out / f'{csvName}-metadata.json')
with open(out / f'{csvName}-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())

output.head(10)

output['Marker'].unique()




