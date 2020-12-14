# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.6.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

from gssutils import * 
import json
import math

info = json.load(open('info.json')) 
#etl_title = info["Name"] 
#etl_publisher = info["Producer"][0] 
#print("Publisher: " + etl_publisher) 
#print("Title: " + etl_title) 

scraper = Scraper(seed="info.json")   
scraper

# +
tidied_sheets = []
trace = TransformTrace()
df = pd.DataFrame()

all_tabs = { tab.name: tab for tab in scraper.distributions[0].as_databaker() }


# -

def cell_to_string(cell):
    s = str(cell)
    start = s.find("'") + len("'")
    end = s.find(">")
    substring = s[start:end].strip("'")
    return substring


# +
#### TAB 1
tab = all_tabs["Records"]

tab_title = "statistics_summary_q2_2020"
tab_columns = ["Period", "Account Type", "Record Since", "Record Highest Value", "Record Highest Date", "Record Lowest Value", "Record Lowest Date", "Measure Type", "Unit"]
trace.start(tab_title, tab, tab_columns, scraper.distributions[0].downloadURL)


period = "Quarter 2 (Apr to June) 2020"
trace.Period("Hardcoded but could have been taken from cell ref A1")

account_type = tab.excel_ref("A7").expand(DOWN).filter(contains_string("(net)")).is_not_blank()
trace.Account_Type("Selected as all values from cell ref A7 down where the value contains the string '(net)'.")

record_since = tab.excel_ref("E8").expand(DOWN).is_not_blank()
trace.Record_Since("Selected as all values from cell ref E8 down.")

record_highest_value = tab.excel_ref("I8").expand(DOWN).is_not_blank() - tab.excel_ref("I8").expand(DOWN).filter(contains_string("Q")).is_not_blank()
trace.Record_Highest_Value("Selected as all values from cell ref I8 down minus the cells containing the string 'Q'.")

record_highest_date = tab.excel_ref("I8").expand(DOWN).filter(contains_string("Q")).is_not_blank()
trace.Record_Highest_Date("Selected as all values from cell ref I8 down where the value contains the string 'Q'.")

record_lowest_value = tab.excel_ref("K8").expand(DOWN).is_not_blank() - tab.excel_ref("K8").expand(DOWN).filter(contains_string("Q")).is_not_blank()
trace.Record_Lowest_Value("Selected as all values from cell ref K8 down minus the cells containing the string 'Q'.")

record_lowest_date = tab.excel_ref("K8").expand(DOWN).filter(contains_string("Q")).is_not_blank()
trace.Record_Lowest_Date("Selected as all values from cell ref K8 down where the value contains the string 'Q'.")

measure_type = tab.excel_ref("A8:A56") - account_type
trace.Measure_Type("Selected as all cells between cell refs A8 and A56 down minus the cells already used by account_type")

unit = "£ Billions"
trace.Unit("Hardcoded but could have been taken from cell K2 - Added '£' symbol.")


observations = tab.excel_ref("C8").expand(DOWN).is_not_blank()

dimensions = [
    HDimConst("Period", period),
    HDim(account_type, "Account Type", CLOSEST, ABOVE),
    HDim(record_since, "Record Since", DIRECTLY, RIGHT),
    HDim(record_highest_value, "Record Highest Value", CLOSEST, ABOVE),
    HDim(record_highest_date, "Record Highest Date", CLOSEST, BELOW),
    HDim(record_lowest_value, "Record Lowest Value", CLOSEST, ABOVE),
    HDim(record_lowest_date, "Record Lowest Date", CLOSEST, BELOW),
    HDim(measure_type, "Measure Type", CLOSEST, ABOVE),
    HDimConst("Unit", unit)
]

tidy_sheet = ConversionSegment(tab, dimensions, observations)
trace.with_preview(tidy_sheet)
#savepreviewhtml(tidy_sheet)
trace.store("combined_" + tab_title, tidy_sheet.topandas())


df = trace.combine_and_trace(tab_title, "combined_" + tab_title)
df.rename(columns={'OBS' : 'Value'}, inplace=True)
trace.render()

