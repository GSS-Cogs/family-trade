# In[23]:


import json
import pandas as pandas
from gssutils import *
from pandas import ExcelWriter
import math 

def left(s, amount):
    return s[:amount]

def cell_to_string(cell):
    s = str(cell)
    start = s.find("'") + len("'")
    end = s.find(">")
    substring = s[start:end].strip("'")
    return substring


metadata = Scraper(seed='info.json')

tidied_sheets = []
df = pd.DataFrame()


# In[24]:


counter = 0
source_name_and_distro = {}

for table in metadata.distributions:
    xls = pd.ExcelFile(metadata.distributions[counter].downloadURL)

    with ExcelWriter("data" + str(counter) + ".xls") as writer:
        for sheet in xls.sheet_names:

            if sheet == "Database (YR)" or sheet == "Database (QR)" or sheet == "Database (Regional Year)" or sheet == "Database (Regional Qtr)":
                pd.read_excel(xls, sheet).to_excel(writer,sheet)

            else:
                continue

        writer.save()

    
    source_name_and_distro["data" + str(counter) + ".xls"] = metadata.distributions[counter]
    counter += 1


# In[25]:


counter = 0
for source_name, distro in source_name_and_distro.items():
    tabs = loadxlstabs(source_name)
    print(source_name) 
    for tab in tabs:
        try:
            tab_title = "data_" + str(counter) + "_" + tab.name
            tab_title = tab_title.replace(" ", "_")
            tab_title = tab_title.replace("(", "")
            tab_title = tab_title.replace(")", "")

            if "YR" in tab_title:
                tidy_sheet_list = []
                cs_list = []
                tab_length = len(tab.excel_ref('A')) # number of rows of data
                batch_number = 10 # iterates over this many rows at a time
                number_of_iterations = math.ceil(tab_length/batch_number) # databaking will iterate this many times

                for i in range(0, number_of_iterations):
                    Min = str(3 + batch_number * i)
                    Max = str(int(Min) + batch_number - 1)
                    
                    year = tab.excel_ref("C"+Min+":C"+Max).is_not_blank()
                    if len(year) == 0:
                        break

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

                df = pd.concat(tidy_sheet_list, sort=False) # dataframe for the whole tab
                df.rename(columns={'OBS' : 'Value'}, inplace=True)
                tidied = df[["Year", "Code", "Region", "Country", "Measure Type", "Unit", "Value"]]
                tidied_sheets.append(tidied)

            elif "QR" in tab_title:
                tidy_sheet_list = []
                #tidy_sheet_iteration = []
                cs_list = []

                tab_length = len(tab.excel_ref('A')) # number of rows of data
                batch_number = 10 # iterates over this many rows at a time
                number_of_iterations = math.ceil(tab_length/batch_number) # databaking will iterate this many times

                for i in range(0, number_of_iterations):
                    Min = str(3 + batch_number * i)
                    Max = str(int(Min) + batch_number - 1)

                    year = tab.excel_ref("C"+Min+":C"+Max).is_not_blank()
                    if len(year) == 0:
                        break

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

                df = pd.concat(tidy_sheet_list, sort=False) # dataframe for the whole tab
                df.rename(columns={'OBS' : 'Value'}, inplace=True)

                tidied = df[["Year", "Quarter", "Code", "Region", "Country", "Measure Type", "Unit", "Value"]]
                tidied_sheets.append(tidied)


            elif "Year" in tab_title:
                tidy_sheet_list = []
                cs_list = []
                
                tab_length = len(tab.excel_ref('A')) # number of rows of data
                batch_number = 10 # iterates over this many rows at a time
                number_of_iterations = math.ceil(tab_length/batch_number) # databaking will iterate this many times

                for i in range(0, number_of_iterations):
                    Min = str(2 + batch_number * i)
                    Max = str(int(Min) + batch_number - 1)

                    year = tab.excel_ref("C"+Min+":C"+Max).is_not_blank()
                    if len(year) == 0:
                        break

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

                df = pd.concat(tidy_sheet_list, sort=False) # dataframe for the whole tab
                df.rename(columns={'OBS' : 'Value'}, inplace=True)

                tidied = df[["Year", "Code", "Region", "Country", "Measure Type", "Unit", "Value"]]
                tidied_sheets.append(tidied)

            elif "Qtr" in tab_title:
                tidy_sheet_list = []
                cs_list = []

                tab_length = len(tab.excel_ref('A')) # number of rows of data
                batch_number = 10 # iterates over this many rows at a time
                number_of_iterations = math.ceil(tab_length/batch_number) # databaking will iterate this many times

                for i in range(0, number_of_iterations):
                    Min = str(2 + batch_number * i)
                    Max = str(int(Min) + batch_number - 1)

                    year = tab.excel_ref("C"+Min+":C"+Max).is_not_blank()
                    if len(year) == 0:
                        break

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

                df = pd.concat(tidy_sheet_list, sort=False) # dataframe for the whole tab
                df.rename(columns={'OBS' : 'Value'}, inplace=True)

                tidied = df[["Year", "Quarter", "Code", "Region", "Country", "Measure Type", "Unit", "Value"]]
                tidied_sheets.append(tidied)

        except Exception as err:
            raise Exception(f'failed on source {source_name} and tab {tab.name})') from err
    counter += 1


