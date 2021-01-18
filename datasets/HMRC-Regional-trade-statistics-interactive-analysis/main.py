#!/usr/bin/env python
# coding: utf-8

# In[15]:


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


# In[16]:


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


# In[17]:


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


# In[18]:


countries = []
region = []


# In[19]:


df = pd.concat([tidied_sheets[0],tidied_sheets[1],tidied_sheets[8],tidied_sheets[9]], sort = True)

df = df.rename(columns={'Year' : 'Period'})

df['Period'] = df.apply(lambda x: 'year/' + left(str(x['Period']), 4) if 'Q' not in str(x['Quarter']) else 'quarter/' + left(x['Period'], 4) + '-' + x['Quarter'], axis = 1)

df = df.drop(['Code', 'Quarter'], axis=1)

df['Flow'] = df.apply(lambda x: 'exports' if 'Exporters' in x['Measure Type'] else ('imports' if 'Importers' in x['Measure Type'] else 'ERROR'), axis = 1)

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
    data["transform"]["columns"]["Value"]["unit"] = "http://gss-data.org.uk/def/concept/measurement-units/trade"
    print("Unit changed to: ", data["transform"]["columns"]["Value"]["unit"] )

    print("Value measure type: ", data["transform"]["columns"]["Value"]["measure"] )
    data["transform"]["columns"]["Value"]["measure"] = "http://gss-data.org.uk/def/measure/proportional-count"
    print("Value measure changed to: ", data["transform"]["columns"]["Value"]["measure"] )

    print("Value dtype: ", data["transform"]["columns"]["Value"]["datatype"] )
    data["transform"]["columns"]["Value"]["datatype"] = "integer"
    print("Value dtype changed to: ", data["transform"]["columns"]["Value"]["datatype"] )

df = df[['Period', 'Country', 'Region', 'Flow', 'Value']]

df['Value'] = df['Value'].astype(int)

csvName = 'prop-count-trades-observations'
scraper.dataset.family = 'trade'
scraper.dataset.title = 'Regional trade statistics interactive analysis - exporters, exporters - proportional business count method'

cubes.add_cube(scraper, df.drop_duplicates(), csvName, info_json_dict=data, graph="HMRC-Regional-trade-statistics-interactive-analysis")

countries.append(df['Country'].unique().tolist())
region.append(df['Region'].unique().tolist())

df


# In[20]:


df = pd.concat([tidied_sheets[2],tidied_sheets[3],tidied_sheets[10],tidied_sheets[11]], sort = True)

df = df.rename(columns={'Year' : 'Period'})

df['Period'] = df.apply(lambda x: 'year/' + left(str(x['Period']), 4) if 'Q' not in str(x['Quarter']) else 'quarter/' + left(x['Period'], 4) + '-' + x['Quarter'], axis = 1)

df['Unit'] = df.apply(lambda x: 'gbp thousands' if 'thousands' in x['Measure Type'] else x['Unit'], axis = 1)
df['Unit'] = df.apply(lambda x: 'gbp billions' if 'billions' in x['Measure Type'] else x['Unit'], axis = 1)
df['Unit'] = df.apply(lambda x: 'count' if 'Number' in x['Measure Type'] else x['Unit'], axis = 1)

df = df.drop(['Code', 'Quarter'], axis=1)

df['Flow'] = df.apply(lambda x: 'exports' if 'export' in x['Measure Type'] else ('imports' if 'import' in x['Measure Type'] else 'ERROR'), axis = 1)

COLUMNS_TO_NOT_PATHIFY = ['Value']

for col in df.columns.values.tolist():
	if col in COLUMNS_TO_NOT_PATHIFY:
		continue
	try:
		df[col] = df[col].apply(pathify)
	except Exception as err:
		raise Exception('Failed to pathify column "{}".'.format(col)) from err

averagePerTrade = df[df['Unit'] == 'gbp-thousands']

