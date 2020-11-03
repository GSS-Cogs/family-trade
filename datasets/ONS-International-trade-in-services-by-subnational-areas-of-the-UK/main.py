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
tab = all_tabs["1. NUTS1, industry"]

tab_title = "1_nuts1_industry"
tab_columns = ["Year", "NUTS1 Area", "Industry", "Measure Type", "Unit"]
trace.start(tab_title, tab, tab_columns, scraper.distributions[0].downloadURL)


year = "2018"
trace.Year("Hardcoded but could have been taken from tab title (cell A1)")

nuts1_area = tab.excel_ref("A4:A42").is_not_blank()
trace.NUTS1_Area("Selected as all non-blank values between cell refs A4 and A42")

industry = tab.excel_ref("C3").expand(RIGHT).is_not_blank()
trace.Industry("Selected as all non-blank values from cell ref C3 going right/across.")

measure_type = tab.excel_ref("B4").expand(DOWN).is_not_blank()
trace.Measure_Type("Selected as all non-blank values from cell ref B4 down.")

unit = "£ millions"
trace.Unit("Hardcoded but could have been taken from cell A2")


observations = tab.excel_ref("C4").expand(RIGHT).expand(DOWN).is_not_blank()

dimensions = [
    HDimConst("Year", year),
    HDim(nuts1_area, "NUTS1 Area", CLOSEST, ABOVE),
    HDim(industry, "Industry", DIRECTLY, ABOVE),
    HDim(measure_type, "Measure Type", DIRECTLY, LEFT),
    HDimConst("Unit", unit)
]

tidy_sheet = ConversionSegment(tab, dimensions, observations)
trace.with_preview(tidy_sheet)
#savepreviewhtml(tidy_sheet)
trace.store("combined_" + tab_title, tidy_sheet.topandas())

df = trace.combine_and_trace(tab_title, "combined_" + tab_title)
df.rename(columns={'OBS' : 'Value'}, inplace=True)
trace.render()

tidied = df[["Year", "NUTS1 Area", "Industry", "Measure Type", "Unit", "Value"]]
tidied_sheets.append(tidied)
        
#pd.set_option("display.max_rows", None, "display.max_columns", None)
#tidied_sheets[0]

#Notes:
    #Will need a datamarker column for values ".."
# +
tab = all_tabs["2. NUTS1, industry, destination"]

tab_title = "2_nuts1_industry_destination"
tab_columns = ["Year", "NUTS1 Area", "Industry", "Destination", "Measure Type", "Unit"]
trace.start(tab_title, tab, tab_columns, scraper.distributions[0].downloadURL)


year = "2018"
trace.Year("Hardcoded but could have been taken from tab title (cell A1)")

nuts1_area = tab.excel_ref("A5:A43").is_not_blank()
trace.NUTS1_Area("Selected as all non-blank values between cell refs A5 and A43")

industry = tab.excel_ref("C3").expand(RIGHT).is_not_blank()
trace.Industry("Selected as all non-blank values from cell ref C3 going right/across.")

destination = tab.excel_ref("C4").expand(RIGHT).is_not_blank()
trace.Destination("Selected as all non-blank values from cell ref C4 going right/across.")

measure_type = tab.excel_ref("B5").expand(DOWN).is_not_blank()
trace.Measure_Type("Selected as all non-blank values from cell ref B5 down.")

unit = "£ millions"
trace.Unit("Hardcoded but could have been taken from cell A2")


observations = tab.excel_ref("C5").expand(RIGHT).expand(DOWN).is_not_blank()

dimensions = [
    HDimConst("Year", year),
    HDim(nuts1_area, "NUTS1 Area", CLOSEST, ABOVE),
    HDim(industry, "Industry", CLOSEST, LEFT),
    HDim(destination, "Destination", DIRECTLY, ABOVE),
    HDim(measure_type, "Measure Type", DIRECTLY, LEFT),
    HDimConst("Unit", unit)
]

tidy_sheet = ConversionSegment(tab, dimensions, observations)
trace.with_preview(tidy_sheet)
#savepreviewhtml(tidy_sheet)
trace.store("combined_" + tab_title, tidy_sheet.topandas())

df = trace.combine_and_trace(tab_title, "combined_" + tab_title)
df.rename(columns={'OBS' : 'Value'}, inplace=True)
trace.render()

tidied = df[["Year", "NUTS1 Area", "Industry", "Destination", "Measure Type", "Unit", "Value"]]
tidied_sheets.append(tidied)

