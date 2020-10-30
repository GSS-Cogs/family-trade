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

tidied_sheets = []
trace = TransformTrace()
df = pd.DataFrame()


def cell_to_string(cell):
    s = str(cell)
    start = s.find("'") + len("'")
    end = s.find(">")
    substring = s[start:end].strip("'")
    return substring


# +
from pandas import ExcelWriter

counter = 0
all_tabs = []

for table in scraper.distributions:
    xls = pd.ExcelFile(scraper.distributions[counter].downloadURL)

    with ExcelWriter("data" + str(counter) + ".xls") as writer:
        for sheet in xls.sheet_names:
            
            if sheet == "Database (YR)" or sheet == "Database (QR)" or sheet == "Database (Regional Year)" or sheet == "Database (Regional Qtr)":
                pd.read_excel(xls, sheet).to_excel(writer,sheet)
            
            else:
                continue
                
        writer.save()
    
    tabs = loadxlstabs("data" + str(counter) + ".xls")
    all_tabs.append(tabs)
    counter += 1



# +
counter = 0
for table in all_tabs:
    for tab in table:
        
        tab_title = "data_" + str(counter) + "_" + tab.name
        tab_title = tab_title.replace(" ", "_")
        tab_title = tab_title.replace("(", "")
        tab_title = tab_title.replace(")", "")

        if "YR" in tab_title:
            tidy_sheet_list = []
            #tidy_sheet_iteration = []
            cs_list = [] 
            
            tab_columns = ["Year", "Code", "Region", "Country", "Measure Type", "Unit"]
            trace.start(tab_title, tab, tab_columns, scraper.distributions[counter].downloadURL)
            
            tab_length = len(tab.excel_ref('A')) # number of rows of data
            batch_number = 10 # iterates over this many rows at a time
            number_of_iterations = math.ceil(tab_length/batch_number) # databaking will iterate this many times
            
            for i in range(0, number_of_iterations):
                Min = str(3 + batch_number * i)
                Max = str(int(Min) + batch_number - 1)
            
                year = tab.excel_ref("C"+Min+":C"+Max).is_not_blank()

                code = tab.excel_ref("B"+Min+":B"+Max).is_not_blank()

                region = tab.excel_ref("D"+Min+":D"+Max).is_not_blank()

                country = tab.excel_ref("E"+Min+":E"+Max).is_not_blank()

                measure_type = tab.excel_ref("F2")

                unit = "Count"


                observations = tab.excel_ref("F"+Min+":F"+Max).is_not_blank()


                dimensions = [
                    HDim(year, "Year", CLOSEST, ABOVE),
                    HDim(code, "Code", CLOSEST, ABOVE),
                    HDim(region, "Region", CLOSEST, ABOVE),
                    HDim(country, "Country", DIRECTLY, LEFT),
                    HDim(measure_type, "Measure Type", DIRECTLY, ABOVE),
                    HDimConst("Unit", unit)
                ]
            
                if len(observations) != 0: # only use ConversionSegment if there is data
                    cs_iteration = ConversionSegment(tab, dimensions, observations) # creating the conversionsegment
                    tidy_sheet_iteration = cs_iteration.topandas() # turning conversionsegment into a pandas dataframe
                    cs_list.append(cs_iteration) # add to list
                    tidy_sheet_list.append(tidy_sheet_iteration) # add to list
                    
            tidy_sheet = pd.concat(tidy_sheet_list, sort=False) # dataframe for the whole tab
            
            trace.Year("Selected as all non-blank values from cell ref C3 going down.")
            trace.Code("Selected as all non-blank values from cell ref B3 going down.")
            trace.Region("Selected as all non-blank values from cell ref D3 going down.")
            trace.Country("Selected as all non-blank values from cell ref E3 going down.")
            trace.Measure_Type("Selected from cell ref F2.")
            trace.Unit("Hardcoded as 'Count'.")
            
            trace.store("combined_" + tab_title, tidy_sheet)

            df = trace.combine_and_trace(tab_title, "combined_" + tab_title)
            df.rename(columns={'OBS' : 'Value'}, inplace=True)
            trace.render()

            tidied = df[["Year", "Code", "Region", "Country", "Measure Type", "Unit", "Value"]]
            tidied_sheets.append(tidied)

            
        elif "QR" in tab_title:
            tidy_sheet_list = []
            #tidy_sheet_iteration = []
            cs_list = [] 
            
            tab_columns = ["Year", "Quarter", "Code", "Region", "Country", "Measure Type", "Unit"]
            trace.start(tab_title, tab, tab_columns, scraper.distributions[counter].downloadURL)
            
            tab_length = len(tab.excel_ref('A')) # number of rows of data
            batch_number = 10 # iterates over this many rows at a time
            number_of_iterations = math.ceil(tab_length/batch_number) # databaking will iterate this many times
            
            for i in range(0, number_of_iterations):
                Min = str(3 + batch_number * i)
                Max = str(int(Min) + batch_number - 1)
            
                year = tab.excel_ref("C"+Min+":C"+Max).is_not_blank()
                
                quarter = tab.excel_ref("D"+Min+":D"+Max).is_not_blank()

                code = tab.excel_ref("B"+Min+":B"+Max).is_not_blank()

                region = tab.excel_ref("E"+Min+":E"+Max).is_not_blank()

                country = tab.excel_ref("F"+Min+":F"+Max).is_not_blank()

                measure_type = tab.excel_ref("G2")

                unit = "Count"


                observations = tab.excel_ref("G"+Min+":G"+Max).is_not_blank()


                dimensions = [
                    HDim(year, "Year", CLOSEST, ABOVE),
                    HDim(quarter, "Quarter", CLOSEST, ABOVE),
                    HDim(code, "Code", CLOSEST, ABOVE),
                    HDim(region, "Region", CLOSEST, ABOVE),
                    HDim(country, "Country", DIRECTLY, LEFT),
                    HDim(measure_type, "Measure Type", DIRECTLY, ABOVE),
                    HDimConst("Unit", unit)
                ]
            
                if len(observations) != 0: # only use ConversionSegment if there is data
                    cs_iteration = ConversionSegment(tab, dimensions, observations) # creating the conversionsegment
                    tidy_sheet_iteration = cs_iteration.topandas() # turning conversionsegment into a pandas dataframe
                    cs_list.append(cs_iteration) # add to list
                    tidy_sheet_list.append(tidy_sheet_iteration) # add to list
                    
            tidy_sheet = pd.concat(tidy_sheet_list, sort=False) # dataframe for the whole tab
            
            trace.Year("Selected as all non-blank values from cell ref C3 going down.")
            trace.Quarter("Selected as all non-blank values from cell ref D3 going down.")
            trace.Code("Selected as all non-blank values from cell ref B3 going down.")
            trace.Region("Selected as all non-blank values from cell ref E3 going down.")
            trace.Country("Selected as all non-blank values from cell ref F3 going down.")
            trace.Measure_Type("Selected from cell ref G2.")
            trace.Unit("Hardcoded as 'Count'.")
                       
            trace.store("combined_" + tab_title, tidy_sheet)

            df = trace.combine_and_trace(tab_title, "combined_" + tab_title)
            df.rename(columns={'OBS' : 'Value'}, inplace=True)
            trace.render()

            tidied = df[["Year", "Quarter", "Code", "Region", "Country", "Measure Type", "Unit", "Value"]]
            tidied_sheets.append(tidied)        
        
        
        elif "Year" in tab_title:
            tidy_sheet_list = []
            #tidy_sheet_iteration = []
            cs_list = [] 
            
            tab_columns = ["Year", "Code", "Region", "Country", "Measure Type", "Unit"]
            trace.start(tab_title, tab, tab_columns, scraper.distributions[counter].downloadURL)
            
            tab_length = len(tab.excel_ref('A')) # number of rows of data
            batch_number = 10 # iterates over this many rows at a time
            number_of_iterations = math.ceil(tab_length/batch_number) # databaking will iterate this many times
            
            for i in range(0, number_of_iterations):
                Min = str(2 + batch_number * i)
                Max = str(int(Min) + batch_number - 1)
            
                year = tab.excel_ref("C"+Min+":C"+Max).is_not_blank()

                code = tab.excel_ref("B"+Min+":B"+Max).is_not_blank()

                region = tab.excel_ref("D"+Min+":D"+Max).is_not_blank()

                country = tab.excel_ref("E"+Min+":E"+Max).is_not_blank()

                measure_type = tab.excel_ref("F"+Min+":F"+Max).is_not_blank()
                
                for mt in measure_type:
                    str_mt = cell_to_string(mt)
                    if "Number" in str_mt:
                        unit = "Count"
                    
                    elif "billions" in str_mt:
                        unit = "£ billions"

                    elif "thousands" in str_mt:
                        unit = "£ thousands"
                        
                    else:
                        unit = "Error - unknown unit"

                observations = tab.excel_ref("G"+Min+":G"+Max).is_not_blank()


                dimensions = [
                    HDim(year, "Year", CLOSEST, ABOVE),
                    HDim(code, "Code", CLOSEST, ABOVE),
                    HDim(region, "Region", CLOSEST, ABOVE),
                    HDim(country, "Country", CLOSEST, ABOVE),
                    HDim(measure_type, "Measure Type", DIRECTLY, LEFT),
                    HDimConst("Unit", unit)
                ]
            
                if len(observations) != 0: # only use ConversionSegment if there is data
                    cs_iteration = ConversionSegment(tab, dimensions, observations) # creating the conversionsegment
                    tidy_sheet_iteration = cs_iteration.topandas() # turning conversionsegment into a pandas dataframe
                    cs_list.append(cs_iteration) # add to list
                    tidy_sheet_list.append(tidy_sheet_iteration) # add to list
                    
            tidy_sheet = pd.concat(tidy_sheet_list, sort=False) # dataframe for the whole tab
            
            trace.Year("Selected as all non-blank values from cell ref C3 going down.")
            trace.Code("Selected as all non-blank values from cell ref B3 going down.")
            trace.Region("Selected as all non-blank values from cell ref D3 going down.")
            trace.Country("Selected as all non-blank values from cell ref E3 going down.")
            trace.Measure_Type("Selected as all non-blank values from cell ref F3 going down.")
            trace.Unit("Hardcoded depending on the measure type in column F")
                       
            trace.store("combined_" + tab_title, tidy_sheet)

            df = trace.combine_and_trace(tab_title, "combined_" + tab_title)
            df.rename(columns={'OBS' : 'Value'}, inplace=True)
            trace.render()

            tidied = df[["Year", "Code", "Region", "Country", "Measure Type", "Unit", "Value"]]
            tidied_sheets.append(tidied)
            
            
        elif "Qtr" in tab_title:
            tidy_sheet_list = []
            #tidy_sheet_iteration = []
            cs_list = [] 
            
            tab_columns = ["Year", "Quarter", "Code", "Region", "Country", "Measure Type", "Unit"]
            trace.start(tab_title, tab, tab_columns, scraper.distributions[counter].downloadURL)
            
            tab_length = len(tab.excel_ref('A')) # number of rows of data
            batch_number = 10 # iterates over this many rows at a time
            number_of_iterations = math.ceil(tab_length/batch_number) # databaking will iterate this many times
            
            for i in range(0, number_of_iterations):
                Min = str(2 + batch_number * i)
                Max = str(int(Min) + batch_number - 1)
            
                year = tab.excel_ref("C"+Min+":C"+Max).is_not_blank()
                
                quarter = tab.excel_ref("D"+Min+":D"+Max).is_not_blank()

                code = tab.excel_ref("B"+Min+":B"+Max).is_not_blank()

                region = tab.excel_ref("E"+Min+":E"+Max).is_not_blank()

                country = tab.excel_ref("F"+Min+":F"+Max).is_not_blank()

                measure_type = tab.excel_ref("G"+Min+":G"+Max).is_not_blank()
                
                for mt in measure_type:
                    str_mt = cell_to_string(mt)
                    if "Number" in str_mt:
                        unit = "Count"
                    
                    elif "billions" in str_mt:
                        unit = "£ billions"

                    elif "thousands" in str_mt:
                        unit = "£ thousands"
                        
                    else:
                        unit = "Error - unknown unit"


                observations = tab.excel_ref("H"+Min+":H"+Max).is_not_blank()


                dimensions = [
                    HDim(year, "Year", CLOSEST, ABOVE),
                    HDim(quarter, "Quarter", CLOSEST, ABOVE),
                    HDim(code, "Code", CLOSEST, ABOVE),
                    HDim(region, "Region", CLOSEST, ABOVE),
                    HDim(country, "Country", CLOSEST, ABOVE),
                    HDim(measure_type, "Measure Type", DIRECTLY, LEFT),
                    HDimConst("Unit", unit)
                ]
            
                if len(observations) != 0: # only use ConversionSegment if there is data
                    cs_iteration = ConversionSegment(tab, dimensions, observations) # creating the conversionsegment
                    tidy_sheet_iteration = cs_iteration.topandas() # turning conversionsegment into a pandas dataframe
                    cs_list.append(cs_iteration) # add to list
                    tidy_sheet_list.append(tidy_sheet_iteration) # add to list
                    
            tidy_sheet = pd.concat(tidy_sheet_list, sort=False) # dataframe for the whole tab
            
            trace.Year("Selected as all non-blank values from cell ref C3 going down.")
            trace.Quarter("Selected as all non-blank values from cell ref D3 going down.")
            trace.Code("Selected as all non-blank values from cell ref B3 going down.")
            trace.Region("Selected as all non-blank values from cell ref E3 going down.")
            trace.Country("Selected as all non-blank values from cell ref F3 going down.")
            trace.Measure_Type("Selected as all non-blank values from cell ref G3 going down.")
            trace.Unit("Hardcoded depending on the measure type in column G")
                       
            trace.store("combined_" + tab_title, tidy_sheet)

            df = trace.combine_and_trace(tab_title, "combined_" + tab_title)
            df.rename(columns={'OBS' : 'Value'}, inplace=True)
            trace.render()

            tidied = df[["Year", "Quarter", "Code", "Region", "Country", "Measure Type", "Unit", "Value"]]
            tidied_sheets.append(tidied)
        
    counter += 1