with open("info.json", "r") as read_file:
    data = json.load(read_file)
    print("Unit: ", data["transform"]["columns"]["Value"]["unit"] )
    data["transform"]["columns"]["Value"]["unit"] = "http://gss-data.org.uk/def/concept/measurement-units/average-value-per-trade"
    print("Unit changed to: ", data["transform"]["columns"]["Value"]["unit"] )

    print("Value measure type: ", data["transform"]["columns"]["Value"]["measure"] )
    data["transform"]["columns"]["Value"]["measure"] = "http://gss-data.org.uk/def/measure/gbp-thousands"
    print("Value measure changed to: ", data["transform"]["columns"]["Value"]["measure"] )

    print("Value dtype: ", data["transform"]["columns"]["Value"]["datatype"] )
    data["transform"]["columns"]["Value"]["datatype"] = "double"
    print("Value dtype changed to: ", data["transform"]["columns"]["Value"]["datatype"] )

averagePerTrade = averagePerTrade.drop(['Measure Type', 'Unit'], axis=1)

averagePerTrade = averagePerTrade[['Period', 'Country', 'Region', 'Flow', 'Value']]

csvName = 'prop-avg-val-per-trade-observations'
scraper.dataset.family = 'trade'
scraper.dataset.title = 'Regional trade statistics interactive analysis - exporters, importers - Average Value per Trade - Proportional Count Method'

cubes.add_cube(scraper, averagePerTrade.drop_duplicates(), csvName, info_json_dict=data, graph="HMRC-Regional-trade-statistics-interactive-analysis")

countries.append(averagePerTrade['Country'].unique().tolist())
region.append(averagePerTrade['Region'].unique().tolist())

averagePerTrade


# In[21]:


#Data included in non regional tabs

#trade = df[df['Unit'] == 'count']

#with open("info.json", "r") as read_file:
#    data = json.load(read_file)
#    print("Unit: ", data["transform"]["columns"]["Value"]["unit"] )
#    data["transform"]["columns"]["Value"]["unit"] = "http://gss-data.org.uk/def/concept/measurement-units/trade"
#    print("Unit changed to: ", data["transform"]["columns"]["Value"]["unit"] )

#    print("Value measure type: ", data["transform"]["columns"]["Value"]["measure"] )
#    data["transform"]["columns"]["Value"]["measure"] = "http://gss-data.org.uk/def/measure/porportional-count"
#    print("Value measure changed to: ", data["transform"]["columns"]["Value"]["measure"] )

#    print("Value dtype: ", data["transform"]["columns"]["Value"]["datatype"] )
#    data["transform"]["columns"]["Value"]["datatype"] = "integer"
#    print("Value dtype changed to: ", data["transform"]["columns"]["Value"]["datatype"] )

#trade = trade.drop(['Measure Type', 'Unit'], axis=1)

#csvName = 'trades-observations'
#scraper.dataset.family = 'trade'
#scraper.dataset.title = 'Regional trade statistics interactive analysis - exporters, importers - Number of Trades - Proportional Count Method'

#cubes.add_cube(scraper, trade.drop_duplicates(), csvName, info_json_dict=data, graph="HMRC-Regional-trade-statistics-interactive-analysis")
#trade


# In[22]:


valueOfTrade = df[df['Unit'] == 'gbp-billions']

with open("info.json", "r") as read_file:
    data = json.load(read_file)
    print("Unit: ", data["transform"]["columns"]["Value"]["unit"] )
    data["transform"]["columns"]["Value"]["unit"] = "http://gss-data.org.uk/def/concept/measurement-units/value-of-trade"
    print("Unit changed to: ", data["transform"]["columns"]["Value"]["unit"] )

    print("Value measure type: ", data["transform"]["columns"]["Value"]["measure"] )
    data["transform"]["columns"]["Value"]["measure"] = "http://gss-data.org.uk/def/measure/gbp-billions"
    print("Value measure changed to: ", data["transform"]["columns"]["Value"]["measure"] )

    print("Value dtype: ", data["transform"]["columns"]["Value"]["datatype"] )
    data["transform"]["columns"]["Value"]["datatype"] = "double"
    print("Value dtype changed to: ", data["transform"]["columns"]["Value"]["datatype"] )

valueOfTrade = valueOfTrade.drop(['Measure Type', 'Unit'], axis=1)

valueOfTrade = valueOfTrade[['Period', 'Country', 'Region', 'Flow', 'Value']]

csvName = 'prop-value-of-trades-observations'
scraper.dataset.family = 'trade'
scraper.dataset.title = 'Regional trade statistics interactive analysis - exporters, importers - Value of Trade - Proportional Count Method'

