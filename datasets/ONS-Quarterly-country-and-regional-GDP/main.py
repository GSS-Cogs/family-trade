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


def find_whitespace(start_cell):
    col = tab.excel_ref(start_cell).expand(DOWN).is_not_blank()
    limits = []
    for n in col:
        n_str = cell_to_string(n)
        if len(n_str) > 13:
            limits.append(n)
            
    return limits


def get_rows(limits):
    rows = []
    for cell in limits:
        as_str = str(cell)
        start = as_str.find("A") + len("'")
        end = as_str.find(" ")
        row = as_str[start:end]
        rows.append(row)
        
    return rows


# +
#### Distribution 1: Quarterly country and regional GDP - 31.07.2020

distribution_date = "31_07_2020" # Hardcoded but could have been extracted from the contents page ("B3").

for tab in scraper.distributions[0].as_databaker():
    
    table_cs_list = []
    table_tidy_sheet_list = []
    
    if tab.name == "Contents":
        continue
    
    else:
        tab_title = cell_to_string(tab.excel_ref("A2")) + " " + cell_to_string(tab.excel_ref("A3")) + " - " + tab.name#Remove Supers. This may be able to be hardcoded for each tab/distribution
        if tab.name == "Key Figures":   
            tab_columns = ["Period", "Region", "Section", "Measure Type", "Unit"]
            
        else:
            tab_columns = ["Period", "Region", "Sector", "Section", "Measure Type", "Unit"]
            
        trace.start(tab_title, tab, tab_columns, scraper.distributions[0].downloadURL)
        
        if tab.name == "Key Figures":
            region = tab.excel_ref("B5").expand(RIGHT).is_not_blank()
            trace.Region("Selected as all non-blank values from cell ref B5 going right/across.")
            
        else:
            region = tab.name
            trace.Region("Selected as the tab name.") 
            
            sector = tab.excel_ref("B5").expand(RIGHT).is_not_blank()
            trace.Sector("Selected as all non-blank values from cell ref B5 going right/across.")
            
        section = tab.excel_ref("B6").expand(RIGHT).is_not_blank()
        trace.Section("Selected as all non-blank values from cell ref B6 going down")
        
        limits = find_whitespace("A8")
        rows = get_rows(limits)
        for i in range(0, 5):
            cell_min = int(rows[i]) + 1
            cell_max = int(rows[i+1]) - 1
            
            period = tab.excel_ref("A"+str(cell_min)+":A"+str(cell_max)).is_not_blank()
            
            measure_type = tab.excel_ref("A"+rows[i])
            
            #unit = NOT SURE WHAT THE UNIT IS FOR EACH (other than percentage)
            
            if tab.name == "Key Figures":
                observations = tab.excel_ref("B"+str(cell_min)+":M"+str(cell_max)).is_not_blank()
                
            else:
                observations = tab.excel_ref("B"+str(cell_min)+":X"+str(cell_max)).is_not_blank()
            
            
            if tab.name == "Key Figures":                
                dimensions = [
                    HDim(period, "Period", DIRECTLY, LEFT),
                    HDim(region, "Region", DIRECTLY, ABOVE),
                    HDim(section, "Section", DIRECTLY, ABOVE),
                    HDim(measure_type, "Measure Type", CLOSEST, ABOVE)
                ]
                
            else:                
                dimensions = [
                    HDim(period, "Period", DIRECTLY, LEFT),
                    HDimConst("Region", region),
                    HDim(sector, "Sector", DIRECTLY, ABOVE),
                    HDim(section, "Section", DIRECTLY, ABOVE),
                    HDim(measure_type, "Measure Type", CLOSEST, ABOVE)
                ]
                
            table_cs_iteration = ConversionSegment(tab, dimensions, observations)
            table_iteration = table_cs_iteration.topandas()
            table_cs_list.append(table_cs_iteration)
            table_tidy_sheet_list.append(table_iteration)
            
        table_tidy_sheet = pd.concat(table_tidy_sheet_list, sort=False)
        
        trace.Period("Selected as all non-blank values from cell contaning last recorded measure type going down until a new measure type is found in column A.")
        trace.Period("Selected as the next value from the rows list.")
        
        trace.store("combined_" + tab.name + "_" + distribution_date, table_tidy_sheet)
        
        df = trace.combine_and_trace(tab_title, "combined_" + tab.name + "_" + distribution_date)
        df.rename(columns={'OBS' : 'Value'}, inplace=True)
        trace.render()
        
        if tab.name == "Key Figures":
            tidied = df[["Period", "Region", "Section", "Measure Type", "Value"]]
            
        else:
            tidied = df[["Period", "Region", "Sector", "Section", "Measure Type", "Value"]]
            
        tidied_sheets.append(tidied)
        
