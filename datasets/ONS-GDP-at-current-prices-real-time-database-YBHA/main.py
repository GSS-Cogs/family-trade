# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
from gssutils import * 
import json 
from urllib.parse import urljoin

cubes = Cubes("info.json")
trace = TransformTrace()
df = pd.DataFrame()
tidied_sheets = []
# -

info = json.load(open('info.json')) 
scraper = Scraper(seed="info.json")   
scraper 

distribution = scraper.distributions[0]
tabs = (t for t in distribution.as_databaker())


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

for tab in tabs:
       
        datasetTitle = 'ONS-GDP-at-current-prices-real-time-database-YBHA'
        columns=['Vintage','Publication','Estimate Type', 'CDID', 'Seasonal Adjustment', 'Marker']
        trace.start(datasetTitle, tab, columns, scraper.distributions[0].downloadURL)
        
        if (tab.name == '1989 - 1999') or (tab.name == '2000 - 2010') or (tab.name == '2011 - 2017') or (tab.name == '2018 -'):
            
            seasonal_adjustment = 'SA'
            trace.Seasonal_Adjustment("Hardcoded as SA, taken from source")
            
            code = tab.excel_ref('B3')
            trace.CDID("Taken from cell ref B3")
            
            vintage = tab.excel_ref('A6').expand(DOWN).is_not_blank() 
            trace.Vintage("Taken from cell A6 down")
            
            estimate_type = tab.excel_ref('B6').expand(RIGHT).is_not_blank()
            trace.Estimate_Type("Taken from cell B6 across")
            
            publication = tab.excel_ref('B7').expand(RIGHT).is_not_blank()
            trace.Publication("Taken from cell B7 across")
                
            if (tab.name == '2011 - 2017') or (tab.name == '2018 -'):
                estimate_type = tab.excel_ref('B5').expand(RIGHT).is_not_blank()
                trace.Estimate_Type("Taken from cell B5 across")
                
                publication = tab.excel_ref('B6').expand(RIGHT).is_not_blank()
                trace.Publication("Taken from cell B6 across")
        
            observations = publication.fill(DOWN).is_not_blank()
        
            dimensions = [
                HDim(vintage, 'GDP Reference Period', DIRECTLY, LEFT),
                HDim(estimate_type, 'GDP Estimate Type', DIRECTLY, ABOVE),
                HDim(publication, 'Publication Date', DIRECTLY, ABOVE),
                #HDim(code, 'CDID', CLOSEST, ABOVE), #dropped for now
                #HDimConst('Seasonal Adjustment', seasonal_adjustment), #dropped for now
            ]

            tidy_sheet = ConversionSegment(tab, dimensions, observations)        
            #savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
            trace.with_preview(tidy_sheet)
            trace.store("combined_dataframe", tidy_sheet.topandas())


df = trace.combine_and_trace(datasetTitle, "combined_dataframe")
df.rename(columns={'OBS' : 'Value','DATAMARKER' : 'Marker'}, inplace=True)
#df['CDID'] = df['CDID'].map(lambda x: right(x,4)) #dropped for now
df['Publication Date'].replace('Q3  1990', 'Q3 1990', inplace=True)  #removing space
df['Publication Date'].replace('Q 2004', 'Q4 2004', inplace=True) #fixing typo
df['GDP Reference Period'].replace('Q2 1010', 'Q2 2010', inplace=True) #fixing typo
df["GDP Reference Period"] = df["GDP Reference Period"].apply(date_time)
df["Publication Date"] = df["Publication Date"].apply(date_time)
df['Marker'].replace('..', 'unknown', inplace=True)
df = df.fillna('')

df['Marker'].unique()

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
tidy = df[['GDP Reference Period','Publication Date','Value','GDP Estimate Type','Marker']]
for column in tidy:
    if column in ('GDP Estimate Type'):
        tidy[column] = tidy[column].str.lstrip()
        tidy[column] = tidy[column].str.rstrip()
        tidy[column] = tidy[column].apply(pathify)

tidy['GDP Estimate Type'] = tidy['GDP Estimate Type'].replace({"m1": "M1", "m2": "M2", "qna": "QNA"})

cubes.add_cube(scraper, tidy, "GDP at current prices – real-time database (YBHA)")
tidy
# -


cubes.output_all()
trace.render()