cubes.add_cube(scraper, valueOfTrade.drop_duplicates(), csvName, info_json_dict=data, graph="HMRC-Regional-trade-statistics-interactive-analysis")

countries.append(valueOfTrade['Country'].unique().tolist())
region.append(valueOfTrade['Region'].unique().tolist())

valueOfTrade


# In[23]:


df = pd.concat([tidied_sheets[4],tidied_sheets[5],tidied_sheets[12],tidied_sheets[13]], sort = True)

df = df.rename(columns={'Year' : 'Period'})

df['Period'] = df.apply(lambda x: 'year/' + left(str(x['Period']), 4) if 'Q' not in str(x['Quarter']) else 'quarter/' + left(x['Period'], 4) + '-' + x['Quarter'], axis = 1)

df = df.drop(['Code', 'Quarter'], axis=1)

df['Flow'] = df.apply(lambda x: 'exports' if 'Exporters' in x['Measure Type'] else ('imports' if 'Importers' in x['Measure Type'] else 'ERROR'), axis = 1)

df = df[df['Period'] != 'year/None']
df = df[df['Country'] != '0.0']

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
    data["transform"]["columns"]["Value"]["unit"] = "http://gss-data.org.uk/def/concept/measurement-units/trade"
    print("Unit changed to: ", data["transform"]["columns"]["Value"]["unit"] )

    print("Value measure type: ", data["transform"]["columns"]["Value"]["measure"] )
    data["transform"]["columns"]["Value"]["measure"] = "http://gss-data.org.uk/def/measure/count"
    print("Value measure changed to: ", data["transform"]["columns"]["Value"]["measure"] )

    print("Value dtype: ", data["transform"]["columns"]["Value"]["datatype"] )
    data["transform"]["columns"]["Value"]["datatype"] = "integer"
    print("Value dtype changed to: ", data["transform"]["columns"]["Value"]["datatype"] )

df = df.drop(['Measure Type', 'Unit'], axis=1)

df = df[['Period', 'Country', 'Region', 'Flow', 'Value', 'Marker']]

df['Value'] = df['Value'].astype(int)

csvName = 'whole-count-trades-observations'
scraper.dataset.family = 'trade'
scraper.dataset.title = 'Regional trade statistics interactive analysis - importers, exporters - whole number count method'

cubes.add_cube(scraper, df.drop_duplicates(), csvName, info_json_dict=data, graph="HMRC-Regional-trade-statistics-interactive-analysis")

countries.append(df['Country'].unique().tolist())
region.append(df['Region'].unique().tolist())

df


# In[24]:


df = pd.concat([tidied_sheets[6],tidied_sheets[7],tidied_sheets[14],tidied_sheets[15]], sort = True)

df = df.rename(columns={'Year' : 'Period'})

df['Period'] = df.apply(lambda x: 'year/' + left(str(x['Period']), 4) if 'Q' not in str(x['Quarter']) else 'quarter/' + left(x['Period'], 4) + '-' + x['Quarter'], axis = 1)

df['Unit'] = df.apply(lambda x: 'gbp thousands' if 'thousands' in x['Measure Type'] else x['Unit'], axis = 1)
df['Unit'] = df.apply(lambda x: 'gbp billions' if 'billions' in x['Measure Type'] else x['Unit'], axis = 1)
df['Unit'] = df.apply(lambda x: 'count' if 'Number' in x['Measure Type'] else x['Unit'], axis = 1)

df = df.drop(['Code', 'Quarter'], axis=1)
df = df[df['Country'] != '0.0']

df['Flow'] = df.apply(lambda x: 'exports' if 'export' in x['Measure Type'] else ('imports' if 'import' in x['Measure Type'] else 'ERROR'), axis = 1)

COLUMNS_TO_NOT_PATHIFY = ['Value']

for col in df.columns.values.tolist():
	if col in COLUMNS_TO_NOT_PATHIFY:
		continue
	try:
		df[col] = df[col].apply(pathify)
	except Exception as err:
		raise Exception('Failed to pathify column "{}".'.format(col)) from err

averagePerTrade = df[df['Unit'] == 'gbp-thousands']