#pd.set_option("display.max_rows", None, "display.max_columns", None)
#tidied_sheets[1]

#Notes:
    #Will need a datamarker column for values ".."


# +
tab = all_tabs["3. NUTS2, industry"]

tab_title = "3_nuts2_industry"
tab_columns = ["Year", "NUTS2", "NUTS2 Area", "Industry", "Measure Type", "Unit"]
trace.start(tab_title, tab, tab_columns, scraper.distributions[0].downloadURL)


year = "2018"
trace.Year("Hardcoded but could have been taken from tab title (cell A1)")

nuts2 = tab.excel_ref("A4:A123").is_not_blank()
trace.NUTS2("Selected as all non-blank values between cell refs A4 and A123")

nuts2_area = tab.excel_ref("B4").expand(DOWN).is_not_blank()
trace.NUTS2_Area("Selected as all non-blank values from cell ref B4 down.")

industry = tab.excel_ref("D3").expand(RIGHT).is_not_blank()
trace.Industry("Selected as all non-blank values from cell ref D3 going right/across.")

measure_type = tab.excel_ref("C4").expand(DOWN).is_not_blank()
trace.Measure_Type("Selected as all non-blank values from cell ref C4 down.")

unit = "£ millions"
trace.Unit("Hardcoded but could have been taken from cell A2")


observations = tab.excel_ref("D4").expand(RIGHT).expand(DOWN).is_not_blank()

dimensions = [
    HDimConst("Year", year),
    HDim(nuts2, "NUTS2", CLOSEST, ABOVE),
    HDim(nuts2_area, "NUTS2 Area", CLOSEST, ABOVE),
    HDim(industry, "Industry", DIRECTLY, ABOVE),
    HDim(measure_type, "Measure Type", DIRECTLY, LEFT),
    HDimConst("Unit", unit)
]

tidy_sheet = ConversionSegment(tab, dimensions, observations)
trace.with_preview(tidy_sheet)
#savepreviewhtml(tidy_sheet)
trace.store("combined_" + tab_title, tidy_sheet.topandas())

df = trace.combine_and_trace(tab_title, "combined_" + tab_title)
df.rename(columns={'OBS' : 'Value'}, inplace=True)
trace.render()

tidied = df[["Year", "NUTS2", "NUTS2 Area", "Industry", "Measure Type", "Unit", "Value"]]
tidied_sheets.append(tidied)
        
#pd.set_option("display.max_rows", None, "display.max_columns", None)
#tidied_sheets[2]

#Notes:
    #Will need a datamarker column for values ".."

# +
tab = all_tabs["4. NUTS2, industry, destination"]

tab_title = "4_nuts2_industry_destination"
tab_columns = ["Year", "NUTS2", "NUTS2 Area", "Industry", "Destination", "Measure Type", "Unit"]
trace.start(tab_title, tab, tab_columns, scraper.distributions[0].downloadURL)


year = "2018"
trace.Year("Hardcoded but could have been taken from tab title (cell A1)")

nuts2 = tab.excel_ref("A5:A124").is_not_blank()
trace.NUTS2("Selected as all non-blank values between cell refs A5 and A124")

nuts2_area = tab.excel_ref("B5").expand(DOWN).is_not_blank()
trace.NUTS2_Area("Selected as all non-blank values from cell ref B5 down.")

industry = tab.excel_ref("D3").expand(RIGHT).is_not_blank()
trace.Industry("Selected as all non-blank values from cell ref D3 going right/across.")

destination = tab.excel_ref("D4").expand(RIGHT).is_not_blank()
trace.Destination("Selected as all non-blank values from cell ref D4 going right/across.")

measure_type = tab.excel_ref("C5").expand(DOWN).is_not_blank()
trace.Measure_Type("Selected as all non-blank values from cell ref C5 down.")

unit = "£ millions"
trace.Unit("Hardcoded but could have been taken from cell A2")


observations = tab.excel_ref("D5").expand(RIGHT).expand(DOWN).is_not_blank()

dimensions = [
    HDimConst("Year", year),
    HDim(nuts2, "NUTS2", CLOSEST, ABOVE),
    HDim(nuts2_area, "NUTS2 Area", CLOSEST, ABOVE),
    HDim(industry, "Industry", CLOSEST, LEFT),
    HDim(destination, "Destination", DIRECTLY, ABOVE),
    HDim(measure_type, "Measure Type", DIRECTLY, LEFT),
    HDimConst("Unit", unit)
]

