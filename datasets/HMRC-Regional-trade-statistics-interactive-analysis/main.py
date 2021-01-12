#!/usr/bin/env python
# coding: utf-8

# In[213]:


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

cubes = Cubes("info.json")
tidied_sheets = []
trace = TransformTrace()
df = pd.DataFrame()

def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

def mid(s, offset, amount):
    return s[offset:offset+amount]


def cell_to_string(cell):
    s = str(cell)
    start = s.find("'") + len("'")
    end = s.find(">")
    substring = s[start:end].strip("'")
    return substring


# In[214]:


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


# In[215]:


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


# In[216]:


#Outputs:
    #See below

#Notes:
    #Transform takes a few minutes to run. Most time spent waiting for new .xls files to be written as tabs could not be loaded using either
    #databaker or pandas in the existing .xlsm format.

    #data0.xls = relevant tabs from distribution 1 : Exports using proportional business count method
    #data0.xls = relevant tabs from distribution 2 : Exports using whole number count method
    #data0.xls = relevant tabs from distribution 3 : Imports using proportional business count method
    #data0.xls = relevant tabs from distribution 4 : Imports using whole number count method


# In[217]:


#tidied_sheets[10] #Data2.xls Database(Regional Year)


# In[218]:


#tidied_sheets[11] #Data2.xls Database(Regional Qtr)


# In[219]:


#tidied_sheets[14] #Data3.xls Database(Regional Year)


# In[220]:


#tidied_sheets[15] #Data0.xls Database(Regional Qtr)


# In[221]:


df = pd.concat([tidied_sheets[0],tidied_sheets[1],tidied_sheets[4],tidied_sheets[5]], sort = True)

df = df.rename(columns={'Year' : 'Period'})

df['Period'] = df.apply(lambda x: 'year/' + left(str(x['Period']), 4) if 'Q' not in str(x['Quarter']) else 'quarter/' + left(x['Period'], 4) + '-' + x['Quarter'], axis = 1)

df = df.drop(['Code', 'Quarter'], axis=1)

df = df.replace({'Measure Type' : {'Number Exporters' : 'exporters'},
                 'Unit' : {'Count' : 'proportional count'}})

df['Flow'] = 'export'

df = df[['Period', 'Country', 'Region', 'Value']]

df['Marker'] = df.apply(lambda x: 'suppressed' if x['Value'] == '' else '', axis = 1)
df['Value'] = df.apply(lambda x: 0 if x['Marker'] == 'suppressed' else x['Value'], axis = 1)

COLUMNS_TO_NOT_PATHIFY = ['Value']

for col in df.columns.values.tolist():
	if col in COLUMNS_TO_NOT_PATHIFY:
		continue
	try:
		df[col] = df[col].apply(pathify)
	except Exception as err:
		raise Exception('Failed to pathify column "{}".'.format(col)) from err

with open("info.json", "r") as read_file:
    data = json.load(read_file)
    print("Unit: ", data["transform"]["columns"]["Value"]["unit"] )
    data["transform"]["columns"]["Value"]["unit"] = "http://gss-data.org.uk/def/concept/measurement-units/exporters"
    print("Unit changed to: ", data["transform"]["columns"]["Value"]["unit"] )

    print("Value measure type: ", data["transform"]["columns"]["Value"]["measure"] )
    data["transform"]["columns"]["Value"]["measure"] = "http://gss-data.org.uk/def/measure/proportional-count"
    print("Value measure changed to: ", data["transform"]["columns"]["Value"]["measure"] )

    print("Value dtype: ", data["transform"]["columns"]["Value"]["datatype"] )
    data["transform"]["columns"]["Value"]["datatype"] = "integer"
    print("Value dtype changed to: ", data["transform"]["columns"]["Value"]["datatype"] )

csvName = 'prop-exp-observations'
scraper.dataset.family = 'trade'
scraper.dataset.title = 'Regional trade statistics interactive analysis - exporters - proportional business count method'

cubes.add_cube(scraper, df.drop_duplicates(), csvName, info_json_dict=data, graph="HMRC-Regional-trade-statistics-interactive-analysis")

df


# In[222]:


df = pd.concat([tidied_sheets[2],tidied_sheets[3],tidied_sheets[6],tidied_sheets[7]], sort = True)

df = df.rename(columns={'Year' : 'Period'})

df['Period'] = df.apply(lambda x: 'year/' + left(str(x['Period']), 4) if 'Q' not in str(x['Quarter']) else 'quarter/' + left(x['Period'], 4) + '-' + x['Quarter'], axis = 1)

