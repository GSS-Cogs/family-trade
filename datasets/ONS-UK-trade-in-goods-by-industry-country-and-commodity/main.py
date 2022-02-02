# %%

# UK trade in goods by industry, country and commodity, exports and imports



# [Notes for Shannon]
# overall i think the ticket 231 mainly wants me to sort the order of columns
# the original file from the amster branch strips out the descriptive part of the commodity, Industry and ONS Partner Geography columns. Do we want that as the end goal? keeping them allows me to sort properly but could delete after.

import pandas as pd
import json
from gssutils import *

# TODO Rich - look at what this means
# pd.options.mode.chained_assignment = None 

cubes = Cubes("info.json")
info = json.load(open('info.json'))

# %%
# get landing page(s) url to where data is located
landingPage = info['landingPage'] # 
landingPage

# %%
# two speparate landing pages
scraper1 = Scraper(landingPage[0])
scraper2 = Scraper(landingPage[1])

# TODO find out what this is doing exactly
scraper1.dataset.family = info['families'] # 
# %%

scraper2.session
# %%
# just grab latest dataset from both landing pages. They're structured the same but one is concerned with exports the other imports.
distribution1 = scraper1.distribution(latest=True) # exports
distribution2 = scraper2.distribution(latest=True) # imports

# %%
# TODO Rich - is new to me. see how to use loadxlstabs function from Databaker or pandas to get data from these distribution objects.
# i imagine it's a case of using distribution1.downloadURL
tabs1 = distribution1.as_databaker()
tabs2 = distribution2.as_databaker()
tabs = tabs1 + tabs2
# tabs

# %%
# not using this atm
url = distribution1.downloadURL
url

# %%
# TODO Shannon - i remove tabs we're not interested in. I had to add ' final' to export tab name. should we control for backwards compatibility?
tabs = [x for x in tabs if x.name in ('tig_ind_ex final', 'tig_ind_im') ]


# %%
tidied_sheets = []

# the title of both datasets is the same except one is for exports the other imports, so just take title from first distribution and add 'and imports' for the combined dataset
title = distribution1.title + ' and imports' 

for tab in tabs:

    # [Dimensions]
    
    if tab.name == 'tig_ind_ex final':
        flow = 'exports'
    elif tab.name == 'tig_ind_im':
        flow = 'imports' 
 
    country = tab.filter('Country').fill(DOWN).is_not_blank()
    industry = tab.filter('Industry').fill(DOWN).is_not_blank()
    commodity = tab.filter('Commodity').fill(DOWN).is_not_blank()
    year = tab.excel_ref('E1').expand(RIGHT).is_not_blank()
    # # comment out these dimensions because they can be defined by info.json file
    # measure = 'GBP Total'
    # unit = 'gbp-million'

    # [Dimensions]

    observations = year.fill(DOWN).is_not_blank() 

    # [Mapping obs to dimensions]

    dimensions = [
                HDimConst('Flow', flow),
                HDim(year,'Period', DIRECTLY,ABOVE),
                HDim(country,'ONS Partner Geography', DIRECTLY,LEFT),
                HDim(commodity,'Commodity', DIRECTLY,LEFT),
                HDim(industry,'Industry', DIRECTLY,LEFT)       
                ]
    cs = ConversionSegment(tab, dimensions, observations)
    tidy_sheet = cs.topandas()
    tidied_sheets.append(tidy_sheet)
# %%

# TODO Rich - cehckout what this is
pd.set_option('display.float_format', lambda x: '%.1f' % x) 

table = pd.concat(tidied_sheets, sort = True).fillna('') 