#pd.set_option("display.max_rows", None, "display.max_columns", None)

#tidied_sheets


# +
#### Distribution 2: Quarterly country and regional GDP - 01.05.2020

distribution_date = "01_05_2020" # Hardcoded but could have been extracted from the contents page ("B3").

for tab in scraper.distributions[1].as_databaker():
    
    table_cs_list = []
    table_tidy_sheet_list = []
    
    if tab.name == "Contents":
        continue
    
    else:
        tab_title = cell_to_string(tab.excel_ref("A2")) + " " + cell_to_string(tab.excel_ref("A3")) + " - " + tab.name#Remove Supers. This may be able to be hardcoded for each tab/distribution
        if tab.name == "Key Figures":   
            tab_columns = ["Period", "Region", "Section", "Measure Type", "Unit"]
            
        else:
            tab_columns = ["Period", "Region", "Sector", "Section", "Measure Type", "Unit"]
            
        trace.start(tab_title, tab, tab_columns, scraper.distributions[1].downloadURL)
        
        if tab.name == "Key Figures":
            region = tab.excel_ref("B5").expand(RIGHT).is_not_blank()
            trace.Region("Selected as all non-blank values from cell ref B5 going right/across.")
            
        else:
            region = tab.name
            trace.Region("Selected as the tab name.")            
            
            sector = tab.excel_ref("B5").expand(RIGHT).is_not_blank()
            trace.Sector("Selected as all non-blank values from cell ref B5 going right/across.")
        
        section = tab.excel_ref("B6").expand(RIGHT).is_not_blank()
        trace.Section("Selected as all non-blank values from cell ref B6 going down")
        
        limits = find_whitespace("A8")
        rows = get_rows(limits)
        for i in range(0, 5):
            cell_min = int(rows[i]) + 1
            cell_max = int(rows[i+1]) - 1
            
            period = tab.excel_ref("A"+str(cell_min)+":A"+str(cell_max)).is_not_blank()
            
            measure_type = tab.excel_ref("A"+rows[i])
            
            #unit = NOT SURE WHAT THE UNIT IS FOR EACH (other than percentage)
            
            if tab.name == "Key Figures":
                observations = tab.excel_ref("B"+str(cell_min)+":M"+str(cell_max)).is_not_blank()
                
            else:
                observations = tab.excel_ref("B"+str(cell_min)+":X"+str(cell_max)).is_not_blank()
            
            
            if tab.name == "Key Figures":                
                dimensions = [
                    HDim(period, "Period", DIRECTLY, LEFT),
                    HDim(region, "Region", DIRECTLY, ABOVE),
                    HDim(section, "Section", DIRECTLY, ABOVE),
                    HDim(measure_type, "Measure Type", CLOSEST, ABOVE)
                ]
                
            else:                
                dimensions = [
                    HDim(period, "Period", DIRECTLY, LEFT),
                    HDimConst("Region", region),
                    HDim(sector, "Sector", DIRECTLY, ABOVE),
                    HDim(section, "Section", DIRECTLY, ABOVE),
                    HDim(measure_type, "Measure Type", CLOSEST, ABOVE)
                ]
                
            table_cs_iteration = ConversionSegment(tab, dimensions, observations)
            table_iteration = table_cs_iteration.topandas()
            table_cs_list.append(table_cs_iteration)
            table_tidy_sheet_list.append(table_iteration)
            
        table_tidy_sheet = pd.concat(table_tidy_sheet_list, sort=False)
        
        trace.Period("Selected as all non-blank values from cell contaning last recorded measure type going down until a new measure type is found in column A.")
        trace.Period("Selected as the next value from the rows list.")
        
        trace.store("combined_" + tab.name + "_" + distribution_date, table_tidy_sheet)
        
        df = trace.combine_and_trace(tab_title, "combined_" + tab.name + "_" + distribution_date)
        df.rename(columns={'OBS' : 'Value'}, inplace=True)
        trace.render()
        
        if tab.name == "Key Figures":
            tidied = df[["Period", "Region", "Section", "Measure Type", "Value"]]
            
        else:
            tidied = df[["Period", "Region", "Sector", "Section", "Measure Type", "Value"]]
            
        tidied_sheets.append(tidied)
        