df = df.replace({'Measure Type' : {'Average value per exporter (£ thousands)' : 'average value per exporter',
                                   'Number of exporters' : 'exporters',
                                   'Value of exports (£ billions)' : 'value of exports'},
                 'Unit' : {'£ billions' : 'gbp billions', '£ thousands' : 'gbp thousands'}})

df = df.drop(['Code', 'Quarter'], axis=1)

df['Flow'] = 'export'

COLUMNS_TO_NOT_PATHIFY = ['Value']

for col in df.columns.values.tolist():
	if col in COLUMNS_TO_NOT_PATHIFY:
		continue
	try:
		df[col] = df[col].apply(pathify)
	except Exception as err:
		raise Exception('Failed to pathify column "{}".'.format(col)) from err

averagePerExporter = df[df['Measure Type'] == 'average-value-per-exporter']

with open("info.json", "r") as read_file:
    data = json.load(read_file)
    print("Unit: ", data["transform"]["columns"]["Value"]["unit"] )
    data["transform"]["columns"]["Value"]["unit"] = "http://gss-data.org.uk/def/concept/measurement-units/average-value-per-exporter"
    print("Unit changed to: ", data["transform"]["columns"]["Value"]["unit"] )

    print("Value measure type: ", data["transform"]["columns"]["Value"]["measure"] )
    data["transform"]["columns"]["Value"]["measure"] = "http://gss-data.org.uk/def/measure/gbp-thousands"
    print("Value measure changed to: ", data["transform"]["columns"]["Value"]["measure"] )

    print("Value dtype: ", data["transform"]["columns"]["Value"]["datatype"] )
    data["transform"]["columns"]["Value"]["datatype"] = "double"
    print("Value dtype changed to: ", data["transform"]["columns"]["Value"]["datatype"] )

averagePerExporter = averagePerExporter.drop(['Measure Type', 'Unit'], axis=1)

csvName = 'avg-val-per-exporter-observations'
scraper.dataset.family = 'trade'
scraper.dataset.title = 'Regional trade statistics interactive analysis - exporters - Average Value per Exporter'

cubes.add_cube(scraper, averagePerExporter.drop_duplicates(), csvName, info_json_dict=data, graph="HMRC-Regional-trade-statistics-interactive-analysis")

exporters = df[df['Measure Type'] == 'exporters']

with open("info.json", "r") as read_file:
    data = json.load(read_file)
    print("Unit: ", data["transform"]["columns"]["Value"]["unit"] )
    data["transform"]["columns"]["Value"]["unit"] = "http://gss-data.org.uk/def/concept/measurement-units/exporters"
    print("Unit changed to: ", data["transform"]["columns"]["Value"]["unit"] )

    print("Value measure type: ", data["transform"]["columns"]["Value"]["measure"] )
    data["transform"]["columns"]["Value"]["measure"] = "http://gss-data.org.uk/def/measure/count"
    print("Value measure changed to: ", data["transform"]["columns"]["Value"]["measure"] )

    print("Value dtype: ", data["transform"]["columns"]["Value"]["datatype"] )
    data["transform"]["columns"]["Value"]["datatype"] = "integer"
    print("Value dtype changed to: ", data["transform"]["columns"]["Value"]["datatype"] )

exporters = exporters.drop(['Measure Type', 'Unit'], axis=1)

csvName = 'exporters-observations'
scraper.dataset.family = 'trade'
scraper.dataset.title = 'Regional trade statistics interactive analysis - exporters - Number of Exporters'

cubes.add_cube(scraper, exporters.drop_duplicates(), csvName, info_json_dict=data, graph="HMRC-Regional-trade-statistics-interactive-analysis")

valueOfExports = df[df['Measure Type'] == 'value-of-exports']

with open("info.json", "r") as read_file:
    data = json.load(read_file)
    print("Unit: ", data["transform"]["columns"]["Value"]["unit"] )
    data["transform"]["columns"]["Value"]["unit"] = "http://gss-data.org.uk/def/concept/measurement-units/value-of-exports"
    print("Unit changed to: ", data["transform"]["columns"]["Value"]["unit"] )

    print("Value measure type: ", data["transform"]["columns"]["Value"]["measure"] )
    data["transform"]["columns"]["Value"]["measure"] = "http://gss-data.org.uk/def/measure/gbp-billions"
    print("Value measure changed to: ", data["transform"]["columns"]["Value"]["measure"] )

    print("Value dtype: ", data["transform"]["columns"]["Value"]["datatype"] )
    data["transform"]["columns"]["Value"]["datatype"] = "double"
    print("Value dtype changed to: ", data["transform"]["columns"]["Value"]["datatype"] )