tidied = df[["Period", "Account Type", "Record Since", "Record Highest Value", "Record Highest Date", "Record Lowest Value", "Record Lowest Date", "Measure Type", "Unit", "Value"]]
tidied_sheets.append(tidied)
        
#pd.set_option("display.max_rows", None, "display.max_columns", None)
tidied_sheets[0]


# +
#### TAB 2
tab = all_tabs["Table A"]

tab_title = "net_transactions_summary"
tab_columns = ["Year", "Quarter", "Account Type", "Income Type", "Payment Type", "Adjustment Type", "Code", "Measure Type", "Unit"]
trace.start(tab_title, tab, tab_columns, scraper.distributions[0].downloadURL)


year = tab.excel_ref("D4").expand(RIGHT).is_not_blank()
trace.Year("Selected as all non-blank values from cell ref D4 going right/across.")

quarter = tab.excel_ref("D5").expand(RIGHT).is_not_blank() #Quarter has value none for years 2018 and 2019
trace.Quarter("Selected as all non-blank values from cell ref D5 going right/across.")

account_type = tab.excel_ref("B9:B64").filter(contains_string("account")).is_not_blank()
trace.Account_Type("Selected as all non-blank values between cell refs B9 and B64 down continaing the string 'account'.")

adjustment_type = tab.excel_ref("B7:B31").filter(contains_string("adjusted")).is_not_blank()
trace.Adjustment_Type("Selected as all non-blank values between cell refs B7 and B31 down continaing the string 'adjusted'.")

income_type = tab.excel_ref("B10").expand(DOWN).filter(contains_string("and services")).is_not_blank() | tab.excel_ref("B10").expand(DOWN).filter(contains_string("   Primary income")).is_not_blank() | tab.excel_ref("B10").expand(DOWN).filter(contains_string("   Secondary income")).is_not_blank()
trace.Income_Type("Selected as all non-blank values from cell ref B10 down continaing the strings 'and services', '   Primary income' and '   Secondary income'.")

payment_type = tab.excel_ref("B10:B64").is_not_blank() - account_type - adjustment_type - income_type #net errors belongs to financial account? Need to remove supers
trace.Payment_Type("Selected as all non-blank values between cell refs B10 and B64 down minus the values selected by account, adjuctment and income types.")

code = tab.excel_ref("C11").expand(DOWN).is_not_blank()
trace.Code("Selected as the value from cell ref C11")

measure_type = tab.excel_ref("B2")
trace.Measure_Type("Selected as the value from cell ref B2")

unit = tab.excel_ref("M3")
trace.Unit("Selected as the value from cell ref M3")


observations = tab.excel_ref("D11").expand(RIGHT).expand(DOWN).is_not_blank()


dimensions = [
    HDim(year, "Year", DIRECTLY, ABOVE),
    HDim(quarter, "Quarter", CLOSEST, LEFT),
    HDim(account_type, "Account Type", CLOSEST, ABOVE),
    HDim(adjustment_type, "Adjustment Type", CLOSEST, ABOVE),
    HDim(income_type, "Income Type", CLOSEST, ABOVE),
    HDim(payment_type, "Payment Type", CLOSEST, ABOVE),
    HDim(code, "Code", DIRECTLY, LEFT),
    HDim(measure_type, "Measure Type", CLOSEST, ABOVE),
    HDim(unit, "Unit", CLOSEST, ABOVE)
]

tidy_sheet = ConversionSegment(tab, dimensions, observations)
trace.with_preview(tidy_sheet)
#savepreviewhtml(tidy_sheet)
trace.store("combined_" + tab_title, tidy_sheet.topandas())


df = trace.combine_and_trace(tab_title, "combined_" + tab_title)
df.rename(columns={'OBS' : 'Value'}, inplace=True)
trace.render()

tidied = df[["Year", "Quarter", "Account Type", "Income Type", "Payment Type", "Adjustment Type", "Code", "Measure Type", "Unit", "Value"]]
tidied_sheets.append(tidied)
        
#pd.set_option("display.max_rows", None, "display.max_columns", None)
tidied_sheets[1]

#Table could probably be split at Financial Account (B55) and remove columns account and adjustment type as they appear to not apply.


#### TAB 3a
# +
tab = all_tabs["Table B"]

