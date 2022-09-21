#!/usr/bin/env python
# coding: utf-8
# %%
from gssutils import *
import json
import numpy as np

# %% 
# TODO i've put net-transactions as default for measure type column since table A was. find out what the others should be. in original the DE put the BoP topics (e..g current account, financial account) as measure type
# TODO should understand this code - "catalog_metadata = metadata.as_csvqb_catalog_metadata()"" - probably no need to keep repeating for each cube
# %%
# variables
info_json_file = 'info.json' # name of info json file
metadata = Scraper(seed = info_json_file) # get first landing page details
metadata # display(metadata) #  to see exactly the data we are loading
# %%
# Reusable Functions
class is_one_of(object):
    def __init__(self, allowed):
        self.allowed = allowed
    def __call__(self, xy_cell):
        if xy_cell.value.strip() in self.allowed:
            return True
        return False   

#Format Date/Quarter
def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

def date_time(date: str) -> str:
    '''
    function to format numeric date to descriptive
    e.g. '2022' becomes 'year/2022'
    '''
    if len(date)  == 4:
        return 'year/' + date
    elif len(date) == 6:
        return 'quarter/' + left(date,4) + '-' + right(date,2)
    else:
        return "Date Formatting Error Unknown"


# %%
distribution = metadata.distribution(latest = True)
# convert source data to databaker object
tabs = distribution.as_databaker()
# keep tabs we're interested in. Ignoring files like: 'Index', 'Records','Table R1', 'Table R2','Table R3','Annex A', 'Annex B', ''
tabs = [x for x in tabs if x.name in ('Table_A','Table_B','Table_BX','Table_C','Table_D1_3','Table_D4_6','Table_D7_9','Table_E', 'Table_F','Table_G', 'Table_H','Table_I','Table_J', 'Table_K') ]
# create dictionary with tab name as key and tab/cell bag as item
tabs = {tab.name: tab for tab in tabs}
datasetTitle = distribution.title

# %%
# identifying tabs for for loop. Naming them so i know which tab the for loop is working on.
summary_of_balance_of_payments = "Table_A"
current_account ="Table_B"
current_account_excluding_precious_metals = "Table_BX"
current_account_transaction_with_the_eu_and_non_eu_countries = "Table_C"
summary_of_IIP_financial_account_investment_income_d1 = "Table_D1_3" 
summary_of_IIP_financial_account_investment_income_d4 = "Table_D4_6"
summary_of_IIP_financial_account_investment_income_d7 = "Table_D7_9"
goods = "Table_E"
services = "Table_F"
primary_income = "Table_G"
secondary_income = "Table_H"
capital_account = "Table_I"
financial_account = "Table_J"
international_investment_position = "Table_K"

# +
#for name,tab in tabs.items():
#    print(name)



# %%


tidied_sheets = [] # reset this for each cube

# [summary_of_balance_of_payments]
for name,tab in tabs.items():
    if name == summary_of_balance_of_payments: # should be Table_A
        # my thinking is separate out the differnt tables on each tab by identifying the last one, then the second one but remove the last, then the first one and remove the last two.

        bop_tab = 'Summary of Balance of Payments'
        currency = 'gbp-million'

        #table locators
        title_of_table_1 = tab.filter("Table A.1, Current Account, seasonally adjusted (£ million)")
        title_of_table_2 = tab.filter("Table A.2, Current Account, not seasonally adjusted (£ million)")
        title_of_table_3 = tab.filter("Table A.3, Financial Account [note 1], not seasonally adjusted (£ million)")


        # separate bags of tables to remove later
        tb3_bag = title_of_table_3.expand(DOWN).expand(RIGHT)
        tb2_tb3_bag = title_of_table_2.expand(DOWN).expand(RIGHT)

        
        # [Table 1 Current accounts]
        tb1_table_name = 'Current Account'
        tb1_seasonal_adjustment = 'SA'

        #table_A_1_all = title_of_table_1.expand(DOWN).expand(RIGHT).is_not_blank().is_not_whitespace() - table_A_3_all - table_A_2_all
        table_A_1_period = title_of_table_1.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() - tb2_tb3_bag
        table_A_1_BOP_service = title_of_table_1.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb2_tb3_bag
        table_A_1_CDID = title_of_table_1.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb2_tb3_bag

        tb1_obs = table_A_1_CDID.waffle(table_A_1_period) 



        # [Table 2 Current accounts]
        tb2_table_name = 'Current Account'
        tb2_seasonal_adjustment = 'NSA'

        #table_A_2_all = title_of_table_2.expand(DOWN).expand(RIGHT).is_not_blank().is_not_whitespace() - table_A_3_all
        table_A_2_period = title_of_table_2.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() - tb3_bag
        table_A_2_BOP_service = title_of_table_2.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb3_bag
        table_A_2_CDID = title_of_table_2.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb3_bag

        tb2_obs = table_A_2_CDID.waffle(table_A_2_period)



        # [Table 3 Financial accounts]
        tb3_table_name = 'Financial Accounts Summary'
        tb3_seasonal_adjustment = 'SA'

        #table_A_3_all = title_of_table_3.expand(DOWN).expand(RIGHT).is_not_blank().is_not_whitespace() # so i can remove it later
        table_A_3_period = title_of_table_3.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace()
        table_A_3_BOP_service = title_of_table_3.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace()
        table_A_3_CDID = title_of_table_3.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace()

        tb3_obs = table_A_3_CDID.waffle(table_A_3_period)



        # [Table 1]
        tb1_dimensions = [
            HDimConst('Table Name', tb1_table_name),
            HDimConst('Seasonal Adjustment', tb1_seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_A_1_period, "Period", DIRECTLY, LEFT),
            HDim(table_A_1_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_A_1_CDID,'CDID',DIRECTLY,UP),
        ]

        # [Table 2]
        tb2_dimensions = [
            HDimConst('Table Name', tb2_table_name),
            HDimConst('Seasonal Adjustment', tb2_seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_A_2_period, "Period", DIRECTLY, LEFT),
            HDim(table_A_2_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_A_2_CDID,'CDID',DIRECTLY,UP),
        ]

        # [Table 3]
        tb3_dimensions = [
            HDimConst('Table Name', tb3_table_name),
            HDimConst('Seasonal Adjustment', tb3_seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_A_3_period, "Period", DIRECTLY, LEFT),
            HDim(table_A_3_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_A_3_CDID,'CDID',DIRECTLY,UP),
        ]
        
        tb1_cs = ConversionSegment(tab, tb1_dimensions, tb1_obs)
        tb2_cs = ConversionSegment(tab, tb2_dimensions, tb2_obs)
        tb3_cs = ConversionSegment(tab, tb3_dimensions, tb3_obs)
        
        tb1_tidy_sheet = tb1_cs.topandas()
        tb2_tidy_sheet = tb2_cs.topandas()
        tb3_tidy_sheet = tb3_cs.topandas()

        # create preview files of each tabs data
        #savepreviewhtml(tb1_cs, fname= name + "PREVIEW.html")

        # append all tables together
        tidied_sheets.append(tb1_tidy_sheet)
        tidied_sheets.append(tb2_tidy_sheet)
        tidied_sheets.append(tb3_tidy_sheet)

    else:
        continue


# %%
# convert the separate tables into one dataframe
df = pd.concat(tidied_sheets, sort = True, ignore_index=True).fillna('')

## [Postrocessing]

# %%
# change period values to ONS standard
df['Period'] = df['Period'].map(lambda x: 'year/' + left(x,4) if 'Q' not in x else 'quarter/' + left(x,4) + '-' + right(x,2))


# convert blank observations to zeros and convert to int type
#df['OBS'].loc[(df['OBS'] == '')] = '0'
df['OBS'] = df['OBS'].astype(int)
df['Measure Type'] = 'net-transactions'
df['CDID'] = df['CDID'].str.strip()
# df = df.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=["",""], regex=True)
df['BOP Service'] = df['BOP Service'].str.strip()
df["BOP Service"] = df["BOP Service"].replace(r'\n',' ', regex=True) 
df["BOP Service"] = df["BOP Service"].replace(',',' ', regex=True)
# the BOP services showing subtotal values include a lot of spaces between words so replacing them with just one. warning, it also removes all whitespace characters (space, tab, newline, return, formfeed)
df["BOP Service"] = df["BOP Service"].apply(lambda x: " ".join(x.split()))
# because we're linking with the local codelists in the codelist directory we have to pathify these columns
df['BOP Service'] = df['BOP Service'].apply(pathify)
df['Table Name'] = df['Table Name'].apply(pathify)
# %%
#df = df.replace({'BOP Service' : {',' : ' , ' }})


#rename columns
df.rename(columns={'OBS' : 'Value', 'Table Name' : 'Account Type', 'Currency' : 'Unit'}, inplace=True)
df

# %%
df = df.replace({'Seasonal Adjustment' : {' Seasonally adjusted' : 'SA', ' Not seasonally adjusted' : 'NSA' }})

# TODO this is temporary until me, SB and RB agree what to put. Copied value from https://github.com/GSS-Cogs/family-trade/blob/master/reference/measures.csv
df['Measure Type'] = "summary-of-balance-of-payments"

#%% 
#reorder columns
df = df[['Period','CDID','Seasonal Adjustment','Account Type','BOP Service','Value','Unit','Measure Type']]

