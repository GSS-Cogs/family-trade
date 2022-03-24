# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.7
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
from gssutils import * 
import json 
from urllib.parse import urljoin

df = pd.DataFrame()
tidied_sheets = []
# -

info = json.load(open('info.json')) 
metadata = Scraper(seed="info.json")   
metadata

# +
# distribution = metadata.distributions[0]
# distribution

# +
# distribution = metadata.distributions[0]
# tabs = {tab.name: tab for tab in metadata.distribution(latest = True).as_databaker()}

# +
# list(tabs)
# -



# +
# for name, tab in tabs.items():
#     # if 'Cover_sheet' in name or 'Table_of_contents' in name:
#     if (tab.name == '1989 - 1999') or (tab.name == '2000 - 2010') or (tab.name == '2011 - 2017') or (tab.name == '2018 -'):
#         continue
#     print(tab.name)

# +
# for tab in tabs:
#     print(tab.name)

# +
def left(s, amount):
    return s[:amount]
def right(s, amount):
    return s[-amount:]

def date_time(time_value):
    time_string = str(time_value).replace(".0", "").strip()
    time_len = len(time_string)
    if time_len == 4:
        return "year/" + time_string
    elif time_len == 7:
        return "quarter/{}-{}".format(time_string[3:7], time_string[:2])
    elif time_len == 10:       
        return 'gregorian-interval/' + time_string[:7] + '-01T00:00:00/P3M'


# -

distribution = metadata.distributions[0]
tabs = (t for t in distribution.as_databaker())

for tab in tabs:
       
        datasetTitle = 'ONS-GDP-at-current-prices-real-time-database-YBHA'
        
        if (tab.name == '1989 - 1999') or (tab.name == '2000 - 2010') or (tab.name == '2011 - 2017') or (tab.name == '2018 - '):
            print(tab.name)
            
            seasonal_adjustment = 'SA'

            vintage = tab.filter("Publication date and time period").fill(DOWN).is_not_blank().is_not_whitespace()

            estimate_type_publication = tab.filter("Publication date and time period").fill(RIGHT).is_not_blank().is_not_whitespace()

            observations = vintage.waffle(estimate_type_publication).is_not_blank()

            dimensions = [
                HDim(vintage, 'GDP Reference Period', DIRECTLY, LEFT),
                HDim(estimate_type_publication, 'GDP Estimate Type Publication', DIRECTLY, ABOVE)
            ]
            tidy_sheet = ConversionSegment(tab, dimensions, observations)
            # savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
            tidied_sheets.append(tidy_sheet.topandas())


df = pd.concat(tidied_sheets, sort = True).fillna('')

df

# +
# df = df.sort_values(by='GDP_Estimate_Type_Publication')
# -

df

df[['Publication Date', 'GDP Estimate Type']] = df['GDP Estimate Type Publication'].str.rsplit(n=1, expand = True)

df

df.drop(['GDP Estimate Type Publication'], axis = 1)
df[['GDP Reference Period', 'Publication Date', 'GDP Estimate Type', 'OBS']]

df['Publication Date'].unique()

df['Publication Date'].replace('Q3  1990', 'Q3 1990', inplace=True)  #removing space
df['Publication Date'].replace('Q 2004', 'Q4 2004', inplace=True)

# df['GDP Reference Period'].unique()
df.rename(columns={'OBS' : 'Value'}, inplace=True)

df['GDP Estimate Type'].unique()

# for columns in df.columns:
#     if 'Publication Date' in columns:
#         print(df.columns)
df[['Month', 'Year']] = df['Publication Date'].str.rsplit(pat = "-" ,n=1, expand = True)

df

# Got it
check_condition = ~(df['Year'].isna())
df['Year'].where(check_condition, df['Month'], inplace = True)

df

df['Month'].unique()

df[['Month', 'Year']] = df['Month'].str.rsplit(pat = ' ' ,n=1, expand = True)

df

df[['again_month', 'again_year']] = df['Publication Date'].str.rsplit(pat = "-" ,n=1, expand = True)

df

# Got it
check_condition = ~(df['Year'].isna())
df['Year'].where(check_condition, df['again_year'], inplace = True)

df

df['again_month'] = df['again_month']+' '+df['again_year']

df

# +
# stop

# +
# df

# +
# df = df.drop(columns = ['GDP Estimate Type Publication', 'again_month', 'again_year'])
# -

df

# +
# Year =[]

# for i in df.Year:
#     if df.loc[i, 'Year'] in ['None', 0]:
#         Year.append(df.loc[i, 'Month'])
#     else:
#         Year.append(df.loc[i, 'Year'])

# df['Year'] = Year

# +
# This doesn't make any sense or doesn't do what it is expected to do
# df['Year'] = df['Year'].map(lambda x: x['Month'] if x['Year'] == None else x)
# -

