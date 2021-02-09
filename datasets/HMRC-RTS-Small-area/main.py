# ---
# jupyter:
#   jupytext:
#     cell_metadata_json: true
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.9.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# cd /workspace/family-trade/datasets/HMRC-RTS-Small-area/

# +
from gssutils import *
import json

info = json.load(open('info.json'))
scraper = Scraper(seed='info.json')  
cubes = Cubes('info.json')
scraper 
# -

scraper.select_dataset(latest=True)

tabs = {tab.name: tab for tab in scraper.distribution(title=lambda t: 'Data Tables' in t).as_databaker()}

year_cell = tabs['Title'].filter('Detailed Data Tables').shift(UP)
year_cell.assert_one()
dataset_year = int(year_cell.value)
#dataset_year

# +
# %%capture

def process_tab(t):
    %run "$t"
    return tidy

table = pd.concat(process_tab(f'{t}.py') for t in ['T1','T2','T3','T4','T5'])
table.count()
# +
import numpy
table['HMRC Partner Geography'] = numpy.where(table['HMRC Partner Geography'] == 'EU', 'C', table['HMRC Partner Geography'])
table['HMRC Partner Geography'] = numpy.where(table['HMRC Partner Geography'] == 'Non-EU', 'non-eu', table['HMRC Partner Geography'])

sorted(table)
table = table[(table['Marker'] != 'residual-trade')]
table = table[(table['Marker'] != 'below-threshold-traders')]
table["Measure Type"] = table["Measure Type"].apply(pathify)
table = table.drop_duplicates()

#Flow has been changed to Flow Direction to differentiate from Migration Flow dimension
table.rename(columns={'Flow':'Flow Directions'}, inplace=True)

# -

scraper.dataset.family = 'trade'
measures = {
    'count-of-businesses': {
                "unit": "http://gss-data.org.uk/def/concept/measurement-units/businesses",
                "measure": "http://gss-data.org.uk/def/trade/measure/count",
                "datatype": "double"
            },
    'gbp-total': {
                "unit": "http://gss-data.org.uk/def/concept/measurement-units/gbp-million",
                "measure": "http://gss-data.org.uk/def/trade/measure/value",
                "datatype": "double"
            }
}
for measure, value_map in measures.items():
    info["transform"]["columns"]["Value"] = value_map
    table_wanted = table.loc[table['Measure Type'].str.strip() == measure].reset_index(drop=True).drop_duplicates()
    cubes.add_cube(scraper, table_wanted, measure, info_json_dict=info, graph='HMRC-RTS-Small-area')   

cubes.output_all()