#pd.set_option("display.max_rows", None, "display.max_columns", None)

#tidied_sheets

# +
#### Distribution 3: Quarterly country and regional GDP - 07.02.2020

distribution_date = "07_02_2020" # Hardcoded but could have been extracted from the contents page ("B3").

for tab in scraper.distributions[2].as_databaker():
    
    table_cs_list = []
    table_tidy_sheet_list = []
    
    if tab.name == "Contents":
        continue
    
    else:
        tab_title = cell_to_string(tab.excel_ref("A2")) + " " + cell_to_string(tab.excel_ref("A3")) + " - " + tab.name#Remove Supers. This may be able to be hardcoded for each tab/distribution
        if tab.name == "Key Figures":   
            tab_columns = ["Period", "Region", "Section", "Measure Type", "Unit"]
            
        else:
            tab_columns = ["Period", "Region", "Sector", "Section", "Measure Type", "Unit"]
            
        trace.start(tab_title, tab, tab_columns, scraper.distributions[2].downloadURL)
        
        if tab.name == "Key Figures":
            region = tab.excel_ref("B5").expand(RIGHT).is_not_blank()
            trace.Region("Selected as all non-blank values from cell ref B5 going right/across.")
            
        else:
            region = tab.name
            trace.Region("Selected as the tab name.")
            
            sector = tab.excel_ref("B5").expand(RIGHT).is_not_blank()
            trace.Sector("Selected as all non-blank values from cell ref B5 going right/across.")
        
        section = tab.excel_ref("B6").expand(RIGHT).is_not_blank()
        trace.Section("Selected as all non-blank values from cell ref B6 going down")
        
        limits = find_whitespace("A8")
        rows = get_rows(limits)
        for i in range(0, 5):
            cell_min = int(rows[i]) + 1
            cell_max = int(rows[i+1]) - 1
            
            period = tab.excel_ref("A"+str(cell_min)+":A"+str(cell_max)).is_not_blank()
            
            measure_type = tab.excel_ref("A"+rows[i])
            
            #unit = NOT SURE WHAT THE UNIT IS FOR EACH (other than percentage)
            
            if tab.name == "Key Figures":
                observations = tab.excel_ref("B"+str(cell_min)+":M"+str(cell_max)).is_not_blank()
                
            else:
                observations = tab.excel_ref("B"+str(cell_min)+":X"+str(cell_max)).is_not_blank()
            
            
            if tab.name == "Key Figures":                
                dimensions = [
                    HDim(period, "Period", DIRECTLY, LEFT),
                    HDim(region, "Region", DIRECTLY, ABOVE),
                    HDim(section, "Section", DIRECTLY, ABOVE),
                    HDim(measure_type, "Measure Type", CLOSEST, ABOVE)
                ]
                
            else:                
                dimensions = [
                    HDim(period, "Period", DIRECTLY, LEFT),
                    HDimConst("Region", region),
                    HDim(sector, "Sector", DIRECTLY, ABOVE),
                    HDim(section, "Section", DIRECTLY, ABOVE),
                    HDim(measure_type, "Measure Type", CLOSEST, ABOVE)
                ]
                
            table_cs_iteration = ConversionSegment(tab, dimensions, observations)
            table_iteration = table_cs_iteration.topandas()
            table_cs_list.append(table_cs_iteration)
            table_tidy_sheet_list.append(table_iteration)
            
        table_tidy_sheet = pd.concat(table_tidy_sheet_list, sort=False)
        
        trace.Period("Selected as all non-blank values from cell contaning last recorded measure type going down until a new measure type is found in column A.")
        trace.Period("Selected as the next value from the rows list.")
        
        trace.store("combined_" + tab.name + "_" + distribution_date, table_tidy_sheet)
        
        df = trace.combine_and_trace(tab_title, "combined_" + tab.name + "_" + distribution_date)
        df.rename(columns={'OBS' : 'Value'}, inplace=True)
        trace.render()
        
        if tab.name == "Key Figures":
            tidied = df[["Period", "Region", "Section", "Measure Type", "Value"]]
            
        else:
            tidied = df[["Period", "Region", "Sector", "Section", "Measure Type", "Value"]]
            
        tidied_sheets.append(tidied)
        
#pd.set_option("display.max_rows", None, "display.max_columns", None)

#tidied_sheets

# +
#### Distribution 4: Quarterly country and regional GDP - 30.10.2019