tab_title = "seasonally_adjusted_balances"
tab_columns = ["Year", "Quarter", "Balance Type", "Income Type", "Adjustment Type", "Code", "Measure Type", "Unit"]
trace.start(tab_title, tab, tab_columns, scraper.distributions[0].downloadURL)


year = tab.excel_ref("D4").expand(RIGHT).is_not_blank()
trace.Year("Selected as all non-blank values from cell ref D4 going right/across.")

quarter = tab.excel_ref("D5").expand(RIGHT).is_not_blank() #Quarter has value none for years 2018 and 2019
trace.Quarter("Selected as all non-blank values from cell ref D5 going right/across.")

#measure_type = tab.excel_ref("B7:B65").filter(contains_string("     ")).filter(contains_string(" Total")).filter(contains_string(" Current balance")).is_not_blank()
measure_type = tab.excel_ref("B7:B65").filter(contains_string("     ")).is_not_blank() | tab.excel_ref("B7:B65").filter(contains_string(" Total")).is_not_blank() | tab.excel_ref("B7:B65").filter(contains_string(" Current balance")).is_not_blank()
trace.Measure_Type("Selected as the value from cell ref B2")

income_type = tab.excel_ref("B7:B65").filter(contains_string("   ")).is_not_blank() - measure_type
trace.Income_Type("Selected as all non-blank values from cell ref B10 down continaing the strings 'and services', '   Primary income' and '   Secondary income'.")

#balance_type = tab.excel_ref("B7:B65").filter(contains_string(" ")).is_not_blank().is_not_whitespace() - measure_type - income_type - tab.excel_ref("B7:B65").filter(contains_string("Total")).is_not_blank().is_not_whitespace() - tab.excel_ref("B7:B65").filter(contains_string("Current balance")).is_not_blank().is_not_whitespace()
balance_type = tab.excel_ref("B7:B65").filter(contains_string(" ")).is_not_blank().is_not_whitespace() - measure_type - income_type
trace.Balance_Type("Selected as all non-blank values between cell refs B9 and B64 down continaing the string 'account'.")

adjustment_type = "Seasonally Adjusted"
trace.Adjustment_Type("Selected as all non-blank values between cell refs B7 and B31 down continaing the string 'adjusted'.")

code = tab.excel_ref("C8").waffle(measure_type)
trace.Code("Selected as the value from cell ref C11")

unit = tab.excel_ref("M3")
trace.Unit("Selected as the value from cell ref M3")


observations = code.waffle(year)


dimensions = [
    HDim(year, "Year", DIRECTLY, ABOVE),
    HDim(quarter, "Quarter", CLOSEST, LEFT),
    HDim(balance_type, "Balance Type", CLOSEST, ABOVE),
    HDimConst("Adjustment Type", adjustment_type),
    HDim(income_type, "Income Type", CLOSEST, ABOVE),
    HDim(code, "Code", DIRECTLY, LEFT),
    HDim(measure_type, "Measure Type", CLOSEST, ABOVE),
    HDim(unit, "Unit", CLOSEST, ABOVE)
]

tidy_sheet = ConversionSegment(tab, dimensions, observations)
trace.with_preview(tidy_sheet)
#savepreviewhtml(tidy_sheet)
trace.store("combined_" + tab_title, tidy_sheet.topandas())


df = trace.combine_and_trace(tab_title, "combined_" + tab_title)
df.rename(columns={'OBS' : 'Value'}, inplace=True)
trace.render()

#count = 0
#for mt in df["Measure Type"]:
#    if mt == " Total":
#        df.iloc[count] = df["Income Type"].map({"Secondary income": "Hi"})
        #df["Income Type"] = "Hi"
#    count+=1 
    
tidied = df[["Year", "Quarter", "Balance Type", "Income Type", "Adjustment Type", "Code", "Measure Type", "Unit", "Value"]]
tidied_sheets.append(tidied)

#pd.set_option("display.max_rows", None, "display.max_columns", None)
tidied_sheets[2]

#Note - 'Total' and 'Current balance' need to have their income type changed to 'balance_type + measure_type' (E.g. income type = 'Debit Total') and 'Balances Current'


#### TAB 3b
# +
tab = all_tabs["Table B"]

