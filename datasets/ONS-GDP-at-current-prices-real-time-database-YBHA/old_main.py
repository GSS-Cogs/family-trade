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

from gssutils import *
from gssutils.metadata import THEME
scraper = Scraper('https://www.ons.gov.uk/economy/grossdomesticproductgdp/datasets/realtimedatabaseforukgdpybha')
scraper

# +
dist = scraper.distributions[0]
tabs = (t for t in dist.as_databaker())
tidied_sheets = []

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
        return "quarter/{}-{}".format(time_string[3:7], time_string[:2])
    elif time_len == 10:       
        return 'gregorian-interval/' + time_string[:7] + '-01T00:00:00/P3M'


# -

for tab in tabs:
        if (tab.name == '1989 - 1999') or (tab.name == '2000 - 2010') or (tab.name == '2011 - 2017') or (tab.name == '2018 -'):
            
            seasonal_adjustment = 'SA'
            code = tab.excel_ref('B3')
            vintage = tab.excel_ref('A6').expand(DOWN).is_not_blank()        
            estimate_type = tab.excel_ref('B6').expand(RIGHT).is_not_blank()
            publication = tab.excel_ref('B7').expand(RIGHT).is_not_blank()
                
            if (tab.name == '2011 - 2017') or (tab.name == '2018 -'):
                estimate_type = tab.excel_ref('B5').expand(RIGHT).is_not_blank()
                publication = tab.excel_ref('B6').expand(RIGHT).is_not_blank()
        
            observations = publication.fill(DOWN).is_not_blank()
        
            dimensions = [
                HDim(vintage, 'GDP Reference Period', DIRECTLY, LEFT),
                HDim(estimate_type, 'GDP Estimate Type', DIRECTLY, ABOVE),
                HDim(publication, 'Publication Date', DIRECTLY, ABOVE),
                #HDim(code, 'CDID', CLOSEST, ABOVE), #dropped for now
                #HDimConst('Seasonal Adjustment', seasonal_adjustment),
                HDimConst('Measure Type', 'GBP Million'),
            ]

            tidy_sheet = ConversionSegment(tab, dimensions, observations)        
            #savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
            tidied_sheets.append(tidy_sheet.topandas())


df = pd.concat(tidied_sheets, ignore_index = True, sort = False)
df.rename(columns={'OBS' : 'Value','DATAMARKER' : 'Marker'}, inplace=True)
#df['CDID'] = df['CDID'].map(lambda x: right(x,4)) #dropped for now
df['Publication Date'].replace('Q3  1990', 'Q3 1990', inplace=True)  #removing space
df['Publication Date'].replace('Q 2004', 'Q4 2004', inplace=True) #fixing typo
df['GDP Reference Period'].replace('Q2 1010', 'Q2 2010', inplace=True) #fixing typo
df["GDP Reference Period"] = df["GDP Reference Period"].apply(date_time)
df["Publication Date"] = df["Publication Date"].apply(date_time)
df['Marker'].replace('..', 'unknown', inplace=True)

tidy = df[['GDP Reference Period','Publication Date','Value','GDP Estimate Type', 'Measure Type','Marker']]
for column in tidy:
    if column in ('GDP Estimate Type'):
        tidy[column] = tidy[column].str.lstrip()
        tidy[column] = tidy[column].str.rstrip()
tidy

out = Path('out-old')
out.mkdir(exist_ok=True)
tidy.drop_duplicates().to_csv(out / 'observations.csv', index = False)

# +
scraper.dataset.family = 'trade'

## Adding short metadata to description
additional_metadata = """ All data is seasonally adjusted.

In July 2018, a new GDP publication model was adopted. Quarterly estimates of GDP have since been published twice a quarter, rather than three times a quarter as happened prior to this.
"""
scraper.dataset.description = scraper.dataset.description + additional_metadata

from gssutils.metadata import THEME

with open(out / 'observations.csv-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())
# -

csvw = CSVWMetadata('https://gss-cogs.github.io/family-trade/reference/')
csvw.create(out / 'observations.csv', out / 'observations.csv-schema.json')
