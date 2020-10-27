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


def remove_super(string):
    no_super_string = ""
    count = -1
    for char in string:
        count  += 1
        if char.isdigit() == True:
            if count + 1 == len(string):
                continue
                
            elif string[count + 1] == ":" or string[count + 2] == ":":
                no_super_string += char
            
            #elif string[count : count + 3] == "2016":
            elif char == "2"  and string[count + 1] == "0":
                no_super_string += char
                no_super_string += string[count + 1]
                no_super_string += string[count + 2]
                no_super_string += string[count + 3]
                count += 3
                
            else:
                continue

        else:
            no_super_string += char

    no_super_string = no_super_string.replace(",", "")
    return(no_super_string)


# +
for tab in scraper.distributions[0].as_databaker():
    
    if tab.name == "Information":
        measure_types = []
        mt_cells = tab.excel_ref("D13").expand(DOWN).is_not_blank()
        for i in mt_cells: 
            measure_types.append(cell_to_string(i))
            
    elif tab.name == "ESRI_MAPINFO_SHEET":
        continue
    
    else:
        tab_title = cell_to_string(tab.excel_ref("A1")) #Still need to get rid of superscripts
        tab_title = remove_super(tab_title)
        print(tab_title)
        tab_columns = ["Year", "Area Type", "Geography Code", "Area Name", "Measure Type", "Unit"]
        trace.start(tab_title, tab, tab_columns, scraper.distributions[0].downloadURL)
        
        year = tab.excel_ref("D2").expand(RIGHT).is_not_blank() #Still need to get rid of superscripts
        trace.Year("Selected as all non-blank values from cell ref D2 going right/across.")
        
        area_type = tab.excel_ref("A2").expand(DOWN).is_not_blank()
        trace.Area_Type("Selected as all non-blank values from cell ref A2 down.")
        
        geography_code = tab.excel_ref("B2").expand(DOWN).is_not_blank()
        trace.Geography_Code("Selected as all non-blank values from cell ref B2 down.")
        
        area_name = tab.excel_ref("C2").expand(DOWN).is_not_blank()
        trace.Area_Name("Selected as all non-blank values from cell ref C2 down.")
        
        measure_type = measure_types[0]
        measure_types.pop(0)
        trace.Measure_Type("Selected as the first value in the measure types list. List made from values in the 'Information' tab.")
        
        unit = tab.excel_ref("X1") #probably needs more work
        trace.Unit("Selected as the value in cell ref X1.")
        
        observations = tab.excel_ref("D3").expand(RIGHT).expand(DOWN).is_not_blank()
        
        
        dimensions = [
            HDim(year, "Year", DIRECTLY, ABOVE),
            HDim(area_type, "Area Type", CLOSEST, ABOVE),
            HDim(geography_code, "Geography Code", CLOSEST, ABOVE),
            HDim(area_name, "Area Name", DIRECTLY, LEFT),
            HDimConst("Measure Type", measure_type),
            HDim(unit, "Unit", CLOSEST, ABOVE)
        ]
        
        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        trace.with_preview(tidy_sheet)
        #savepreviewhtml(tidy_sheet)
        trace.store("combined_" + tab_title[:9].strip(" ").strip(":").replace(" ", "_"), tidy_sheet.topandas())
        
        df = trace.combine_and_trace(tab_title, "combined_" + tab_title[:9].strip(" ").strip(":").replace(" ", "_"))
        df.rename(columns={'OBS' : 'Value'}, inplace=True)
        trace.render()
        
        tidied = df[["Year", "Area Type", "Geography Code", "Area Name", "Measure Type", "Unit", "Value"]]
        tidied_sheets.append(tidied)
        
#tidied_sheets
# -

#Outputs:
    #tidied_sheets[0] = Table 1: Enterprise Regions: Gross Value Added (Balanced) at current basic prices
    #tidied_sheets[1] = Table 2: Enterprise Regions: Value Added Tax (VAT) on products
    #tidied_sheets[2] = Table 3: Enterprise Regions: Other taxes on products
    #tidied_sheets[3] = Table 4: Enterprise Regions: Subsidies on products
    #tidied_sheets[4] = Table 5: Enterprise Regions: Gross Domestic Product (GDP) at current market prices
    #tidied_sheets[5] = Table 6: Enterprise Regions: Total resident population numbers
    #tidied_sheets[6] = Table 7: Enterprise Regions: Gross Domestic Product (GDP) per head at current market prices
    #tidied_sheets[7] = Table 8: Enterprise Regions: Whole economy GVA implied deflators
    #tidied_sheets[8] = Table 9: Enterprise Regions: Gross Domestic Product (GDP) chained volume measures (CVM) index
    #tidied_sheets[9] = Table 10: Enterprise Regions: Gross Domestic Product (GDP) chained volume measures (CVM) in 2016 money value
    #tidied_sheets[10] = Table 11: Enterprise Regions: Gross Domestic Product (GDP) chained volume measures (CVM) per head
    #tidied_sheets[11] = Table 12: Enterprise Regions: Gross Domestic Product (GDP) chained volume measures (CVM) annual growth rates
    #tidied_sheets[12] = 