tab_title = "seasonally_adjusted_as_gdp_percentage"
tab_columns = ["Year", "Quarter", "Balance Type", "Income Type", "Adjustment Type", "Code", "Measure Type", "Unit"]
trace.start(tab_title, tab, tab_columns, scraper.distributions[0].downloadURL)


year = tab.excel_ref("D4").expand(RIGHT).is_not_blank()
trace.Year("Selected as all non-blank values from cell ref D4 going right/across.")

quarter = tab.excel_ref("D5").expand(RIGHT).is_not_blank() #Quarter has value none for first instance of years 2018 and 2019 (total?)
trace.Quarter("Selected as all non-blank values from cell ref D5 going right/across.")

measure_type = tab.excel_ref("B67:B76").filter(contains_string("     ")).is_not_blank() | tab.excel_ref("B67:B76").filter(contains_string(" Current")).is_not_blank() | tab.excel_ref("B67:B76").filter(contains_string("   Total")).is_not_blank()
trace.Measure_Type("Selected as the value from cell ref B2")

income_type = tab.excel_ref("B67:B76").filter(contains_string("   ")).is_not_blank() - measure_type
trace.Income_Type("Selected as all non-blank values from cell ref B10 down continaing the strings 'and services', '   Primary income' and '   Secondary income'.")

balance_type = tab.excel_ref("B67:B76").filter(contains_string(" ")).is_not_blank().is_not_whitespace() - measure_type - income_type
trace.Balance_Type("Selected as all non-blank values between cell refs B9 and B64 down continaing the string 'account'.")

adjustment_type = "Seasonally Adjusted"
trace.Adjustment_Type("Selected as all non-blank values between cell refs B7 and B31 down continaing the string 'adjusted'.")

code = tab.excel_ref("C8").waffle(measure_type)
trace.Code("Selected as the value from cell ref C11")

unit = "Percentage of GDP"
trace.Unit("Selected as the value from cell ref M3")


observations = code.waffle(year)


dimensions = [
    HDim(year, "Year", DIRECTLY, ABOVE),
    HDim(quarter, "Quarter", CLOSEST, LEFT),
    HDim(balance_type, "Balance Type", CLOSEST, ABOVE),
    HDimConst("Adjustment Type", adjustment_type),
    HDim(income_type, "Income Type", CLOSEST, ABOVE),
    HDim(code, "Code", DIRECTLY, LEFT),
    HDim(measure_type, "Measure Type", CLOSEST, ABOVE),
    HDimConst("Unit", unit)
]

tidy_sheet = ConversionSegment(tab, dimensions, observations)
#trace.with_preview(tidy_sheet)
savepreviewhtml(tidy_sheet)
trace.store("combined_" + tab_title, tidy_sheet.topandas())


df = trace.combine_and_trace(tab_title, "combined_" + tab_title)
df.rename(columns={'OBS' : 'Value'}, inplace=True)
trace.render()

    
tidied = df[["Year", "Quarter", "Balance Type", "Income Type", "Adjustment Type", "Code", "Measure Type", "Unit", "Value"]]
tidied_sheets.append(tidied)

#pd.set_option("display.max_rows", None, "display.max_columns", None)
tidied_sheets[3]

#Notes - Need to remove super from Balance Type
#

# +
tab = all_tabs["Table C"]

tab_title = "seasonally_adjusted_current_account_transactions"
tab_columns = ["Year", "Quarter", "Transaction Partner", "Balance Type", "CDID", "Measure Type", "Unit"]
trace.start(tab_title, tab, tab_columns, scraper.distributions[0].downloadURL)

year = tab.excel_ref("D4").expand(RIGHT).is_not_blank()
trace.Year("Selected as all non-blank values from cell ref D4 going right/across.")

quarter = tab.excel_ref("D5").expand(RIGHT).is_not_blank() #Quarter has value none for first instance of years 2018 and 2019 (total?)
trace.Quarter("Selected as all non-blank values from cell ref D5 going right/across.")

transaction_partner = tab.excel_ref("B7:B75").filter(contains_string("Transactions")).is_not_blank()
trace.Transaction_Partner("Selected as all non-blank values between cells B7 and B75 containing the string 'Transactions'.")

