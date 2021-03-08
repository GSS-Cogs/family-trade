#!/usr/bin/env python
# coding: utf-8
# %% [markdown]
# ### ONS Quarterly National Accounts
#

# %%
from gssutils import *
import json

trace = TransformTrace()
df = pd.DataFrame()
cubes = Cubes("info.json")
info = json.load(open('info.json'))
scraper = Scraper(seed = 'info.json')
distribution = scraper.distribution(latest = True)
tabs = { tab.name: tab for tab in distribution.as_databaker() }
distribution

# %%
#grouping tab into topics to iterate through by their names
national_account_aggregates = ['A1 AGGREGATES', 'A2 AGGREGATES']
output_indicators = ['B1 CVM OUTPUT', 'B2 CVM OUTPUT']
expenditure_indicators = ['C1 EXPENDITURE', 'C2 EXPENDITURE']
income_indicators = ['D INCOME']
household_expenditure_indicators = ['E1 EXPENDITURE', 'E2 EXPENDITURE', 'E3 EXPENDITURE', 'E4 EXPENDITURE']
gross_fixed_capitol = ['F1 GFCF', 'F2 GFCF']
inventories = ['G1 INVENTORIES', 'G2 INVENTORIES']
trade = ['H1 TRADE', 'H2 TRADE']

tidied_sheets = []

