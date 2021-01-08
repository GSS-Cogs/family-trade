#!/usr/bin/env python
# coding: utf-8
# %%
from gssutils import *
import json

cubes = Cubes("info.json")
scraper_1 = Scraper('https://www.ons.gov.uk/businessindustryandtrade/' + \
                  'internationaltrade/datasets/uktradeinservicesallcountriesnonseasonallyadjusted')
scraper_1
trace = TransformTrace()

# %%
info = json.load(open("info.json"))
scraper_1.dataset.family = info["families"]

# %%
dist_1 = scraper_1.distributions[0]
dist_1

# %%
first_url = dist_1.downloadURL
first_url

# %%
tabs = {tab.name: tab for tab in scraper_1.distribution(latest=True, mediaType=Excel).as_databaker()}


# %%
tab = tabs["TiS by country"]

# %%
tab = tabs['TiS by country']
datasetTitle = "ONS-UK-trade-in-services"
columns = ["Period", "ONS Partner Geography", "Flow", "Trade Services", "Measure Type", "Unit", "Marker"]

# %%
trace.start(datasetTitle, tab, columns, first_url)

# trace.obs("Taken from cell C7 across and down which are non blank")
observations = tab.excel_ref('C7').expand(DOWN).expand(RIGHT).is_not_blank()

trace.Period("Taken from cell C4 across")
period = tab.excel_ref('C4').expand(RIGHT).is_not_whitespace()

trace.Flow("Taken from cells B5 and B252")
flow = tab.excel_ref('B').expand(DOWN).by_index([5,252])

footer = tab.excel_ref("A500").expand(RIGHT).expand(DOWN)

trace.Trade_Services("Hardcoded as all")

trace.ONS_Partner_Geography("Taken from cell A7 down")
ons_partner_geography = tab.excel_ref('A7').expand(DOWN).is_not_blank() - footer

dimensions = [
            HDim(period, 'Period', DIRECTLY,ABOVE),
            HDim(ons_partner_geography, 'ONS Partner Geography', DIRECTLY,LEFT),
            HDim(flow, 'Flow', CLOSEST,ABOVE),
            HDimConst("Trade Services", "all"),
           ]
tidy_sheet = ConversionSegment(tab, dimensions, observations)
savepreviewhtml(tidy_sheet, fname = tab.name + "Preview.html")
trace.with_preview(tidy_sheet)
trace.store("combined_dataframe", tidy_sheet.topandas())

# %%
#scraped second landing page
from gssutils import *
import json

# %%
info = json.load(open("info.json"))
scraper_2 = Scraper(seed="info.json")
scraper_2

# %%
dist_2 = scraper_2.distributions[0]
dist_2

# %%
second_url = dist_2.downloadURL
second_url

# %%
tabs = {tab.name: tab for tab in scraper_2.distribution(latest=True, mediaType=Excel).as_databaker()}

# %%
tab = tabs['Time Series']

datasetTitle = 'UK trade in services by partner country'
columns=["Period", "Flow", "Trade Services", "ONS Partner Geography", "Marker", "Seasonal Adjustment"]
trace.start(datasetTitle, tab, columns, second_url)

observations = tab.excel_ref("F2").expand(RIGHT).expand(DOWN).is_not_blank()

period = tab.excel_ref("F1").expand(RIGHT).is_not_blank()
trace.Period("Values taken from cell ref F1 across. Contains Year and Quarter values")

flow = tab.excel_ref("A2").expand(DOWN).is_not_blank()
trace.Flow("Values taken from cell ref A2 across. Contains exports or imports")

trade_services = tab.excel_ref("B2").expand(DOWN).is_not_blank()
trace.Trade_Services("Values taken from cell ref B2 across")

ons_partner_geography = tab.excel_ref("D2").expand(DOWN).is_not_blank()
trace.ONS_Partner_Geography("Values taken from cell ref D2 down")

dimensions =[
    HDim(period, 'Period', DIRECTLY, ABOVE),
    HDim(flow, 'Flow', DIRECTLY, LEFT),
    HDim(trade_services, 'Trade Services', DIRECTLY, LEFT),
    HDim(ons_partner_geography, 'ONS Partner Geography', DIRECTLY, LEFT),
]