# df = df.apply(lambda x: )
df

df['Month'].unique()
# calendar.month_name[list(calendar.month_abbr).index(['Apr'])]

df['Month'].replace('June', 'Jun', inplace = True)

df['Month'].unique()


# +
# def month_abrev_to_full_name(some_month_abrev_string):
#     month_dict = {"Jan": "January",
#               "Feb": "February",
#               "Mar": "March",
#               "Apr": "April",
#               "May": "May",
#               "Jun": "June",
#               "Jul": "July",
#               "Aug": "August",
#               "Sep": "September",
#               "Oct": "October",
#               "Nov": "November",
#               "Dec": "December"}
#     find_abrev = filter(lambda abrev_month: abrev_month in some_month_abrev_string, month_dict.keys())
#     for abrev in find_abrev:
#         some_month_abrev_string = some_month_abrev_string.replace(abrev, month_dict[abrev])
#     return some_month_abrev_string

# df['Month'] = df['Month'].map(month_abrev_to_full_name)

# +
def month_abrev_to_full_name(some_month_abrev_string):
    month_dict = {"Jan": "Q1",
              "Feb": "Q1",
              "Mar": "Q1",
              "Apr": "Q2",
              "May": "Q2",
              "Jun": "Q2",
              "Jul": "Q3",
              "Aug": "Q3",
              "Sep": "Q3",
              "Oct": "Q4",
              "Nov": "Q4",
              "Dec": "Q4"}
    find_abrev = filter(lambda abrev_month: abrev_month in some_month_abrev_string, month_dict.keys())
    for abrev in find_abrev:
        some_month_abrev_string = some_month_abrev_string.replace(abrev, str(month_dict[abrev]))
    return some_month_abrev_string

df['Month'] = df['Month'].map(month_abrev_to_full_name)
# -

df['Month'].unique()

df['Year'].unique()

df

# +
# stop

# +
# df['Year'] = df['Year'].replace([None], 'Hi', inplace = True)
# -

df['Publication Date'] = df['Month']+' '+df['Year']

df

stop

df[['unwanted_month', 'unwanted_year']] = df['again_month'].str.rsplit(pat = ' ' ,n=1, expand = True)

df

df['unwanted_month'] = df['unwanted_month'].map(month_abrev_to_full_name)

df['qtr'] = pd.to_datetime(df.unwanted_month).dt.quarter

df

stop

df['Year'].unique()

df

df['Month']

# +
# df['Month'] = df.apply(lambda x: pd.to_datetime(df.Month, format='%B').dt.month if x['Month'] == "January" or "February" or "March" or "April" or "May" or "June" or "July" or "August" or "September" or "October" or "November" or "December" else x, axis = 1)

# +
# from time import strptime
# month_number = strptime(df.Month, '%b').tm_mon
# month_number
# This doesn't take Series
# -

stop

# +
# df.rename(columns={'OBS' : 'Value'}, inplace=True)
# #df['CDID'] = df['CDID'].map(lambda x: right(x,4)) #dropped for now
# df['Publication Date'].replace('Q3  1990', 'Q3 1990', inplace=True)  #removing space
# df['Publication Date'].replace('Q 2004', 'Q4 2004', inplace=True) #fixing typo
# df['GDP Reference Period'].replace('Q2 1010', 'Q2 2010', inplace=True) #fixing typo
# df["GDP Reference Period"] = df["GDP Reference Period"].apply(date_time)
# df["Publication Date"] = df["Publication Date"].apply(date_time)
# # df['Marker'].replace('..', 'unknown', inplace=True)
# df = df.fillna('')
# -

# info = json.load(open('info.json')) 
# codelistcreation = info['transform']['codelists'] 
# print(codelistcreation)
# print("-------------------------------------------------------")
#
# codeclass = CSVCodelists()
# for cl in codelistcreation:
#     if cl in df.columns:
#         df[cl] = df[cl].str.replace("-"," ")
#         df[cl] = df[cl].str.capitalize()
#         codeclass.create_codelists(pd.DataFrame(df[cl]), 'codelists', scraper.dataset.family, Path(os.getcwd()).name.lower())

# +
tidy = df[['GDP Reference Period','Publication Date','Value','GDP Estimate Type']]
for column in tidy:
    if column in ('GDP Estimate Type'):
        tidy[column] = tidy[column].str.lstrip()
        tidy[column] = tidy[column].str.rstrip()
        tidy[column] = tidy[column].apply(pathify)

tidy['GDP Estimate Type'] = tidy['GDP Estimate Type'].replace({"m1": "M1", "m2": "M2", "qna": "QNA"})
tidy
# -


df['Publication Date'].unique()

df[6010:6015]