# +
#Outputs:
    #See below
    
#Notes:
    #Transform takes a few minutes to run. Most time spent waiting for new .xls files to be written as tabs could not be loaded using either
    #databaker or pandas in the existing .xlsm format.
    
    #data0.xls = relevant tabs from distribution 1 : Exports using proportional business count method
    #data0.xls = relevant tabs from distribution 2 : Exports using whole number count method
    #data0.xls = relevant tabs from distribution 3 : Imports using proportional business count method
    #data0.xls = relevant tabs from distribution 4 : Imports using whole number count method
    


# +
#tidied_sheets[0] #data0.xls Database(YR)

# +
#tidied_sheets[1] #data0.xls Database(QR)

# +
#tidied_sheets[2] #Data0.xls Database(Regional Year)

# +
#tidied_sheets[3] #Data0.xls Database(Regional Qtr)

# +
#tidied_sheets[4] #Data1.xls Database(YR)

# +
#tidied_sheets[5] #Data1.xls Database(QR)

# +
#tidied_sheets[6] #Data1.xls Database(Regional Year)

# +
#tidied_sheets[7] #Data1.xls Database(Regional Qtr)

# +
#tidied_sheets[8] #Data2.xls Database(YR)

# +
#tidied_sheets[9] #Data2.xls Database(QR)

# +
#tidied_sheets[10] #Data2.xls Database(Regional Year)

# +
#tidied_sheets[11] #Data2.xls Database(Regional Qtr)

# +
#tidied_sheets[12] #Data3.xls Database(YR)

# +
#tidied_sheets[13] #Data3.xls Database(QR)

# +
#tidied_sheets[14] #Data3.xls Database(Regional Year)

# +
#tidied_sheets[15] #Data0.xls Database(Regional Qtr)
# -