distribution_date = "30_10_2019" # Hardcoded but could have been extracted from the contents page ("B3").

for tab in scraper.distributions[3].as_databaker():
    
    table_cs_list = []
    table_tidy_sheet_list = []
    
    if tab.name == "Information":
        continue
    
    else:
        tab_title = cell_to_string(tab.excel_ref("A2")) + " " + cell_to_string(tab.excel_ref("A3")) + " - " + tab.name#Remove Supers. This may be able to be hardcoded for each tab/distribution
        if tab.name == "Key Figures":   
            tab_columns = ["Period", "Region", "Section", "Measure Type", "Unit"]
            
        else:
            tab_columns = ["Period", "Region", "Sector", "Section", "Measure Type", "Unit"]
            
        trace.start(tab_title, tab, tab_columns, scraper.distributions[3].downloadURL)
        
        if tab.name == "Key Figures":
            region = tab.excel_ref("B4").expand(RIGHT).is_not_blank()
            trace.Region("Selected as all non-blank values from cell ref B5 going right/across.")
            
        else:
            region = tab.name
            trace.Region("Selected as the tab name.")            
            
            sector = tab.excel_ref("B4").expand(RIGHT).is_not_blank()
            trace.Sector("Selected as all non-blank values from cell ref B5 going right/across.")
        
        section = tab.excel_ref("B5").expand(RIGHT).is_not_blank()
        trace.Section("Selected as all non-blank values from cell ref B6 going down")
        
        limits = find_whitespace("A7")
        rows = get_rows(limits)
        for i in range(0, 3):
            cell_min = int(rows[i]) + 1
            cell_max = int(rows[i+1]) - 1
            
            period = tab.excel_ref("A"+str(cell_min)+":A"+str(cell_max)).is_not_blank()
            
            measure_type = tab.excel_ref("A"+rows[i])
            
            #unit = NOT SURE WHAT THE UNIT IS FOR EACH (other than percentage)
            
            if tab.name == "Key Figures":
                observations = tab.excel_ref("B"+str(cell_min)+":M"+str(cell_max)).is_not_blank()
                
            else:
                observations = tab.excel_ref("B"+str(cell_min)+":X"+str(cell_max)).is_not_blank()
            
            
            if tab.name == "Key Figures":                
                dimensions = [
                    HDim(period, "Period", DIRECTLY, LEFT),
                    HDim(region, "Region", DIRECTLY, ABOVE),
                    HDim(section, "Section", DIRECTLY, ABOVE),
                    HDim(measure_type, "Measure Type", CLOSEST, ABOVE)
                ]
                
            else:                
                dimensions = [
                    HDim(period, "Period", DIRECTLY, LEFT),
                    HDimConst("Region", region),
                    HDim(sector, "Sector", DIRECTLY, ABOVE),
                    HDim(section, "Section", DIRECTLY, ABOVE),
                    HDim(measure_type, "Measure Type", CLOSEST, ABOVE)
                ]
                
            table_cs_iteration = ConversionSegment(tab, dimensions, observations)
            table_iteration = table_cs_iteration.topandas()
            table_cs_list.append(table_cs_iteration)
            table_tidy_sheet_list.append(table_iteration)
            
        table_tidy_sheet = pd.concat(table_tidy_sheet_list, sort=False)
        
        trace.Period("Selected as all non-blank values from cell contaning last recorded measure type going down until a new measure type is found in column A.")
        trace.Period("Selected as the next value from the rows list.")
        
        trace.store("combined_" + tab.name + "_" + distribution_date, table_tidy_sheet)
        
        df = trace.combine_and_trace(tab_title, "combined_" + tab.name + "_" + distribution_date)
        df.rename(columns={'OBS' : 'Value'}, inplace=True)
        trace.render()
        
        if tab.name == "Key Figures":
            tidied = df[["Period", "Region", "Section", "Measure Type", "Value"]]
            
        else:
            tidied = df[["Period", "Region", "Sector", "Section", "Measure Type", "Value"]]
            
        tidied_sheets.append(tidied)
        
#pd.set_option("display.max_rows", None, "display.max_columns", None)

#tidied_sheets

# +
#### Distribution 5: Quarterly country and regional GDP - 05.09.2019

distribution_date = "05_09_2019" # Hardcoded but could have been extracted from the contents page ("B3").