tidy_sheet = ConversionSegment(tab, dimensions, observations)
trace.with_preview(tidy_sheet)
#savepreviewhtml(tidy_sheet)
trace.store("combined_" + tab_title, tidy_sheet.topandas())

df = trace.combine_and_trace(tab_title, "combined_" + tab_title)
df.rename(columns={'OBS' : 'Value'}, inplace=True)
trace.render()

tidied = df[["Year", "NUTS2", "NUTS2 Area", "Industry", "Destination", "Measure Type", "Unit", "Value"]]
tidied_sheets.append(tidied)

#pd.set_option("display.max_rows", None, "display.max_columns", None)
#tidied_sheets[3]

#Notes:
    #Will need a datamarker column for values ".."

# +
tab = all_tabs["5. NUTS3, destination"]

tab_title = "5_nuts3_destination_trade_value"
tab_columns = ["Year", "NUTS3", "NUTS3 Area", "Destination", "Measure Type", "Unit"]
trace.start(tab_title, tab, tab_columns, scraper.distributions[0].downloadURL)


year = "2018"
trace.Year("Hardcoded but could have been taken from tab title (cell A1)")

nuts3 = tab.excel_ref("A4:A507").is_not_blank()
trace.NUTS3("Selected as all non-blank values between cell refs A4 and A507")

nuts3_area = tab.excel_ref("B4").expand(DOWN).is_not_blank()
trace.NUTS3_Area("Selected as all non-blank values from cell ref B4 down.")

destination = tab.excel_ref("E3:G3").is_not_blank()
trace.Destination("Selected as all non-blank values between cell ref E3 and G3 going right/across.")

measure_type = tab.excel_ref("D4").expand(DOWN).is_not_blank()
trace.Measure_Type("Selected as all non-blank values from cell ref D4 down.")

unit = "£ millions"
trace.Unit("Hardcoded but could have been taken from cell A2")


observations = tab.excel_ref("E4:G4").expand(DOWN).is_not_blank()

dimensions = [
    HDimConst("Year", year),
    HDim(nuts3, "NUTS3", CLOSEST, ABOVE),
    HDim(nuts3_area, "NUTS3 Area", CLOSEST, ABOVE),
    HDim(destination, "Destination", DIRECTLY, ABOVE),
    HDim(measure_type, "Measure Type", DIRECTLY, LEFT),
    HDimConst("Unit", unit)
]

tidy_sheet = ConversionSegment(tab, dimensions, observations)
trace.with_preview(tidy_sheet)
#savepreviewhtml(tidy_sheet)
trace.store("combined_" + tab_title, tidy_sheet.topandas())

df = trace.combine_and_trace(tab_title, "combined_" + tab_title)
df.rename(columns={'OBS' : 'Value'}, inplace=True)
trace.render()

tidied = df[["Year", "NUTS3", "NUTS3 Area", "Destination", "Measure Type", "Unit", "Value"]]
tidied_sheets.append(tidied)

#pd.set_option("display.max_rows", None, "display.max_columns", None)
#tidied_sheets[4]

#Notes:
    #Will need a datamarker column for values ".."

# +
tab = all_tabs["5. NUTS3, destination"]

tab_title = "5_nuts3_destination_percentage"
tab_columns = ["Year", "NUTS3", "NUTS3 Area", "Import Export", "Measure Type", "Unit"]
trace.start(tab_title, tab, tab_columns, scraper.distributions[0].downloadURL)


year = "2018"
trace.Year("Hardcoded but could have been taken from tab title (cell A1)")

nuts3 = tab.excel_ref("A4:A507").is_not_blank()
trace.NUTS3("Selected as all non-blank values between cell refs A4 and A507")

nuts3_area = tab.excel_ref("B4").expand(DOWN).is_not_blank()
trace.NUTS3_Area("Selected as all non-blank values from cell ref B5 down.")

imp_exp = tab.excel_ref("D4").expand(DOWN).is_not_blank()
trace.Import_Export("Selected as all non-blank values from cell ref D4 down.")

measure_type = tab.excel_ref("H3")
trace.Measure_Type("Selected as all non-blank values from cell ref D4 down.")

unit = "Percentage (%)"
trace.Unit("Hardcoded but could have been taken from cell A2")


observations = tab.excel_ref("H4").expand(DOWN).is_not_blank()