cdid = tab.excel_ref("C10").expand(DOWN).is_not_blank().is_not_whitespace()
trace.CDID("Selected as all non-blank and non-whitespace values from cell ref C10 down.")

measure_type = tab.excel_ref("B7:B75").spaceprefix(3).is_not_blank() | tab.excel_ref("B7:B75").filter(contains_string("Total")).is_not_blank()
trace.Measure_Type("Selected as all non-blank values between cells B7 and B75 prefixed by 3 spaces or containing the string 'Total'.")

balance_type = tab.excel_ref("B7:B75").is_not_whitespace() - transaction_partner - measure_type
trace.Balance_Type("Selected as all non-blank values between cells B7 and B75 minus the values of transaction_partner and measure_type.")

unit = tab.excel_ref("M3")
trace.Unit("Selected as the value in cell M3")

observations = tab.excel_ref("D10").expand(DOWN).expand(RIGHT).is_not_blank()


dimensions = [
    HDim(year, "Year", DIRECTLY, ABOVE),
    HDim(quarter, "Quarter", CLOSEST, LEFT),
    HDim(transaction_partner, "Transaction Partner", CLOSEST, ABOVE),
    HDim(cdid, "CDID", DIRECTLY, LEFT),
    HDim(measure_type, "Measure Type", CLOSEST, ABOVE),
    HDim(balance_type, "Balance Type", CLOSEST, ABOVE),
    HDim(unit, "Unit", CLOSEST, ABOVE)
]

tidy_sheet = ConversionSegment(tab, dimensions, observations)
trace.with_preview(tidy_sheet)
#savepreviewhtml(tidy_sheet)
trace.store("combined_" + tab_title, tidy_sheet.topandas())


df = trace.combine_and_trace(tab_title, "combined_" + tab_title)
df.rename(columns={'OBS' : 'Value'}, inplace=True)
trace.render()


tidied = df[["Year", "Quarter", "Transaction Partner", "Balance Type", "CDID", "Measure Type", "Unit", "Value"]]
tidied_sheets.append(tidied)

#pd.set_option("display.max_rows", None, "display.max_columns", None)
tidied_sheets[4]

#REMOVE SUPERS

# +
tab = all_tabs["Table D"]

tab_title = "non_seasonally_adjusted_investments_summary"
tab_columns = ["Year", "Quarter", "Investment Type", "Investment Details", "CDID", "Measure Type", "Unit"]
trace.start(tab_title, tab, tab_columns, scraper.distributions[0].downloadURL)

year = tab.excel_ref("D4").expand(RIGHT).is_not_blank()
trace.Year("Selected as all non-blank values from cell ref D4 going right/across.")

quarter = tab.excel_ref("D5").expand(RIGHT).is_not_blank() #Quarter has value none for first instance of years 2018 and 2019 (total?)
trace.Quarter("Selected as all non-blank values from cell ref D5 going right/across.")

investment_type = tab.excel_ref("B").by_index([7, 35, 59])
trace.Year("Selected as the values in column B at indexes: 7, 35 and 59")

cdid = tab.excel_ref("C10").expand(DOWN).is_not_blank().is_not_whitespace()
trace.CDID("Selected as all non-blank and non-whitespace values from cell ref C10 down.")

measure_type = tab.excel_ref("B7:B85").spaceprefix(3)
trace.Year("Selected as all non-blank values between cells B7 and B85 prefixed by 3 spaces.")

investment_details = tab.excel_ref("B7:B85").spaceprefix(1) - investment_type
trace.Year("Selected as all values between cells B7 and B85 minus the values of investment_type.")

unit = tab.excel_ref("M3")
trace.Unit("Selected as the value in cell M3")

observations = tab.excel_ref("D10").expand(DOWN).expand(RIGHT).is_not_blank()


dimensions = [
    HDim(year, "Year", DIRECTLY, ABOVE),
    HDim(quarter, "Quarter", CLOSEST, LEFT),
    HDim(investment_type, "Investment Type", CLOSEST, ABOVE),
    HDim(cdid, "CDID", DIRECTLY, LEFT),
    HDim(measure_type, "Measure Type", CLOSEST, ABOVE),
    HDim(investment_details, "Investment Details", CLOSEST, ABOVE),
    HDim(unit, "Unit", CLOSEST, ABOVE)
]

