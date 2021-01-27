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

scraper = Scraper(seed="info.json")   
scraper 

# +
tidied_sheets = []
trace = TransformTrace()
df = pd.DataFrame()

#dist_num = len(scraper.distributions) - 1
# -

def cell_to_string(cell):
    s = str(cell)
    start = s.find("'") + len("'")
    end = s.find(">")
    substring = s[start:end].strip("'")
    return substring


def find_whitespace(start_cell):
    col = tab.excel_ref(start_cell).expand(DOWN).is_not_blank()
    #print(col)
    limits = []
    for n in col:
        n_str = cell_to_string(n)
        #print(n_str)
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


def remove_supers(string):
    old_title = string
    new_title = ""
    for char in old_title:
        if char.isdigit():
            continue
        else:
            new_title = new_title + char
    
    new_title = new_title.replace(",", "")
    new_title = new_title.replace(" ", "_")
    
    return new_title


def format_period(period):
    period_str = cell_to_string(period)
    if "Q" in period_str:
        print(period_str)
        #tidy_period = "quarter/" + year + "-" quarter
        tidy_period = period_str
    
    else:
        start = period_str.find(" ") + len(" ")
        end = period_str.find(".")
        year = period_str[start:end].strip("'")
        tidy_period = "year/" + year
        
    return tidy_period


# +
#### Distribution 1: Quarterly country and regional GDP - Most Recently Published

distribution_date = str(scraper.distributions[0].issued)

for tab in scraper.distributions[0].as_databaker():
    
    table_cs_list = []
    table_tidy_sheet_list = []
    
    if tab.name == "Contents":
        continue
    
    else:
        tab_title_super = cell_to_string(tab.excel_ref("A2")) + " " + cell_to_string(tab.excel_ref("A3")) + " - " + tab.name#Remove Supers. This may be able to be hardcoded for each tab/distribution
        tab_title = remove_supers(tab_title_super)
        if tab.name == "Key Figures":   
            tab_columns = ["Period", "Region", "Industry Section", "Measure Type", "Unit"]
            
        else:
            tab_columns = ["Period", "Region", "Sector", "Industry Section", "Measure Type", "Unit"]
            
        trace.start(tab_title, tab, tab_columns, scraper.distributions[0].downloadURL)
        
        if tab.name == "Key Figures":
            region = tab.excel_ref("B5").expand(RIGHT).is_not_blank()
            trace.Region("Selected as all non-blank values from cell ref B5 going right/across.")
            
        else:
            region = tab.name
            trace.Region("Selected as the tab name.") 
            
            sector = tab.excel_ref("B5").expand(RIGHT).is_not_blank()
            trace.Sector("Selected as all non-blank values from cell ref B5 going right/across.")
            
        industry_section = tab.excel_ref("B6").expand(RIGHT).is_not_blank()
        trace.Industry_Section("Selected as all non-blank values from cell ref B6 going down")
        
        limits = find_whitespace("A8")
        rows = get_rows(limits)
        for i in range(0, 5):
            cell_min = int(rows[i]) + 1
            cell_max = int(rows[i+1]) - 1
            
            period = tab.excel_ref("A"+str(cell_min)+":A"+str(cell_max)).is_not_blank()
            
            measure_type = tab.excel_ref("A"+rows[i])
            change_type = tab.excel_ref("A"+rows[i])
            
            unit = "gdp"
            
            if tab.name == "Key Figures":
                observations = tab.excel_ref("B"+str(cell_min)+":M"+str(cell_max)).is_not_blank()
                
            else:
                observations = tab.excel_ref("B"+str(cell_min)+":X"+str(cell_max)).is_not_blank()
            
            
            if tab.name == "Key Figures":                
                dimensions = [
                    HDim(period, "Period", DIRECTLY, LEFT),
                    HDim(region, "Region", DIRECTLY, ABOVE),
                    HDim(industry_section, "Industry Section", DIRECTLY, ABOVE),
                    HDim(measure_type, "Measure Type", CLOSEST, ABOVE),
                    HDim(measure_type, "Change Type", CLOSEST, ABOVE),
                    HDimConst("Unit", unit)
                ]
                
            else:                
                dimensions = [
                    HDim(period, "Period", DIRECTLY, LEFT),
                    HDimConst("Region", region),
                    HDim(sector, "Sector", DIRECTLY, ABOVE),
                    HDim(industry_section, "Industry Section", DIRECTLY, ABOVE),
                    HDim(measure_type, "Measure Type", CLOSEST, ABOVE),
                    HDim(measure_type, "Change Type", CLOSEST, ABOVE),
                    HDimConst("Unit", unit)
                ]
                
            table_cs_iteration = ConversionSegment(tab, dimensions, observations)
            table_iteration = table_cs_iteration.topandas()
            table_cs_list.append(table_cs_iteration)
            table_tidy_sheet_list.append(table_iteration)
            
        table_tidy_sheet = pd.concat(table_tidy_sheet_list, sort=False)
        
        trace.Period("Selected as all non-blank values from cell contaning last recorded measure type going down until a new measure type is found in column A.")
        trace.Measure_Type("Selected as the next value from the rows list.")
        
        trace.store("combined_" + tab.name + "_" + distribution_date, table_tidy_sheet)
        
        df = trace.combine_and_trace(tab_title, "combined_" + tab.name + "_" + distribution_date)
        df.rename(columns={'OBS' : 'Value'}, inplace=True)
        trace.render()
        
        if tab.name == "Key Figures":
            tidied = df[["Period", "Region", "Industry Section", "Measure Type", "Change Type", "Unit", "Value"]]
            
        else:
            tidied = df[["Period", "Region", "Sector", "Industry Section", "Measure Type", "Change Type", "Unit", "Value"]]
            
        tidied_sheets.append(tidied)
        