with open("info.json", "r") as read_file:
    data = json.load(read_file)
    print("Unit: ", data["transform"]["columns"]["Value"]["unit"] )
    data["transform"]["columns"]["Value"]["unit"] = "http://gss-data.org.uk/def/concept/measurement-units/average-value-per-trade"
    print("Unit changed to: ", data["transform"]["columns"]["Value"]["unit"] )

    print("Value measure type: ", data["transform"]["columns"]["Value"]["measure"] )
    data["transform"]["columns"]["Value"]["measure"] = "http://gss-data.org.uk/def/measure/gbp-thousands"
    print("Value measure changed to: ", data["transform"]["columns"]["Value"]["measure"] )

    print("Value dtype: ", data["transform"]["columns"]["Value"]["datatype"] )
    data["transform"]["columns"]["Value"]["datatype"] = "double"
    print("Value dtype changed to: ", data["transform"]["columns"]["Value"]["datatype"] )

averagePerTrade = averagePerTrade.drop(['Measure Type', 'Unit'], axis=1)

averagePerTrade = averagePerTrade[['Period', 'Country', 'Region', 'Flow', 'Value']]

csvName = 'whole-avg-val-per-trade-observations'
scraper.dataset.family = 'trade'
scraper.dataset.title = 'Regional trade statistics interactive analysis - importers, exporters - Average Value per Trade - Whole number count method'

cubes.add_cube(scraper, averagePerTrade.drop_duplicates(), csvName, info_json_dict=data, graph="HMRC-Regional-trade-statistics-interactive-analysis")

countries.append(averagePerTrade['Country'].unique().tolist())
region.append(averagePerTrade['Region'].unique().tolist())

averagePerTrade


# In[25]:


#Data included in Non Regional Tabs

#trades = df[df['Unit'] == 'count']

#with open("info.json", "r") as read_file:
#    data = json.load(read_file)
#    print("Unit: ", data["transform"]["columns"]["Value"]["unit"] )
#    data["transform"]["columns"]["Value"]["unit"] = "http://gss-data.org.uk/def/concept/measurement-units/trade"
#    print("Unit changed to: ", data["transform"]["columns"]["Value"]["unit"] )

#    print("Value measure type: ", data["transform"]["columns"]["Value"]["measure"] )
#    data["transform"]["columns"]["Value"]["measure"] = "http://gss-data.org.uk/def/measure/count"
#    print("Value measure changed to: ", data["transform"]["columns"]["Value"]["measure"] )

#    print("Value dtype: ", data["transform"]["columns"]["Value"]["datatype"] )
#    data["transform"]["columns"]["Value"]["datatype"] = "integer"
#    print("Value dtype changed to: ", data["transform"]["columns"]["Value"]["datatype"] )

#trades = trades.drop(['Measure Type', 'Unit'], axis=1)

#csvName = 'whole-count-trades-observations'
#scraper.dataset.family = 'trade'
#scraper.dataset.title = 'Regional trade statistics interactive analysis - importers, exporters - Number of Trade - Whole number count method'

#cubes.add_cube(scraper, trades.drop_duplicates(), csvName, info_json_dict=data, graph="HMRC-Regional-trade-statistics-interactive-analysis")
#trades


# In[26]:


valueOfTrades = df[df['Unit'] == 'gbp-billions']

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

valueOfTrades = valueOfTrades.drop(['Measure Type', 'Unit'], axis=1)

valueOfTrades = valueOfTrades[['Period', 'Country', 'Region', 'Flow', 'Value']]

csvName = 'whole-value-of-trades-observations'
scraper.dataset.family = 'trade'
scraper.dataset.title = 'Regional trade statistics interactive analysis - importers, exporters - Value of Trades - Whole number count method'

cubes.add_cube(scraper, valueOfTrades.drop_duplicates(), csvName, info_json_dict=data, graph="HMRC-Regional-trade-statistics-interactive-analysis")

countries.append(valueOfTrades['Country'].unique().tolist())
region.append(valueOfTrades['Region'].unique().tolist())

valueOfTrades


# In[27]:


from IPython.core.display import HTML
for col in df:
    if col not in ['Value']:
        df[col] = df[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(df[col].cat.categories)


# In[28]:


cubes.output_all()
trace.render()