tidy_sheet = ConversionSegment(tab, dimensions, observations)
savepreviewhtml(tidy_sheet, fname = tab.name +"PREVIEW.html")
trace.with_preview(tidy_sheet)
trace.store("combined_dataframe", tidy_sheet.topandas())

# %%
new_table = trace.combine_and_trace(datasetTitle, "combined_dataframe")

# %%
new_table

# %%
trace.add_column("Renaming OBS column into Value and DATAMARKER column into Marker")
new_table.rename(columns = {'OBS':'Value', 'DATAMARKER':'Marker'},inplace = True)
new_table

# %%
new_table['Value'] = pd.to_numeric(new_table['Value'], errors = 'coerce')


# %%
def left(s, amount):
    return s[:amount]
def right(s, amount):
    return s[-amount:]
def date_time (date):
    if len(date)  == 5:
        return 'year/' + left(date, 4)
    #year/2019
    elif len(date) == 6:
        return 'quarter/' + left(date,4) + '-' + right(date,2)
    #quarter/2019-01
    else:
        return date


# %%
new_table['Period'] = new_table['Period'].astype(str).replace('\.', '', regex=True)
new_table['Period'] =  new_table["Period"].apply(date_time)
trace.Period("Formating to be year/0000 and quarter/2019-01 ")

# %%
new_table = new_table.replace({'Marker' : {'-' : 'itis-nil', '..' : 'disclosive'}})
trace.Marker("Replcaing - to mean itis-nil and .. to mean disclosive")

# %%
new_table['Seasonal Adjustment'] =  'NSA'
trace.Seasonal_Adjustment("Adding in column Seasonal Adjustment with value NSA")

# %%
new_table['Flow'] = new_table['Flow'].apply(pathify)

# %%
tidy = new_table[['ONS Partner Geography', 'Period','Flow','Trade Services', 'Seasonal Adjustment', 'Value', 'Marker' ]]

# %%
tidy = tidy.drop_duplicates()
tidy

# %%
cubes.add_cube(scraper_1, tidy, "ONS UK trade in services by country" )
cubes.add_cube(scraper_2, tidy, "ONS UK trade in services by partner country")
cubes.output_all()

# %%
trace.render("spec_v1.html")

# %%
# NOT SURE IF THIS CODE IS REQUIRED
# new_table = new_table.loc[new_table['ONS_Partner_Geography'].isin(['AD','AE','AF','AG','AI','AM','AO','AQ','AS','AW','AZ','BA','BB','BD','BF',	
#                                                                 'BH','BI','BJ','BM','BN','BO','BQ','BS','BT','BV','BW','BZ','CC','CD','CF',
#                                                                 'CG','CI','CK','CM','CR','CU','CV','CW','CX','D5','DJ','DM','DO','DZ','EC',
#                                                                 'ER','ET','FJ','FK','FM','FO','GA','GD','GE','GG','GH','GI','GL','GM','GN',
#                                                                 'GQ','GS','GT','GU','GW','GY','HM','HN','HT','IM','IO','IQ','JE','JM','JO',
#                                                                 'KE','KG','KH','KI','KM','KN','KP','KW','KY','KZ','LA',	'LB','LC','LK','LR',
#                                                                 'LS','LY','MD','MG','MH','MK','ML','MM','MN','MO','MP','MR','MS','MU','MV',
#                                                                 'MW','MZ','NA','NC','NE','NF','NG','NI','NP','NR','NU','OM','PA','PE','PF',
#                                                                 'PG','PN','PS','PW','PY','QA','RW','SB','SC','SD','SH','SL','SM','SN','SO',
#                                                                 'SR','SS','ST','SV','SX','SY','SZ','TC','TD','TF','TG','TJ','TK','TL','TM',
#                                                                 'TN','TO','TT','TV','TZ','UG','UM','UZ','VA','VC','VG','VI','VN','VU','WF',
#                                                                 'WS','XK','YE','ZM','ZW'])]