#pd.set_option("display.max_rows", None, "display.max_columns", None)

#tidied_sheets
# -

# Outputs (as of 10.11.2020):
    #Distribution 1:
        #tidied_sheets[0:12]    13 tabs

# +
indicies_tabs = []
percentage_tabs = []

for sheet in tidied_sheets:
    indicies_tabs.append(sheet[sheet["Measure Type"] == "Indices 2016=100"])
    percentage_tabs.append(sheet[sheet["Measure Type"] != "Indices 2016=100"])

indicies = pd.concat(indicies_tabs)
percentage_change = pd.concat(percentage_tabs)


# +
#seperating depending on indicies / percentage and post processing.

tidied_indicies = indicies[["Period", "Region", "Industry Section", "Value"]]
tidied_percentage_change = percentage_change[["Period", "Region", "Industry Section", "Change Type", "Value"]]

tidied_indicies['Region'] = tidied_indicies['Region'].map(lambda x: pathify(x))
tidied_percentage_change['Region'] = tidied_percentage_change['Region'].map(lambda x: pathify(x))

#Format Date/Quarter
def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

tidied_indicies['Period'] = tidied_indicies['Period'].astype(str).replace('\.0', '', regex=True)
tidied_percentage_change['Period'] = tidied_percentage_change['Period'].astype(str).replace('\.0', '', regex=True)

def date_time(date):
    if len(date)  == 4:
        return 'year/' + date
    elif len(date) == 7:
        return 'quarter/' + left(date,4) + '-' + right(date,2)
    else:
        return "Date Formatting Error"
    
tidied_indicies["Period"] =  tidied_indicies["Period"].apply(date_time)
tidied_percentage_change["Period"] =  tidied_percentage_change["Period"].apply(date_time)

#Format Change Type
def change_type(change_type):
    tidy_ct = change_type[19:]
    tidy_ct = tidy_ct.replace(" ", "-")
    return(tidy_ct)

tidied_percentage_change["Change Type"] =  tidied_percentage_change["Change Type"].apply(change_type)

to_output = []
to_output.append([tidied_indicies, "indicies", "ons-quarterly-country-and-regional-gdp/indices", "Quarterly country and regional GDP - Indices", "Indices 2016 = 100.", "/indicies"])
to_output.append([tidied_percentage_change, "percentage_change", "ons-quarterly-country-and-regional-gdp/percentagechange", "Quarterly country and regional GDP - Percentage change", "Percentage change.", "/percentagechange"])
# -

tidied_percentage_change

tidied_indicies

# +
from urllib.parse import urljoin
import os

for i in to_output:
    
    csvName = i[1] + "_observations.csv"
    out = Path("out")
    out.mkdir(exist_ok=True)
    i[0].drop_duplicates().to_csv(out / csvName, index = False)
        
    scraper.dataset.family = "trade"

    scraper.dataset.description = """Quarterly economic activity within Wales and the nine English regions (North East, North West, 
    Yorkshire and The Humber, East Midlands, West Midlands, East of England, London, South East, and South West).""" + i[4] + """
    Regional GDP is designated as experimental statistics. Indices reflect values measured at basic prices, which exclude taxes less 
    subsidies on products. Estimates cannot be regarded as accurate to the last digit shown. Any apparent inconsistencies between the 
    index numbers and the percentage change are due to rounding."""

    scraper.dataset.comment = "Quarterly economic activity within Wales and the nine English regions (North East, North West, Yorkshire and The Humber, East Midlands, West Midlands, East of England, London, South East, and South West)." + i[4]
    scraper.dataset.title = i[3]

    dataset_path = pathify(os.environ.get('JOB_NAME', f'gss_data/{scraper.dataset.family}/' + Path(os.getcwd()).name) + i[5]).lower()
    scraper.set_base_uri('http://gss-data.org.uk')
    scraper.set_dataset_id(i[2])
    

    csvw_transform = CSVWMapping()
    csvw_transform.set_csv(out / csvName)
    csvw_transform.set_mapping(json.load(open('info.json')))
    csvw_transform.set_dataset_uri(urljoin(scraper._base_uri, f'data/{scraper._dataset_id}'))
    csvw_transform.write(out / f'{csvName}-metadata.json')

    with open(out / f'{csvName}-metadata.trig', 'wb') as metadata:
        metadata.write(scraper.generate_trig())
# -