# In[26]:


formatted_sheets = []
# Regional Trade in goods statistics - Business Count (Exports, proportion method)
df = pd.concat([tidied_sheets[0],tidied_sheets[1],tidied_sheets[8],tidied_sheets[9]], sort = True)
df = df.rename(columns={'Year' : 'Period'})
df['Period'] = df.apply(lambda x: 'year/' + left(str(x['Period']), 4) if 'Q' not in str(x['Quarter']) else 'quarter/' + left(x['Period'], 4) + '-' + x['Quarter'], axis = 1)
df = df.drop(['Code', 'Quarter'], axis=1)
df['Flow'] = df.apply(lambda x: 'exports' if 'Exporters' in x['Measure Type'] else ('imports' if 'Importers' in x['Measure Type'] else 'ERROR'), axis = 1)
df['Marker'] = df.apply(lambda x: 'suppressed' if x['Value'] == '' else '', axis = 1)
df['Value'] = df.apply(lambda x: 0 if x['Marker'] == 'suppressed' else x['Value'], axis = 1)

COLUMNS_TO_NOT_PATHIFY = ['Value', 'Period']
for col in df.columns.values.tolist():
	if col in COLUMNS_TO_NOT_PATHIFY:
		continue
	try:
		df[col] = df[col].apply(pathify)
	except Exception as err:
		raise Exception('Failed to pathify column "{}".'.format(col)) from err

df['Measure Type'] = 'number-of-exporters'
df['Unit'] = 'businesses'
df['Method'] = 'proportion'

df = df[['Period', 'Country', 'Region', 'Flow', 'Method', 'Value', 'Measure Type', 'Unit']]
df['Value'] = df['Value'].astype(int)
# Adding Business counts for PROPORTION method for both IMPORTS and EXPORTS
formatted_sheets.append(df)


# In[27]:


# Regional Trade in goods statistics - Regional Comparison (Exports, proportion method)
df = pd.concat([tidied_sheets[2],tidied_sheets[3],tidied_sheets[10],tidied_sheets[11]], sort = True)
df = df.rename(columns={'Year' : 'Period'})
df['Period'] = df.apply(lambda x: 'year/' + left(str(x['Period']), 4) if 'Q' not in str(x['Quarter']) else 'quarter/' + left(x['Period'], 4) + '-' + x['Quarter'], axis = 1)
df['Unit'] = df.apply(lambda x: 'gbp thousands' if 'thousands' in x['Measure Type'] else x['Unit'], axis = 1)
df['Unit'] = df.apply(lambda x: 'gbp billions' if 'billions' in x['Measure Type'] else x['Unit'], axis = 1)
df['Unit'] = df.apply(lambda x: 'count' if 'Number' in x['Measure Type'] else x['Unit'], axis = 1)
df = df.drop(['Code', 'Quarter'], axis=1)
df['Flow'] = df.apply(lambda x: 'exports' if 'export' in x['Measure Type'] else ('imports' if 'import' in x['Measure Type'] else 'ERROR'), axis = 1)

COLUMNS_TO_NOT_PATHIFY = ['Value', 'Period']

for col in df.columns.values.tolist():
	if col in COLUMNS_TO_NOT_PATHIFY:
		continue
	try:
		df[col] = df[col].apply(pathify)
	except Exception as err:
		raise Exception('Failed to pathify column "{}".'.format(col)) from err


# In[28]:


df['Measure Type'] = df['Measure Type'].str.replace('-ps-thousands','')
df['Measure Type'] = df['Measure Type'].str.replace('-ps-billions','')
df['Unit'] = df['Unit'].str.replace('count','businesses')
df['Method'] = 'proportion'
print(df['Measure Type'].unique())
print(df['Unit'].unique())