dimensions = [
    HDimConst("Year", year),
    HDim(nuts3, "NUTS3", CLOSEST, ABOVE),
    HDim(nuts3_area, "NUTS3 Area", CLOSEST, ABOVE),
    HDim(imp_exp, "Import/Export", DIRECTLY, LEFT),
    HDim(measure_type, "Measure Type", DIRECTLY, ABOVE),
    HDimConst("Unit", unit)
]

tidy_sheet = ConversionSegment(tab, dimensions, observations)
trace.with_preview(tidy_sheet)
#savepreviewhtml(tidy_sheet)
trace.store("combined_" + tab_title, tidy_sheet.topandas())

df = trace.combine_and_trace(tab_title, "combined_" + tab_title)
df.rename(columns={'OBS' : 'Value'}, inplace=True)
trace.render()

tidied = df[["Year", "NUTS3", "NUTS3 Area", "Import/Export", "Measure Type", "Unit", "Value"]]
tidied_sheets.append(tidied)

#pd.set_option("display.max_rows", None, "display.max_columns", None)
#tidied_sheets[5]

#Notes:
    #Will need a datamarker column for values ".."

# +
tab = all_tabs["6. City Region, industry"]

tab_title = "6_city_region_industry"
tab_columns = ["Year", "City_Region_Name", "Industry", "Measure Type", "Unit"]
trace.start(tab_title, tab, tab_columns, scraper.distributions[0].downloadURL)


year = "2018"
trace.Year("Hardcoded but could have been taken from tab title (cell A1)")

city_region_name = tab.excel_ref("A4:A48").is_not_blank()
trace.City_Region_Name("Selected as all non-blank values between cell refs A4 and A48")

industry = tab.excel_ref("C3").expand(RIGHT).is_not_blank()
trace.Industry("Selected as all non-blank values from cell ref C3 going right/across.")

measure_type = tab.excel_ref("B4").expand(DOWN).is_not_blank()
trace.Measure_Type("Selected as all non-blank values from cell ref B4 down.")

unit = "£ millions"
trace.Unit("Hardcoded but could have been taken from cell A2")


observations = tab.excel_ref("C4").expand(RIGHT).expand(DOWN).is_not_blank()

dimensions = [
    HDimConst("Year", year),
    HDim(city_region_name, "City Region Name", CLOSEST, ABOVE),
    HDim(industry, "Industry", DIRECTLY, ABOVE),
    HDim(measure_type, "Measure Type", DIRECTLY, LEFT),
    HDimConst("Unit", unit)
]

tidy_sheet = ConversionSegment(tab, dimensions, observations)
trace.with_preview(tidy_sheet)
#savepreviewhtml(tidy_sheet)
trace.store("combined_" + tab_title, tidy_sheet.topandas())

df = trace.combine_and_trace(tab_title, "combined_" + tab_title)
df.rename(columns={'OBS' : 'Value'}, inplace=True)
trace.render()

tidied = df[["Year", "City Region Name", "Industry", "Measure Type", "Unit", "Value"]]
tidied_sheets.append(tidied)
        
#pd.set_option("display.max_rows", None, "display.max_columns", None)
#tidied_sheets[6]

#Notes:
    #Will need a datamarker column for values ".."

# +
tab = all_tabs["7. City Region, industry, dest."]

tab_title = "7_city_region_dest"
tab_columns = ["Year", "City Region Name", "Industry", "Destination", "Measure Type", "Unit"]
trace.start(tab_title, tab, tab_columns, scraper.distributions[0].downloadURL)


year = "2018"
trace.Year("Hardcoded but could have been taken from tab title (cell A1)")

city_region_name = tab.excel_ref("A5:A49").is_not_blank()
trace.City_Region_Name("Selected as all non-blank values between cell refs A5 and A48")

industry = tab.excel_ref("C3").expand(RIGHT).is_not_blank()
trace.Industry("Selected as all non-blank values from cell ref C3 going right/across.")

destination = tab.excel_ref("C4").expand(RIGHT).is_not_blank()
trace.Destination("Selected as all non-blank values from cell ref C4 going right/across.")

measure_type = tab.excel_ref("B5").expand(DOWN).is_not_blank()
trace.Measure_Type("Selected as all non-blank values from cell ref B5 down.")

unit = "£ millions"
trace.Unit("Hardcoded but could have been taken from cell A2")


observations = tab.excel_ref("C5").expand(RIGHT).expand(DOWN).is_not_blank()