tidy_sheet = ConversionSegment(tab, dimensions, observations)
trace.with_preview(tidy_sheet)
#savepreviewhtml(tidy_sheet)
trace.store("combined_" + tab_title, tidy_sheet.topandas())


df = trace.combine_and_trace(tab_title, "combined_" + tab_title)
df.rename(columns={'OBS' : 'Value'}, inplace=True)
trace.render()


tidied = df[["Year", "Quarter", "Investment Type", "Investment Details", "CDID", "Measure Type", "Unit", "Value"]]
tidied_sheets.append(tidied)

#pd.set_option("display.max_rows", None, "display.max_columns", None)
tidied_sheets[5]

#REMOVE SUPERS

# +
tab = all_tabs["Table E"]

tab_title = "seasonally_adjusted_trade_in_goods"
tab_columns = ["Year", "Quarter", "Trade Direction", "Goods Type", "CDID", "Measure Type", "Unit"]
trace.start(tab_title, tab, tab_columns, scraper.distributions[0].downloadURL)

year = tab.excel_ref("D4").expand(RIGHT).is_not_blank()
trace.Year("Selected as all non-blank values from cell ref D4 going right/across.")

quarter = tab.excel_ref("D5").expand(RIGHT).is_not_blank() #Quarter has value none for first instance of years 2018 and 2019 (total?)
trace.Quarter("Selected as all non-blank values from cell ref D5 going right/across.")

trade_direction = tab.excel_ref("B7").expand(DOWN).spaceprefix(1) - tab.excel_ref("B7").expand(DOWN).filter(contains_string("Total"))
trace.Year("Selected as the all values from cell ref B7 down prefixed by 1 space, minus all values from cell ref B7 down containing the string 'Total'.")

cdid = tab.excel_ref("C8").expand(DOWN).is_not_blank().is_not_whitespace()
trace.CDID("Selected as all non-blank and non-whitespace values from cell ref C8 down.")

measure_type = "Trade In Goods"
trace.Year("Hardcoded as the string but could have been taken from cell B1.")

goods_type = tab.excel_ref("B7").expand(DOWN).spaceprefix(3).is_not_blank() | tab.excel_ref("B7").expand(DOWN).filter(contains_string("Total")).is_not_blank()
trace.Year("Selected as all values from cell ref B7 down prefixed by 3 spaces or all values from cell ref B7 down containing the string 'Total'.")

unit = tab.excel_ref("M3")
trace.Unit("Selected as the value in cell M3")

observations = tab.excel_ref("D8").expand(DOWN).expand(RIGHT).is_not_blank()


dimensions = [
    HDim(year, "Year", DIRECTLY, ABOVE),
    HDim(quarter, "Quarter", CLOSEST, LEFT),
    HDim(trade_direction, "Trade Direction", CLOSEST, ABOVE),
    HDim(cdid, "CDID", DIRECTLY, LEFT),
    HDimConst("Measure Type", measure_type),
    HDim(goods_type, "Goods Type", CLOSEST, ABOVE),
    HDim(unit, "Unit", CLOSEST, ABOVE)
]

tidy_sheet = ConversionSegment(tab, dimensions, observations)
trace.with_preview(tidy_sheet)
#savepreviewhtml(tidy_sheet)
trace.store("combined_" + tab_title, tidy_sheet.topandas())


df = trace.combine_and_trace(tab_title, "combined_" + tab_title)
df.rename(columns={'OBS' : 'Value'}, inplace=True)
trace.render()


tidied = df[["Year", "Quarter", "Trade Direction", "Goods Type", "CDID", "Measure Type", "Unit", "Value"]]
tidied_sheets.append(tidied)

#pd.set_option("display.max_rows", None, "display.max_columns", None)
tidied_sheets[6]

#REMOVE SUPERS

# +
#Outputs:


#Notes:
    #info.json has been modified to remove "/current" from the landing page URL
    #notes on tabs (Table A, Table D) indicate sign should be reversed if  was obtained from the Pink Book dataset
# -


