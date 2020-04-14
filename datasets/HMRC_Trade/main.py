# -*- coding: utf-8 -*-
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

# +
from gssutils import *
import json 
import requests

info = json.load(open('info.json')) 
landingPage = info['landingPage2']  

scraper = Scraper(landingPage)

idbrs = sorted(
    [dist for dist in scraper.distributions if dist.title.startswith('IDBR')],
    key=lambda d: d.title, reverse=True)
idbr = idbrs[0]
display(idbr.title)
yr = idbr.title[-4:]
#tabs = {tab.name: tab for tab in idbr.as_databaker()}
#tabs.keys()
print('Year: ' + yr)

# -

url = idbr.downloadURL
#url = 'https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/847399/IDBR_OTS_tables_2018.XLS'
myfile = requests.get(url)
open('data.xls', 'wb').write(myfile.content)

# +
sheets = ['1. Industry Group', '2. Age Group','3. Business Size']

grops = 'HMRC Industry'
types = 'HMRC Trade Statistic Type'
flows = 'Flow Directions'

alltbls = []
# -

for sh in sheets:
    df = pd.read_excel(io='data.xls', sheet_name=sh)

    df[df.columns[0]][df[df.columns[0]] == 'Total8'] = 'Total'
    df[df.columns[0]][df[df.columns[0]] == 'Unknown7'] = 'Unknown'
    
    # Save the notes in a separate var and remove from main var
    notesind = list(df.index[df[df.columns[0]] == 'Notes:'])
    notes = df.loc[notesind[0]:,]
    df = df.loc[0:notesind[0]-1,]

    df = df.fillna('-')
    # Get the Row numbers of instances of Exports dn Total, which define where the tables are
    expind = list(df.index[df[df.columns[2]] == 'Exports'])
    totind = list(df.index[df[df.columns[0]] == 'Total'])

    print(sh + ' - Row Numbers for Exports: ' + str(expind))
    print(sh + ' - Row Numbers for Total: ' + str(totind))
    
    tbls = []
    ind2 = 0
    for ind1 in expind:
        try:
            tbl = df.loc[ind1+3:totind[ind2]]
            tbl[tbl.columns[1]] = df.iloc[ind1 - 1,0]
            tbl['Unit'] = df.iloc[ind1 - 1,4]
            tbl.columns = [grops, types, 'Exports', 'Spare', 'Imports', 'Unit']
            
            t1 = tbl[[grops, types, 'Exports', 'Unit']]
            t1 = t1.rename(columns={'Exports': 'Value'})
            t1[flows] = 'Exports'
            t2 = tbl[[grops, types, 'Imports', 'Unit']]
            t2 = t2.rename(columns={'Imports': 'Value'})
            t2[flows] = 'Imports'
            tbl = pd.concat([t1,t2])
            tbls.append(tbl)
            
        except Exception as e:
            print('Error creating table: ' + str(e))
        ind2 = ind2 + 1
    
    tbls = pd.concat(tbls)
    
    tbls['Period'] = yr
    tbls['Marker'] = ''
    
    if sh == sheets[0]:
        tbls['Marker'][tbls['Value'].str.strip() == '.'] = 'unknown'
        tbls['Unit'] = '£ millions'
    elif sh == sheets[1]:
        tbls['Marker'][tbls['Value'].str.strip() == '.'] = 'not-applicable'
        tbls['Unit'] = 'business count'
    elif sh == sheets[2]:  
        tbls['Marker'][tbls['Value'].str.strip() == '.'] = 'not-applicable'
        tbls['Unit'] = 'employee count'
    
    tbls = tbls[tbls['Value'].str.strip() != '-']
    tbls['Value'][tbls['Value'] == '.'] = '0'
    alltbls.append(tbls)


# +
age = 'Age of Business'
size = 'Size of Business by no of Employees'
colord = ['Period', grops, age, size, types, flows, 'Unit', 'Value', 'Marker']

alltbls[0][age] = 'All'
alltbls[0][size] = 'All'
alltbls[0] = alltbls[0][colord]

alltbls[1] = alltbls[1].rename(columns={grops: age})
alltbls[1][grops] = 'All'
alltbls[1][size] = 'All'
alltbls[1] = alltbls[1][colord]

