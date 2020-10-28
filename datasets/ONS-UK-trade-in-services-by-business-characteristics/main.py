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

for tab in scraper.distributions[0].as_databaker():
    
    if tab.name == "Contents":
        continue
        
    elif len(tab.name) > 4:
        tab_title = tab.name + "_ownership"
        
        tab_columns = ["Period", "Industry", "Ownership", "Measure Type", "Unit"]
        trace.start(tab_title, tab, tab_columns, scraper.distributions[0].downloadURL)
        
        
        period = tab.name[0:4]
        trace.Period("Selected from the tab title")
        
        industry = tab.excel_ref("A1").expand(DOWN).is_not_blank()
        trace.Industry("Selected as all non-blank values from cell ref A1 down.")
        
        ownership = tab.excel_ref("B1").expand(DOWN).is_not_blank()
        trace.Ownership("Selected as all non-blank values from cell ref B1 down.")
        
        measure_type = tab.excel_ref("C1:D1")
        trace.Measure_Type("Selected as the two values in cells C1 and D1")
        
        unit = "£m"
        trace.Unit("Hardcoded value but could have been taken from the measure types or from the contents page.")
        
        observations = tab.excel_ref("C2:D271").is_not_blank()
        
        dimensions = [
            HDimConst("Period", period),
            HDim(industry, "Industry", CLOSEST, ABOVE),
            HDim(ownership, "Ownership", DIRECTLY, LEFT),
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
        
        tidied = df[["Period", "Industry", "Ownership", "Measure Type", "Unit", "Value"]]
        tidied_sheets.append(tidied)
    
    else:
        markers = [["1", "8"], ["10", "19"], ["21", "33"]]
        
        for table in markers:
            if table == markers[0]:
                
                tab_title = tab.name + "_business_size_and_ownership"
            
                tab_columns = ["Period", "Business Size", "Ownership", "Measure Type", "Unit"]
                trace.start(tab_title, tab, tab_columns, scraper.distributions[0].downloadURL)
                
                
                period = tab.name[0:4]
                trace.Period("Selected from the tab title")
                
                business_size = tab.excel_ref("A"+table[0]+":A"+table[1]).is_not_blank()
                trace.Business_Size("Selected as all non-blank values between the cell refs using markers from the list.")
                
                ownership = tab.excel_ref("A"+table[0]+":A"+table[1]).is_not_blank()
                trace.Ownership("Selected as all non-blank values between the cell refs using markers from the list.")
                
                measure_type = tab.excel_ref("C1:D1")
                trace.Measure_Type("Selected as the two values in cells C1 and D1")
                
                unit = "£m"
                trace.Unit("Hardcoded value but could have been taken from the measure types or from the contents page.")
                
                observations = tab.excel_ref("C"+str(int(table[0])+1)+":D"+table[1]).is_not_blank()


                dimensions = [
                    HDimConst("Period", period),
                    HDim(business_size, "Business Size", CLOSEST, ABOVE),
                    HDim(ownership, "Ownership", DIRECTLY, LEFT),
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

                tidied = df[["Period", "Business Size", "Ownership", "Measure Type", "Unit", "Value"]]
                tidied_sheets.append(tidied)
                
            elif table == markers[1]:
                
                tab_title = tab.name + "_country_and_ownership"
                
                tab_columns = ["Period", "Country", "Ownership", "Measure Type", "Unit"]
                trace.start(tab_title, tab, tab_columns, scraper.distributions[0].downloadURL)
                
                
                period = tab.name[0:4]
                trace.Period("Selected from the tab title")
                
                country = tab.excel_ref("A"+table[0]+":A"+table[1]).is_not_blank()
                trace.Country("Selected as all non-blank values between the cell refs using markers from the list.")
                
                ownership = tab.excel_ref("A"+table[0]+":A"+table[1]).is_not_blank()
                trace.Ownership("Selected as all non-blank values between the cell refs using markers from the list.")
                
                measure_type = tab.excel_ref("C1:D1")
                trace.Measure_Type("Selected as the two values in cells C1 and D1")
                
                unit = "£m"
                trace.Unit("Hardcoded value but could have been taken from the measure types or from the contents page.")
                
                observations = tab.excel_ref("C"+str(int(table[0])+1)+":D"+table[1]).is_not_blank()
                
                
                dimensions = [
                    HDimConst("Period", period),
                    HDim(country, "Country", CLOSEST, ABOVE),
                    HDim(ownership, "Ownership", DIRECTLY, LEFT),
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

                tidied = df[["Period", "Country", "Ownership", "Measure Type", "Unit", "Value"]]
                tidied_sheets.append(tidied)
                
            elif table == markers[2]:
                tab_title = tab.name + "_country_and_business_size"
                
                tab_columns = ["Period", "Country", "Business Size", "Measure Type", "Unit"]
                trace.start(tab_title, tab, tab_columns, scraper.distributions[0].downloadURL)
                
                
                period = tab.name[0:4]
                trace.Period("Selected from the tab title")
                
                country = tab.excel_ref("A"+table[0]+":A"+table[1]).is_not_blank()
                trace.Country("Selected as all non-blank values between the cell refs using markers from the list.")
                
                business_size = tab.excel_ref("A"+table[0]+":A"+table[1]).is_not_blank()
                trace.Business_Size("Selected as all non-blank values between the cell refs using markers from the list.")
                
                measure_type = tab.excel_ref("C1:D1")
                trace.Measure_Type("Selected as the two values in cells C1 and D1")
                
                unit = "£m"
                trace.Unit("Hardcoded value but could have been taken from the measure types or from the contents page.")
                
                observations = tab.excel_ref("C"+str(int(table[0])+1)+":D"+table[1]).is_not_blank()
                
                
                dimensions = [
                    HDimConst("Period", period),
                    HDim(country, "Country", CLOSEST, ABOVE),
                    HDim(business_size, "Business Size", CLOSEST, ABOVE),
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

                tidied = df[["Period", "Country", "Business Size", "Measure Type", "Unit", "Value"]]
                tidied_sheets.append(tidied)


# +
for tab in scraper.distributions[0].as_databaker():
    
    if tab.name == "Contents":
        continue
        
    elif len(tab.name) > 4:
        tab_title = tab.name + "_business_size"
        
        tab_columns = ["Period", "Industry", "Business Size", "Measure Type", "Unit"]
        trace.start(tab_title, tab, tab_columns, scraper.distributions[0].downloadURL)
       
    
        period = tab.name[0:4]
        trace.Period("Selected from the tab title")
        
        industry = tab.excel_ref("F1").expand(DOWN).is_not_blank()
        trace.Industry("Selected as all non-blank values from cell ref F1 down.")
        
        business_size = tab.excel_ref("G1").expand(DOWN).is_not_blank()
        trace.Business_Size("Selected as all non-blank values from cell ref G1 down.")
        
        measure_type = tab.excel_ref("H1:I1")
        trace.Measure_Type("Selected as the two values in cells H1 and I1")
        
        unit = "£m"
        trace.Unit("Hardcoded value but could have been taken from the measure types or from the contents page.")
        
        observations = tab.excel_ref("H2:I361").is_not_blank()
        
        dimensions = [
            HDimConst("Period", period),
            HDim(industry, "Industry", CLOSEST, ABOVE),
            HDim(business_size, "Business Size", DIRECTLY, LEFT),
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
        
        tidied = df[["Period", "Industry", "Business Size", "Measure Type", "Unit", "Value"]]
        tidied_sheets.append(tidied)
    


# +
#Outputs:
    #tidied_sheets[0] \
    #tidied_sheets[4]  --> Industry totals: attribute = Ownership
    #tidied_sheets[8] /
    
    #tidied_sheets[12] \
    #tidied_sheets[13]  --> Industry totals: attribute = Business Size
    #tidied_sheets[14] /
    
    #tidied_sheets[1] \
    #tidied_sheets[5]  --> Year: attributes = Business Size + Ownership
    #tidied_sheets[9] /
    
    #tidied_sheets[2] \
    #tidied_sheets[6]  --> Year: attributes = Country + Ownership
    #tidied_sheets[10] /
    
    #tidied_sheets[3] \
    #tidied_sheets[7]  --> Year: attributes = Country + Business Size
    #tidied_sheets[11] /
    

#Notes:
    #Multiple measures still present in all tables but should be very easy to separate as they alternate (exports/imports).
# -