# %%
for name, tab in tabs.items():
    #shared dimensions across all tabs
    seasonal_adjustment = tab.excel_ref('A5').expand(DOWN).filter(contains_string('Seasonally'))
    period = tab.excel_ref('A6').expand(DOWN).is_not_blank() - seasonal_adjustment
    p_change =  tab.excel_ref('A6').expand(DOWN).filter(contains_string('Percentage')) 
    measure = tab.excel_ref('G1').expand(RIGHT).is_not_blank()
    
    if name in national_account_aggregates:
       
        cdid = tab.excel_ref('B4').expand(RIGHT).is_not_blank() | p_change.shift(0,2).expand(RIGHT).is_not_blank()
        indicies = tab.excel_ref('C2').expand(RIGHT).is_not_blank()
        gross = tab.excel_ref('C3').expand(RIGHT).is_not_blank()
        observations = cdid.fill(DOWN).is_not_blank().is_not_whitespace() - cdid
        
        dimensions = [
            HDim(period,'Period',DIRECTLY,LEFT),
            HDim(seasonal_adjustment,'Seasonal Adjustment',CLOSEST,ABOVE),
            HDim(p_change, 'Percentage Change',CLOSEST,ABOVE),
            HDim(cdid, 'CDID',DIRECTLY,ABOVE),
            HDim(indicies, 'Indicies',CLOSEST,LEFT),
            HDim(gross, 'gross',DIRECTLY,ABOVE),
            HDim(measure, 'measure',CLOSEST,ABOVE),
        ]
        c1 = ConversionSegment(tab, dimensions, observations)  
        #savepreviewhtml(c1, fname=tab.name + "Preview.html")
        tidy_sheet = c1.topandas()
        tidied_sheets.append(tidy_sheet)
        
    elif name in output_indicators:
        cdid = tab.excel_ref('B5').expand(RIGHT).is_not_blank() | p_change.shift(0,1).expand(RIGHT).is_not_blank()
        observations = cdid.fill(DOWN).is_not_blank().is_not_whitespace() - cdid
        sector = tab.excel_ref('B2').expand(RIGHT).is_not_blank()
        industry = tab.excel_ref('B3').expand(RIGHT).is_not_blank()
        weights = tab.excel_ref('B4').expand(RIGHT).is_not_blank()
        
        dimensions = [
            HDim(period,'Period',DIRECTLY,LEFT),
            HDim(seasonal_adjustment,'Seasonal Adjustment',CLOSEST,ABOVE),
            HDim(p_change, 'Percentage Change',CLOSEST,ABOVE),
            HDim(cdid, 'CDID',DIRECTLY,ABOVE),
            HDim(weights, '2018 Weights',DIRECTLY,ABOVE),
            HDim(sector, 'Sector',CLOSEST,LEFT),
            HDim(industry, 'Industry',DIRECTLY,ABOVE),
            HDim(measure, 'measure',CLOSEST,ABOVE),
            
        ]
        c1 = ConversionSegment(tab, dimensions, observations)   
        #savepreviewhtml(c1, fname=tab.name + "Preview.html")
        tidy_sheet = c1.topandas()
        tidied_sheets.append(tidy_sheet)
    elif name in expenditure_indicators:
        cdid = tab.excel_ref('B5').expand(RIGHT).is_not_blank() | p_change.shift(1,1).expand(RIGHT).is_not_blank() | p_change.shift(1,2).expand(RIGHT).is_not_blank().is_not_number()
        cdid = cdid - cdid.shift(0,1).expand(RIGHT)
        expenditure = tab.excel_ref('C3').expand(RIGHT).is_not_blank()
        expenditure_cat = tab.excel_ref('C4').expand(RIGHT).is_not_blank()
        
        observations = cdid.fill(DOWN).is_not_blank().is_not_whitespace() - cdid
        dimensions = [
            HDim(period,'Period',DIRECTLY,LEFT),
            HDim(seasonal_adjustment,'Seasonal Adjustment',CLOSEST,ABOVE),
            HDim(p_change, 'Percentage Change',CLOSEST,ABOVE),
            HDim(cdid, 'CDID',DIRECTLY,ABOVE),
            HDim(measure, 'measure',CLOSEST,ABOVE),
            HDim(expenditure, 'Expenditure',CLOSEST,LEFT),
            HDim(expenditure_cat, 'Expendisture Category',DIRECTLY,ABOVE),
        ]
        c1 = ConversionSegment(tab, dimensions, observations)   
        #savepreviewhtml(c1, fname=tab.name + "Preview.html")
        tidy_sheet = c1.topandas()
        tidied_sheets.append(tidy_sheet)
    elif name in income_indicators:
        cdid = tab.excel_ref('B4').expand(RIGHT).is_not_blank() | p_change.shift(0,2).expand(RIGHT).is_not_blank()
        cat_income = tab.excel_ref('A3').expand(RIGHT).is_not_blank()
        gross = tab.excel_ref('A2').expand(RIGHT).is_not_blank()
        observations = cdid.fill(DOWN).is_not_blank() - cdid
        dimensions = [
            HDim(period,'Period',DIRECTLY,LEFT),
            HDim(seasonal_adjustment,'Seasonal Adjustment',CLOSEST,ABOVE),
            HDim(p_change, 'Percentage Change',CLOSEST,ABOVE),
            HDim(cdid, 'CDID',DIRECTLY,ABOVE),
            HDim(measure, 'measure',CLOSEST,ABOVE),
            HDim(gross, 'Gross Domestic Product',CLOSEST,LEFT),
            HDim(cat_income, 'Category of Income',DIRECTLY,ABOVE),

        ]
        c1 = ConversionSegment(tab, dimensions, observations)   
        #savepreviewhtml(c1, fname=tab.name + "Preview.html")
        tidy_sheet = c1.topandas()
        tidied_sheets.append(tidy_sheet)
        
    elif name in household_expenditure_indicators:
        if name in household_expenditure_indicators[0] or name in household_expenditure_indicators[2]:
            cdid = tab.excel_ref('B6').expand(RIGHT).is_not_blank() | p_change.shift(0,2).expand(RIGHT).is_not_blank()
            COICOP = tab.excel_ref('B5').expand(RIGHT).is_not_blank()
            measure = tab.excel_ref('G1').expand(RIGHT).is_not_blank()
            expenditure = tab.excel_ref('B4').expand(RIGHT).is_not_blank()
        else:
            cdid = tab.excel_ref('B8').expand(RIGHT).is_not_blank() | p_change.shift(0,2).expand(RIGHT).is_not_blank()
            COICOP = tab.excel_ref('B7').expand(RIGHT)
            measure = tab.excel_ref('G2').expand(RIGHT).is_not_blank()
            expenditure = tab.excel_ref('B6').expand(RIGHT).is_not_blank()
            
        observations = cdid.fill(DOWN).is_not_blank().is_not_whitespace() - cdid
        dimensions = [
            HDim(period,'Period',DIRECTLY,LEFT),
            HDim(seasonal_adjustment,'Seasonal Adjustment',CLOSEST,ABOVE),
            HDim(p_change, 'Percentage Change',CLOSEST,ABOVE),
            HDim(cdid, 'CDID',DIRECTLY,ABOVE),
            HDim(COICOP, 'COICOP',DIRECTLY,ABOVE),
            HDim(expenditure, 'Household Expenditure',DIRECTLY,ABOVE),
            HDim(measure, 'measure',CLOSEST,ABOVE),

        ]
        c1 = ConversionSegment(tab, dimensions, observations)   
        #savepreviewhtml(c1, fname=tab.name + "Preview.html")
        tidy_sheet = c1.topandas()
        tidied_sheets.append(tidy_sheet)
    elif name in gross_fixed_capitol:
        cdid = tab.excel_ref('B5').expand(RIGHT).is_not_blank() | p_change.shift(0,2).expand(RIGHT).is_not_blank()
        analysis_by = tab.excel_ref('B2').expand(RIGHT).is_not_blank()
        observations = cdid.fill(DOWN).is_not_blank().is_not_whitespace() - cdid
        capitol_formation = tab.excel_ref('B4').expand(RIGHT).is_not_blank()
        dimensions = [
            HDim(period,'Period',DIRECTLY,LEFT),
            HDim(seasonal_adjustment,'Seasonal Adjustment',CLOSEST,ABOVE),
            HDim(p_change, 'Percentage Change',CLOSEST,ABOVE),
            HDim(cdid, 'CDID',DIRECTLY,ABOVE),
            HDim(analysis_by, 'analysed by',CLOSEST,LEFT),
            HDim(capitol_formation, 'Capital Formation',DIRECTLY,ABOVE),
            HDim(measure, 'measure',CLOSEST,ABOVE),
        ]
        c1 = ConversionSegment(tab, dimensions, observations)   
        #savepreviewhtml(c1, fname=tab.name + "Preview.html")
        tidy_sheet = c1.topandas()
        tidied_sheets.append(tidy_sheet)
    elif name in inventories:
        cdid = tab.excel_ref('B5').expand(RIGHT).is_not_blank() | p_change.shift(0,2).expand(RIGHT).is_not_blank()
        observations = cdid.fill(DOWN).is_not_blank().is_not_whitespace() - cdid
        sector = tab.excel_ref('B3').expand(RIGHT).is_not_blank() 
        level_held_title = tab.excel_ref('A4').is_not_blank() 
        level_held = level_held_title.expand(RIGHT).is_not_blank()
        dimensions = [
            HDim(period,'Period',DIRECTLY,LEFT),
            HDim(seasonal_adjustment,'Seasonal Adjustment',CLOSEST,ABOVE),
            HDim(p_change, 'Percentage Change',CLOSEST,ABOVE),
            HDim(cdid, 'CDID',DIRECTLY,ABOVE),
            HDim(sector, 'Sector',DIRECTLY,ABOVE),
            HDim(level_held, 'Level of inventories held at end-December 2018',DIRECTLY,ABOVE),
            HDim(measure, 'measure',CLOSEST,ABOVE),
        ]
        c1 = ConversionSegment(tab, dimensions, observations)   
        #savepreviewhtml(c1, fname=tab.name + "Preview.html")
        tidy_sheet = c1.topandas()
        tidied_sheets.append(tidy_sheet)
    elif name in trade: 
        if name in trade[0]:
            cdid = tab.excel_ref('B5').expand(RIGHT).is_not_blank() | p_change.shift(0,2).expand(RIGHT).is_not_blank()
            goods_services = tab.excel_ref('B3').expand(RIGHT).is_not_blank() 
            flow = tab.excel_ref('B2').expand(RIGHT)#.is_not_blank() 
        else:
            cdid = tab.excel_ref('B6').expand(RIGHT).is_not_blank() | p_change.shift(0,1).expand(RIGHT).is_not_blank()
            measure = tab.excel_ref('C2').expand(RIGHT).is_not_blank()
            goods_services = tab.excel_ref('B4').expand(RIGHT).is_not_blank() 
            flow = tab.excel_ref('B3').expand(RIGHT)#.is_not_blank() 
        observations = cdid.fill(DOWN).is_not_blank().is_not_whitespace() - cdid
        
        dimensions = [
            HDim(period,'Period',DIRECTLY,LEFT),
            HDim(seasonal_adjustment,'Seasonal Adjustment',CLOSEST,ABOVE),
            HDim(p_change, 'Percentage Change',CLOSEST,ABOVE),
            HDim(cdid, 'CDID',DIRECTLY,ABOVE),
            HDim(flow, 'Flow',DIRECTLY,ABOVE),
            HDim(goods_services, 'Goods or Services',DIRECTLY,ABOVE),
            HDim(measure, 'measure',CLOSEST,ABOVE),
        ]
        c1 = ConversionSegment(tab, dimensions, observations)   
        #savepreviewhtml(c1, fname=tab.name + "Preview.html")
        tidy_sheet = c1.topandas()
        tidied_sheets.append(tidy_sheet)
    else:
        continue


