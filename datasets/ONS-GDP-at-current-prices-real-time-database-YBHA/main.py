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
# metadata

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

df[['Publication Date', 'GDP Estimate Type']] = df['GDP Estimate Type Publication'].str.rsplit(n=1, expand = True)

df.drop(['GDP Estimate Type Publication'], axis = 1)
df[['GDP Reference Period', 'Publication Date', 'GDP Estimate Type', 'OBS']]

df['Publication Date'].replace('Q3  1990', 'Q3 1990', inplace=True)  #removing space
df['Publication Date'].replace('Q 2004', 'Q4 2004', inplace=True)

df.rename(columns={'OBS' : 'Value'}, inplace=True)

df['GDP Estimate Type'].unique()

df[['Month', 'Year']] = df['Publication Date'].str.rsplit(pat = "-" ,n=1, expand = True)

check_condition = ~(df['Year'].isna())
df['Year'].where(check_condition, df['Month'], inplace = True)

df[['Month', 'Year']] = df['Month'].str.rsplit(pat = ' ' ,n=1, expand = True)

df[['again_month', 'again_year']] = df['Publication Date'].str.rsplit(pat = "-" ,n=1, expand = True)

check_condition = ~(df['Year'].isna())
df['Year'].where(check_condition, df['again_year'], inplace = True)

df['again_month'] = df['again_month']+' '+df['again_year']

df = df.drop(columns = ['GDP Estimate Type Publication', 'again_month', 'again_year'])

df['Month'].replace('June', 'Jun', inplace = True)


# +
def month_abrev_to_quarter(some_month_abrev_string):
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

df['Month'] = df['Month'].map(month_abrev_to_quarter)
# -

df['Publication Date'] = df['Month']+' '+df['Year']

df = df.drop(columns = ['Month', 'Year'])

df.drop_duplicates(subset = df.columns.difference(['Value']), inplace = True)

duplicate_df = df[df.duplicated(['GDP Reference Period', 'Value', 'Publication Date',
       'GDP Estimate Type'], keep = False)]
duplicate_df

df["GDP Reference Period"] = df["GDP Reference Period"].apply(date_time)
df["Publication Date"] = df["Publication Date"].apply(date_time)

df[['GDP Reference Period', 'GDP Estimate Type', 'Publication Date', 'Value']]

df.to_csv("observations.csv", index = False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('catalog-metadata.json')