# Remove businesses as numbers are rounded differently for some numbers compared to the whole coun method meaning we get duplicate keys in Jenkins
df = df[df['Unit'] != 'businesses']

formatted_sheets.append(df)


# In[29]:


# Regional Trade in goods statistics - Business Count (Exports, whole number method)
df = pd.concat([tidied_sheets[4],tidied_sheets[5],tidied_sheets[12],tidied_sheets[13]], sort = True)
df = df.rename(columns={'Year' : 'Period'})
df['Period'] = df.apply(lambda x: 'year/' + left(str(x['Period']), 4) if 'Q' not in str(x['Quarter']) else 'quarter/' + left(x['Period'], 4) + '-' + x['Quarter'], axis = 1)
df = df.drop(['Code', 'Quarter'], axis=1)
df['Flow'] = df.apply(lambda x: 'exports' if 'Exporters' in x['Measure Type'] else ('imports' if 'Importers' in x['Measure Type'] else 'ERROR'), axis = 1)
df = df[df['Period'] != 'year/None']
df = df[df['Country'] != '0.0']
df['Marker'] = df.apply(lambda x: 'suppressed' if x['Value'] == '' else '', axis = 1)
df['Value'] = df.apply(lambda x: 0 if x['Marker'] == 'suppressed' else x['Value'], axis = 1)

COLUMNS_TO_NOT_PATHIFY = ['Value', 'Period']

for col in df.columns.values.tolist():
	if col in COLUMNS_TO_NOT_PATHIFY:
		continue
	try:
		df[col] = df[col].apply(pathify)
	except Exception as err:
		raise Exception('Failed to pathify column "{}".'.format(col)) from err

df['Value'] = df['Value'].astype(int)


# In[30]:


df['Measure Type'] = 'number-of-exporters'
df['Unit'] = 'businesses'
df['Method'] = 'whole-number'
print(df['Measure Type'].unique())
print(df['Unit'].unique())
df.head(5)
df = df[['Period', 'Country', 'Region', 'Flow', 'Method', 'Value', 'Marker', 'Measure Type', 'Unit']]
formatted_sheets.append(df)


# In[31]:


# Regional Trade in goods statistics - Regional Comparisons (Exports, whole number method)
df = pd.concat([tidied_sheets[6],tidied_sheets[7],tidied_sheets[14],tidied_sheets[15]], sort = True)
df = df.rename(columns={'Year' : 'Period'})
df['Period'] = df.apply(lambda x: 'year/' + left(str(x['Period']), 4) if 'Q' not in str(x['Quarter']) else 'quarter/' + left(x['Period'], 4) + '-' + x['Quarter'], axis = 1)
df['Unit'] = df.apply(lambda x: 'gbp thousands' if 'thousands' in x['Measure Type'] else x['Unit'], axis = 1)
df['Unit'] = df.apply(lambda x: 'gbp billions' if 'billions' in x['Measure Type'] else x['Unit'], axis = 1)
df['Unit'] = df.apply(lambda x: 'count' if 'Number' in x['Measure Type'] else x['Unit'], axis = 1)
df = df.drop(['Code', 'Quarter'], axis=1)
df = df[df['Country'] != '0.0']
df['Flow'] = df.apply(lambda x: 'exports' if 'export' in x['Measure Type'] else ('imports' if 'import' in x['Measure Type'] else 'ERROR'), axis = 1)

COLUMNS_TO_NOT_PATHIFY = ['Value', 'Period']
for col in df.columns.values.tolist():
	if col in COLUMNS_TO_NOT_PATHIFY:
		continue
	try:
		df[col] = df[col].apply(pathify)
	except Exception as err:
		raise Exception('Failed to pathify column "{}".'.format(col)) from err


# In[32]:


df['Measure Type'] = df['Measure Type'].str.replace('-ps-thousands','')
df['Measure Type'] = df['Measure Type'].str.replace('-ps-billions','')
df['Unit'] = df['Unit'].str.replace('count','businesses')
df['Method'] = 'whole-number'
print(df['Measure Type'].unique())
print(df['Unit'].unique())
print(df['Flow'].unique())

# Remove businesses as numbers are rounded differently for some numbers compared to the whole coun method meaning we get duplicate keys in Jenkins
df = df[df['Unit'] != 'businesses']

formatted_sheets.append(df)


# In[33]:


notes = """
Data source

This is additional analysis using the HMRC Regional Trade in Goods Statistics. 

How to interpret the data

Business Count: This data shows the number of businesses importing or exporting goods. This is broken down by their UK region and partner countries.
Regional comparisons: This data shows import or export data within a particular quarter or year for UK regions alongside the same data for the UK. This is based on three metrics; the number of importing or exporting businesses , the value of trade, and the average value per business.

Businesses can appear in more than one quarter and can trade with more than one destination. Therefore users should not add up across quarters or partner countries. 

1. Methodology for allocating businesses to UK regions

As a result of the HMRC RTS methodology consultation the way businesses are allocated to UK region and country has changed. The previous methodology allocated trade to a region based on where the headquarters of a business is located, supplemented by survey data to allow better allocation of multi-site businesses. 
This survey data is out of date and HMRC decided to develop a new methodology.
In the current methodology the trade value of a multi-site business is allocated to different regions based on a proportion of their employees in each region (based on linked information from the Inter Departmental Business Register). 
Data on the number of traders is shown in two different way in the RTS release tables:
Whole Number Method (does not add up to UK total): A business will be counted as one in every region they have employees. This represents the actual count of businesses in any region. However, it will mean the sum of the business count for each region will be greater than that for the UK. 

Proportion Method (adds up to UK total): A business will be counted as a fraction in each region they trade based on the proportion of their employees in each region. An individual business counts as one business in the UK. The sum of businesses (whole and fractions) gives the total business count for a region.
The data in this analysis uses both methods. Please refer to the correct output for each methodology and flow.

2. The number of businesses importing or exporting

Business counts are a count of all VAT Registered businesses exporting and importing. 
Aside from the EU/non-EU split (published as part of the RTS) there is no disaggregation of businesses not required to submit full EU declarations (below threshold traders) by EU partner country. The supplementary analysis provided here does split the number of businesses by EU partner country but these do not include the below threshold traders.

Exclusions
This dataset excludes businesses that cannot be allocated to a region due to lack of information about the business (unallocated - unknown). It does include businesses where details are known, but cannot be allocated due to the type of business (unallocated - known).  Further information can be found in the 

RTS Methodology paper.

This analysis also excludes 'unallocated - unknown' in the UK value totals, in order to make ratios (exports per exporter) and comparisons valid. Where information is known about a business but it is not possible to allocate to a specific region it is classed as 'unallocated - known'. These 'unallocated - known' businesses are included in both the value and count for UK totals.
RTS data excludes trade in non-monetary gold, whereas HMRC OTS data does include this from 2005 onwards. RTS data also excludes non-response estimates. Therefore, it matches the 'total reported trade' figures in the OTS with the exception of non-monetary gold. More information can be found in section 3.20 of the RTS Methodology Paper.

Suppressions
A very small number of cells in the Business Counts tab have been suppressed under our statistical disclosure policy. These are shown a ‘S’ under the business count. Due to a review of disclosure, some data previously suppressed under the output produce by Department for International Trade (Exports proportion method only) may now be shown.
Further information on trade in goods by UK region
HMRC publish quarterly data on trade by UK region in Regional Trade in Goods Statistics. This includes information on the number of exporters to the EU and Non-EU.
https://www.uktradeinfo.com/Statistics/RTS/Pages/default.aspx

Detail on trade value by UK region, trade partner and commodity is available in Build Your Own Tables:
https://www.uktradeinfo.com/Statistics/BuildYourOwnTables/Pages/Home.aspx

2020 data is provisional and subject to update.
"""


# In[34]:


metadata.dataset.comment = "These spreadsheets provide supplementary data to that in the release of the HM Revenue & Customs Regional trade in goods statistics."
metadata.dataset.description = notes
#request from publisher to change title to RTS business counts
metadata.dataset.title = 'RTS Business Counts'
#print(metadata.dataset.title)
#print(metadata.dataset.comment)
#print(metadata.dataset.description)


# In[35]:


print("Number of dataframes in List: " + str(len(formatted_sheets)))
formatted_df = pd.concat(formatted_sheets, sort = True).fillna('')

formatted_df = formatted_df[['Period', 'Country', 'Region', 'Flow', 'Method', 'Measure Type', 'Unit', 'Marker', 'Value']]


# In[36]:


formatted_df.to_csv("observations.csv", index = False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')


# In[37]:


from IPython.core.display import HTML
for col in formatted_df:
    if col not in ['Value']:
        formatted_df[col] = formatted_df[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(formatted_df[col].cat.categories)