valueOfExports = valueOfExports.drop(['Measure Type', 'Unit'], axis=1)

csvName = 'value-of-exports-observations'
scraper.dataset.family = 'trade'
scraper.dataset.title = 'Regional trade statistics interactive analysis - exporters - Value of Exports'

cubes.add_cube(scraper, valueOfExports.drop_duplicates(), csvName, info_json_dict=data, graph="HMRC-Regional-trade-statistics-interactive-analysis")


# In[223]:


df = pd.concat([tidied_sheets[8],tidied_sheets[9],tidied_sheets[12],tidied_sheets[13]], sort = True)

df = df.rename(columns={'Year' : 'Period'})

df['Period'] = df.apply(lambda x: 'year/' + left(str(x['Period']), 4) if 'Q' not in str(x['Quarter']) else 'quarter/' + left(x['Period'], 4) + '-' + x['Quarter'], axis = 1)

df = df.drop(['Code', 'Quarter'], axis=1)

df = df.replace({'Measure Type' : {'Number Importers' : 'importers'},
                 'Unit' : {'Count' : 'proportional count'}})

df['Flow'] = 'import'

df = df[['Period', 'Country', 'Region', 'Value']]

df = df[df['Period'] != 'year/None']

df['Marker'] = df.apply(lambda x: 'suppressed' if x['Value'] == '' else '', axis = 1)
df['Value'] = df.apply(lambda x: 0 if x['Marker'] == 'suppressed' else x['Value'], axis = 1)

COLUMNS_TO_NOT_PATHIFY = ['Value']

for col in df.columns.values.tolist():
	if col in COLUMNS_TO_NOT_PATHIFY:
		continue
	try:
		df[col] = df[col].apply(pathify)
	except Exception as err:
		raise Exception('Failed to pathify column "{}".'.format(col)) from err

with open("info.json", "r") as read_file:
    data = json.load(read_file)
    print("Unit: ", data["transform"]["columns"]["Value"]["unit"] )
    data["transform"]["columns"]["Value"]["unit"] = "http://gss-data.org.uk/def/concept/measurement-units/importers"
    print("Unit changed to: ", data["transform"]["columns"]["Value"]["unit"] )

    print("Value measure type: ", data["transform"]["columns"]["Value"]["measure"] )
    data["transform"]["columns"]["Value"]["measure"] = "http://gss-data.org.uk/def/measure/proportional-count"
    print("Value measure changed to: ", data["transform"]["columns"]["Value"]["measure"] )

    print("Value dtype: ", data["transform"]["columns"]["Value"]["datatype"] )
    data["transform"]["columns"]["Value"]["datatype"] = "integer"
    print("Value dtype changed to: ", data["transform"]["columns"]["Value"]["datatype"] )

csvName = 'prop-imp-observations'
scraper.dataset.family = 'trade'
scraper.dataset.title = 'Regional trade statistics interactive analysis - importers - proportional business count method'

cubes.add_cube(scraper, df.drop_duplicates(), csvName, info_json_dict=data, graph="HMRC-Regional-trade-statistics-interactive-analysis")

df


# In[224]:


df = pd.concat([tidied_sheets[10],tidied_sheets[11],tidied_sheets[14],tidied_sheets[15]], sort = True)

df = df.rename(columns={'Year' : 'Period'})

df['Period'] = df.apply(lambda x: 'year/' + left(str(x['Period']), 4) if 'Q' not in str(x['Quarter']) else 'quarter/' + left(x['Period'], 4) + '-' + x['Quarter'], axis = 1)

df = df.replace({'Measure Type' : {'Average value per importer (£ thousands)' : 'average value per importer',
                                   'Number of importers' : 'importers',
                                   'Value of imports (£ billions)' : 'value of imports'},
                 'Unit' : {'£ billions' : 'gbp billions', '£ thousands' : 'gbp thousands'}})

df = df.drop(['Code', 'Quarter'], axis=1)

df['Flow'] = 'import'

COLUMNS_TO_NOT_PATHIFY = ['Value']

for col in df.columns.values.tolist():
	if col in COLUMNS_TO_NOT_PATHIFY:
		continue
	try:
		df[col] = df[col].apply(pathify)
	except Exception as err:
		raise Exception('Failed to pathify column "{}".'.format(col)) from err