# %% [markdown]
#     Tabs transformed and appended to tidied_sheets to make it easier to understand for a DM.. hopefully 
#     Things to note, I have done no post processing atm due to this being a little annoying and want clarity from a DM first. 
#
# ##### National Accounts aggregates 
#     tidied_sheets[0] (A1 AGGREGATES)
#     tidied_sheets[1] (A2 AGGREGATES)
#   
# ##### Output indicators
#     tidied_sheets[2] (B1 CVM OUTPUT)
#     tidied_sheets[3] (B2 CVM OUTPUT)
#     
# ##### Expenditure Indicators 
#     tidied_sheets[4] (C1 Expenditure)
#     tidied_sheets[5] (C2 Expenditure)
#    
# ##### Income indicators
#     tidied_sheets[6] (D Income)
#     
# ##### Household Expendisture Indicators
#     tidied_sheets[7] (E1 Expenditure)
#     tidied_sheets[8] (E2 Expenditure)
#     tidied_sheets[9] (E3 Expenditure)
#     tidied_sheets[10](E4 Expenditure)
#     
#     Note another dimension will need to be added during post processsing called something like 'Expenditure Category' which will either be: Public corporations or Private sector, depending on the value in Household expenditure dimension. 
#    
#
# ##### Gross Fixed Capitol 
#     tidied_sheets[11](F1 GFCF)
#     tidied_sheets[12](F1 GFCF)
#      
#      Note another dimension will need to be added during post processsing called something like 'Sector' which will either be: UK National or UK dommestic, depending on the value in Capital Formation dimension.    
#
# ##### Inventories 
#     tidied_sheets[13](G1 Inventories)
#     tidied_sheets[14](G2 Inventories)
#     
#     Note another dimension will need to be added during post processsing called something like 'Industry' which will either be: Manufacturing industries or Distributive, depending on the value in Sector dimension.    
#     
# ##### Trade 
#     tidied_sheets[15](H1 TRADE)
#     tidied_sheets[16](H2 TRADE)
#     
#     Note I will need to do a bit of wrangling to fix the flow dimension in post processing, this is due to some tables using a horrible centered headings for flow values. 
#     
# ##### Other 
#
#     The following tabs were not included when this was previously done, is this still the case ?
#     
#     
#      'L GVAbp',
#      'M Alignment adjustments',
#      'N Financial Year Variables',
#      'O Selected imp def',
#      'P GDP per head',
#      'R Quarterly Revisions',
#      'AA Annex A',
#      'AB Annex B',
#      'AC Annex C',
#      'AD Annex D',
#      'AE Annex E',
#      'AF Annex F',
#      'AG Annex G'
#      