for tab in scraper.distributions[4].as_databaker():
    
    table_cs_list = []
    table_tidy_sheet_list = []
    
    if tab.name == "Information":
        continue
    
    else:
        tab_title = cell_to_string(tab.excel_ref("A2")) + " " + cell_to_string(tab.excel_ref("A3")) + " - " + tab.name#Remove Supers. This may be able to be hardcoded for each tab/distribution
        if tab.name == "Key Figures":   
            tab_columns = ["Period", "Region", "Section", "Measure Type", "Unit"]
            
        else:
            tab_columns = ["Period", "Region", "Sector", "Section", "Measure Type", "Unit"]
            
        trace.start(tab_title, tab, tab_columns, scraper.distributions[4].downloadURL)
        
        if tab.name == "Key Figures":
            region = tab.excel_ref("B5").expand(RIGHT).is_not_blank()
            trace.Region("Selected as all non-blank values from cell ref B5 going right/across.")
            
        else:
            region = tab.name
            trace.Region("Selected as the tab name.")            
            
            sector = tab.excel_ref("B5").expand(RIGHT).is_not_blank()
            trace.Sector("Selected as all non-blank values from cell ref B5 going right/across.")
            
        section = tab.excel_ref("B6").expand(RIGHT).is_not_blank()
        trace.Section("Selected as all non-blank values from cell ref B6 going down")
        
        limits = find_whitespace("A8")
        rows = get_rows(limits)
        for i in range(0, 5):
            cell_min = int(rows[i]) + 1
            cell_max = int(rows[i+1]) - 1
            
            period = tab.excel_ref("A"+str(cell_min)+":A"+str(cell_max)).is_not_blank()
            
            measure_type = tab.excel_ref("A"+rows[i])
            
            #unit = NOT SURE WHAT THE UNIT IS FOR EACH (other than percentage)
            
            if tab.name == "Key Figures":
                observations = tab.excel_ref("B"+str(cell_min)+":M"+str(cell_max)).is_not_blank()
                
            else:
                observations = tab.excel_ref("B"+str(cell_min)+":X"+str(cell_max)).is_not_blank()
            
            
            if tab.name == "Key Figures":                
                dimensions = [
                    HDim(period, "Period", DIRECTLY, LEFT),
                    HDim(region, "Region", DIRECTLY, ABOVE),
                    HDim(section, "Section", DIRECTLY, ABOVE),
                    HDim(measure_type, "Measure Type", CLOSEST, ABOVE)
                ]
                
            else:                
                dimensions = [
                    HDim(period, "Period", DIRECTLY, LEFT),
                    HDimConst("Region", region),
                    HDim(sector, "Sector", DIRECTLY, ABOVE),
                    HDim(section, "Section", DIRECTLY, ABOVE),
                    HDim(measure_type, "Measure Type", CLOSEST, ABOVE)
                ]
                
            table_cs_iteration = ConversionSegment(tab, dimensions, observations)
            table_iteration = table_cs_iteration.topandas()
            table_cs_list.append(table_cs_iteration)
            table_tidy_sheet_list.append(table_iteration)
            
        table_tidy_sheet = pd.concat(table_tidy_sheet_list, sort=False)
        
        trace.Period("Selected as all non-blank values from cell contaning last recorded measure type going down until a new measure type is found in column A.")
        trace.Period("Selected as the next value from the rows list.")
        
        trace.store("combined_" + tab.name + "_" + distribution_date, table_tidy_sheet)
        
        df = trace.combine_and_trace(tab_title, "combined_" + tab.name + "_" + distribution_date)
        df.rename(columns={'OBS' : 'Value'}, inplace=True)
        trace.render()
        
        if tab.name == "Key Figures":
            tidied = df[["Period", "Region", "Section", "Measure Type", "Value"]]
            
        else:
            tidied = df[["Period", "Region", "Sector", "Section", "Measure Type", "Value"]]
            
        tidied_sheets.append(tidied)
        
#pd.set_option("display.max_rows", None, "display.max_columns", None)

#tidied_sheets

# +
# Outputs:
    #Distribution 1:
        #tidied_sheets[0:12]
        
    #Distribution 2:
        #tidied_sheets[13:25]

    #Distribution 3:
        #tidied_sheets[26:38]
        
    #Distribution 4:
        #tidied_sheets[39:51]
        
    #Distribution 5:
        #tidied_sheets[52:62]
        
#Notes:
    #Was unsure which values to assign as units as each tab contains multiple measures.
    #Each dataframe still contains multiple measures which I expect to break up in stage 2.
    #tab_title still contains superscripts.

# -