averagePerImporter = df[df['Measure Type'] == 'average-value-per-importer']

with open("info.json", "r") as read_file:
    data = json.load(read_file)
    print("Unit: ", data["transform"]["columns"]["Value"]["unit"] )
    data["transform"]["columns"]["Value"]["unit"] = "http://gss-data.org.uk/def/concept/measurement-units/average-value-per-importer"
    print("Unit changed to: ", data["transform"]["columns"]["Value"]["unit"] )

    print("Value measure type: ", data["transform"]["columns"]["Value"]["measure"] )
    data["transform"]["columns"]["Value"]["measure"] = "http://gss-data.org.uk/def/measure/gbp-thousands"
    print("Value measure changed to: ", data["transform"]["columns"]["Value"]["measure"] )

    print("Value dtype: ", data["transform"]["columns"]["Value"]["datatype"] )
    data["transform"]["columns"]["Value"]["datatype"] = "double"
    print("Value dtype changed to: ", data["transform"]["columns"]["Value"]["datatype"] )

averagePerImporter = averagePerImporter.drop(['Measure Type', 'Unit'], axis=1)

csvName = 'avg-val-per-importer-observations'
scraper.dataset.family = 'trade'
scraper.dataset.title = 'Regional trade statistics interactive analysis - importers - Average Value per Importer'

cubes.add_cube(scraper, averagePerImporter.drop_duplicates(), csvName, info_json_dict=data, graph="HMRC-Regional-trade-statistics-interactive-analysis")

importers = df[df['Measure Type'] == 'importers']

with open("info.json", "r") as read_file:
    data = json.load(read_file)
    print("Unit: ", data["transform"]["columns"]["Value"]["unit"] )
    data["transform"]["columns"]["Value"]["unit"] = "http://gss-data.org.uk/def/concept/measurement-units/importers"
    print("Unit changed to: ", data["transform"]["columns"]["Value"]["unit"] )

    print("Value measure type: ", data["transform"]["columns"]["Value"]["measure"] )
    data["transform"]["columns"]["Value"]["measure"] = "http://gss-data.org.uk/def/measure/count"
    print("Value measure changed to: ", data["transform"]["columns"]["Value"]["measure"] )

    print("Value dtype: ", data["transform"]["columns"]["Value"]["datatype"] )
    data["transform"]["columns"]["Value"]["datatype"] = "integer"
    print("Value dtype changed to: ", data["transform"]["columns"]["Value"]["datatype"] )

importers = importers.drop(['Measure Type', 'Unit'], axis=1)

csvName = 'importers-observations'
scraper.dataset.family = 'trade'
scraper.dataset.title = 'Regional trade statistics interactive analysis - importers - Number of Importers'

cubes.add_cube(scraper, importers.drop_duplicates(), csvName, info_json_dict=data, graph="HMRC-Regional-trade-statistics-interactive-analysis")

valueOfImports = df[df['Measure Type'] == 'value-of-imports']

with open("info.json", "r") as read_file:
    data = json.load(read_file)
    print("Unit: ", data["transform"]["columns"]["Value"]["unit"] )
    data["transform"]["columns"]["Value"]["unit"] = "http://gss-data.org.uk/def/concept/measurement-units/value-of-imports"
    print("Unit changed to: ", data["transform"]["columns"]["Value"]["unit"] )

    print("Value measure type: ", data["transform"]["columns"]["Value"]["measure"] )
    data["transform"]["columns"]["Value"]["measure"] = "http://gss-data.org.uk/def/measure/gbp-billions"
    print("Value measure changed to: ", data["transform"]["columns"]["Value"]["measure"] )

    print("Value dtype: ", data["transform"]["columns"]["Value"]["datatype"] )
    data["transform"]["columns"]["Value"]["datatype"] = "double"
    print("Value dtype changed to: ", data["transform"]["columns"]["Value"]["datatype"] )

valueOfImports = valueOfImports.drop(['Measure Type', 'Unit'], axis=1)

csvName = 'value-of-imports-observations'
scraper.dataset.family = 'trade'
scraper.dataset.title = 'Regional trade statistics interactive analysis - importers - Value of Imports'

cubes.add_cube(scraper, valueOfImports.drop_duplicates(), csvName, info_json_dict=data, graph="HMRC-Regional-trade-statistics-interactive-analysis")


# In[225]:


from IPython.core.display import HTML
for col in df:
    if col not in ['Value']:
        df[col] = df[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(df[col].cat.categories)


# In[226]:


cubes.output_all()
trace.render()

