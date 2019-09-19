# ---
# jupyter:
#   jupytext:
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

# +
from gssutils import *

scraper = Scraper('https://www.ons.gov.uk/businessindustryandtrade/internationaltrade/datasets/' + \
                  'internationaltradeinservicesreferencetables')
scraper
# -

tabs = scraper.distributions[0].as_databaker()
str([tab.name for tab in tabs])


# +
def fix_service(row):
    service = pathify(row['H2'])
    group = pathify(row['H1'])
    if service == '':
        if group == 'total-international-trade-in-services':
            service = 'all'
        elif group.startswith('total-'):
            service = group[len('total-'):]
        else:
            assert False, 'Service label is empty, expecting some "total" grouping.'
    elif not group.startswith('total-'):
        service = group + '-' + service
    return service

def fix_title(s):
    service = pathify(s)
    pos = service.find('-analysed-by-')
    if pos != -1:
        service = service[:pos]
    # one title doesn't use "analysed by"
    pos = service.find('-industry-by-product-')
    if pos != -1:
        service = service[:pos + len('-industry')]
    return service    

def fix_area(row):
    area = pathify(row['H2'])
    if area == '':
        area = pathify(row['H1'])
    if area == 'total-international-trade-in-services':
        area = 'world'
    elif area.startswith('total-'):
        area = area[len('total-'):]
    return f"itis/{area}"

def process_tab(tab):
    tab_group = tab.name.strip()[:len('Table XX')][-2:]
    tab_title = tab.excel_ref('A1').fill(RIGHT).is_not_blank().by_index(1).value.strip()
    display(f"Processing '{tab.name}' ({tab_group}) '{tab_title}'")
    # not doing C0 which is a bit different
    top_left = tab.excel_ref('A1').fill(DOWN).is_not_blank().by_index(1)
    if tab_group[0] == 'C':
        bottom_left = tab.filter('Total International Trade in Services')
    else:
        bottom_left = tab.filter('TOTAL INTERNATIONAL TRADE IN SERVICES')
    bottom_left.assert_one()
    h1_labels = (top_left.expand(DOWN) & bottom_left.expand(UP)).filter(lambda c: c.value.strip() != '') | \
        (top_left.shift(RIGHT).expand(DOWN) & bottom_left.shift(RIGHT).expand(UP)).filter(lambda c: c.value.strip() != '')
    h2_labels = (top_left.expand(DOWN) & bottom_left.expand(UP)).shift(RIGHT).shift(RIGHT)
    year = top_left.shift(UP).fill(RIGHT).is_not_blank()
    # some flow labels are in a strange place as cells have been merged inconsistently
    flow = top_left.shift(UP).shift(UP).fill(RIGHT).is_not_blank()
    observations = (h2_labels.fill(RIGHT) & year.fill(DOWN)).is_not_blank()
    h1_dim = HDim(h1_labels, 'H1', CLOSEST, ABOVE) # can this be DIRECTLY?
    h1_dim.AddCellValueOverride('Total European Union', 'Total European Union (EU)')
    h1_dim.AddCellValueOverride('Total Information Services', 'Total Telecommunication Computer and Information Services Information Services')
    h1_dim.AddCellValueOverride('Total Construction Goods and Services', 'Total Construction Services')
    h1_dim.AddCellValueOverride('Total Australasia,Oceania and Total Unallocated', 'Total Australasia and Oceania and Total Unallocated')
    h2_dim = HDim(h2_labels, 'H2', DIRECTLY, LEFT)
    h2_dim.AddCellValueOverride('Other techincal services', 'Other technical services')
    cs = ConversionSegment(observations, [
        HDim(year, 'Year', DIRECTLY, ABOVE),
        h1_dim,
        h2_dim,
        HDim(flow, 'Flow', CLOSEST, LEFT),
    ])
    obs = cs.topandas()
    obs['Value'] = pd.to_numeric(obs['OBS'])
#     obs.dropna(subset=['Value'], inplace=True)
    obs.drop(columns=['OBS'], inplace=True)
#     if 'Marker' in obs:
#         obs.drop(columns=['Marker'], inplace=True)  
    obs['Year'] = obs['Year'].apply(lambda y: int(float(y)))
    if tab_group[0] in ['A', 'B']:
        obs['ITIS Industry'] = 'all'
        obs['ITIS Service'] = fix_title(tab_title)
        obs['ONS Trade Areas ITIS'] = obs.apply(fix_area, axis='columns')
    elif tab_group[0] == 'C':
        if tab_group == 'C1':
            obs['ITIS Industry'] = 'all'
        else:
            obs['ITIS Industry'] = fix_title(tab_title)
        obs['ITIS Service'] = obs.apply(fix_service, axis='columns')
        obs['ONS Trade Areas ITIS'] = 'itis/world'
    else:
        # Table D2 has 'Exports' in the wrong place
        if tab_group == 'D2':
            obs['Flow'].fillna('exports', inplace=True)
        obs['ITIS Industry'] = fix_title(tab_title)
        obs['ITIS Service'] = 'total-international-trade-in-services'
        obs['ONS Trade Areas ITIS'] = obs.apply(fix_area, axis='columns')
    obs.drop(columns=['H1', 'H2'], inplace=True)
    obs['Flow'] = obs['Flow'].apply(lambda x: pathify(x.strip()))
    obs['International Trade Basis'] = 'BOP'
    obs['Measure Type'] = 'GBP Total'
    obs['Unit'] = 'gbp-million'
    return obs
    return obs[['ONS Trade Areas ITIS', 'Year', 'Flow', 'ITIS Service', 'ITIS Industry',
                'International Trade Basis','Measure Type','Value','Unit', 'Marker']]

observations = pd.concat(process_tab(t) for t in tabs if t.name not in ['Contents', 'Table C0'])
# -

observations.rename(index= str, columns= {'DATAMARKER':'Marker'}, inplace = True)
observations['Marker'] = observations['Marker'].map(lambda x: { '-' : 'itis-nil','..' : 'disclosive'}.get(x, x))

for col in ['ONS Trade Areas ITIS', 'Flow', 'ITIS Service', 'ITIS Industry']:
    observations[col] = observations[col].astype('category')
    display(observations[col].cat.categories)

out = Path('out')
out.mkdir(exist_ok=True)
observations.drop_duplicates().to_csv(out / 'observations.csv', index = False)

# +
from gssutils.metadata import THEME
scraper.dataset.family = 'Trade'
scraper.dataset.theme = THEME['business-industry-trade-energy']

with open(out / 'dataset.trig', 'wb') as metadata:
     metadata.write(scraper.generate_trig())
csvw = CSVWMetadata('https://ons-opendata.github.io/ref_trade/')
csvw.create(out / 'observations.csv', out / 'observations.csv-schema.json')
# -