descr = """
Experimental dataset providing a breakdown of UK trade in goods by industry, country and commodity on a balance of payments basis. Data are subject to disclosure control, which means some data have been suppressed to protect confidentiality of individual traders.

Users should note the following:
Industry data has been produced using Standard Industrial Classification 2007 (SIC07).

Commodity data has been produced using Standard International Trade Classification (SITC).

Due to risks around disclosing data related to individual firms we are only able to provide data for certain combinations of the dimensions included, i.e. country, commodity and industry. This dataset therefore provides the following two combinations:
    Industry (SIC07 2 digit), by Commodity (SITC 2 digit), by geographic region (worldwide, EU and non-EU)
    Industry (SIC07 2 digit), by Commodity total, by individual country

Some data has been suppressed to protect confidentiality so that individual traders cannot be identified.

Methodology improvements
Within this latest experimental release improvements have been made to the methodology that has resulted in some revisions when compared to our previous release in April 2019.
These changes include; improvements to the data linking methodology and a targeted allocation of some of the Balance of Payments (BoP) adjustments to industry.
The data linking improvements were required due to subtleties in both the HMRC data and IDBR not previously recognised within Trade.

While we are happy with the quality of the data in this experimental release we have noticed some data movements, specifically in 2018.
We will continue to review the movements seen in both the HMRC microdata and the linking methodology and, where appropriate, will further develop the methodology for Trade in Goods by Industry for future releases. 

Data
All data is in £ million, current prices.

Rounding
Some of the totals within this release (e.g. EU, Non EU and worldwide) may not exactly match data published via other trade releases due to small rounding differences.

Trade Asymmetries
These data are our best estimate of these bilateral UK trade flows. Users should note that alternative estimates are available, in some cases, via the statistical agencies for bilateral countries or through central databases such as UN Comtrade.
UN Comtrade.
"""
# %%
# TODO Shannon - why are we updating both of these, and they're different from the title created earlier? Does the scraper object get used later?
scraper1.dataset.title = 'UK trade in goods by industry, country and commodity - Imports & Exports'
scraper2.dataset.title = 'UK trade in goods by industry, country and commodity - Imports & Exports'
scraper1.dataset.description = descr
scraper2.dataset.description = descr

# [Clean up]
# %%

#remove rows
# TODO Rich - confused. i'm removing observations here if zero, but putting them back in two lines down...maybe it's totals
table = table[table['OBS'] != 0] # remove rows with 0 values in observations
# TODO TODO check what is being removed and put back in place

# replace DATAMARKER values
table.loc[table['DATAMARKER'].astype(str) == '..', 'DATAMARKER'] = 'suppressed' 
# replace empty values with 0
table['OBS'].loc[(table['OBS'] == '')] = 0 
table['OBS'] = table['OBS'].astype(int) 


# %%
## pre-sort preparation

# separate code from descriptive name so can order columns later
table['Commodity Code'] = table['Commodity'].str[:2]
table['ONS Partner Geography Code'] = table['ONS Partner Geography'].str[:2]
table['Industry Code'] = table['Industry'].str[:2]
#%%
# TODO Rich - might come back to this. see if end users want code separated
# # need to remove code from descriptive name
# table['Commodity'] = table['Commodity'].str[2:]
# table['ONS Partner Geography'] = table['ONS Partner Geography'].str[2:]
# table['Industry'] = table['Industry'].str[2:]
#%%
#trimming the code and description columns would have left some unwanted spaces so removing them
# TODO Rich - might un comment these depending on previous TODO
# table['Industry'] = table['Industry'].str.strip()
# table['Commodity'] = table['Commodity'].str.strip()
# table['ONS Partner Geography'] = table['ONS Partner Geography'].str.strip()
table['Industry Code'] = table['Industry Code'].str.strip()
table['Commodity Code'] = table['Commodity Code'].str.strip()
table['ONS Partner Geography Code'] = table['ONS Partner Geography Code'].str.strip()

# %%
# temporarily replace non numeric codes. picked 99 so non-numeric codes go at end of table and don't think it's being used by others
non_numeric_codes_to_replace = {
'Commodity Code' : { 'T' : '99', '7E' : '99', '7M' : '99' ,'8O': '99'} # TODO Rich - search a quicker way to set them all to 99
,'Industry Code': {'U':'99'}
}

table = table.replace(non_numeric_codes_to_replace) 

# %%
#convert codes to int so i can sort later. need to replace letters with numbers first then change back later
table['Commodity Code']= table['Commodity Code'].astype(int)
table['Industry Code'] = table['Industry Code'].astype(int)

table.head(10)
# %%
# sort column order
table = table.sort_values(['Period', 'ONS Partner Geography Code','Industry Code','Commodity Code'], ascending = (False, True, True, True))

# TODO Rich - del columns no longer needed...might come back and put them in depending on previous
del table['Industry Code']
del table['Commodity Code']
del table['ONS Partner Geography Code']

# %%
#reformat period column
table['Period'] = 'year/' + table['Period'].str[0:4]

#%%
#rename columns
table.rename(columns={'OBS': 'Value', 'DATAMARKER' : 'Marker'}, inplace=True)

# %%
#reorder columns
table = table[['Period','ONS Partner Geography','Industry','Flow','Commodity', 'Value', 'Marker']]

#%%

cubes.add_cube(scraper1, table, title)
cubes.output_all()