dimensions = [
    HDimConst("Year", year),
    HDim(city_region_name, "City Region Name", CLOSEST, ABOVE),
    HDim(industry, "Industry", CLOSEST, LEFT),
    HDim(destination, "Destination", DIRECTLY, ABOVE),
    HDim(measure_type, "Measure Type", DIRECTLY, LEFT),
    HDimConst("Unit", unit)
]

tidy_sheet = ConversionSegment(tab, dimensions, observations)
trace.with_preview(tidy_sheet)
#savepreviewhtml(tidy_sheet)
trace.store("combined_" + tab_title, tidy_sheet.topandas())

df = trace.combine_and_trace(tab_title, "combined_" + tab_title)
df.rename(columns={'OBS' : 'Value'}, inplace=True)
trace.render()

tidied = df[["Year", "City Region Name", "Industry", "Destination", "Measure Type", "Unit", "Value"]]
tidied_sheets.append(tidied)

#pd.set_option("display.max_rows", None, "display.max_columns", None)
#tidied_sheets[7]

#Notes:
    #Will need a datamarker column for values ".."

# +
tab = all_tabs["8. Travel"]

tab_title = "8_travel"
tab_columns = ["Year", "NUTS1 Area", "Travel Type", "Origin", "Measure Type", "Unit"]
trace.start(tab_title, tab, tab_columns, scraper.distributions[0].downloadURL)


year = "2018"
trace.Year("Hardcoded but could have been taken from tab title (cell A1)")

nuts1_area = tab.excel_ref("A5:A17").is_not_blank()
trace.NUTS1_Area("Selected as all non-blank values between cell refs A5 and A17")

travel_type = tab.excel_ref("B3").expand(RIGHT).is_not_blank()
trace.Travel_Type("Selected as all non-blank values from cell ref B3 going right/across.")

origin = tab.excel_ref("B4").expand(RIGHT).is_not_blank()
trace.Origin("Selected as all non-blank values from cell ref B4 going right/across.")

measure_type = "Travel-Related Service Imports Value"
trace.Measure_Type("Hardcoded but could have been taken from cell A1")

unit = "£ millions"
trace.Unit("Hardcoded but could have been taken from cell A2")


observations = tab.excel_ref("B5").expand(RIGHT).expand(DOWN).is_not_blank()

dimensions = [
    HDimConst("Year", year),
    HDim(nuts1_area, "NUTS1 Area", CLOSEST, ABOVE),
    HDim(travel_type, "Travel Type", CLOSEST, LEFT),
    HDim(origin, "Origin", DIRECTLY, ABOVE),
    HDimConst("Measure Type", measure_type),
    HDimConst("Unit", unit)
]

tidy_sheet = ConversionSegment(tab, dimensions, observations)
trace.with_preview(tidy_sheet)
#savepreviewhtml(tidy_sheet)
trace.store("combined_" + tab_title, tidy_sheet.topandas())

df = trace.combine_and_trace(tab_title, "combined_" + tab_title)
df.rename(columns={'OBS' : 'Value'}, inplace=True)
trace.render()

tidied = df[["Year", "NUTS1 Area", "Travel Type", "Origin", "Measure Type", "Unit", "Value"]]
tidied_sheets.append(tidied)

#pd.set_option("display.max_rows", None, "display.max_columns", None)
#tidied_sheets[8]

#Notes:
    #Will need a datamarker column for values ".."

# +
tab = all_tabs["9. Tidy format"]

tidy_sheet_list = []
cs_list = [] 

tab_title = "8_tidy_format"
tab_columns = ["Year", "NUTS Level", "NUTS Code", "NUTS Area Name", "Industry Grouping", "Country or Origin of Trade", "Direction of Trade", "Measure Type", "Unit"]
trace.start(tab_title, tab, tab_columns, scraper.distributions[0].downloadURL)

tab_length = len(tab.excel_ref('B')) # number of rows of data
batch_number = 10 # iterates over this many rows at a time
number_of_iterations = math.ceil(tab_length/batch_number) # databaking will iterate this many times
            