alltbls[2] = alltbls[2].rename(columns={grops: size})
alltbls[2][grops] = 'All'
alltbls[2][age] = 'All'
alltbls[2] = alltbls[2][colord]

alltbls1 = pd.concat(alltbls)
#alltbls1.head(60)
# -

del df
sheets = ['4. Industry_Age', '5. Industry_BusinessSize', '6. BusinessSize_Age']

tbls = []
for sh in sheets:
    df = pd.read_excel(io='data.xls', sheet_name=sh)
    
    df[df.columns[0]][df[df.columns[0]] == 'Grand Total7'] = 'Total'
    df[df.columns[0]][df[df.columns[0]] == 'Grand Total8'] = 'Total'
    
    # Save the notes in a separate var and remove from main var
    notesind = list(df.index[df[df.columns[0]] == 'Notes:'])
    notes = df.loc[notesind[0]:,]
    df = df.loc[0:notesind[0]-1,]
    
    # Get the Row numbers of instances of Exports dn Total, which define where the tables are
    expind = list(df.index[df[df.columns[3]] == 'Exports'])
    totind = list(df.index[df[df.columns[0]] == 'Total'])
    
    df[df.columns[0]].fillna(value = pd.np.nan, inplace = True)
    df[df.columns[0]] = df[df.columns[0]].ffill()
    df = df.fillna('-')
    
    print(sh + ' - Row Numbers for Exports: ' + str(expind))
    print(sh + ' - Row Numbers for Total: ' + str(totind))
    ind2 = 0
    for ind1 in expind:
        try:
            tbl = df.loc[ind1+3:totind[ind2]]
            cn = list(tbl.columns)
            t1 = tbl[[cn[0],cn[1],cn[3]]]
            t1 = t1.rename(columns={cn[3]: 'Value'})
            t1[flows] = 'Exports'
            t1['Unit'] = '£ million'
            t2 = tbl[[cn[0],cn[1],cn[4]]]
            t2 = t2.rename(columns={cn[4]: 'Value'})
            t2[flows] = 'Exports'
            t2['Unit'] = 'Business Count'
            t3 = tbl[[cn[0],cn[1],cn[5]]]
            t3 = t3.rename(columns={cn[5]: 'Value'})
            t3[flows] = 'Exports'
            t3['Unit'] = 'Employee Count'
            t4 = tbl[[cn[0],cn[1],cn[7]]]
            t4 = t4.rename(columns={cn[7]: 'Value'})
            t4[flows] = 'Imports'
            t4['Unit'] = '£ million'
            t5 = tbl[[cn[0],cn[1],cn[8]]]
            t5 = t5.rename(columns={cn[8]: 'Value'})
            t5[flows] = 'Imports'
            t5['Unit'] = 'Business Count'
            t6 = tbl[[cn[0],cn[1],cn[9]]]
            t6 = t6.rename(columns={cn[9]: 'Value'})
            t6[flows] = 'Imports'
            t6['Unit'] = 'Employee Count'

            tbl = pd.concat([t1,t2,t3,t4,t5,t6])
            tbl['Marker'] = ''
            tbl['Marker'][tbl['Value'].str.strip() == '.'] = 'not-applicable'
            tbl.columns = [grops, age, 'Value', flows, 'Unit', 'Marker']
            tbl = tbl[tbl['Value'].str.strip() != '-']
            tbls.append(tbl)
            #print(tbls)
        except Exception as e:
            print('Error creating table: ' + str(e))
        ind2 = ind2 + 1


# +
tbls[0][size] = 'All'
tbls[0]['Period'] = yr
tbls[0][types] = 'Employee count for business by Industry group and Age of business'
tbls[0] = tbls[0][colord]

tbls[1]['Period'] = yr
tbls[1] = tbls[1].rename(columns={age: size})
tbls[1][age] = 'All'
tbls[1][types] = 'Employee count for business by Industry group and Business size'
tbls[1] = tbls[1][colord]

tbls[2] = tbls[2].rename(columns={grops: size})
tbls[2]['Period'] = yr
tbls[2][grops] = 'All'
tbls[2][types] = 'Employee count for business by Business size and Age of business'
tbls[2] = tbls[2][colord]

alltbls2 = pd.concat(tbls)
#alltbls2.head(60)
# -

alltbls = pd.concat([alltbls1, alltbls2])