# %%
# Update all the metadata for each cube 
# mainTitle = metadata.dataset.title # orig title didn't have capital letters for the first letter of each word
mainTitle = 'Balance of Payments'
maincomment = "Balance of Payments: Quarterly summary of balance of payments accounts including the current account, capital transfers, transactions, and levels of UK external assets and liabilities.\n"
maindescr = "Balance of Payments:\n\nQuarterly summary of balance of payments accounts including the current account, capital transfers, transactions, and levels of UK external assets and liabilities.\n"
# %%
# +
metadata.dataset.title = mainTitle + ' - Summary of Balance of Payments'
metadata.dataset.comment = maincomment + r"""
This dataset: Summary of Balance of Payments (£ million)
"""
metadata.dataset.description = maindescr + r"""
Summary of Balance of Payments:

This series represents net errors and omissions in the balance of payments accounts. It is the converse of the current and capital balances (HBOG and FKMJ) and net financial account transactions (HBNT) and is required to balance these three accounts, not seasonally adjusted.

The quarters in the table refer to: Q1 = Jan to Mar, Q2 = Apr to June, Q3 = July to Sept, Q4 = Oct to Dec.

These tables refer to CDID's which stands for Central Database Identifier, the codes used to identify specific datasets.

As previously announced by HMRC, changes to the way EU imports data have been recorded collected from January 2022 onwards may have led to a discontinuity in trade figures and the Current Account. We advise caution when interpreting 2022 compared with other periods as the impacts of these changes are still being investigated. In addition, changes to the sample framework for foreign direct investment (FDI) statistics means there is a higher degree of uncertainty than usual with inward FDI data. As such, users should be cautious when interpreting Q1 2022 balance of payments statistics. 
"""
# -
# %%
df.to_csv('summary_of_balance_of_payments-observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('summary_of_balance_of_payments-catalog-metadata.json')

# %%
tidied_sheets = [] 

# [current account, seasonally adjusted]
for name,tab in tabs.items():
    if name == current_account: # should be Table_B

        bop_tab = 'Current Acount'
        seasonal_adjustment = 'SA'
        currency = 'gbp-million'

        #table locators
        title_of_table_1 = tab.filter("Table B.1, Current Account Credits (£ million)")
        title_of_table_2 = tab.filter("Table B.2, Current Account Debits (£ million)")
        title_of_table_3 = tab.filter("Table B.3, Current Account Balances (£ million)")
        title_of_table_4 = tab.filter("Table B.4, Current Account Balances as a percentage of GDP (percentage) [note 1]")


        # separate bags of tables to remove later on
        tb4_bag = title_of_table_4.expand(DOWN).expand(RIGHT)
        tb3_tb4_bag = title_of_table_3.expand(DOWN).expand(RIGHT)
        tb2_tb3_tb4_bag = title_of_table_2.expand(DOWN).expand(RIGHT)



        # [Table 1 - Credits]
        tb1_table_name = 'Credits'

        table_1_period = title_of_table_1.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() - tb2_tb3_tb4_bag
        table_1_BOP_service = title_of_table_1.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb2_tb3_tb4_bag
        table_1_CDID = title_of_table_1.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb2_tb3_tb4_bag

        tb1_obs = table_1_CDID.waffle(table_1_period) 



        # [Table 2 Current accounts]
        tb2_table_name = 'Debits'

        #table_A_2_all = title_of_table_2.expand(DOWN).expand(RIGHT).is_not_blank().is_not_whitespace() - table_A_3_all
        table_2_period = title_of_table_2.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() - tb3_tb4_bag
        table_2_BOP_service = title_of_table_2.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb3_tb4_bag
        table_2_CDID = title_of_table_2.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb3_tb4_bag

        tb2_obs = table_2_CDID.waffle(table_2_period)



        # [Table 3 Financial accounts]
        tb3_table_name = 'Balances'

        #table_A_3_all = title_of_table_3.expand(DOWN).expand(RIGHT).is_not_blank().is_not_whitespace() # so i can remove it later
        table_3_period = title_of_table_3.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() - tb4_bag
        table_3_BOP_service = title_of_table_3.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb4_bag
        table_3_CDID = title_of_table_3.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb4_bag

        tb3_obs = table_3_CDID.waffle(table_3_period)



        # [Table 4 Financial accounts]
        tb4_table_name = 'Balances as %'

        #table_A_3_all = title_of_table_3.expand(DOWN).expand(RIGHT).is_not_blank().is_not_whitespace() # so i can remove it later
        table_4_period = title_of_table_4.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace()
        table_4_BOP_service = title_of_table_4.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace()
        table_4_CDID = title_of_table_4.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace()

        tb4_obs = table_4_CDID.waffle(table_4_period)




        # [Table 1]
        tb1_dimensions = [
            HDimConst('Table Name', tb1_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_1_period, "Period", DIRECTLY, LEFT),
            HDim(table_1_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_1_CDID,'CDID',DIRECTLY,UP),
        ]

        # [Table 2]
        tb2_dimensions = [
            HDimConst('Table Name', tb2_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_2_period, "Period", DIRECTLY, LEFT),
            HDim(table_2_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_2_CDID,'CDID',DIRECTLY,UP),
        ]

        # [Table 3]
        tb3_dimensions = [
            HDimConst('Table Name', tb3_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_3_period, "Period", DIRECTLY, LEFT),
            HDim(table_3_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_3_CDID,'CDID',DIRECTLY,UP),
        ]

            # [Table 4]
        tb4_dimensions = [
            HDimConst('Table Name', tb4_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_4_period, "Period", DIRECTLY, LEFT),
            HDim(table_4_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_4_CDID,'CDID',DIRECTLY,UP),
        ]
        
        tb1_cs = ConversionSegment(tab, tb1_dimensions, tb1_obs)
        tb2_cs = ConversionSegment(tab, tb2_dimensions, tb2_obs)
        tb3_cs = ConversionSegment(tab, tb3_dimensions, tb3_obs)
        tb4_cs = ConversionSegment(tab, tb4_dimensions, tb4_obs)
        
        tb1_tidy_sheet = tb1_cs.topandas()
        tb2_tidy_sheet = tb2_cs.topandas()
        tb3_tidy_sheet = tb3_cs.topandas()
        tb4_tidy_sheet = tb4_cs.topandas()

        ## create preview files of one table
        #savepreviewhtml(tb1_cs, fname= name + "PREVIEW.html")

        # append all tables together
        tidied_sheets.append(tb1_tidy_sheet)
        tidied_sheets.append(tb2_tidy_sheet)
        tidied_sheets.append(tb3_tidy_sheet)
        tidied_sheets.append(tb4_tidy_sheet)

    else:
        continue


# convert the separate tables into one dataframe
df = pd.concat(tidied_sheets, sort = True, ignore_index=True).fillna('')

## [Postrocessing]

#%%
# change period values to ONS standard
df['Period'] = df['Period'].map(lambda x: 'year/' + left(x,4) if 'Q' not in x else 'quarter/' + left(x,4) + '-' + right(x,2))

# convert blank observations to zeros and convert to int type
#df['OBS'].loc[(df['OBS'] == '')] = '0'
df['OBS'] = df['OBS'].astype(int)
# df['Measure Type'] = 'net-transactions'
df['CDID'] = df['CDID'].str.strip()
df['BOP Service'] = df['BOP Service'].str.strip() # whitespace in total credit
#df = df.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=["",""], regex=True)
df["BOP Service"] = df["BOP Service"].replace(r'\n',' ', regex=True) 
df["BOP Service"] = df["BOP Service"].replace(',',' ', regex=True)
# the BOP services showing subtotal values includea lot of spaces between words so replacing them with just one. warning, it also removes all whitespace characters (space, tab, newline, return, formfeed)
df["BOP Service"] = df["BOP Service"].apply(lambda x: " ".join(x.split()))
# conflicting value in Trade total and Trade Total when making a codelist
df["BOP Service"] = df["BOP Service"].replace('Trade total','Trade Total', regex=True)
# because we're linking with the local codelists in the codelist directory we have to pathify these columns
df['BOP Service'] = df['BOP Service'].apply(pathify)
df['Table Name'] = df['Table Name'].apply(pathify)

#rename columns
df.rename(columns={'OBS' : 'Value', 'Table Name' : 'Account Type', 'Currency' : 'Unit'}, inplace=True)
df


# TODO this is temporary until me, SB and RB agree what to put. Copied value from https://github.com/GSS-Cogs/family-trade/blob/master/reference/measures.csv
df['Measure Type'] = "current-account"

#%% 
#reorder columns
df = df[['Period','CDID','Seasonal Adjustment','Account Type','BOP Service','Value','Unit','Measure Type']]

#%%
metadata.dataset.title = mainTitle + ' - Current Account'
metadata.dataset.comment = maincomment + r"""
This dataset: Current Account, seasonally adjusted (£ million and %)
"""
metadata.dataset.description = maindescr + r"""
Current Account:

Using series YBHA, GDP at current market prices.

The quarters in the table refer to: Q1 = Jan to Mar, Q2 = Apr to June, Q3 = July to Sept, Q4 = Oct to Dec.

These tables refer to CDID's which stands for Central Database Identifier, the codes used to identify specific datasets.

As previously announced by HMRC, changes to the way EU imports data have been recorded collected from January 2022 onwards may have led to a discontinuity in trade figures and the Current Account. We advise caution when interpreting 2022 compared with other periods as the impacts of these changes are still being investigated. In addition, changes to the sample framework for foreign direct investment (FDI) statistics means there is a higher degree of uncertainty than usual with inward FDI data. As such, users should be cautious when interpreting Q1 2022 balance of payments statistics. 
"""

#%%
df.to_csv('current_account-observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata() 
catalog_metadata.to_json_file('current_account-catalog-metadata.json')

#%%  

# +
tidied_sheets = [] # think i want to reset this each time

# [current account, excluding precious metals]
for name,tab in tabs.items():
    if name == current_account_excluding_precious_metals: # should be Table_BX       

        #print(name)

        bop_tab = 'Current Acount Exc Precious Metals'
        seasonal_adjustment = 'SA'
        currency = 'gbp-million'

        #table locators
        title_of_table_1 = tab.filter("Table BX.1, Current Account Credits, excluding precious metals (£ million)")
        title_of_table_2 = tab.filter("Table BX.2, Current Account Debits, excluding precious metals (£ million)")
        title_of_table_3 = tab.filter("Table BX.3, Current Account Balances, excluding precious metals (£ million)")
        title_of_table_4 = tab.filter("Table BX.4, Current Account Balances as a percentage of GDP, excluding precious metals (percentage) [note 2]")


        # separate bags of tables to remove later on
        tb4_bag = title_of_table_4.expand(DOWN).expand(RIGHT)
        tb3_tb4_bag = title_of_table_3.expand(DOWN).expand(RIGHT)
        tb2_tb3_tb4_bag = title_of_table_2.expand(DOWN).expand(RIGHT)


        # [Table 1 - Credits]
        tb1_table_name = 'Credits'

        table_1_period = title_of_table_1.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() - tb2_tb3_tb4_bag
        table_1_BOP_service = title_of_table_1.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb2_tb3_tb4_bag
        table_1_CDID = title_of_table_1.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb2_tb3_tb4_bag

        tb1_obs = table_1_CDID.waffle(table_1_period) 



        # [Table 2 Current accounts]
        tb2_table_name = 'Debits'

        #table_A_2_all = title_of_table_2.expand(DOWN).expand(RIGHT).is_not_blank().is_not_whitespace() - table_A_3_all
        table_2_period = title_of_table_2.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() - tb3_tb4_bag
        table_2_BOP_service = title_of_table_2.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb3_tb4_bag
        table_2_CDID = title_of_table_2.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb3_tb4_bag

        tb2_obs = table_2_CDID.waffle(table_2_period)



        # [Table 3 Financial accounts]
        tb3_table_name = 'Balances'

        #table_A_3_all = title_of_table_3.expand(DOWN).expand(RIGHT).is_not_blank().is_not_whitespace() # so i can remove it later
        table_3_period = title_of_table_3.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() - tb4_bag
        table_3_BOP_service = title_of_table_3.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb4_bag
        table_3_CDID = title_of_table_3.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb4_bag

        tb3_obs = table_3_CDID.waffle(table_3_period)



        # [Table 4 Financial accounts]
        tb4_table_name = 'Balances as %'

        #table_A_3_all = title_of_table_3.expand(DOWN).expand(RIGHT).is_not_blank().is_not_whitespace() # so i can remove it later
        table_4_period = title_of_table_4.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace()
        table_4_BOP_service = title_of_table_4.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace()
        table_4_CDID = title_of_table_4.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace()

        tb4_obs = table_4_CDID.waffle(table_4_period)



        # [Table 1]
        tb1_dimensions = [
            HDimConst('Table Name', tb1_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_1_period, "Period", DIRECTLY, LEFT),
            HDim(table_1_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_1_CDID,'CDID',DIRECTLY,UP),
        ]

        # [Table 2]
        tb2_dimensions = [
            HDimConst('Table Name', tb2_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_2_period, "Period", DIRECTLY, LEFT),
            HDim(table_2_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_2_CDID,'CDID',DIRECTLY,UP),
        ]

        # [Table 3]
        tb3_dimensions = [
            HDimConst('Table Name', tb3_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_3_period, "Period", DIRECTLY, LEFT),
            HDim(table_3_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_3_CDID,'CDID',DIRECTLY,UP),
        ]

            # [Table 4]
        tb4_dimensions = [
            HDimConst('Table Name', tb4_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_4_period, "Period", DIRECTLY, LEFT),
            HDim(table_4_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_4_CDID,'CDID',DIRECTLY,UP),
        ]
        
        tb1_cs = ConversionSegment(tab, tb1_dimensions, tb1_obs)
        tb2_cs = ConversionSegment(tab, tb2_dimensions, tb2_obs)
        tb3_cs = ConversionSegment(tab, tb3_dimensions, tb3_obs)
        tb4_cs = ConversionSegment(tab, tb4_dimensions, tb4_obs)
        
        tb1_tidy_sheet = tb1_cs.topandas()
        tb2_tidy_sheet = tb2_cs.topandas()
        tb3_tidy_sheet = tb3_cs.topandas()
        tb4_tidy_sheet = tb4_cs.topandas()

        ## create preview files of one table
        #savepreviewhtml(tb1_cs, fname= name + "PREVIEW.html")

        # append all tables together
        tidied_sheets.append(tb1_tidy_sheet)
        tidied_sheets.append(tb2_tidy_sheet)
        tidied_sheets.append(tb3_tidy_sheet)
        tidied_sheets.append(tb4_tidy_sheet)

    else:
        continue


# convert the separate tables into one dataframe
df = pd.concat(tidied_sheets, sort = True, ignore_index=True).fillna('')

## [Postrocessing]

# change period values to ONS standard
df['Period'] = df['Period'].map(lambda x: 'year/' + left(x,4) if 'Q' not in x else 'quarter/' + left(x,4) + '-' + right(x,2))

# convert blank observations to zeros and convert to int type
#df['OBS'].loc[(df['OBS'] == '')] = '0'
df['OBS'] = df['OBS'].astype(int)
df['Measure Type'] = 'net-transactions'
df['CDID'] = df['CDID'].str.strip()
df['BOP Service'] = df['BOP Service'].str.strip() # whitespace in total credit
#df = df.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=["",""], regex=True)
df["BOP Service"] = df["BOP Service"].replace(r'\n',' ', regex=True) 
df["BOP Service"] = df["BOP Service"].replace(',',' ', regex=True)
# the BOP services showing subtotal values includea lot of spaces between words so replacing them with just one. warning, it also removes all whitespace characters (space, tab, newline, return, formfeed)
df["BOP Service"] = df["BOP Service"].apply(lambda x: " ".join(x.split()))
# conflicting value in Trade total and Trade Total when making a codelist
df["BOP Service"] = df["BOP Service"].replace('Trade total','Trade Total', regex=True)
# because we're linking with the local codelists in the codelist directory we have to pathify these columns
df['BOP Service'] = df['BOP Service'].apply(pathify)
df['Table Name'] = df['Table Name'].apply(pathify)


#rename columns
df.rename(columns={'OBS' : 'Value', 'Table Name' : 'Account Type', 'Currency' : 'Unit'}, inplace=True)
df


# TODO this is temporary until me, SB and RB agree what to put. Copied value from https://github.com/GSS-Cogs/family-trade/blob/master/reference/measures.csv
df['Measure Type'] = "current-account-excluding-precious-metals"


#reorder columns
df = df[['Period','CDID','Seasonal Adjustment','Account Type','BOP Service','Value','Unit','Measure Type']]
#%% 

metadata.dataset.title = mainTitle + ' - Current Acount Excluding Precious Metals'
metadata.dataset.comment = maincomment + r"""
This dataset: Current Acount Excluding Precious Metals, seasonally adjusted (£ million and %)
"""
metadata.dataset.description = maindescr + r"""
Current Account:

Precious metals includes: Non:Monetary Gold (NMG), Platinum, Palladium and Silver.

Using series YBHA, GDP at current market prices.

The quarters in the table refer to: Q1 = Jan to Mar, Q2 = Apr to June, Q3 = July to Sept, Q4 = Oct to Dec.

These tables refer to CDID's which stands for Central Database Identifier, the codes used to identify specific datasets.

As previously announced by HMRC, changes to the way EU imports data have been recorded collected from January 2022 onwards may have led to a discontinuity in trade figures and the Current Account. We advise caution when interpreting 2022 compared with other periods as the impacts of these changes are still being investigated. In addition, changes to the sample framework for foreign direct investment (FDI) statistics means there is a higher degree of uncertainty than usual with inward FDI data. As such, users should be cautious when interpreting Q1 2022 balance of payments statistics. 
"""

df.to_csv('current_account_exc_precious_metals-observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata() 
catalog_metadata.to_json_file('current_account_exc_precious_metals-catalog-metadata.json')


# %%
tidied_sheets = [] # think i want to reset this each time

# [current account, transactions with EU and non EU countries]
for name,tab in tabs.items():
    if name == current_account_transaction_with_the_eu_and_non_eu_countries: # should be Table_C 

        bop_tab = 'Current Acount Trans with EU and Non-EU'
        seasonal_adjustment = 'SA'
        currency = 'gbp-million'

        #table locators
        title_of_table_1 = tab.filter("Table C.1, Transactions with the European Union, Credits [note 1] [note 2] [note 3] [note 4] [note 5] (£ million)")
        title_of_table_2 = tab.filter("Table C.2, Transactions with the European Union, Debits [note 1] [note 2] [note 3] [note 4] [note 5] (£ million)")
        title_of_table_3 = tab.filter("Table C.3, Transactions with the European Union, Balances [note 1] [note 2] [note 3] [note 4] [note 5] (£ million)")
        title_of_table_4 = tab.filter("Table C.4, Transactions with non-EU countries, Credits [note 4] [note 5] [note 6] [note 7] (£ million)")
        title_of_table_5 = tab.filter("Table C.5, Transactions with non-EU countries, Debits [note 4] [note 5] [note 6] [note 7] (£ million)")
        title_of_table_6 = tab.filter("Table C.6, Transactions with non-EU countries, Balances [note 4] [note 5] [note 6] [note 7] (£ million)")



        # separate bags of tables to remove later on
        tb6_bag = title_of_table_6.expand(DOWN).expand(RIGHT)
        tb6_tb5_bag = title_of_table_5.expand(DOWN).expand(RIGHT)
        tb6_tb5_tb4_bag = title_of_table_4.expand(DOWN).expand(RIGHT)
        tb6_tb5_tb4_tb3_bag = title_of_table_3.expand(DOWN).expand(RIGHT)
        tb6_tb5_tb4_tb3_tb2_bag = title_of_table_2.expand(DOWN).expand(RIGHT) # TODO



        # [Assigning values to dimensions and observations]

        tb1_table_name = 'EU Credits'

        table_1_period = title_of_table_1.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() - tb6_tb5_tb4_tb3_tb2_bag
        table_1_BOP_service = title_of_table_1.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb6_tb5_tb4_tb3_tb2_bag
        table_1_CDID = title_of_table_1.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb6_tb5_tb4_tb3_tb2_bag

        tb1_obs = table_1_CDID.waffle(table_1_period) 



        tb2_table_name = 'EU Debits'

        table_2_period = title_of_table_2.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() - tb6_tb5_tb4_tb3_bag
        table_2_BOP_service = title_of_table_2.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb6_tb5_tb4_tb3_bag
        table_2_CDID = title_of_table_2.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb6_tb5_tb4_tb3_bag

        tb2_obs = table_2_CDID.waffle(table_2_period)



        tb3_table_name = 'EU Balances'

        table_3_period = title_of_table_3.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() - tb6_tb5_tb4_bag
        table_3_BOP_service = title_of_table_3.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb6_tb5_tb4_bag
        table_3_CDID = title_of_table_3.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb6_tb5_tb4_bag

        tb3_obs = table_3_CDID.waffle(table_3_period)



        tb4_table_name = 'Non-EU Credits'

        table_4_period = title_of_table_4.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() - tb6_tb5_bag
        table_4_BOP_service = title_of_table_4.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb6_tb5_bag
        table_4_CDID = title_of_table_4.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb6_tb5_bag

        tb4_obs = table_4_CDID.waffle(table_4_period)



        tb5_table_name = 'Non-EU Debits'

        table_5_period = title_of_table_5.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() - tb6_bag
        table_5_BOP_service = title_of_table_5.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb6_bag
        table_5_CDID = title_of_table_5.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb6_bag

        tb5_obs = table_5_CDID.waffle(table_5_period)



        tb6_table_name = 'Non-EU Balances'

        table_6_period = title_of_table_6.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace()
        table_6_BOP_service = title_of_table_6.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace()
        table_6_CDID = title_of_table_6.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace()

        tb6_obs = table_6_CDID.waffle(table_6_period)


        # [Coupling observations with dimensions]

        # [Table 1]
        tb1_dimensions = [
            HDimConst('Table Name', tb1_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_1_period, "Period", DIRECTLY, LEFT),
            HDim(table_1_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_1_CDID,'CDID',DIRECTLY,UP),
        ]

        # [Table 2]
        tb2_dimensions = [
            HDimConst('Table Name', tb2_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_2_period, "Period", DIRECTLY, LEFT),
            HDim(table_2_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_2_CDID,'CDID',DIRECTLY,UP),
        ]

        # [Table 3]
        tb3_dimensions = [
            HDimConst('Table Name', tb3_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_3_period, "Period", DIRECTLY, LEFT),
            HDim(table_3_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_3_CDID,'CDID',DIRECTLY,UP),
        ]

            # [Table 4]
        tb4_dimensions = [
            HDimConst('Table Name', tb4_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_4_period, "Period", DIRECTLY, LEFT),
            HDim(table_4_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_4_CDID,'CDID',DIRECTLY,UP),
        ]

            # [Table 5]
        tb5_dimensions = [
            HDimConst('Table Name', tb5_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_5_period, "Period", DIRECTLY, LEFT),
            HDim(table_5_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_5_CDID,'CDID',DIRECTLY,UP),
        ]

            # [Table 6]
        tb6_dimensions = [
            HDimConst('Table Name', tb6_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_6_period, "Period", DIRECTLY, LEFT),
            HDim(table_6_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_6_CDID,'CDID',DIRECTLY,UP),
        ]


        tb1_cs = ConversionSegment(tab, tb1_dimensions, tb1_obs)
        tb2_cs = ConversionSegment(tab, tb2_dimensions, tb2_obs)
        tb3_cs = ConversionSegment(tab, tb3_dimensions, tb3_obs)
        tb4_cs = ConversionSegment(tab, tb4_dimensions, tb4_obs)
        tb5_cs = ConversionSegment(tab, tb5_dimensions, tb5_obs)
        tb6_cs = ConversionSegment(tab, tb6_dimensions, tb6_obs)
        
        tb1_tidy_sheet = tb1_cs.topandas()
        tb2_tidy_sheet = tb2_cs.topandas()
        tb3_tidy_sheet = tb3_cs.topandas()
        tb4_tidy_sheet = tb4_cs.topandas()
        tb5_tidy_sheet = tb5_cs.topandas()
        tb6_tidy_sheet = tb6_cs.topandas()

        ## create preview files of one table
        #savepreviewhtml(tb1_cs, fname= name + "PREVIEW.html")

        # append all tables together
        tidied_sheets.append(tb1_tidy_sheet)
        tidied_sheets.append(tb2_tidy_sheet)
        tidied_sheets.append(tb3_tidy_sheet)
        tidied_sheets.append(tb4_tidy_sheet)
        tidied_sheets.append(tb5_tidy_sheet)
        tidied_sheets.append(tb6_tidy_sheet)

    else:
        continue



# convert the separate tables into one dataframe
df = pd.concat(tidied_sheets, sort = True, ignore_index=True).fillna('')

## [Postrocessing]

# change period values to ONS standard
df['Period'] = df['Period'].map(lambda x: 'year/' + left(x,4) if 'Q' not in x else 'quarter/' + left(x,4) + '-' + right(x,2))

# convert blank observations to zeros and convert to int type
df['OBS'].loc[(df['OBS'] == '')] = None
#df['OBS'] = df['OBS'].astype(int)
df['Measure Type'] = 'net-transactions'
df['CDID'] = df['CDID'].str.strip()
df['BOP Service'] = df['BOP Service'].str.strip() # whitespace in total credit
#df = df.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=["",""], regex=True)
df["BOP Service"] = df["BOP Service"].replace(r'\n',' ', regex=True) 
df["BOP Service"] = df["BOP Service"].replace(',',' ', regex=True)
# the BOP services showing subtotal values includea lot of spaces between words so replacing them with just one. warning, it also removes all whitespace characters (space, tab, newline, return, formfeed)
df["BOP Service"] = df["BOP Service"].apply(lambda x: " ".join(x.split()))
# conflicting value in Trade total and Trade Total when making a codelist
df["BOP Service"] = df["BOP Service"].replace('Trade total','Trade Total', regex=True)
# because we're linking with the local codelists in the codelist directory we have to pathify these columns
df['BOP Service'] = df['BOP Service'].apply(pathify)
df['Table Name'] = df['Table Name'].apply(pathify)

# replace data marker values
df['DATAMARKER'].loc[(df['DATAMARKER'] == 'x')] ="not-available"

#rename columns
df.rename(columns={'OBS' : 'Value', 'Table Name' : 'Account Type', 'Currency' : 'Unit','DATAMARKER' : 'Marker'}, inplace=True)
df


# TODO this is temporary until me, SB and RB agree what to put. Copied value from https://github.com/GSS-Cogs/family-trade/blob/master/reference/measures.csv
df['Measure Type'] = "current-account-transactions-with-the-european-union-eu-and-with-non-eu-countries"

#%% 
#reorder columns
df = df[['Period','CDID','Seasonal Adjustment','Account Type','BOP Service','Value','Unit','Marker','Measure Type']]

metadata.dataset.title = mainTitle + ' - Current account, Transactions with the European Union (EU) and with non-EU countries'
metadata.dataset.comment = maincomment + r"""
This dataset: Current account, Transactions with the European Union (EU) and with non-EU countries, seasonally adjusted (£ million)
"""
metadata.dataset.description = maindescr + r"""
Current account, Transactions with the European Union (EU) and with non-EU countries:

EU presented on an EU basis.

Includes transactions with European Union institutions.

A quarterly breakdown of the UK's current account with the Euro area (as a whole) is published in table B6 of United Kingdom Economic Accounts (UKEA) at http://www.ons.gov.uk/economy/nationalaccounts/uksectoraccounts

These data are our best estimates of these bilateral UK trade flows. Users should note that alternative estimates are Available, in some cases, via the statistical agencies for bilateral countries or through the central databases such as UN Comtrade (www.comtrade.un.org).

Cells containing 'x' represent unavailable data.

A quarterly geographic breakdown of the UK's current account with the USA, Japan, Canada, Switzerland, Brazil, China, Hong Kong, India and Russia is also Available and is published in table B6B of UKEA (see [note 3])

Includes transactions with international organisations other than European Union institutions.

The quarters in the table refer to: Q1 = Jan to Mar, Q2 = Apr to June, Q3 = July to Sept, Q4 = Oct to Dec.

These tables refer to CDID's which stands for Central Database Identifier, the codes used to identify specific datasets.

As previously announced by HMRC, changes to the way EU imports data have been recorded collected from January 2022 onwards may have led to a discontinuity in trade figures and the Current Account. We advise caution when interpreting 2022 compared with other periods as the impacts of these changes are still being investigated. In addition, changes to the sample framework for foreign direct investment (FDI) statistics means there is a higher degree of uncertainty than usual with inward FDI data. As such, users should be cautious when interpreting Q1 2022 balance of payments statistics. 
"""

# %%
df.to_csv('current_account_transactions_with_the_eu_and_non_eu_countries-observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata() 
catalog_metadata.to_json_file('current_account_transactions_with_the_eu_and_non_eu_countries-catalog-metadata.json')



# +
tidied_sheets_iip = [] # changing name because i'm combining the next three tabs

# [Summary of international investment position (IIP), financial account transactions, and investment income]
for name,tab in tabs.items():
    if name == summary_of_IIP_financial_account_investment_income_d1: # should be Table_D1_3

        bop_tab = 'Summary of IIP, financial account and investment income'
        seasonal_adjustment = 'NSA'
        currency = 'gbp-billion'

        #table locators
        title_of_table_1 = tab.filter("Table D.1, Investment abroad, International investment position (£ billion)")
        title_of_table_2 = tab.filter("Table D.2, Investment abroad, Financial account transactions [note 1] (£ billion)")
        title_of_table_3 = tab.filter("Table D.3, Investment abroad, Investment income earnings (£ billion)")



        # separate bags of tables to remove later on
        tb3_bag = title_of_table_3.expand(DOWN).expand(RIGHT)
        tb3_tb2_bag = title_of_table_2.expand(DOWN).expand(RIGHT)


        
        # [Assigning values to dimensions and observations]

        tb1_table_name = 'Investment abroad, International investment position'

        table_1_period = title_of_table_1.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() - tb3_tb2_bag
        table_1_BOP_service = title_of_table_1.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb3_tb2_bag
        table_1_CDID = title_of_table_1.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb3_tb2_bag

        tb1_obs = table_1_CDID.waffle(table_1_period) 



        tb2_table_name = 'Investment abroad, Financial account transactions'

        table_2_period = title_of_table_2.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() - tb3_bag
        table_2_BOP_service = title_of_table_2.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb3_bag
        table_2_CDID = title_of_table_2.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb3_bag

        tb2_obs = table_2_CDID.waffle(table_2_period)



        tb3_table_name = 'Investment abroad, Investment income earnings'

        table_3_period = title_of_table_3.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() 
        table_3_BOP_service = title_of_table_3.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace()
        table_3_CDID = title_of_table_3.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() 

        tb3_obs = table_3_CDID.waffle(table_3_period)




        # [Coupling observations with dimensions]

        # [Table 1]
        tb1_dimensions = [
            HDimConst('Table Name', tb1_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_1_period, "Period", DIRECTLY, LEFT),
            HDim(table_1_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_1_CDID,'CDID',DIRECTLY,UP),
        ]

        # [Table 2]
        tb2_dimensions = [
            HDimConst('Table Name', tb2_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_2_period, "Period", DIRECTLY, LEFT),
            HDim(table_2_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_2_CDID,'CDID',DIRECTLY,UP),
        ]

        # [Table 3]
        tb3_dimensions = [
            HDimConst('Table Name', tb3_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_3_period, "Period", DIRECTLY, LEFT),
            HDim(table_3_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_3_CDID,'CDID',DIRECTLY,UP),
        ]



        tb1_cs = ConversionSegment(tab, tb1_dimensions, tb1_obs)
        tb2_cs = ConversionSegment(tab, tb2_dimensions, tb2_obs)
        tb3_cs = ConversionSegment(tab, tb3_dimensions, tb3_obs)
        
        tb1_tidy_sheet = tb1_cs.topandas()
        tb2_tidy_sheet = tb2_cs.topandas()
        tb3_tidy_sheet = tb3_cs.topandas()

        ## create preview files of one table
        #savepreviewhtml(tb1_cs, fname= name + "PREVIEW.html")

        # append all tables together
        tidied_sheets_iip.append(tb1_tidy_sheet)
        tidied_sheets_iip.append(tb2_tidy_sheet)
        tidied_sheets_iip.append(tb3_tidy_sheet)


    else:
        continue



# +
# [Summary of international investment position (IIP), financial account transactions, and investment income]
for name,tab in tabs.items():
    if name == summary_of_IIP_financial_account_investment_income_d4: # should be Table_D4_6

        bop_tab = 'Summary of IIP, financial account and investment income'
        seasonal_adjustment = 'NSA'
        currency = 'gbp-billion'

        #table locators
        title_of_table_1 = tab.filter("Table D.4, Investment in the UK, International investment position (£ billion)")
        title_of_table_2 = tab.filter("Table D.5, Investment in the UK, Financial account transactions (£ billion)")
        title_of_table_3 = tab.filter("Table D.6, Investment in the UK, Investment income earnings (£ billion)")



        # separate bags of tables to remove later on
        tb3_bag = title_of_table_3.expand(DOWN).expand(RIGHT)
        tb3_tb2_bag = title_of_table_2.expand(DOWN).expand(RIGHT)


        
        # [Assigning values to dimensions and observations]

        tb1_table_name = 'Investment in the UK, International investment position'

        table_1_period = title_of_table_1.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() - tb3_tb2_bag
        table_1_BOP_service = title_of_table_1.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb3_tb2_bag
        table_1_CDID = title_of_table_1.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb3_tb2_bag

        tb1_obs = table_1_CDID.waffle(table_1_period) 



        tb2_table_name = 'Investment in the UK, Financial account transactions'

        table_2_period = title_of_table_2.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() - tb3_bag
        table_2_BOP_service = title_of_table_2.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb3_bag
        table_2_CDID = title_of_table_2.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb3_bag

        tb2_obs = table_2_CDID.waffle(table_2_period)



        tb3_table_name = 'Investment in the UK, Investment income earnings'

        table_3_period = title_of_table_3.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() 
        table_3_BOP_service = title_of_table_3.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace()
        table_3_CDID = title_of_table_3.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() 

        tb3_obs = table_3_CDID.waffle(table_3_period)




        # [Coupling observations with dimensions]

        # [Table 1]
        tb1_dimensions = [
            HDimConst('Table Name', tb1_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_1_period, "Period", DIRECTLY, LEFT),
            HDim(table_1_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_1_CDID,'CDID',DIRECTLY,UP),
        ]

        # [Table 2]
        tb2_dimensions = [
            HDimConst('Table Name', tb2_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_2_period, "Period", DIRECTLY, LEFT),
            HDim(table_2_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_2_CDID,'CDID',DIRECTLY,UP),
        ]

        # [Table 3]
        tb3_dimensions = [
            HDimConst('Table Name', tb3_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_3_period, "Period", DIRECTLY, LEFT),
            HDim(table_3_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_3_CDID,'CDID',DIRECTLY,UP),
        ]



        tb1_cs = ConversionSegment(tab, tb1_dimensions, tb1_obs)
        tb2_cs = ConversionSegment(tab, tb2_dimensions, tb2_obs)
        tb3_cs = ConversionSegment(tab, tb3_dimensions, tb3_obs)
        
        tb1_tidy_sheet = tb1_cs.topandas()
        tb2_tidy_sheet = tb2_cs.topandas()
        tb3_tidy_sheet = tb3_cs.topandas()

        ## create preview files of one table
        #savepreviewhtml(tb1_cs, fname= name + "PREVIEW.html")

        # append all tables together
        tidied_sheets_iip.append(tb1_tidy_sheet)
        tidied_sheets_iip.append(tb2_tidy_sheet)
        tidied_sheets_iip.append(tb3_tidy_sheet)


    else:
        continue



# +
# [Summary of international investment position (IIP), financial account transactions, and investment income]
for name,tab in tabs.items():
    if name == summary_of_IIP_financial_account_investment_income_d7: # should be Table_D7_9

        bop_tab = 'Summary of IIP, financial account and investment income'
        seasonal_adjustment = 'NSA'
        currency = 'gbp-billion'

        #table locators
        title_of_table_1 = tab.filter("Table D.7, Net investment, International investment position (£ billion)")
        title_of_table_2 = tab.filter("Table D.8, Net investment, Financial account transactions [note 1] (£ billion)")
        title_of_table_3 = tab.filter("Table D.9, Net investment, Investment income earnings (£ billion)")



        # separate bags of tables to remove later on
        tb3_bag = title_of_table_3.expand(DOWN).expand(RIGHT)
        tb3_tb2_bag = title_of_table_2.expand(DOWN).expand(RIGHT)


        
        # [Assigning values to dimensions and observations]

        tb1_table_name = 'Net investment, International investment position'

        table_1_period = title_of_table_1.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() - tb3_tb2_bag
        table_1_BOP_service = title_of_table_1.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb3_tb2_bag
        table_1_CDID = title_of_table_1.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb3_tb2_bag

        tb1_obs = table_1_CDID.waffle(table_1_period) 



        tb2_table_name = 'Net investment, Financial account transactions'

        table_2_period = title_of_table_2.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() - tb3_bag
        table_2_BOP_service = title_of_table_2.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb3_bag
        table_2_CDID = title_of_table_2.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb3_bag

        tb2_obs = table_2_CDID.waffle(table_2_period)



        tb3_table_name = 'Net investment, Investment income earnings'

        table_3_period = title_of_table_3.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() 
        table_3_BOP_service = title_of_table_3.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace()
        table_3_CDID = title_of_table_3.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() 

        tb3_obs = table_3_CDID.waffle(table_3_period)




        # [Coupling observations with dimensions]

        # [Table 1]
        tb1_dimensions = [
            HDimConst('Table Name', tb1_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_1_period, "Period", DIRECTLY, LEFT),
            HDim(table_1_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_1_CDID,'CDID',DIRECTLY,UP),
        ]

        # [Table 2]
        tb2_dimensions = [
            HDimConst('Table Name', tb2_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_2_period, "Period", DIRECTLY, LEFT),
            HDim(table_2_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_2_CDID,'CDID',DIRECTLY,UP),
        ]

        # [Table 3]
        tb3_dimensions = [
            HDimConst('Table Name', tb3_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_3_period, "Period", DIRECTLY, LEFT),
            HDim(table_3_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_3_CDID,'CDID',DIRECTLY,UP),
        ]



        tb1_cs = ConversionSegment(tab, tb1_dimensions, tb1_obs)
        tb2_cs = ConversionSegment(tab, tb2_dimensions, tb2_obs)
        tb3_cs = ConversionSegment(tab, tb3_dimensions, tb3_obs)
        
        tb1_tidy_sheet = tb1_cs.topandas()
        tb2_tidy_sheet = tb2_cs.topandas()
        tb3_tidy_sheet = tb3_cs.topandas()

        ## create preview files of one table
        #savepreviewhtml(tb1_cs, fname= name + "PREVIEW.html")

        # append all tables together
        tidied_sheets_iip.append(tb1_tidy_sheet)
        tidied_sheets_iip.append(tb2_tidy_sheet)
        tidied_sheets_iip.append(tb3_tidy_sheet)


    else:
        continue


# convert the separate tables into one dataframe
df = pd.concat(tidied_sheets_iip, sort = True, ignore_index=True).fillna('')

## [Postrocessing]

# change period values to ONS standard
df['Period'] = df['Period'].map(lambda x: 'year/' + left(x,4) if 'Q' not in x else 'quarter/' + left(x,4) + '-' + right(x,2))

# convert blank observations to zeros and convert to int type
#df['OBS'].loc[(df['OBS'] == '')] = '0'
df['OBS'] = df['OBS'].astype(int)
df['Measure Type'] = 'net-transactions'
df['CDID'] = df['CDID'].str.strip()
df['BOP Service'] = df['BOP Service'].str.strip()
df["BOP Service"] = df["BOP Service"].replace(r'\n',' ', regex=True) 
df["BOP Service"] = df["BOP Service"].replace(',',' ', regex=True)
# the BOP services showing subtotal values includea lot of spaces between words so replacing them with just one. warning, it also removes all whitespace characters (space, tab, newline, return, formfeed)
df["BOP Service"] = df["BOP Service"].apply(lambda x: " ".join(x.split()))
# conflicting value in Trade total and Trade Total when making a codelist
df["BOP Service"] = df["BOP Service"].replace('Trade total','Trade Total', regex=True)
# because we're linking with the local codelists in the codelist directory we have to pathify these columns
df['BOP Service'] = df['BOP Service'].apply(pathify)
df['Table Name'] = df['Table Name'].apply(pathify)


#rename columns
df.rename(columns={'OBS' : 'Value', 'Table Name' : 'Account Type', 'Currency' : 'Unit'}, inplace=True)
df


# TODO this is temporary until me, SB and RB agree what to put. Copied value from https://github.com/GSS-Cogs/family-trade/blob/master/reference/measures.csv
df['Measure Type'] = "summary-of-international-investment-position-financial-account-and-investment-income"

#%% 
#reorder columns
df = df[['Period','CDID','Seasonal Adjustment','Account Type','BOP Service','Value','Unit','Measure Type']]


#%%
metadata.dataset.title = mainTitle + ' - Summary of international investment position (IIP), financial account transactions, and investment income'
metadata.dataset.comment = maincomment + r"""
This dataset: Summary of international investment position (IIP), financial account transactions, and investment income; not seasonally adjusted (£ billion)
"""
metadata.dataset.description = maindescr + r"""
The quarters in the table refer to: Q1 = Jan to Mar, Q2 = Apr to June, Q3 = July to Sept, Q4 = Oct to Dec.

These tables refer to CDID's which stands for Central Database Identifier, the codes used to identify specific datasets.

As previously announced by HMRC, changes to the way EU imports data have been recorded collected from January 2022 onwards may have led to a discontinuity in trade figures and the Current Account. We advise caution when interpreting 2022 compared with other periods as the impacts of these changes are still being investigated. In addition, changes to the sample framework for foreign direct investment (FDI) statistics means there is a higher degree of uncertainty than usual with inward FDI data. As such, users should be cautious when interpreting Q1 2022 balance of payments statistics. 
"""

df.to_csv('summary_of_IIP_financial_account_investment_income-observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata() 
catalog_metadata.to_json_file('summary_of_IIP_financial_account_investment_income-catalog-metadata.json')

#%%
# +
tidied_sheets = [] # reset this each time so you're not appending to previous tables

# [Trade in Goods]
for name,tab in tabs.items():
    if name == goods: # should be Table_E

        bop_tab = 'Trade in Goods'
        seasonal_adjustment = 'SA'
        currency = 'gbp-million'

        #table locators
        title_of_table_1 = tab.filter("Table E.1, Exports of goods (£ million)")
        title_of_table_2 = tab.filter("Table E.2, Imports of goods (£ million)")
        title_of_table_3 = tab.filter("Table E.3, Balances of goods (£ million)")



        # separate bags of tables to remove later on
        tb3_bag = title_of_table_3.expand(DOWN).expand(RIGHT)
        tb3_tb2_bag = title_of_table_2.expand(DOWN).expand(RIGHT) # TODO



        # [Assigning values to dimensions and observations]

        tb1_table_name = 'Exports'

        table_1_period = title_of_table_1.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() -tb3_tb2_bag
        table_1_BOP_service = title_of_table_1.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() -tb3_tb2_bag
        table_1_CDID = title_of_table_1.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() -tb3_tb2_bag

        tb1_obs = table_1_CDID.waffle(table_1_period) 



        tb2_table_name = 'Imports'

        table_2_period = title_of_table_2.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() - tb3_bag
        table_2_BOP_service = title_of_table_2.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb3_bag
        table_2_CDID = title_of_table_2.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb3_bag

        tb2_obs = table_2_CDID.waffle(table_2_period)



        tb3_table_name = 'Balances'

        table_3_period = title_of_table_3.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() 
        table_3_BOP_service = title_of_table_3.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace()
        table_3_CDID = title_of_table_3.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() 

        tb3_obs = table_3_CDID.waffle(table_3_period)



        # [Coupling observations with dimensions]

        # [Table 1]
        tb1_dimensions = [
            HDimConst('Table Name', tb1_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_1_period, "Period", DIRECTLY, LEFT),
            HDim(table_1_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_1_CDID,'CDID',DIRECTLY,UP),
        ]

        # [Table 2]
        tb2_dimensions = [
            HDimConst('Table Name', tb2_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_2_period, "Period", DIRECTLY, LEFT),
            HDim(table_2_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_2_CDID,'CDID',DIRECTLY,UP),
        ]

        # [Table 3]
        tb3_dimensions = [
            HDimConst('Table Name', tb3_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_3_period, "Period", DIRECTLY, LEFT),
            HDim(table_3_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_3_CDID,'CDID',DIRECTLY,UP),
        ]



        tb1_cs = ConversionSegment(tab, tb1_dimensions, tb1_obs)
        tb2_cs = ConversionSegment(tab, tb2_dimensions, tb2_obs)
        tb3_cs = ConversionSegment(tab, tb3_dimensions, tb3_obs)
        
        tb1_tidy_sheet = tb1_cs.topandas()
        tb2_tidy_sheet = tb2_cs.topandas()
        tb3_tidy_sheet = tb3_cs.topandas()

        ## create preview files of one table
        #savepreviewhtml(tb1_cs, fname= name + "PREVIEW.html")

        # append all tables together
        tidied_sheets.append(tb1_tidy_sheet)
        tidied_sheets.append(tb2_tidy_sheet)
        tidied_sheets.append(tb3_tidy_sheet)


    else:
        continue


# convert the separate tables into one dataframe
df = pd.concat(tidied_sheets, sort = True, ignore_index=True).fillna('')

## [Postrocessing]

# change period values to ONS standard
df['Period'] = df['Period'].map(lambda x: 'year/' + left(x,4) if 'Q' not in x else 'quarter/' + left(x,4) + '-' + right(x,2))

# convert blank observations to zeros and convert to int type
#df['OBS'].loc[(df['OBS'] == '')] = '0'
df['OBS'] = df['OBS'].astype(int)
df['Measure Type'] = 'net-transactions'
df['CDID'] = df['CDID'].str.strip()
df['BOP Service'] = df['BOP Service'].str.strip()
df["BOP Service"] = df["BOP Service"].replace(r'\n',' ', regex=True) 
df["BOP Service"] = df["BOP Service"].replace(',',' ', regex=True)
# the BOP services showing subtotal values includea lot of spaces between words so replacing them with just one. warning, it also removes all whitespace characters (space, tab, newline, return, formfeed)
df["BOP Service"] = df["BOP Service"].apply(lambda x: " ".join(x.split()))
# conflicting value in Trade total and Trade Total when making a codelist
df["BOP Service"] = df["BOP Service"].replace('Trade total','Trade Total', regex=True)
# because we're linking with the local codelists in the codelist directory we have to pathify these columns
df['BOP Service'] = df['BOP Service'].apply(pathify)
df['Table Name'] = df['Table Name'].apply(pathify)


#%%

#rename columns
df.rename(columns={'OBS' : 'Value', 'Table Name' : 'Account Type', 'Currency' : 'Unit'}, inplace=True)
df


# TODO this is temporary until me, SB and RB agree what to put. Copied value from https://github.com/GSS-Cogs/family-trade/blob/master/reference/measures.csv
df['Measure Type'] = "trade-in-goods"

#%% 
#reorder columns
df = df[['Period','CDID','Seasonal Adjustment','Account Type','BOP Service','Value','Unit','Measure Type']]

#%%
metadata.dataset.title = mainTitle + ' - Trade in Goods'
metadata.dataset.comment = maincomment + r"""
This dataset: Trade in goods; seasonally adjusted (£ million)
"""
metadata.dataset.description = maindescr + r"""
Trade in Goods:

The quarters in the table refer to: Q1 = Jan to Mar, Q2 = Apr to June, Q3 = July to Sept, Q4 = Oct to Dec.

These tables refer to CDID's which stands for Central Database Identifier, the codes used to identify specific datasets.

As previously announced by HMRC, changes to the way EU imports data have been recorded collected from January 2022 onwards may have led to a discontinuity in trade figures and the Current Account. We advise caution when interpreting 2022 compared with other periods as the impacts of these changes are still being investigated. In addition, changes to the sample framework for foreign direct investment (FDI) statistics means there is a higher degree of uncertainty than usual with inward FDI data. As such, users should be cautious when interpreting Q1 2022 balance of payments statistics. 
"""

df.to_csv('goods-observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata() 
catalog_metadata.to_json_file('goods-catalog-metadata.json')


#%%

# +
tidied_sheets = [] # reset this each time so you're not appending to previous tables

# [Trade in Services]
for name,tab in tabs.items():
    if name == services: # should be Table_F

        bop_tab = 'Trade in Services'
        seasonal_adjustment = 'SA'
        currency = 'gbp-million'

        #table locators
        title_of_table_1 = tab.filter("Table F.1, Exports of services (£ million)")
        title_of_table_2 = tab.filter("Table F.2, Imports of services (£ million)")
        title_of_table_3 = tab.filter("Table F.3, Balances of services (£ million)")



        # separate bags of tables to remove later on
        tb3_bag = title_of_table_3.expand(DOWN).expand(RIGHT)
        tb3_tb2_bag = title_of_table_2.expand(DOWN).expand(RIGHT) # TODO



        # [Assigning values to dimensions and observations]

        tb1_table_name = 'Exports'

        table_1_period = title_of_table_1.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() -tb3_tb2_bag
        table_1_BOP_service = title_of_table_1.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() -tb3_tb2_bag
        table_1_CDID = title_of_table_1.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() -tb3_tb2_bag

        tb1_obs = table_1_CDID.waffle(table_1_period) 



        tb2_table_name = 'Imports'

        table_2_period = title_of_table_2.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() - tb3_bag
        table_2_BOP_service = title_of_table_2.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb3_bag
        table_2_CDID = title_of_table_2.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb3_bag

        tb2_obs = table_2_CDID.waffle(table_2_period)



        tb3_table_name = 'Balances'

        table_3_period = title_of_table_3.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() 
        table_3_BOP_service = title_of_table_3.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace()
        table_3_CDID = title_of_table_3.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() 

        tb3_obs = table_3_CDID.waffle(table_3_period)




        # [Coupling observations with dimensions]

        # [Table 1]
        tb1_dimensions = [
            HDimConst('Table Name', tb1_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_1_period, "Period", DIRECTLY, LEFT),
            HDim(table_1_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_1_CDID,'CDID',DIRECTLY,UP),
        ]

        # [Table 2]
        tb2_dimensions = [
            HDimConst('Table Name', tb2_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_2_period, "Period", DIRECTLY, LEFT),
            HDim(table_2_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_2_CDID,'CDID',DIRECTLY,UP),
        ]

        # [Table 3]
        tb3_dimensions = [
            HDimConst('Table Name', tb3_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_3_period, "Period", DIRECTLY, LEFT),
            HDim(table_3_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_3_CDID,'CDID',DIRECTLY,UP),
        ]



        tb1_cs = ConversionSegment(tab, tb1_dimensions, tb1_obs)
        tb2_cs = ConversionSegment(tab, tb2_dimensions, tb2_obs)
        tb3_cs = ConversionSegment(tab, tb3_dimensions, tb3_obs)
        
        tb1_tidy_sheet = tb1_cs.topandas()
        tb2_tidy_sheet = tb2_cs.topandas()
        tb3_tidy_sheet = tb3_cs.topandas()

        ## create preview files of one table
        #savepreviewhtml(tb1_cs, fname= name + "PREVIEW.html")

        # append all tables together
        tidied_sheets.append(tb1_tidy_sheet)
        tidied_sheets.append(tb2_tidy_sheet)
        tidied_sheets.append(tb3_tidy_sheet)


    else:
        continue


# convert the separate tables into one dataframe
df = pd.concat(tidied_sheets, sort = True, ignore_index=True).fillna('')

## [Postrocessing]

# change period values to ONS standard
df['Period'] = df['Period'].map(lambda x: 'year/' + left(x,4) if 'Q' not in x else 'quarter/' + left(x,4) + '-' + right(x,2))

# convert blank observations to zeros and convert to int type
#df['OBS'].loc[(df['OBS'] == '')] = '0'
df['OBS'] = df['OBS'].astype(int)
df['Measure Type'] = 'net-transactions'
df['CDID'] = df['CDID'].str.strip()
df['BOP Service'] = df['BOP Service'].str.strip()
df["BOP Service"] = df["BOP Service"].replace(r'\n',' ', regex=True) 
df["BOP Service"] = df["BOP Service"].replace(',',' ', regex=True)
# the BOP services showing subtotal values includea lot of spaces between words so replacing them with just one. warning, it also removes all whitespace characters (space, tab, newline, return, formfeed)
df["BOP Service"] = df["BOP Service"].apply(lambda x: " ".join(x.split()))
# conflicting value in Trade total and Trade Total when making a codelist
df["BOP Service"] = df["BOP Service"].replace('Trade total','Trade Total', regex=True)
# because we're linking with the local codelists in the codelist directory we have to pathify these columns
df['BOP Service'] = df['BOP Service'].apply(pathify)
df['Table Name'] = df['Table Name'].apply(pathify)


# %%

#rename columns
df.rename(columns={'OBS' : 'Value', 'Table Name' : 'Account Type', 'Currency' : 'Unit'}, inplace=True)
df


# TODO this is temporary until me, SB and RB agree what to put. Copied value from https://github.com/GSS-Cogs/family-trade/blob/master/reference/measures.csv
df['Measure Type'] = "trade-in-services"

#%% 
#reorder columns
df = df[['Period','CDID','Seasonal Adjustment','Account Type','BOP Service','Value','Unit','Measure Type']]

metadata.dataset.title = mainTitle + ' - Trade in Services'
metadata.dataset.comment = maincomment + r"""
This dataset: Trade in services; seasonally adjusted (£ million)
"""
metadata.dataset.description = maindescr + r"""
Trade in Services:

The quarters in the table refer to: Q1 = Jan to Mar, Q2 = Apr to June, Q3 = July to Sept, Q4 = Oct to Dec.

These tables refer to CDID's which stands for Central Database Identifier, the codes used to identify specific datasets.

As previously announced by HMRC, changes to the way EU imports data have been recorded collected from January 2022 onwards may have led to a discontinuity in trade figures and the Current Account. We advise caution when interpreting 2022 compared with other periods as the impacts of these changes are still being investigated. In addition, changes to the sample framework for foreign direct investment (FDI) statistics means there is a higher degree of uncertainty than usual with inward FDI data. As such, users should be cautious when interpreting Q1 2022 balance of payments statistics. 
"""

df.to_csv('services-observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata() 
catalog_metadata.to_json_file('services-catalog-metadata.json')


#%%

# +
tidied_sheets = [] # reset this each time so you're not appending to previous tables

# [Primary Income]
for name,tab in tabs.items():
    if name == primary_income: # should be Table_G

        bop_tab = 'Primary Income'
        seasonal_adjustment = 'SA'
        currency = 'gbp-million'

        #table locators
        title_of_table_1 = tab.filter("Table G.1, Primary income, credits (£ million)")
        title_of_table_2 = tab.filter("Table G.2, Primary income, debits (£ million)")
        title_of_table_3 = tab.filter("Table G.3, Primary income, balances (£ million)")



        # separate bags of tables to remove later on
        tb3_bag = title_of_table_3.expand(DOWN).expand(RIGHT)
        tb3_tb2_bag = title_of_table_2.expand(DOWN).expand(RIGHT)



        # [Assigning values to dimensions and observations]

        tb1_table_name = 'Credits'

        table_1_period = title_of_table_1.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() -tb3_tb2_bag
        table_1_BOP_service = title_of_table_1.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() -tb3_tb2_bag
        table_1_CDID = title_of_table_1.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() -tb3_tb2_bag

        tb1_obs = table_1_CDID.waffle(table_1_period) 



        tb2_table_name = 'Debits'

        table_2_period = title_of_table_2.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() - tb3_bag
        table_2_BOP_service = title_of_table_2.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb3_bag
        table_2_CDID = title_of_table_2.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb3_bag

        tb2_obs = table_2_CDID.waffle(table_2_period)



        tb3_table_name = 'Balances'

        table_3_period = title_of_table_3.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() 
        table_3_BOP_service = title_of_table_3.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace()
        table_3_CDID = title_of_table_3.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() 

        tb3_obs = table_3_CDID.waffle(table_3_period)




        # [Coupling observations with dimensions]

        # [Table 1]
        tb1_dimensions = [
            HDimConst('Table Name', tb1_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_1_period, "Period", DIRECTLY, LEFT),
            HDim(table_1_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_1_CDID,'CDID',DIRECTLY,UP),
        ]

        # [Table 2]
        tb2_dimensions = [
            HDimConst('Table Name', tb2_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_2_period, "Period", DIRECTLY, LEFT),
            HDim(table_2_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_2_CDID,'CDID',DIRECTLY,UP),
        ]

        # [Table 3]
        tb3_dimensions = [
            HDimConst('Table Name', tb3_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_3_period, "Period", DIRECTLY, LEFT),
            HDim(table_3_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_3_CDID,'CDID',DIRECTLY,UP),
        ]



        tb1_cs = ConversionSegment(tab, tb1_dimensions, tb1_obs)
        tb2_cs = ConversionSegment(tab, tb2_dimensions, tb2_obs)
        tb3_cs = ConversionSegment(tab, tb3_dimensions, tb3_obs)
        
        tb1_tidy_sheet = tb1_cs.topandas()
        tb2_tidy_sheet = tb2_cs.topandas()
        tb3_tidy_sheet = tb3_cs.topandas()

        ## create preview files of one table
        #savepreviewhtml(tb1_cs, fname= name + "PREVIEW.html")

        # append all tables together
        tidied_sheets.append(tb1_tidy_sheet)
        tidied_sheets.append(tb2_tidy_sheet)
        tidied_sheets.append(tb3_tidy_sheet)


    else:
        continue


# convert the separate tables into one dataframe
df = pd.concat(tidied_sheets, sort = True, ignore_index=True).fillna('')

## [Postrocessing]

# change period values to ONS standard
df['Period'] = df['Period'].map(lambda x: 'year/' + left(x,4) if 'Q' not in x else 'quarter/' + left(x,4) + '-' + right(x,2))

# convert blank observations to zeros and convert to int type
#df['OBS'].loc[(df['OBS'] == '')] = '0'
df['OBS'] = df['OBS'].astype(int)
df['Measure Type'] = 'net-transactions'
df['CDID'] = df['CDID'].str.strip()
df['BOP Service'] = df['BOP Service'].str.strip()
df["BOP Service"] = df["BOP Service"].replace(r'\n',' ', regex=True) 
df["BOP Service"] = df["BOP Service"].replace(',',' ', regex=True)
# the BOP services showing subtotal values includea lot of spaces between words so replacing them with just one. warning, it also removes all whitespace characters (space, tab, newline, return, formfeed)
df["BOP Service"] = df["BOP Service"].apply(lambda x: " ".join(x.split()))
# conflicting value in Trade total and Trade Total when making a codelist
df["BOP Service"] = df["BOP Service"].replace('Trade total','Trade Total', regex=True)
# because we're linking with the local codelists in the codelist directory we have to pathify these columns
df['BOP Service'] = df['BOP Service'].apply(pathify)
df['Table Name'] = df['Table Name'].apply(pathify)



#rename columns
df.rename(columns={'OBS' : 'Value', 'Table Name' : 'Account Type', 'Currency' : 'Unit'}, inplace=True)
df


# TODO this is temporary until me, SB and RB agree what to put. Copied value from https://github.com/GSS-Cogs/family-trade/blob/master/reference/measures.csv
df['Measure Type'] = "primary-income"


#reorder columns
df = df[['Period','CDID','Seasonal Adjustment','Account Type','BOP Service','Value','Unit','Measure Type']]
#%% 
metadata.dataset.title = mainTitle + ' - Primary Income'
metadata.dataset.comment = maincomment + r"""
This dataset: Primary income; seasonally adjusted (£ million)
"""
metadata.dataset.description = maindescr + r"""
Primary Income:

The quarters in the table refer to: Q1 = Jan to Mar, Q2 = Apr to June, Q3 = July to Sept, Q4 = Oct to Dec.

These tables refer to CDID's which stands for Central Database Identifier, the codes used to identify specific datasets.

As previously announced by HMRC, changes to the way EU imports data have been recorded collected from January 2022 onwards may have led to a discontinuity in trade figures and the Current Account. We advise caution when interpreting 2022 compared with other periods as the impacts of these changes are still being investigated. In addition, changes to the sample framework for foreign direct investment (FDI) statistics means there is a higher degree of uncertainty than usual with inward FDI data. As such, users should be cautious when interpreting Q1 2022 balance of payments statistics. 
"""

df.to_csv('primary_income-observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata() 
catalog_metadata.to_json_file('primary_income-catalog-metadata.json')


# %%

# +
tidied_sheets = [] # reset this each time so you're not appending to previous tables

# [Secondary Income]
for name,tab in tabs.items():
    if name == secondary_income: # should be Table_H

        bop_tab = 'Secondary Income'
        seasonal_adjustment = 'SA'
        currency = 'gbp-million'

        #table locators
        title_of_table_1 = tab.filter("Table H.1, Secondary income, credits (£ million)")
        title_of_table_2 = tab.filter("Table H.2, Secondary income, debits (£ million)")
        title_of_table_3 = tab.filter("Table H.3, Secondary income, balances (£ million)")



        # separate bags of tables to remove later on
        tb3_bag = title_of_table_3.expand(DOWN).expand(RIGHT)
        tb3_tb2_bag = title_of_table_2.expand(DOWN).expand(RIGHT)



        # [Assigning values to dimensions and observations]

        tb1_table_name = 'Credits'

        table_1_period = title_of_table_1.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() -tb3_tb2_bag
        table_1_BOP_service = title_of_table_1.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() -tb3_tb2_bag
        table_1_CDID = title_of_table_1.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() -tb3_tb2_bag

        tb1_obs = table_1_CDID.waffle(table_1_period) 



        tb2_table_name = 'Debits'

        table_2_period = title_of_table_2.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() - tb3_bag
        table_2_BOP_service = title_of_table_2.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb3_bag
        table_2_CDID = title_of_table_2.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb3_bag

        tb2_obs = table_2_CDID.waffle(table_2_period)



        tb3_table_name = 'Balances'

        table_3_period = title_of_table_3.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() 
        table_3_BOP_service = title_of_table_3.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace()
        table_3_CDID = title_of_table_3.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() 

        tb3_obs = table_3_CDID.waffle(table_3_period)




        # [Coupling observations with dimensions]

        # [Table 1]
        tb1_dimensions = [
            HDimConst('Table Name', tb1_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_1_period, "Period", DIRECTLY, LEFT),
            HDim(table_1_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_1_CDID,'CDID',DIRECTLY,UP),
        ]

        # [Table 2]
        tb2_dimensions = [
            HDimConst('Table Name', tb2_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_2_period, "Period", DIRECTLY, LEFT),
            HDim(table_2_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_2_CDID,'CDID',DIRECTLY,UP),
        ]

        # [Table 3]
        tb3_dimensions = [
            HDimConst('Table Name', tb3_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_3_period, "Period", DIRECTLY, LEFT),
            HDim(table_3_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_3_CDID,'CDID',DIRECTLY,UP),
        ]



        tb1_cs = ConversionSegment(tab, tb1_dimensions, tb1_obs)
        tb2_cs = ConversionSegment(tab, tb2_dimensions, tb2_obs)
        tb3_cs = ConversionSegment(tab, tb3_dimensions, tb3_obs)
        
        tb1_tidy_sheet = tb1_cs.topandas()
        tb2_tidy_sheet = tb2_cs.topandas()
        tb3_tidy_sheet = tb3_cs.topandas()

        ## create preview files of one table
        #savepreviewhtml(tb1_cs, fname= name + "PREVIEW.html")

        # append all tables together
        tidied_sheets.append(tb1_tidy_sheet)
        tidied_sheets.append(tb2_tidy_sheet)
        tidied_sheets.append(tb3_tidy_sheet)


    else:
        continue


# convert the separate tables into one dataframe
df = pd.concat(tidied_sheets, sort = True, ignore_index=True).fillna('')

## [Postrocessing]

# change period values to ONS standard
df['Period'] = df['Period'].map(lambda x: 'year/' + left(x,4) if 'Q' not in x else 'quarter/' + left(x,4) + '-' + right(x,2))

# convert blank observations to zeros and convert to int type
#df['OBS'].loc[(df['OBS'] == '')] = '0'
df['OBS'] = df['OBS'].astype(int)
df['Measure Type'] = 'net-transactions'
df['CDID'] = df['CDID'].str.strip()
df['BOP Service'] = df['BOP Service'].str.strip()
df["BOP Service"] = df["BOP Service"].replace(r'\n',' ', regex=True) 
df["BOP Service"] = df["BOP Service"].replace(',',' ', regex=True)
# the BOP services showing subtotal values includea lot of spaces between words so replacing them with just one. warning, it also removes all whitespace characters (space, tab, newline, return, formfeed)
df["BOP Service"] = df["BOP Service"].apply(lambda x: " ".join(x.split()))
# conflicting value in Trade total and Trade Total when making a codelist
df["BOP Service"] = df["BOP Service"].replace('Trade total','Trade Total', regex=True)
# because we're linking with the local codelists in the codelist directory we have to pathify these columns
df['BOP Service'] = df['BOP Service'].apply(pathify)
df['Table Name'] = df['Table Name'].apply(pathify)




#rename columns
df.rename(columns={'OBS' : 'Value', 'Table Name' : 'Account Type', 'Currency' : 'Unit'}, inplace=True)
df


# TODO this is temporary until me, SB and RB agree what to put. Copied value from https://github.com/GSS-Cogs/family-trade/blob/master/reference/measures.csv
df['Measure Type'] = "secondary-income"


#reorder columns
df = df[['Period','CDID','Seasonal Adjustment','Account Type','BOP Service','Value','Unit','Measure Type']]

#%%
metadata.dataset.title = mainTitle + ' - Secondary Income'
metadata.dataset.comment = maincomment + r"""
This dataset: Secondary income; seasonally adjusted (£ million)
"""
metadata.dataset.description = maindescr + r"""
Secondary Income:

The quarters in the table refer to: Q1 = Jan to Mar, Q2 = Apr to June, Q3 = July to Sept, Q4 = Oct to Dec.

These tables refer to CDID's which stands for Central Database Identifier, the codes used to identify specific datasets.

As previously announced by HMRC, changes to the way EU imports data have been recorded collected from January 2022 onwards may have led to a discontinuity in trade figures and the Current Account. We advise caution when interpreting 2022 compared with other periods as the impacts of these changes are still being investigated. In addition, changes to the sample framework for foreign direct investment (FDI) statistics means there is a higher degree of uncertainty than usual with inward FDI data. As such, users should be cautious when interpreting Q1 2022 balance of payments statistics. 
"""

df.to_csv('secondary_income-observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata() 
catalog_metadata.to_json_file('secondary_income-catalog-metadata.json')



# +
tidied_sheets = [] # reset this each time so you're not appending to previous tables

# [Capital Account]
for name,tab in tabs.items():
    if name == capital_account: # should be Table_I

        bop_tab = 'Capital Account'
        seasonal_adjustment = 'SA'
        currency = 'gbp-million'

        #table locators
        title_of_table_1 = tab.filter("Table I.1, Capital account, credits (£ million)")
        title_of_table_2 = tab.filter("Table I.2, Capital account, debits (£ million)")
        title_of_table_3 = tab.filter("Table I.3, Capital account, balances (£ million)")



        # separate bags of tables to remove later on
        tb3_bag = title_of_table_3.expand(DOWN).expand(RIGHT)
        tb3_tb2_bag = title_of_table_2.expand(DOWN).expand(RIGHT)



        # [Assigning values to dimensions and observations]

        tb1_table_name = 'Credits'

        table_1_period = title_of_table_1.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() -tb3_tb2_bag
        table_1_BOP_service = title_of_table_1.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() -tb3_tb2_bag
        table_1_CDID = title_of_table_1.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() -tb3_tb2_bag

        tb1_obs = table_1_CDID.waffle(table_1_period) 



        tb2_table_name = 'Debits'

        table_2_period = title_of_table_2.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() - tb3_bag
        table_2_BOP_service = title_of_table_2.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb3_bag
        table_2_CDID = title_of_table_2.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb3_bag

        tb2_obs = table_2_CDID.waffle(table_2_period)



        tb3_table_name = 'Balances'

        table_3_period = title_of_table_3.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() 
        table_3_BOP_service = title_of_table_3.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace()
        table_3_CDID = title_of_table_3.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() 

        tb3_obs = table_3_CDID.waffle(table_3_period)




        # [Coupling observations with dimensions]

        # [Table 1]
        tb1_dimensions = [
            HDimConst('Table Name', tb1_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_1_period, "Period", DIRECTLY, LEFT),
            HDim(table_1_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_1_CDID,'CDID',DIRECTLY,UP),
        ]

        # [Table 2]
        tb2_dimensions = [
            HDimConst('Table Name', tb2_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_2_period, "Period", DIRECTLY, LEFT),
            HDim(table_2_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_2_CDID,'CDID',DIRECTLY,UP),
        ]

        # [Table 3]
        tb3_dimensions = [
            HDimConst('Table Name', tb3_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_3_period, "Period", DIRECTLY, LEFT),
            HDim(table_3_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_3_CDID,'CDID',DIRECTLY,UP),
        ]



        tb1_cs = ConversionSegment(tab, tb1_dimensions, tb1_obs)
        tb2_cs = ConversionSegment(tab, tb2_dimensions, tb2_obs)
        tb3_cs = ConversionSegment(tab, tb3_dimensions, tb3_obs)
        
        tb1_tidy_sheet = tb1_cs.topandas()
        tb2_tidy_sheet = tb2_cs.topandas()
        tb3_tidy_sheet = tb3_cs.topandas()

        ## create preview files of one table
        #savepreviewhtml(tb1_cs, fname= name + "PREVIEW.html")

        # append all tables together
        tidied_sheets.append(tb1_tidy_sheet)
        tidied_sheets.append(tb2_tidy_sheet)
        tidied_sheets.append(tb3_tidy_sheet)


    else:
        continue


# convert the separate tables into one dataframe
df = pd.concat(tidied_sheets, sort = True, ignore_index=True).fillna('')

## [Postrocessing]

# change period values to ONS standard
df['Period'] = df['Period'].map(lambda x: 'year/' + left(x,4) if 'Q' not in x else 'quarter/' + left(x,4) + '-' + right(x,2))

# convert blank observations to zeros and convert to int type
#df['OBS'].loc[(df['OBS'] == '')] = '0'
df['OBS'] = df['OBS'].astype(int)
df['Measure Type'] = 'net-transactions'
df['CDID'] = df['CDID'].str.strip()
df['BOP Service'] = df['BOP Service'].str.strip()
df["BOP Service"] = df["BOP Service"].replace(r'\n',' ', regex=True) 
df["BOP Service"] = df["BOP Service"].replace(',',' ', regex=True)
# the BOP services showing subtotal values includea lot of spaces between words so replacing them with just one. warning, it also removes all whitespace characters (space, tab, newline, return, formfeed)
df["BOP Service"] = df["BOP Service"].apply(lambda x: " ".join(x.split()))
# conflicting value in Trade total and Trade Total when making a codelist
df["BOP Service"] = df["BOP Service"].replace('Trade total','Trade Total', regex=True)
# because we're linking with the local codelists in the codelist directory we have to pathify these columns
df['BOP Service'] = df['BOP Service'].apply(pathify)
df['Table Name'] = df['Table Name'].apply(pathify)



#rename columns
df.rename(columns={'OBS' : 'Value', 'Table Name' : 'Account Type', 'Currency' : 'Unit'}, inplace=True)
df


# TODO this is temporary until me, SB and RB agree what to put. Copied value from https://github.com/GSS-Cogs/family-trade/blob/master/reference/measures.csv
df['Measure Type'] = "capital-account"


#reorder columns
df = df[['Period','CDID','Seasonal Adjustment','Account Type','BOP Service','Value','Unit','Measure Type']]
#%%
metadata.dataset.title = mainTitle + ' - Capital Account'
metadata.dataset.comment = maincomment + r"""
This dataset: Capital Account; seasonally adjusted (£ million)
"""
metadata.dataset.description = maindescr + r"""
Capital Account:

The quarters in the table refer to: Q1 = Jan to Mar, Q2 = Apr to June, Q3 = July to Sept, Q4 = Oct to Dec.

These tables refer to CDID's which stands for Central Database Identifier, the codes used to identify specific datasets.

As previously announced by HMRC, changes to the way EU imports data have been recorded collected from January 2022 onwards may have led to a discontinuity in trade figures and the Current Account. We advise caution when interpreting 2022 compared with other periods as the impacts of these changes are still being investigated. In addition, changes to the sample framework for foreign direct investment (FDI) statistics means there is a higher degree of uncertainty than usual with inward FDI data. As such, users should be cautious when interpreting Q1 2022 balance of payments statistics. 
"""

df.to_csv('capital_account-observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata() 
catalog_metadata.to_json_file('capital_account-catalog-metadata.json')


#%%

# +
tidied_sheets = [] # reset this each time so you're not appending to previous tables

# [Financial Account]
for name,tab in tabs.items():
    if name == financial_account: # should be Table_J

        bop_tab = 'Financial Account'
        seasonal_adjustment = 'NSA'
        currency = 'gbp-million'

        #table locators
        title_of_table_1 = tab.filter("Table J.1, UK Investment Abroad (net acquisition of financial assets) (£ million)")
        title_of_table_2 = tab.filter("Table J.2, Investment in the UK (net incurrance of liabilities) (£ million)")
        title_of_table_3 = tab.filter("Table J.3, Net Transactions (net assets less net liabilities) (£ million)")



        # separate bags of tables to remove later on
        tb3_bag = title_of_table_3.expand(DOWN).expand(RIGHT)
        tb3_tb2_bag = title_of_table_2.expand(DOWN).expand(RIGHT)



        # [Assigning values to dimensions and observations]

        tb1_table_name = 'UK Investment Abroad (net acquisition of financial assets)'

        table_1_period = title_of_table_1.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() -tb3_tb2_bag
        table_1_BOP_service = title_of_table_1.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() -tb3_tb2_bag
        table_1_CDID = title_of_table_1.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() -tb3_tb2_bag

        tb1_obs = table_1_CDID.waffle(table_1_period) 



        tb2_table_name = 'Investment in the UK (net incurrance of liabilities)'

        table_2_period = title_of_table_2.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() - tb3_bag
        table_2_BOP_service = title_of_table_2.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb3_bag
        table_2_CDID = title_of_table_2.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb3_bag

        tb2_obs = table_2_CDID.waffle(table_2_period)



        tb3_table_name = 'Net Transactions (net assets less net liabilities)'

        table_3_period = title_of_table_3.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() 
        table_3_BOP_service = title_of_table_3.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace()
        table_3_CDID = title_of_table_3.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() 

        tb3_obs = table_3_CDID.waffle(table_3_period)




        # [Coupling observations with dimensions]

        # [Table 1]
        tb1_dimensions = [
            HDimConst('Table Name', tb1_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_1_period, "Period", DIRECTLY, LEFT),
            HDim(table_1_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_1_CDID,'CDID',DIRECTLY,UP),
        ]

        # [Table 2]
        tb2_dimensions = [
            HDimConst('Table Name', tb2_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_2_period, "Period", DIRECTLY, LEFT),
            HDim(table_2_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_2_CDID,'CDID',DIRECTLY,UP),
        ]

        # [Table 3]
        tb3_dimensions = [
            HDimConst('Table Name', tb3_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_3_period, "Period", DIRECTLY, LEFT),
            HDim(table_3_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_3_CDID,'CDID',DIRECTLY,UP),
        ]



        tb1_cs = ConversionSegment(tab, tb1_dimensions, tb1_obs)
        tb2_cs = ConversionSegment(tab, tb2_dimensions, tb2_obs)
        tb3_cs = ConversionSegment(tab, tb3_dimensions, tb3_obs)
        
        tb1_tidy_sheet = tb1_cs.topandas()
        tb2_tidy_sheet = tb2_cs.topandas()
        tb3_tidy_sheet = tb3_cs.topandas()

        ## create preview files of one table
        #savepreviewhtml(tb1_cs, fname= name + "PREVIEW.html")

        # append all tables together
        tidied_sheets.append(tb1_tidy_sheet)
        tidied_sheets.append(tb2_tidy_sheet)
        tidied_sheets.append(tb3_tidy_sheet)


    else:
        continue


# convert the separate tables into one dataframe
df = pd.concat(tidied_sheets, sort = True, ignore_index=True).fillna('')

## [Postrocessing]

# change period values to ONS standard
df['Period'] = df['Period'].map(lambda x: 'year/' + left(x,4) if 'Q' not in x else 'quarter/' + left(x,4) + '-' + right(x,2))

# convert blank observations to zeros and convert to int type
#df['OBS'].loc[(df['OBS'] == '')] = '0'
df['OBS'] = df['OBS'].astype(int)
df['Measure Type'] = 'net-transactions'
df['CDID'] = df['CDID'].str.strip()
df['BOP Service'] = df['BOP Service'].str.strip()
df["BOP Service"] = df["BOP Service"].replace(r'\n',' ', regex=True) 
df["BOP Service"] = df["BOP Service"].replace(',',' ', regex=True)
# the BOP services showing subtotal values includea lot of spaces between words so replacing them with just one. warning, it also removes all whitespace characters (space, tab, newline, return, formfeed)
df["BOP Service"] = df["BOP Service"].apply(lambda x: " ".join(x.split()))
# conflicting value in Trade total and Trade Total when making a codelist
df["BOP Service"] = df["BOP Service"].replace('Trade total','Trade Total', regex=True)
# because we're linking with the local codelists in the codelist directory we have to pathify these columns
df['BOP Service'] = df['BOP Service'].apply(pathify)
df['Table Name'] = df['Table Name'].apply(pathify)



#rename columns
df.rename(columns={'OBS' : 'Value', 'Table Name' : 'Account Type', 'Currency' : 'Unit'}, inplace=True)
df


# TODO this is temporary until me, SB and RB agree what to put. Copied value from https://github.com/GSS-Cogs/family-trade/blob/master/reference/measures.csv
df['Measure Type'] = "financial-account"


#reorder columns
df = df[['Period','CDID','Seasonal Adjustment','Account Type','BOP Service','Value','Unit','Measure Type']]
#%%

metadata.dataset.title = mainTitle + ' - Financial Account'
metadata.dataset.comment = maincomment + r"""
This dataset: Financial account; not seasonally adjusted (£ million)
"""
metadata.dataset.description = maindescr + r"""
Financial Account:

Further detail of the quarterly financial account is published in tables B8 to B13 of United Kingdom Economic Accounts at http://www.ons.gov.uk/ons/search/index.html?newquery=ukea

The quarters in the table refer to: Q1 = Jan to Mar, Q2 = Apr to June, Q3 = July to Sept, Q4 = Oct to Dec.

These tables refer to CDID's which stands for Central Database Identifier, the codes used to identify specific datasets.

As previously announced by HMRC, changes to the way EU imports data have been recorded collected from January 2022 onwards may have led to a discontinuity in trade figures and the Current Account. We advise caution when interpreting 2022 compared with other periods as the impacts of these changes are still being investigated. In addition, changes to the sample framework for foreign direct investment (FDI) statistics means there is a higher degree of uncertainty than usual with inward FDI data. As such, users should be cautious when interpreting Q1 2022 balance of payments statistics. 
"""

df.to_csv('financial_account-observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata() 
catalog_metadata.to_json_file('financial_account-catalog-metadata.json')


#%%

# +
tidied_sheets = [] # reset this each time so you're not appending to previous tables

# [International Investment Position]
for name,tab in tabs.items():
    if name == international_investment_position: # should be Table_K

        bop_tab = 'International Investment Position'
        seasonal_adjustment = 'NSA'
        currency = 'gbp-million'

        #table locators
        title_of_table_1 = tab.filter("Table K.1, UK Assets (£ billion)")
        title_of_table_2 = tab.filter("Table K.2, UK Liabilities (£ billion)")
        title_of_table_3 = tab.filter("Table K.3, Net International Investment Position (£ billion)")



        # separate bags of tables to remove later on
        tb3_bag = title_of_table_3.expand(DOWN).expand(RIGHT)
        tb3_tb2_bag = title_of_table_2.expand(DOWN).expand(RIGHT)




        # [Assigning values to dimensions and observations]

        tb1_table_name = 'UK Assets'

        table_1_period = title_of_table_1.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() -tb3_tb2_bag
        table_1_BOP_service = title_of_table_1.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() -tb3_tb2_bag
        table_1_CDID = title_of_table_1.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() -tb3_tb2_bag

        tb1_obs = table_1_CDID.waffle(table_1_period) 



        tb2_table_name = 'UK Liabilities'

        table_2_period = title_of_table_2.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() - tb3_bag
        table_2_BOP_service = title_of_table_2.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb3_bag
        table_2_CDID = title_of_table_2.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() - tb3_bag

        tb2_obs = table_2_CDID.waffle(table_2_period)



        tb3_table_name = 'Net International Investment Position'

        table_3_period = title_of_table_3.shift(DOWN).shift(DOWN).shift(DOWN).expand(DOWN).is_not_blank().is_not_whitespace() 
        table_3_BOP_service = title_of_table_3.shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace()
        table_3_CDID = title_of_table_3.shift(DOWN).shift(DOWN).shift(RIGHT).expand(RIGHT).is_not_blank().is_not_whitespace() 

        tb3_obs = table_3_CDID.waffle(table_3_period)




        # [Coupling observations with dimensions]

        # [Table 1]
        tb1_dimensions = [
            HDimConst('Table Name', tb1_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_1_period, "Period", DIRECTLY, LEFT),
            HDim(table_1_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_1_CDID,'CDID',DIRECTLY,UP),
        ]

        # [Table 2]
        tb2_dimensions = [
            HDimConst('Table Name', tb2_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_2_period, "Period", DIRECTLY, LEFT),
            HDim(table_2_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_2_CDID,'CDID',DIRECTLY,UP),
        ]

        # [Table 3]
        tb3_dimensions = [
            HDimConst('Table Name', tb3_table_name),
            HDimConst('Seasonal Adjustment', seasonal_adjustment),
            HDimConst('Currency', currency),
            HDimConst('BoP Section', bop_tab),
            HDim(table_3_period, "Period", DIRECTLY, LEFT),
            HDim(table_3_BOP_service,'BOP Service',DIRECTLY,UP),
            HDim(table_3_CDID,'CDID',DIRECTLY,UP),
        ]



        tb1_cs = ConversionSegment(tab, tb1_dimensions, tb1_obs)
        tb2_cs = ConversionSegment(tab, tb2_dimensions, tb2_obs)
        tb3_cs = ConversionSegment(tab, tb3_dimensions, tb3_obs)
        
        tb1_tidy_sheet = tb1_cs.topandas()
        tb2_tidy_sheet = tb2_cs.topandas()
        tb3_tidy_sheet = tb3_cs.topandas()

        ## create preview files of one table
        #savepreviewhtml(tb1_cs, fname= name + "PREVIEW.html")

        # append all tables together
        tidied_sheets.append(tb1_tidy_sheet)
        tidied_sheets.append(tb2_tidy_sheet)
        tidied_sheets.append(tb3_tidy_sheet)


    else:
        continue


# convert the separate tables into one dataframe
df = pd.concat(tidied_sheets, sort = True, ignore_index=True).fillna('')

## [Postrocessing]

# change period values to ONS standard
df['Period'] = df['Period'].map(lambda x: 'year/' + left(x,4) if 'Q' not in x else 'quarter/' + left(x,4) + '-' + right(x,2))

# convert blank observations to zeros and convert to int type
#df['OBS'].loc[(df['OBS'] == '')] = '0'
df['OBS'] = df['OBS'].astype(int)
df['Measure Type'] = 'net-transactions'
df['CDID'] = df['CDID'].str.strip()
df['BOP Service'] = df['BOP Service'].str.strip()
# because we're linking with the local codelists in the codelist directory we have to pathify these columns
df['BOP Service'] = df['BOP Service'].apply(pathify)
df['Table Name'] = df['Table Name'].apply(pathify)


#rename columns
df.rename(columns={'OBS' : 'Value', 'Table Name' : 'Account Type', 'Currency' : 'Unit'}, inplace=True)
df


# TODO this is temporary until me, SB and RB agree what to put. Copied value from https://github.com/GSS-Cogs/family-trade/blob/master/reference/measures.csv
df['Measure Type'] = "international-investment-position"


#reorder columns
df = df[['Period','CDID','Seasonal Adjustment','Account Type','BOP Service','Value','Unit','Measure Type']]
#%%
metadata.dataset.title = mainTitle + ' - International Investment Position'
metadata.dataset.comment = maincomment + r"""
This dataset: International investment position; not seasonally adjusted (£ billion)
"""
metadata.dataset.description = maindescr + r"""
International Investment Position:

Further detail of the quarterly international investment position is published in tables B14 to B19 of United Kingdom Economic Accounts at http://www.ons.gov.uk/ons/search/index.html?newquery=ukea

The quarters in the table refer to: Q1 = Jan to Mar, Q2 = Apr to June, Q3 = July to Sept, Q4 = Oct to Dec.

These tables refer to CDID's which stands for Central Database Identifier, the codes used to identify specific datasets.

As previously announced by HMRC, changes to the way EU imports data have been recorded collected from January 2022 onwards may have led to a discontinuity in trade figures and the Current Account. We advise caution when interpreting 2022 compared with other periods as the impacts of these changes are still being investigated. In addition, changes to the sample framework for foreign direct investment (FDI) statistics means there is a higher degree of uncertainty than usual with inward FDI data. As such, users should be cautious when interpreting Q1 2022 balance of payments statistics. 
"""

df.to_csv('international_investment_position-observations.csv', index=False)
catalog_metadata = metadata.as_csvqb_catalog_metadata() 
catalog_metadata.to_json_file('international_investment_position-catalog-metadata.json')

