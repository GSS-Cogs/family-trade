# -*- coding: utf-8 -*-
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

# ## Balance of Payments: Current Account and Capital Accounts

# +
import copy 
import pandas as pd
from gssutils import *
import json
from databaker.framework import *

cubes = Cubes("info.json")

pd.options.mode.chained_assignment = None 

scraper = Scraper(seed='info.json')

distribution = scraper.distribution(latest=True)

mainDescr = scraper.dataset.description
mainDescr
# -

tabs = distribution.as_databaker()


# +
def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]


# -

with open("info.json", "r") as jsonFile:
    data = json.load(jsonFile)
data["transform"]["columns"]["Value"]["measure"] = "http://gss-data.org.uk/def/measure/bop-current-account"
with open("info.json", "w") as jsonFile:
    json.dump(data, jsonFile, indent = 2)

# +
trace = TransformTrace()

for tab in tabs:
    if 'B1' in tab.name:      
        title = distribution.title + ' - Summary of balance of payments' 
        columns = ['Period','Flow Directions','Services','Seasonal Adjustment', 'CDID', 'Account Type', 'Value', 
           'Measure Type', 'Unit']
        trace.start(title, tab, columns, distribution.downloadURL) 
        
        scraper.dataset.title = "UK Economic Accounts: balance of payments - Current Account - Summary of balance of payments"
        scraper.dataset.comment = "Contents of the balance of payments: Current Account. Summary of balance of payments - Quarterly transactions"
        scraper.dataset.description = scraper.dataset.comment  + """
        Current balance as a percentage of GDP: using series YBHA: GDP at current market prices
        Financial Accounts: when downloading data from the UKEA dataset users should reverse the sign of series that have an identifier that is prefixed with a minus sign.
        Net errors and omossions: This series represents net errors and omissions in the balance of payments accounts. It is the converse of the not seasonally adjusted current and capital balances (HBOG and FKMJ) and net financial account transactions (HBNT) and is required to balance these three accounts.
        """
        
        ## "Removing records of 'Balances as a percentage of GDP' & 'Current balance as a % of GDP' information")
        remove_percentage = tab.excel_ref('A30').expand(RIGHT).expand(DOWN) - tab.excel_ref('A41').expand(RIGHT).expand(DOWN)
        
        trace.Account_Type("Selected as current account and financial account")
        account_type = tab.excel_ref('B').expand(DOWN).by_index([9,44,66]) - tab.excel_ref('B76').expand(DOWN)
        
        trace.Seasonal_Adjustment("Selected as Seasonally Adjusted or Non-seasonally Adjusted")
        seasonal_adjustment = tab.excel_ref('B').expand(DOWN).by_index([7,42]) - tab.excel_ref('B76').expand(DOWN)
        
        flow = tab.excel_ref('B2')
        
        trace.Services("Selected as trade activities, from cell 'B' with the removal of percentage, account type and seasonal ajuestment")
        services = tab.excel_ref('B10').expand(DOWN).is_not_blank() - remove_percentage - account_type - seasonal_adjustment 
        
        code = tab.excel_ref('C7').expand(DOWN).is_not_blank()
        year =  tab.excel_ref('D4').expand(RIGHT).is_not_blank()
        quarter = tab.excel_ref('D5').expand(RIGHT)
        observations = quarter.fill(DOWN).is_not_blank() - remove_percentage
        
        dimensions = [
            HDim(account_type, 'Account Type', CLOSEST, ABOVE),
            HDim(seasonal_adjustment, 'Seasonal Adjustment', CLOSEST, ABOVE),
            HDim(flow, 'Flow Directions', CLOSEST, ABOVE),
            HDim(services, 'Services', DIRECTLY, LEFT),
            HDim(code, 'CDID', DIRECTLY, LEFT),
            HDim(year, 'Period', DIRECTLY, ABOVE),
            HDim(quarter, 'Quarter', DIRECTLY, ABOVE),
            HDimConst('Measure Type', 'bop-current-account'),
            HDimConst('Unit', 'gbp-million')
        ]
        
        cs = ConversionSegment(tab, dimensions, observations)        
        tidy_sheet = cs.topandas() 
        trace.store('dataframeB1', tidy_sheet)
        df = trace.combine_and_trace(title, 'dataframeB1')

        df['Period'] = df.Period.str.replace('\.0', '')
        df['Quarter'] = df['Quarter'].str.lstrip()
        df['Period'] = df['Period'] + df['Quarter']
        df['Period'] = df['Period'].map(lambda x: 'year/' + left(x,4) if 'Q' not in x else 'quarter/' + left(x,4) + '-' + right(x,2))
        df.drop(['Quarter'], axis=1, inplace=True)
        
        if 'CDID' in df.columns:
            df.drop('CDID', axis=1, inplace=True)
        
        df['OBS'].loc[(df['OBS'] == '')] = '0'
        df['OBS'] = df['OBS'].astype(int)

        df['Account Type'] = df['Account Type'].map(lambda x: x.split()[0]) + ' ' +  df['Account Type'].map(lambda x: x.split()[1])
        df['Account Type'] = df['Account Type'].str.rstrip('1')
        df['Account Type'] = df['Account Type'].str.rstrip('2')
        df['Services'] = df['Services'].str.rstrip('3')
        df['Services'] = df['Services'].str.lstrip()
        df = df.replace({'Seasonal Adjustment' : {' Seasonally adjusted' : 'SA', ' Not seasonally adjusted': 'NSA' }})
        df['Flow Directions'] = df['Flow Directions'].map(lambda x: x.split()[0])
        df.rename(columns={'OBS' : 'Value', 'DATAMARKER' : 'Marker'}, inplace=True)

        #tidy = df[['Period','Flow Directions','Services','Seasonal Adjustment', 'CDID', 'Account Type', 'Value', 
        #  'Measure Type', 'Unit']]
        tidy = df[['Period','Flow Directions','Services','Seasonal Adjustment', 'Account Type', 'Value']]
        for column in tidy:
            if column in ('Flow Directions', 'Services', 'Account Type'):
                tidy[column] = tidy[column].str.lstrip()
                tidy[column] = tidy[column].map(lambda x: pathify(x))

        cubes.add_cube(copy.deepcopy(scraper), tidy, scraper.dataset.title)
    
    
    # B2 B2A B3B3A
    title = distribution.title + ' :Trade in goods and services'
    #columns = ['Period','Flow Directions','Product','Seasonal Adjustment', 'CDID', 'Services', 'Account Type', 'Value', 'Marker', 'Measure Type', 'Unit']
    columns = ['Period','Flow Directions','Product','Seasonal Adjustment', 'Services', 'Account Type', 'Value', 'Marker', 'Measure Type', 'Unit']
    scraper.dataset.title = "UK Economic Accounts: balance of payments - Current Account - Trade in goods and services"
    scraper.dataset.comment = "Contents of the balance of payments: Trade in goods and services - Quarterly transactions"
    scraper.dataset.description = scraper.dataset.comment
    
    if 'B2' in tab.name: 

        trace.start(title, tab, columns, distribution.downloadURL)
        trace.Flow_Directions("Selected as Exports, Imports and Balances")
        flow = tab.excel_ref('B').expand(DOWN).by_index([7,21,35]) - tab.excel_ref('B46').expand(DOWN)

        trace.Product("Selcted as products from cell B and removing flow directions, trade and seasonal adjustment")
        product = tab.excel_ref('B').expand(DOWN).is_not_blank().is_not_whitespace() - flow  - tab.excel_ref('B3').expand(UP)

        code = tab.excel_ref('C7').expand(DOWN).is_not_blank()
        year =  tab.excel_ref('D4').expand(RIGHT).is_not_blank()
        quarter = tab.excel_ref('D5').expand(RIGHT)
        seasonal_adjustment = tab.excel_ref('B2')
        trade = tab.excel_ref('B1')
        observations = quarter.fill(DOWN).is_not_blank()

        dimensions = [
            HDim(year, 'Period', DIRECTLY, ABOVE),
            HDim(quarter, 'Quarter', DIRECTLY, ABOVE),
            HDim(code, 'CDID', DIRECTLY, LEFT),
            HDim(flow, 'Flow Directions', CLOSEST, ABOVE),
            HDim(product, 'Product', DIRECTLY, LEFT),
            HDim(seasonal_adjustment, 'Seasonal Adjustment', CLOSEST, LEFT),
            HDim(trade, 'Services', CLOSEST, LEFT),
            HDimConst('Account Type', 'Current Account')#,
            #HDimConst('Measure Type', 'bop-current-account'),
            #HDimConst('Unit', 'gbp-million')   
        ]
        
        cs = ConversionSegment(tab, dimensions, observations) 
        tidy_sheet = cs.topandas() 
        trace.store('combined_dataframeB23', tidy_sheet)

    elif 'B3' in tab.name: 

        trace.start(title, tab, columns, distribution.downloadURL)

        flow = tab.excel_ref('B').expand(DOWN).by_index([7,22,37]) - tab.excel_ref('B51').expand(DOWN)
        product = tab.excel_ref('B').expand(DOWN).is_not_blank().is_not_whitespace() - flow  - tab.excel_ref('B3').expand(UP)
        code = tab.excel_ref('C7').expand(DOWN).is_not_blank()
        year =  tab.excel_ref('D4').expand(RIGHT).is_not_blank()
        quarter = tab.excel_ref('D5').expand(RIGHT)
        seasonal_adjustment = tab.excel_ref('B2')
        trade = tab.excel_ref('B1')
        observations = quarter.fill(DOWN).is_not_blank()

        dimensions = [
            HDim(year, 'Period', DIRECTLY, ABOVE),
            HDim(quarter, 'Quarter', DIRECTLY, ABOVE),
            HDim(code, 'CDID', DIRECTLY, LEFT),
            HDim(flow, 'Flow Directions', CLOSEST, ABOVE),
            HDim(product, 'Product', DIRECTLY, LEFT),
            HDim(seasonal_adjustment, 'Seasonal Adjustment', CLOSEST, LEFT),
            HDim(trade, 'Services', CLOSEST, LEFT),
            HDimConst('Account Type', 'Current Account'),
            HDimConst('Measure Type', 'bop-current-account'),
            HDimConst('Unit', 'gbp-million'),
         ]

        cs = ConversionSegment(tab, dimensions, observations)
        tidy_sheet = cs.topandas() 
        trace.store('combined_dataframeB23', tidy_sheet)
        df = trace.combine_and_trace(title, "combined_dataframeB23")
        
        df['Period'] = df.Period.str.replace('\.0', '')
        df['Quarter'] = df['Quarter'].str.lstrip()
        df['Period'] = df['Period'] + df['Quarter']
        df['Period'] = df['Period'].map(lambda x: 'year/' + left(x,4) if 'Q' not in x else 'quarter/' + left(x,4) + '-' + right(x,2))
        df.drop(['Quarter'], axis=1, inplace=True)
        
        if 'CDID' in df.columns:
            df.drop('CDID', axis=1, inplace=True)
        
        df['OBS'].loc[(df['OBS'] == '')] = '0'
        df['OBS'] = df['OBS'].astype(int)
        
        df['Flow Directions'] = df['Flow Directions'].map(lambda x: x.split()[0])
        df = df.replace({'Seasonal Adjustment' : {' Seasonally adjusted' : 'SA', ' Not seasonally adjusted' : 'NSA' }})
        df['Product'] = df['Product'].str.lstrip()
        df.rename(columns={'OBS' : 'Value','DATAMARKER' : 'Marker'}, inplace=True)
        df['Marker'].replace(' -', 'unknown', inplace=True)
        
        #tidy = df[['Period','Flow Directions','Product','Seasonal Adjustment', 'CDID', 'Services', 'Account Type', 'Value', 'Marker', 'Measure Type', 'Unit']]
        tidy = df[['Period','Flow Directions','Product','Seasonal Adjustment', 'Services', 'Account Type', 'Value', 'Marker']]
        for column in tidy:
            if column in ('Flow Directions', 'Product', 'Services', 'Account Type'):
                tidy[column] = tidy[column].str.lstrip()
                tidy[column] = tidy[column].map(lambda x: pathify(x))

        cubes.add_cube(copy.deepcopy(scraper), tidy, scraper.dataset.title)
        
    #B4, B4A & B4B
    if 'B4' in tab.name: 
        title = distribution.title + ' :Primary income'
        #columns = ['Period','Flow Directions', 'Income', 'Income Description', 'Earnings', 'Account Type', 'Seasonal Adjustment', 'CDID', 'Value', 'Marker', 'Measure Type', 'Unit']
        columns = ['Period','Flow Directions', 'Income', 'Income Description', 'Earnings', 'Account Type', 'Seasonal Adjustment', 'Value', 'Marker', 'Measure Type', 'Unit']
        
        scraper.dataset.title = "UK Economic Accounts: balance of payments - Current Account - Primary Income"
        scraper.dataset.comment = "Contents of the balance of payments: Primary Income - Quarterly transactions"
        scraper.dataset.description = scraper.dataset.comment + """
        Other primary income: includes taxes and subsidies on products and production was previously classified to secondary income.
        Monetary financial institutions:  Banks and building societies
        """
        
        trace.start(title, tab, columns, distribution.downloadURL)   
        
        income = tab.excel_ref('B10').expand(DOWN).is_not_blank()  
        code = tab.excel_ref('C7').expand(DOWN).is_not_blank()
        year =  tab.excel_ref('D4').expand(RIGHT).is_not_blank()
        quarter = tab.excel_ref('D5').expand(RIGHT)
        seasonal_adjustment = tab.excel_ref('B2')
        income_type = tab.excel_ref('B1')
        observations = quarter.fill(DOWN).is_not_blank()
        
        if tab.name == 'B4B':
            flow = tab.excel_ref('B').expand(DOWN).by_index([7,18,29]) - tab.excel_ref('B40').expand(DOWN)
            earning_type = tab.excel_ref('B').expand(DOWN).by_index([9,20,31]) - tab.excel_ref('B40').expand(DOWN)
        if tab.name == 'B4':
            earning_type = tab.excel_ref('B').expand(DOWN).by_index([9,31,52]) - tab.excel_ref('B72').expand(DOWN)
            flow = tab.excel_ref('B').expand(DOWN).by_index([7,29,50]) - tab.excel_ref('B72').expand(DOWN)
        if tab.name == 'B4A':
            earning_type = tab.excel_ref('B').expand(DOWN).by_index([9,31,51]) - tab.excel_ref('B70').expand(DOWN)
            flow = tab.excel_ref('B').expand(DOWN).by_index([7,29,50]) - tab.excel_ref('B70').expand(DOWN)
        
        dimensions = [
            HDim(year, 'Period', DIRECTLY, ABOVE),
            HDim(quarter, 'Quarter', DIRECTLY, ABOVE),
            HDim(code, 'CDID', DIRECTLY, LEFT),
            HDim(flow, 'Flow Directions', CLOSEST, ABOVE),
            HDim(income, 'Income Description', DIRECTLY, LEFT),
            HDim(seasonal_adjustment, 'Seasonal Adjustment', CLOSEST, LEFT),
            HDim(earning_type, 'Earnings', CLOSEST, ABOVE),
            HDim(income_type, 'Income', CLOSEST, LEFT),
            HDimConst('Account Type', 'Current Account'),
            HDimConst('Measure Type', 'bop-current-account'),
            HDimConst('Unit', 'gbp-million'),
        ]
        
        cs = ConversionSegment(tab, dimensions, observations)
        tidy_sheet = cs.topandas() 
        trace.store('combined_dataframeB4', tidy_sheet)
        df = trace.combine_and_trace(title, "combined_dataframeB4")
        
        df['Period'] = df.Period.str.replace('\.0', '')
        df['Quarter'] = df['Quarter'].str.lstrip()
        df['Period'] = df['Period'] + df['Quarter']
        df['Period'] = df['Period'].map(lambda x: 'year/' + left(x,4) if 'Q' not in x else 'quarter/' + left(x,4) + '-' + right(x,2))
        df.drop(['Quarter'], axis=1, inplace=True)
        
        if 'CDID' in df.columns:
            df.drop('CDID', axis=1, inplace=True)
        
        df['OBS'].loc[(df['OBS'] == '')] = '0'
        df['OBS'] = df['OBS'].astype(int)
        
        df.rename(columns={'OBS' : 'Value'}, inplace=True)

        df['Income Description'] = df['Income Description'].str.lstrip()
        df['Income Description'] = df['Income Description'].str.rstrip('1')
        
        df = df.replace({'Seasonal Adjustment' : {' Seasonally adjusted' : 'SA', ' Not seasonally adjusted': 'NSA', ' Sector analysis': 'sector-analysis' }})
        df = df.replace({'Earnings' : { '' : 'Net earnings', 
                                   ' (Net earnings)' : 'Net earnings',
                                   ' (Earnings of UK residents on investment abroad)' : 'Earnings of UK residents on investment abroad',
                                   ' (Foreign earnings on investment in UK)' : 'Foreign earnings on investment in the UK',
                                   ' (Foreign earnings on investment in the UK)' : 'Foreign earnings on investment in the UK'}})
    
        #tidy = df[['Period','Flow Directions', 'Income', 'Income Description', 'Earnings', 'Account Type', 'Seasonal Adjustment', 'CDID', 'Value', 'Measure Type', 'Unit']]
        tidy = df[['Period','Flow Directions', 'Income', 'Income Description', 'Earnings', 'Account Type', 'Seasonal Adjustment', 'Value']]
        
        for column in tidy:
            if column in ('Flow Directions', 'Income', 'Income Description', 'Earnings', 'Account Type'):
                tidy[column] = tidy[column].str.lstrip()
                tidy[column] = tidy[column].str.rstrip()
                tidy[column] = tidy[column].map(lambda x: pathify(x))

        cubes.add_cube(copy.deepcopy(scraper), tidy, scraper.dataset.title)

    # Tabs B5 and B5A    
    if (tab.name == 'B5') or (tab.name == 'B5A'):
        title = distribution.title + ' :Secondary income'
        #columns = ['Period','Flow Directions', 'Income', 'Income Description', 'Sector', 'Account Type', 'Seasonal Adjustment', 
        #   'CDID', 'Value', 'Marker', 'Measure Type', 'Unit']
        columns = ['Period','Flow Directions', 'Income', 'Income Description', 'Sector', 'Account Type', 'Seasonal Adjustment', 
           'Value', 'Marker', 'Measure Type', 'Unit']
        trace.start(title, tab, columns, distribution.downloadURL)
        
        scraper.dataset.title = "UK Economic Accounts: balance of payments - Current Account - Secondary Income"
        scraper.dataset.comment = "Contents of the balance of payments: Secondary Income - Quarterly transactions"
        scraper.dataset.description = scraper.dataset.comment + """
         Taxes and subsidies on products and production are now classified to other primary income within the primary income account.
         Social fund: receipts by local goverment are included up to 2005 Q4. From 2006 Q1 they are included in general government other EU receipts.
         GNI own resource and adjustments: Includes VAT-based third EU own resource and GNI-based fourth own resource.
        """
        
        flow = tab.excel_ref('B').expand(DOWN).by_index([7,24,43]) - tab.excel_ref('B51').expand(DOWN)
        sector = tab.excel_ref('B').expand(DOWN).by_index([8,14,25,34,44,45]) - tab.excel_ref('B51').expand(DOWN)
        income = tab.excel_ref('B10').expand(DOWN).is_not_blank() - tab.excel_ref('B51').expand(DOWN)
        code = tab.excel_ref('C7').expand(DOWN).is_not_blank()
        year =  tab.excel_ref('D4').expand(RIGHT).is_not_blank()
        quarter = tab.excel_ref('D5').expand(RIGHT)
        seasonal_adjustment = tab.excel_ref('B2')
        income_type = tab.excel_ref('B1')
        observations = quarter.fill(DOWN).is_not_blank()
        
        dimensions = [
            HDim(flow, 'Flow Directions', CLOSEST, ABOVE),
            HDim(sector, 'Sector', CLOSEST, ABOVE),
            HDim(income, 'Income Description', DIRECTLY, LEFT),
            HDim(code, 'CDID', DIRECTLY, LEFT),
            HDim(year, 'Period', DIRECTLY, ABOVE),
            HDim(quarter, 'Quarter', DIRECTLY, ABOVE),        
            HDim(seasonal_adjustment, 'Seasonal Adjustment', CLOSEST, LEFT),
            HDim(income_type, 'Income', CLOSEST, LEFT),
            HDimConst('Account Type', 'Current Account'),
            HDimConst('Measure Type', 'bop-current-account'),
            HDimConst('Unit', 'gbp-million'),
        ]
        
        cs = ConversionSegment(tab, dimensions, observations)
        tidy_sheet = cs.topandas() 
        trace.store('combined_dataframeB5', tidy_sheet)
        df = trace.combine_and_trace(title, "combined_dataframeB5")
        
        df['Period'] = df.Period.str.replace('\.0', '')
        df['Quarter'] = df["Quarter"].str.lstrip()
        df['Period'] = df['Period'] + df['Quarter']
        df['Period'] = df['Period'].map(lambda x: 'year/' + left(x,4) if 'Q' not in x else 'quarter/' + left(x,4) + '-' + right(x,2))
        df.drop(['Quarter'], axis=1, inplace=True)
        
        if 'CDID' in df.columns:
            df.drop('CDID', axis=1, inplace=True)
        
        df['OBS'].loc[(df['OBS'] == '')] = '0'
        df['OBS'] = df['OBS'].astype(int)
        
        df['Income Description'] = df['Income Description'].str.rstrip('2')
        df['Income Description'] = df['Income Description'].str.rstrip('3')
        df['Income Description'] = df['Income Description'].str.lstrip()
        
        df['Income'] = df['Income'].str.rstrip('1')
        df['Sector'] = df['Sector'].str.lstrip()
        
        df = df.replace({'Seasonal Adjustment' : {' Seasonally adjusted' : 'SA', ' Not Seasonally adjusted': 'NSA' }})
        
        df.rename(columns={'OBS' : 'Value', 'DATAMAKER' : 'Marker'}, inplace=True)
        
        #tidy = df[['Period','Flow Directions', 'Income', 'Income Description', 'Sector', 'Account Type', 'Seasonal Adjustment', 'CDID', 'Value', 'Measure Type', 'Unit']]
        tidy = df[['Period','Flow Directions', 'Income', 'Income Description', 'Sector', 'Account Type', 'Seasonal Adjustment', 'Value']]
        
        for column in tidy:
            if column in ('Flow Directions', 'Income', 'Income Description', 'Sector', 'Account Type'):
                tidy[column] = tidy[column].str.lstrip()
                tidy[column] = tidy[column].map(lambda x: pathify(x))

        cubes.add_cube(copy.deepcopy(scraper), tidy, scraper.dataset.title)
       
      
    if (tab.name == 'B6') or (tab.name == 'B6A'):
        title = distribution.title + ' :Transactions with the EU and EMU'
        #columns = ['Period','Flow Directions', 'Account Type', 'Transaction Type', 'Services', 'Members', 'Seasonal Adjustment', 'CDID', 'Value', 'Measure Type', 'Unit']
        columns = ['Period','Flow Directions', 'Account Type', 'Transaction Type', 'Services', 'Members', 'Seasonal Adjustment', 'Value', 'Measure Type', 'Unit']
        
        trace.start(title, tab, columns, distribution.downloadURL)
        
        scraper.dataset.title = "UK Economic Accounts: balance of payments - Current Account - Transactions with the EU and EMU"
        scraper.dataset.comment = "Contents of the balance of payments: Transactions with the EU and EMU - Quarterly transactions"
        scraper.dataset.description = scraper.dataset.comment + """
        Includes transactions with European Union institutions.
        Transactions with non-EU countries continue to be shown in tables B6B and B6C.
        EMU members : Austria, Belgium, Cyprus, Estonia, Finland, France, Germany, Greece, Irish Republic, Italy, Latvia, Lithuania, Luxembourg, Malta, Netherlands, Portugal, Slovakia, Slovenia and Spain.
        Of which EMU members: Lithuania became a member of the EMU on 1 January 2015. The table presents EMU19 figures for 2014Q1 to 2015Q1 and EMU18 figures for 1999Q1 to 2013Q4. ONS will publish EMU19 figures for the full time series within the 2015Q2 publication in September 2015.
        """
        
        emu_index = [12,14,17,19,21,25,29,31,34,36,38,42,46,48,51,53,55,59]
        flow = tab.excel_ref('B').expand(DOWN).by_index([10,27,44]) - tab.excel_ref('B60').expand(DOWN)
        emu_only = tab.excel_ref('B').expand(DOWN).by_index(emu_index) - tab.excel_ref('B60').expand(DOWN)
        services = tab.excel_ref('B11').expand(DOWN).is_not_blank() - emu_only - flow - tab.excel_ref('B60').expand(DOWN)
        emu_and_services = tab.excel_ref('B11').expand(DOWN).is_not_blank() - flow  - tab.excel_ref('B60').expand(DOWN)
        
        account_Type = tab.excel_ref('B1')
        seasonal_adjustment = tab.excel_ref('B3')
        transaction_type = tab.excel_ref('B8')
        code = tab.excel_ref('C7').expand(DOWN).is_not_blank()
        year =  tab.excel_ref('D5').expand(RIGHT).is_not_blank()
        quarter = tab.excel_ref('D6').expand(RIGHT)
        observations = quarter.fill(DOWN).is_not_blank()
        
        dimensions = [
            HDim(account_Type, 'Account Type', CLOSEST, LEFT),
            HDim(seasonal_adjustment, 'Seasonal Adjustment', CLOSEST, LEFT),
            HDim(transaction_type, 'Transaction Type', CLOSEST, LEFT),
            HDim(flow, 'Flow Directions', CLOSEST, ABOVE),
            HDim(code, 'CDID', DIRECTLY, LEFT),
            HDim(year, 'Period', DIRECTLY, ABOVE),
            HDim(quarter, 'Quarter', DIRECTLY, ABOVE),
            HDim(services, 'Services', CLOSEST, ABOVE),
            HDim(emu_and_services, 'Members', DIRECTLY, LEFT),
            HDimConst('Measure Type', 'bop-current-account'),
            HDimConst('Unit', 'gbp-million'),
        ]
        
        cs = ConversionSegment(tab, dimensions, observations)
        tidy_sheet = cs.topandas() 
        trace.store('combined_dataframeB6A', tidy_sheet)
        df = trace.combine_and_trace(title, "combined_dataframeB6A")
        
        df['Period'] = df.Period.str.replace('\.0', '')
        df['Quarter'] = df['Quarter'].map(lambda x: x.lstrip() if isinstance(x, str) else x)
        df['Period'] = df['Period'] + df['Quarter']
        df['Period'] = df['Period'].map(lambda x: 'year/' + left(x,4) if 'Q' not in x else 'quarter/' + left(x,4) + '-' + right(x,2))
        df.drop(['Quarter'], axis=1, inplace=True)
        
        if 'CDID' in df.columns:
            df.drop('CDID', axis=1, inplace=True)
        
        df['OBS'].loc[(df['OBS'] == '')] = '0'
        df['OBS'] = df['OBS'].astype(int)
        
        df['Account Type'] = df['Account Type'].map(lambda x: x.split()[0]) + ' ' +  df['Account Type'].map(lambda x: x.split()[1])
        df['Account Type'] = df['Account Type'].str.rstrip(':')
        df['Services'] = df['Services'].str.rstrip('4')
        df['Members'] = df['Members'].map(lambda x: 'of which EMU members' if '     of which EMU members4' in x else 'European Union (EU)')
        df = df.replace({'Seasonal Adjustment' : {' Seasonally adjusted' : 'SA', ' Not seasonally adjusted': 'NSA' }})
        
        df.rename(columns={'OBS' : 'Value','DATAMARKER' : 'Marker'}, inplace=True)
        df['Marker'].replace(' -', 'unknown', inplace=True)
        
        df['Flow Directions'] = df['Flow Directions'].str.strip().apply(pathify)
        df['Account Type'] = df['Account Type'].str.strip().apply(pathify)
        df['Transaction Type'] = df['Transaction Type'].str.strip().apply(pathify)
        df['Services'] = df['Services'].str.strip().apply(pathify)
        df['Members'] = df['Members'].str.strip().apply(pathify)
        
        #tidy = df[['Period','Flow Directions', 'Account Type', 'Transaction Type', 'Services', 'Members', 'Seasonal Adjustment', 'CDID', 'Value', 'Marker', 'Measure Type', 'Unit']]
        tidy = df[['Period','Flow Directions', 'Account Type', 'Transaction Type', 'Services', 'Members', 'Seasonal Adjustment', 'Value', 'Marker']]

        cubes.add_cube(copy.deepcopy(scraper), tidy, scraper.dataset.title)

        
    # # Tabs B6B_B6B2_B6B3_B6C_B6C2_B6C3
    if (tab.name == 'B6B') or (tab.name == 'B6B_2') or (tab.name == 'B6B_3') or (tab.name == 'B6C') or (tab.name == 'B6C_2') or (tab.name == 'B6C_3'):
        title = distribution.title + ' :Transactions with non-EU countries'
        #columns = ['Period','Flow Directions', 'Services', 'Account Type', 'Transaction Type', 'Country Transaction', 'Seasonal Adjustment', 
        #   'CDID', 'Value', 'Marker', 'Measure Type', 'Unit']
        columns = ['Period','Flow Directions', 'Services', 'Account Type', 'Transaction Type', 'Country Transaction', 'Seasonal Adjustment', 
           'Value', 'Marker', 'Measure Type', 'Unit']
        trace.start(title, tab, columns, distribution.downloadURL)
       
        scraper.dataset.title = "UK Economic Accounts: balance of payments - Current Account - Transactions with non-EU countries"
        scraper.dataset.comment = "Contents of the balance of payments: Transactions with non-EU countries - Quarterly transactions"
        scraper.dataset.description = scraper.dataset.comment + """
        Includes transactions with international organisations other than European Union institutions.
        """
    
        account_Type = tab.excel_ref('B1')
        seasonal_adjustment = tab.excel_ref('B3')
        transaction_type = tab.excel_ref('B8')
        flow = tab.excel_ref('B').expand(DOWN).by_index([10]) - tab.excel_ref('B72').expand(DOWN)
        services = tab.excel_ref('B').expand(DOWN).by_index([11,21,31,41,51,62]) - tab.excel_ref('B72').expand(DOWN)
        country = tab.excel_ref('B10').expand(DOWN).is_not_blank()
        code = tab.excel_ref('C7').expand(DOWN).is_not_blank()
        year =  tab.excel_ref('D5').expand(RIGHT).is_not_blank()
        quarter = tab.excel_ref('D6').expand(RIGHT)
        
        if (tab.name == 'B6B_2') or (tab.name == 'B6B_3') or (tab.name == 'B6C_2') or (tab.name == 'B6C_3'):
            transaction_type = tab.excel_ref('B9')
            flow = tab.excel_ref('B').expand(DOWN).by_index([11]) - tab.excel_ref('B72').expand(DOWN)
            services = tab.excel_ref('B').expand(DOWN).by_index([12,22,32,42,52,63]) - tab.excel_ref('B73').expand(DOWN)
            year =  tab.excel_ref('D6').expand(RIGHT).is_not_blank()
            quarter = tab.excel_ref('D7').expand(RIGHT)
        if (tab.name == 'B6B_3') or (tab.name == 'B6C_2') or (tab.name == 'B6C_3'):
            services = tab.excel_ref('B').expand(DOWN).by_index([12,22,32,42,52,63]) - tab.excel_ref('B73').expand(DOWN)
        
        observations = quarter.fill(DOWN).is_not_blank()   
        
        dimensions = [
            HDim(account_Type, 'Account Type', CLOSEST, LEFT),
            HDim(seasonal_adjustment, 'Seasonal Adjustment', CLOSEST, LEFT),
            HDim(transaction_type, 'Transaction Type', CLOSEST, LEFT),
            HDim(flow, 'Flow Directions', CLOSEST, ABOVE),
            HDim(services, 'Services', CLOSEST, ABOVE),
            HDim(country, 'Country Transaction', DIRECTLY, LEFT),
            HDim(code, 'CDID', DIRECTLY, LEFT),
            HDim(year, 'Period', DIRECTLY, ABOVE),
            HDim(quarter, 'Quarter', DIRECTLY, ABOVE),
            HDimConst('Measure Type', 'bop-current-account'),
            HDimConst('Unit', 'gbp-million'),
        ]
        
        cs = ConversionSegment(tab, dimensions, observations)
        tidy_sheet = cs.topandas() 
        trace.store('combined_dataframeB6B', tidy_sheet)
        df = trace.combine_and_trace(title, 'combined_dataframeB6B')
        
        df['Period'] = df.Period.str.replace('\.0', '')
        df['Quarter'] = df['Quarter'].map(lambda x: x.lstrip() if isinstance(x, str) else x)
        df['Period'] = df['Period'] + df['Quarter']
        df['Period'] = df['Period'].map(lambda x: 'year/' + left(x,4) if 'Q' not in x else 'quarter/' + left(x,4) + '-' +                                 right(x,2))
        df.drop(['Quarter'], axis=1, inplace=True)
        
        if 'CDID' in df.columns:
            df.drop('CDID', axis=1, inplace=True)
        
        df['OBS'].loc[(df['OBS'] == '')] = '0'
        df['OBS'] = df['OBS'].astype(int)
        
        df['Account Type'] = df['Account Type'].map(lambda x: x.split()[0]) + ' ' +  df['Account Type'].map(lambda x: x.split()[1])
        df['Account Type'] = df['Account Type'].str.rstrip(':')
        df['Transaction Type'] = df['Transaction Type'].str.rstrip('1')
        df['Country Transaction'] = df['Country Transaction'].str.lstrip()
        df = df.replace({'Seasonal Adjustment' : {' Seasonally adjusted' : 'SA', ' Not seasonally adjusted': 'NSA' }})
        
        df.rename(columns={'OBS' : 'Value','DATAMARKER' : 'Marker'}, inplace=True)
        
        #tidy = df[['Period','Flow Directions', 'Services', 'Account Type', 'Transaction Type', 'Country Transaction', 'Seasonal Adjustment', 'CDID', 'Value', 'Measure Type', 'Unit']]
        tidy = df[['Period','Flow Directions', 'Services', 'Account Type', 'Transaction Type', 'Country Transaction', 'Seasonal Adjustment', 'Value']]
        
        for column in tidy:
            if column in ('Flow Directions', 'Services', 'Account Type', 'Transaction Type', 'Country Transaction'):
                tidy[column] = tidy[column].str.lstrip()
                tidy[column] = tidy[column].map(lambda x: pathify(x))
        cubes.add_cube(copy.deepcopy(scraper), tidy, scraper.dataset.title)

    
    # # Tabs B7_B7A
    if 'B7' in tab.name: 
        title = distribution.title + ' :Capital Account'
        #columns = ['Period','Flow Directions','Services','Sector','Seasonal Adjustment', 'CDID', 'Account Type', 'Value', 
        #   'Marker','Measure Type', 'Unit']
        columns = ['Period','Flow Directions','Services','Sector','Seasonal Adjustment', 'Account Type', 'Value', 
           'Marker','Measure Type', 'Unit']
        trace.start(title, tab, columns, distribution.downloadURL)
        
        scraper.dataset.title = "UK Economic Accounts: balance of payments - Capital Account"
        scraper.dataset.comment = "Contents of the balance of payments: Capital Account"
        scraper.dataset.description = scraper.dataset.comment + """
        Under the Balance of Payments Manual edition 6 there is no longer a record of migrant transfers within the Capital Account.
        Total debt forgiveness: this series also appears in the Financial Account (see Table B12 in spreadsheet publication)
        """
        
        sector_index = [9,14,16,22,32,37,46,54,59,64]
        flow = tab.excel_ref('B').expand(DOWN).by_index([7,30,52]) - tab.excel_ref('B70').expand(DOWN)
        sector_only = tab.excel_ref('B').expand(DOWN).by_index(sector_index) - tab.excel_ref('B70').expand(DOWN)
        services = tab.excel_ref('B8').expand(DOWN).is_not_blank() - sector_only - flow - tab.excel_ref('B70').expand(DOWN)
        code = tab.excel_ref('C7').expand(DOWN).is_not_blank()
        year =  tab.excel_ref('D4').expand(RIGHT).is_not_blank()
        quarter = tab.excel_ref('D5').expand(RIGHT)
        seasonal_adjustment = tab.excel_ref('B2')
        account_Type = tab.excel_ref('B1')
        observations = quarter.fill(DOWN).is_not_blank()
        
        dimensions = [
            HDim(account_Type, 'Account Type', CLOSEST, LEFT),
            HDim(seasonal_adjustment, 'Seasonal Adjustment', CLOSEST, LEFT),
            HDim(flow, 'Flow Directions', CLOSEST, ABOVE),
            HDim(services, 'Services', DIRECTLY, LEFT),
            HDim(sector_only, 'Sector', CLOSEST, ABOVE),
            HDim(code, 'CDID', DIRECTLY, LEFT),
            HDim(year, 'Period', DIRECTLY, ABOVE),
            HDim(quarter, 'Quarter', DIRECTLY, ABOVE),
            HDimConst('Measure Type', 'bop-capital-account'),
            HDimConst('Unit', 'gbp-million'),
        ]
        cs = ConversionSegment(tab, dimensions, observations)
        tidy_sheet = cs.topandas() 
        trace.store('combined_dataframeB7', tidy_sheet)
        df = trace.combine_and_trace(title, 'combined_dataframeB7')
        
        df['Period'] = df.Period.str.replace('\.0', '')
        df['Quarter'] = df["Quarter"].map(lambda x: x.lstrip() if isinstance(x, str) else x)
        df['Period'] = df['Period'] + df['Quarter']
        df['Period'] = df['Period'].map(lambda x: 'year/' + left(x,4) if 'Q' not in x else 'quarter/' + left(x,4) + '-' + right(x,2))
        df.drop(['Quarter'], axis=1, inplace=True)
        
        if 'CDID' in df.columns:
            df.drop('CDID', axis=1, inplace=True)

        df['OBS'].loc[(df['OBS'] == '')] = '0'
        df['OBS'] = df['OBS'].astype(int)
            
        df['Account Type'] = df['Account Type'].map(lambda x: x.split()[0]) + ' ' +  df['Account Type'].map(lambda x: x.split()[1])
        df['Account Type'] = df['Account Type'].str.rstrip('1')
        df['Services'] = df['Services'].str.rstrip('2')
        df['Services'] = df['Services'].str.lstrip()
        df = df.replace({'Sector' : {' ' : 'total'}})
        
        df.rename(columns={'OBS' : 'Value', 'DATAMARKER' : 'Marker'}, inplace=True)
        df['Marker'].replace(' -', 'unknown', inplace=True)
        
        df = df.replace({'Seasonal Adjustment' : {' Seasonally adjusted' : 'SA', ' Not seasonally adjusted': 'NSA' }})
        #tidy = df[['Period','Flow Directions','Services','Sector','Seasonal Adjustment', 'CDID', 'Account Type', 'Value', 
        #   'Marker','Measure Type', 'Unit']]
        tidy = df[['Period','Flow Directions','Services','Sector','Seasonal Adjustment', 'Account Type', 'Value', 'Marker']]
        for column in tidy:
            if column in ('Flow Directions', 'Services', 'Account Type', 'Sector'):
                tidy[column] = tidy[column].str.lstrip()
                tidy[column] = tidy[column].map(lambda x: pathify(x))

        with open("info.json", "r") as jsonFile:
            data = json.load(jsonFile)
        data["transform"]["columns"]["Value"]["measure"] = "http://gss-data.org.uk/def/measure/bop-capital-account"
        with open("info.json", "w") as jsonFile:
            json.dump(data, jsonFile)
    
        cubes.add_cube(copy.deepcopy(scraper), tidy, scraper.dataset.title)
# -

for cube in cubes.cubes:
    print(cube.scraper.title)

cubes.output_all()

trace.render("spec_v1.html")

# +
#scraper.dataset.description
# -