# +
alltbls[grops] = (alltbls[grops].str[:8]).apply(pathify)
alltbls[grops][alltbls[grops] == 'total'] = 'all'

alltbls[size][alltbls[size] == 0] = '0'
alltbls[size] = alltbls[size] + ' Employees'
alltbls[size][alltbls[size].str.strip() == '250 +'] = '250'
alltbls[size] = alltbls[size].apply(pathify)
alltbls[size][alltbls[size] == ''] = 'all'
alltbls[size][alltbls[size].str.strip() == '-employees'] = 'all-employees'

alltbls[age][alltbls[age] == '-'] = 'all'
alltbls[age][alltbls[age].str.strip() == '20 +'] = '20'
alltbls[age] = (alltbls[age] + ' Years').apply(pathify)
alltbls[age][alltbls[age] == 'unknown-years'] = 'unknown'
alltbls[age][alltbls[age] == 'total-years'] = 'total'
alltbls[age][alltbls[age] == 'all-years'] = 'total'

alltbls[types] = alltbls[types].apply(pathify)
alltbls[flows] = alltbls[flows].apply(pathify)

alltbls.replace({'Unit': {'number': 'Count'}}, inplace=True)
alltbls['Unit'] = alltbls['Unit'].apply(pathify)
alltbls.replace({'Unit': {'ps-million': 'gbp-million', 'ps-millions': 'gbp-million'}}, inplace=True)

alltbls['Marker'][alltbls['Value'].str.strip() == 'S'] = 'suppressed'
alltbls['Value'][alltbls['Value'].str.strip() == 'S'] = 0
alltbls['Value'][alltbls['Value'].str.strip() == '.'] = 0

alltbls['Measure Type'] = ''
alltbls['Measure Type'][alltbls['Unit'] == 'gbp-million'] = 'GBP Total'
#alltbls['Unit'][alltbls['Unit'] == 'employee-count'] = 'count-of-businesses'
#alltbls['Unit'][alltbls['Unit'] == 'business-count'] = 'count-of-employees'
alltbls['Measure Type'][alltbls['Unit'] == 'business-count'] = 'Count'
alltbls['Measure Type'][alltbls['Unit'] == 'employee-count'] = 'Count'

alltbls['Period'] = 'year/' + alltbls['Period']
#alltbls.head(60)
# -



from pathlib import Path
import numpy as np
out = Path('out')
out.mkdir(exist_ok=True)

# +
from os import environ

tit1 = 'ONS International exports of services from the UK by NUTS area, Industry and destination'

fn1 = 'observations'

scraper.dataset.family = 'trade'
from gssutils.metadata import THEME
scraper.dataset.theme = THEME['business-industry-trade-energy']

alltbls.drop_duplicates().to_csv(out / (fn1 + '.csv'), index = False)
scraper.set_dataset_id(f'{pathify(environ.get("JOB_NAME", ""))}/{fn1}')

comDesc = """
    Supporting tables for the UK trade in goods by business characteristics 2018
    This spreadsheet contains estimates of trade in goods data matched with registered businesses from the 
    Inter-Departmental Business Register (IDBR) for exporters and importers for 2018.
    This data is now presented on a 'Special Trade' basis, in line with the change in the compilation method 
    for the UK Overseas Trade Statistics (OTS).
    More details on the methodology used to produce these estimates and issues to be aware of when using 
    the data can be found on the
    metadata tab.
    These estimates do not cover all businesses. They do not cover:
    Unregistered businesses (those not registered for VAT or Economic Operator Registration and Identification (EORI)).
    Due to these experimental statistics being subject to active disclosure controls the data has been suppressed 
    according to GSS guidance on disclosure control.  Suppressed cells are shown with an 'S'
    """
scraper.dataset.comment = 'Supporting tables for the UK trade in goods by business characteristics 2018'
scraper.dataset.description = comDesc
scraper.dataset.title = 'HMRC Trade in Goods'

with open(out / (fn1 + '.csv-metadata.trig'), 'wb') as metadata:metadata.write(scraper.generate_trig())
csvw = CSVWMetadata('https://gss-cogs.github.io/family-trade/reference/')
csvw.create(out / (fn1 + '.csv'), out / ((fn1 + '.csv') + '-schema.json'))
# -