for i in range(0, number_of_iterations):
    Min = str(5 + batch_number * i)
    Max = str(int(Min) + batch_number - 1)

    year = "2018"
    
    nuts_level = tab.excel_ref("A"+Min+":A"+Max).is_not_blank()
    
    nuts_code = tab.excel_ref("B"+Min+":B"+Max).is_not_blank()
    
    nuts_area_name = tab.excel_ref("C"+Min+":C"+Max).is_not_blank()
    
    industry_grouping = tab.excel_ref("D"+Min+":D"+Max).is_not_blank()
    
    trade_country_or_origin = tab.excel_ref("E"+Min+":E"+Max).is_not_blank()
    
    direction_of_trade = tab.excel_ref("F"+Min+":F"+Max).is_not_blank()
    
    measure_type = "Trade in Services Total Value"
    
    unit = "£ millions"
    

    observations = tab.excel_ref("G"+Min+":G"+Max).is_not_blank()

    dimensions = [
        HDimConst("Year", year),
        HDim(nuts_level, "NUTS Level", CLOSEST, ABOVE),
        HDim(nuts_code, "NUTS Code", CLOSEST, ABOVE),
        HDim(nuts_area_name, "NUTS Area Name", CLOSEST, ABOVE),
        HDim(industry_grouping, "Industry Grouping", CLOSEST, ABOVE),
        HDim(trade_country_or_origin, "Country or Origin of Trade", CLOSEST, ABOVE),
        HDim(direction_of_trade, "Direction of Trade", CLOSEST, ABOVE),
        HDimConst("Measure Type", measure_type),
        HDimConst("Unit", unit)
    ]

    if len(observations) != 0: # only use ConversionSegment if there is data
        cs_iteration = ConversionSegment(tab, dimensions, observations) # creating the conversionsegment
        tidy_sheet_iteration = cs_iteration.topandas() # turning conversionsegment into a pandas dataframe
        cs_list.append(cs_iteration) # add to list
        tidy_sheet_list.append(tidy_sheet_iteration) # add to list
                    
tidy_sheet = pd.concat(tidy_sheet_list, sort=False) # dataframe for the whole tab

trace.Year("Hardcoded but could have been taken from tab title (cell A1)")
trace.NUTS_Level("Selected as all non-blank values between cell refs A5 and A7693")
trace.NUTS_Code("Selected as all non-blank values from cell ref B5 going down.")
trace.NUTS_Area_Name("Selected as all non-blank values from cell ref C5 going down.")
trace.Industry_Grouping("Selected as all non-blank values from cell ref D5 going down.")
trace.Country_or_Origin_of_Trade("Selected as all non-blank values from cell ref E5 going down.")
trace.Direction_of_Trade("Selected as all non-blank values from cell ref F5 going down.")
trace.Measure_Type("Hardcoded but could have been taken from cell A1")
trace.Unit("Hardcoded but could have been taken from cell A2")

trace.store("combined_" + tab_title, tidy_sheet)

df = trace.combine_and_trace(tab_title, "combined_" + tab_title)
df.rename(columns={'OBS' : 'Value'}, inplace=True)
trace.render()

tidied = df[["Year", "NUTS Level", "NUTS Code", "NUTS Area Name", "Industry Grouping", "Country or Origin of Trade", "Direction of Trade", "Measure Type", "Unit", "Value"]]
tidied_sheets.append(tidied)

#pd.set_option("display.max_rows", None, "display.max_columns", None)
#tidied_sheets[9]

#Notes:
    #Will need a datamarker column for values ".."
# -

#Outputs:
    #tidied_sheets[0] = Total value of trade in services (including travel) in the UK by NUTS1 area and industry, 2018
    #tidied_sheets[1] = Total value of trade in services (including travel) in the UK by NUTS1 area, industry and destination, 2018
    #tidied_sheets[2] = Total value of trade in services (excluding travel) in Great Britain by NUTS2 area and industry group, 2018 
    #tidied_sheets[3] = Total value of trade in services (excluding travel) in Great Britain by NUTS2 area, broad industry group and destination, 2018
    #tidied_sheets[4] = Total value of trade in services (excluding travel) in Great Britain by NUTS3 area and destination, 2018 - Trade Value
    #tidied_sheets[5] = Total value of trade in services (excluding travel) in Great Britain by NUTS3 area and destination, 2018 - EU Trade Percentage
    #tidied_sheets[6] = Total value of trade in services (excluding travel) in Great Britain by City Region and industry, 2018
    #tidied_sheets[7] = Total value of trade in services (excluding travel) in Great Britain by City Region, industry and destination, 2018
    #tidied_sheets[8] = Total value of travel-related service imports to the UK by NUTS1 area and country of origin, 2018
    #tidied_sheets[9] = Total value of trade in services in tidy format, 2018