#!/usr/bin/env python
# coding: utf-8
# %% [markdown]
# ### ONS Quarterly National Accounts
#

# %%
from gssutils import *
import json
import copy 
import numpy as np

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
def with_indices_overrides(indices_dimension):
    """
    Adding a cellvalue overrides to each cell within the dimension AFTER
    it's been defined.
    So replacing the value of any dimensions cells that are blank with the appropriate index (or indice).
    """
    not_blank_cells = [cell for cell in indices_dimension.hbagset if cell.value != '']
    for cell in indices_dimension.hbagset:
        # If a dimension cell is blank
        if cell.value == '': 
            # Is there a value two cells to the left? if so use that value
            cell_checked = [cell for cell in not_blank_cells if cell.x == cell.x-2]
            if len(cell_checked) > 0:
                indices_dimension.AddCellValueOverride(cell, cell_checked[0].value)
           
        # Is there a value one cell to the left? if so use that value
            cell_checked = [cell for cell in not_blank_cells if cell.x == cell.x-1]
            if len(cell_checked) > 0:
                indices_dimension.AddCellValueOverride(cell, cell_checked[0].value)
                
            # Is there a value one cells to the right? if so use that value
            cell_checked = [cell for cell in not_blank_cells if cell.x == cell.x+1]
            if len(cell_checked) > 0:
                indices_dimension.AddCellValueOverride(cell, cell_checked[0].value)
                
            # Is there a value two cells to the right? if so use that value
            cell_checked = [cell for cell in not_blank_cells if cell.x == cell.x+1]
            if len(cell_checked) > 0:
                indices_dimension.AddCellValueOverride(cell, cell_checked[0].value)
    
    return indices_dimension


# %%
for name, tab in tabs.items():
    #shared dimensions across all tabs
    seasonal_adjustment = tab.excel_ref('A5').expand(DOWN).filter(contains_string('Seasonally'))
    period = tab.excel_ref('A6').expand(DOWN).is_not_blank() - seasonal_adjustment
    measure = tab.excel_ref('G1').expand(RIGHT).is_not_blank()
    p_change =  tab.excel_ref('A6').expand(DOWN).filter(contains_string('Percentage'))  | tab.excel_ref('A3')
   
    if name in national_account_aggregates:
        cdid = tab.excel_ref('B4').expand(RIGHT).is_not_blank() | p_change.shift(1,2).expand(RIGHT).is_not_blank()
        gross = tab.excel_ref('C3').expand(RIGHT).is_not_blank()
        observations = cdid.fill(DOWN).is_not_blank().is_not_whitespace() - cdid
        gross = tab.excel_ref('C3').expand(RIGHT).is_not_blank()
        indices = gross.shift(UP)
        
        dimensions = [
            HDim(period,'Period',DIRECTLY,LEFT),
            HDim(seasonal_adjustment,'Seasonal Adjustment',CLOSEST,ABOVE),
            HDim(p_change, 'Percentage Change',CLOSEST,ABOVE),
            HDim(cdid, 'CDID',DIRECTLY,ABOVE),
            HDim(indices, 'Indices', DIRECTLY, ABOVE), 
            HDim(gross, 'Gross', DIRECTLY, ABOVE),
            HDim(gross, 'gross',DIRECTLY,ABOVE),
            HDim(measure, 'measure',CLOSEST,ABOVE),
        ]
        
        dimensions[0] = with_indices_overrides(dimensions[0])
        c1 = ConversionSegment(tab, dimensions, observations)  
        #savepreviewhtml(c1, fname=tab.name + "Preview.html")
        tidy_sheet = c1.topandas()
        tidy_sheet = tidy_sheet.replace(r'^\s*$', np.nan, regex=True)
        tidied_sheets.append(tidy_sheet)
        
    elif name in output_indicators:
        cdid = tab.excel_ref('B5').expand(RIGHT).is_not_blank() | p_change.shift(1,1).expand(RIGHT).is_not_blank()
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
        tidy_sheet = tidy_sheet.replace(r'^\s*$', np.nan, regex=True)
        tidied_sheets.append(tidy_sheet)
        
    elif name in expenditure_indicators:
        p_change =  tab.excel_ref('A6').expand(DOWN).filter(contains_string('Percentage'))  | tab.excel_ref('C6')
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
        tidy_sheet = tidy_sheet.replace(r'^\s*$', np.nan, regex=True)
        tidied_sheets.append(tidy_sheet)
    elif name in income_indicators:
        cdid = tab.excel_ref('B4').expand(RIGHT).is_not_blank() | p_change.shift(1,2).expand(RIGHT).is_not_blank()
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
        tidy_sheet = tidy_sheet.replace(r'^\s*$', np.nan, regex=True)
        tidied_sheets.append(tidy_sheet)
        
    elif name in household_expenditure_indicators:
        if name in household_expenditure_indicators[0] or name in household_expenditure_indicators[2]:
            cdid = tab.excel_ref('B6').expand(RIGHT).is_not_blank() | p_change.shift(1,2).expand(RIGHT).is_not_blank()
            COICOP = tab.excel_ref('B5').expand(RIGHT).is_not_blank()
            measure = tab.excel_ref('G1').expand(RIGHT).is_not_blank()
            expenditure = tab.excel_ref('B4').expand(RIGHT).is_not_blank()
        else:
            p_change =  tab.excel_ref('A6').expand(DOWN).filter(contains_string('Percentage'))  | tab.excel_ref('B6')
            cdid = tab.excel_ref('B8').expand(RIGHT).is_not_blank() | p_change.shift(1,2).expand(RIGHT).is_not_blank()
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
        tidy_sheet = tidy_sheet.replace(r'^\s*$', np.nan, regex=True)
        tidied_sheets.append(tidy_sheet)
    elif name in gross_fixed_capitol:
        cdid = tab.excel_ref('B5').expand(RIGHT).is_not_blank() | p_change.shift(1,2).expand(RIGHT).is_not_blank()
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
        tidy_sheet = tidy_sheet.replace(r'^\s*$', np.nan, regex=True)
        tidied_sheets.append(tidy_sheet)
    elif name in inventories:
        cdid = tab.excel_ref('B5').expand(RIGHT).is_not_blank() | p_change.shift(1,2).expand(RIGHT).is_not_blank()
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
        tidy_sheet = tidy_sheet.replace(r'^\s*$', np.nan, regex=True)
        tidied_sheets.append(tidy_sheet)
    elif name in trade: 
        if name in trade[0]:
            cdid = tab.excel_ref('B5').expand(RIGHT).is_not_blank() | p_change.shift(1,2).expand(RIGHT).is_not_blank()
            goods_services = tab.excel_ref('B3').expand(RIGHT).is_not_blank() 
            flow = tab.excel_ref('B2').expand(RIGHT)#.is_not_blank() 
        else:
            cdid = tab.excel_ref('B6').expand(RIGHT).is_not_blank() | p_change.shift(1,1).expand(RIGHT).is_not_blank()
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
        tidy_sheet = tidy_sheet.replace(r'^\s*$', np.nan, regex=True)
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

# %%
import numpy as np

def strip_superscripts(dataset, dimension):
    try:
        for x in range(1, 11):
            comnum = str(x) + ','
            dataset[dimension] = dataset[dimension].str.replace(comnum, '', regex=False) 
            dataset[dimension] = dataset[dimension].str.replace(str(x), '', regex=False) 
            dataset[dimension] = dataset[dimension].str.strip()
            
        return dataset
    except Exception as e:
        print('strip_superscripts error: ' + str(e))
        return dataset
    

def prefix_refperiod(dataset, dimension):
    try:
        dataset[dimension] = 'quarter/' + dataset[dimension].astype(str)
        dataset[dimension] = dataset[dimension].str.replace(' ','-')
        for x in range(1930, 2030):
            dataset[dimension].loc[dataset[dimension] == 'quarter/' + str(x) + '.0'] = 'year/' + str(x)
            
        return dataset
    except Exception as e:
        print('prefix_refperiod: ' + str(e))
        return dataset
    
    
def convet_dimension_to_int(dataset, dimension):
    try:
        dataset[dimension] = dataset[dimension].fillna(-1)
        dataset[dimension] = dataset[dimension].replace('',-1)
        dataset[dimension] = dataset[dimension].astype(int)
        dataset[dimension] = dataset[dimension].astype(str)
        dataset[dimension] = dataset[dimension].replace('-1', np.nan)
        return dataset
    except Exception as e:
        print('convet_dimension_to_int: ' + str(e))
        return dataset


# %%
cubes = Cubes("info.json")

# %%
# A2
a2 = tidied_sheets[1]
# Only use the main value data for now
try:
    a2 = a2.loc[a2['Percentage Change'].isna()] 
except:
    ind = ind 

a2 = prefix_refperiod(a2, 'Period')

a2['gross'].loc[a2['CDID'] == 'YBHA'] = 'Gross domestic product at market prices'  
a2['Indices'].loc[a2['CDID'] == 'YBHA'] = 'Current prices'

a2 = strip_superscripts(a2, 'gross')
    
a2['Indices'].loc[a2['Indices'] == 'Current prices'] = 'current-price'
a2['Indices'].loc[a2['Indices'] == 'Chained Volume Measure (Reference year 2018)'] = 'chained-volume-measure'

a2['gross'] = a2['gross'].apply(pathify)

a2 = a2.rename(columns={'OBS':'Value'})

a2 = convet_dimension_to_int(a2, 'Value')

try:
    a2.drop(['Seasonal Adjustment','Percentage Change','measure'], axis=1, inplace=True)
except:
    ind = ind

a2 = a2.rename(columns={'Indices':'Estimate Type', 'gross':'Aggregate'})
a2cdids = a2['CDID'].unique()

# %%
mainTitle = scraper.dataset.title
maincomme = scraper.dataset.comment
maindescr = scraper.dataset.description

scraper.dataset.title = mainTitle + ' - National Accounts aggregates (A2)'
scraper.dataset.comment = maincomme + ' - National Accounts aggregates (A2) - GDP and GVA in £ million. Seasonally Adjusted'
scraper.dataset.description = maindescr + """
Estimates are given to the nearest £ million but cannot be regarded as accurate to this degree. 
Data has been Seasonally Adjusted. 
Reference year is 2018. 
Less Basic price adjustment: Taxes on products less subsidies. 
Gross value added excluding oil & gas: Calculated by using gross value added at basic prices minus extraction of crude petroleum and natural gas.
"""

with open("info.json", "r") as jsonFile:
    data = json.load(jsonFile)
    data["transform"]["columns"]["Value"]["measure"] = "http://gss-data.org.uk/def/measure/na-aggregates"
    data["transform"]["columns"]["Value"]["unit"] = "http://gss-data.org.uk/def/concept/measurement-units/gbp-million"
    with open("info.json", "w") as jsonFile:
        json.dump(data, jsonFile)
       
cubes.add_cube(copy.deepcopy(scraper), a2, "gbp–data-tables-aggregates", 'gbp–data-tables-aggregates', data)
del a2

# %%
# B1
b1 = tidied_sheets[2]
# Only use the main value data for now, CVMs
try:
    b1 = b1.loc[b1['Percentage Change'].isna()] 
except:
    ind = ind 
    
b1 = strip_superscripts(b1, 'Industry')

b1 = b1.loc[b1['CDID'] != 'CGCE'] # We do not want Gross value added at basic prices as it messes up the cube
b1 = b1.loc[b1['CDID'] != 'KLH7'] # We do not want Gross value added excluding oil & gas as it messes up the cube

b1['Sector'].loc[b1['CDID'].isin(['L2KR'])] = 'Production'
b1['Sector'].loc[b1['CDID'].isin(['L2KL'])] = 'Agriculture'  
b1['Sector'].loc[b1['CDID'].isin(['L2N8'])] = 'Construction' 

b1 = prefix_refperiod(b1, 'Period')
    
try:
    b1.drop(['Seasonal Adjustment','Percentage Change','measure'], axis=1, inplace=True)
except:
    ind = ind    

b1['Sector'] = b1['Sector'].apply(pathify)
b1['Industry'] = b1['Industry'].apply(pathify)

b1 = b1.rename(columns={'OBS':'Value', '2018 Weights':'Weights 2018'})

b1 = convet_dimension_to_int(b1, 'Value')


# %%
# B2
b2 = tidied_sheets[3]

try:
    b2 = b2.loc[b2['Percentage Change'].isna()] 
except:
    ind = ind 
    
b2['Sector'] = 'Service industries'

b2 = strip_superscripts(b2, 'Industry')

b2 = prefix_refperiod(b2, 'Period')

try:
    b2.drop(['Seasonal Adjustment','Percentage Change','measure'], axis=1, inplace=True)
except:
    ind = ind   

b2['Sector'] = b2['Sector'].apply(pathify)
b2['Industry'] = b2['Industry'].apply(pathify)

b2 = b2.rename(columns={'OBS':'Value', '2018 Weights':'Weights 2018'})
b2 = convet_dimension_to_int(b2, 'Value')


# %%
b1b2 = pd.concat([b1, b2])
b1b2cdids = b1b2['CDID'].unique()
del b1, b2

# %%
scraper.dataset.title = mainTitle + ' - Gross value added chained volume measures at basic prices, by category of output (B1 & B2)'
scraper.dataset.comment = maincomme + ' - Gross value added chained volume measures at basic prices, by category of output (B1 & B2) - Seasonally Adjusted'
scraper.dataset.description = maindescr + """
Estimates cannot be regarded as accurate to the last digit shown.
Data has been Seasonally Adjusted. 
Reference year is 2018.
Components of outputs are valued at basic prices, which excludes taxes and includes subsidies on products.
Weights may not sum to totals due to rounding.
This is a balanced index of UK GVA, taking into account data from the income and expenditure approaches. Thus it will not necessarily be the weighted sum of the industrial indices.
"""

with open("info.json", "r") as jsonFile:
    data = json.load(jsonFile)
    data["transform"]["columns"]["Value"]["measure"] = "http://gss-data.org.uk/def/measure/gva"
    data["transform"]["columns"]["Value"]["unit"] = "http://gss-data.org.uk/def/concept/measurement-units/gbp-million"
    with open("info.json", "w") as jsonFile:
        json.dump(data, jsonFile)
      
cubes.add_cube(copy.deepcopy(scraper), b1b2, "gbp–data-tables-cvm-output", 'gbp–data-tables-cvm-output', data)
del b1b2

# %%
# C1
c1 = tidied_sheets[4]

try:
    c1 = c1.loc[c1['Percentage Change'].isna()] 
except:
    ind = ind 

c1 = c1.loc[c1['CDID'] != 'YBHA'] # This is already in one of the other datasets
c1['Expenditure'].loc[c1['CDID'].isin(['YBIL','IKBH','ABMF','IKBI','IKBJ','GIXM'])] = 'not-applicable'
c1['Expenditure'].loc[c1['CDID'].isin(['ABJQ'])] = 'Final consumption expenditure'
c1['Expenditure'].loc[c1['CDID'].isin(['NPQS','NPEK'])] = 'Gross capital formation'

c1 = strip_superscripts(c1, 'Expendisture Category')

c1 = prefix_refperiod(c1, 'Period')

try:
    c1.drop(['Seasonal Adjustment','Percentage Change','measure'], axis=1, inplace=True)
except:
    ind = ind   

c1['Expendisture Category'] = c1['Expendisture Category'].apply(pathify)
c1['Expenditure'] = c1['Expenditure'].apply(pathify)

c1 = c1.rename(columns={'OBS':'Value','Expendisture Category':'Expenditure Category','Expenditure':'Economic Concept'})

c1 = convet_dimension_to_int(c1, 'Value')

c1['Estimate Type'] = 'current-price'
c1.head(5)

# %%
# C2
c2 = tidied_sheets[5]

try:
    c2 = c2.loc[c2['Percentage Change'].isna()] 
except:
    ind = ind 

c2 = c2.loc[c2['CDID'] != 'ABMI'] # This is already in one of the other datasets
c2['Expenditure'].loc[c2['CDID'].isin(['YBIM','IKBK','ABMG','IKBL','IKBM','GIXS'])] = 'not-applicable'
c2['Expenditure'].loc[c2['CDID'].isin(['ABJR'])] = 'Final consumption expenditure'
c2['Expenditure'].loc[c2['CDID'].isin(['NPQT','NPEL'])] = 'Gross capital formation'

c2 = strip_superscripts(c2, 'Expendisture Category')

c2 = prefix_refperiod(c2, 'Period')

try:
    c2.drop(['Seasonal Adjustment','Percentage Change','measure'], axis=1, inplace=True)
except:
    ind = ind   

c2['Expendisture Category'] = c2['Expendisture Category'].apply(pathify)
c2['Expenditure'] = c2['Expenditure'].apply(pathify)

c2 = c2.rename(columns={'OBS':'Value','Expendisture Category':'Expenditure Category','Expenditure':'Economic Concept'})

c2 = convet_dimension_to_int(c2, 'Value')
    
c2['Estimate Type'] = 'chained-volume-measure'
c2.head(5)

# %%
c1c2 = pd.concat([c1, c2])
c1c2cdids = c1c2['CDID'].unique()
del c1, c2

# %%
scraper.dataset.title = mainTitle + ' - Gross domestic product: expenditure at current prices and chained volume measures (C1 & C2)'
scraper.dataset.comment = maincomme + ' - Gross domestic product: expenditure at current prices and chained volume measures (C1 & C2) - Seasonally Adjusted'
scraper.dataset.description = maindescr + """
Data has been Seasonally Adjusted. 
Reference year is 2018.
Estimates are given to the nearest £ million but cannot be regarded as accurate to this degree.
Non-profit institutions: Non-profit institutions serving households.
Further breakdown of business investment can be found in the 'Business investment in the UK' bulletin
Changes in inventories: Quarterly alignment adjustment included in this series.
Acquisitions less disposals of valuables can be a volatile series, due to the inclusion of non-monetary gold, but any volatility is likely to be GDP neutral as this is offset in UK trade figures
Trade balance is calculated by using exports of goods and services minus imports of goods and services
Non-profit institutions: There is a small difference between the gross operating surplus of the NPISH sector in the SFA release, compared with the consumption of fixed capital for the NPISH sector published in the GDP release.  This affects 2019Q1 onwards. The latest figures for the affected series can be found in the SFA release.
"""

with open("info.json", "r") as jsonFile:
    data = json.load(jsonFile)
    data["transform"]["columns"]["Value"]["measure"] = "http://gss-data.org.uk/def/measure/gdp"
    data["transform"]["columns"]["Value"]["unit"] = "http://gss-data.org.uk/def/concept/measurement-units/gbp-million"
    with open("info.json", "w") as jsonFile:
        json.dump(data, jsonFile)
       
cubes.add_cube(copy.deepcopy(scraper), c1c2, "gbp–data-tables-expenditure", 'gbp–data-tables-expenditure', data)
del c1c2

# %%
# D1
d1 = tidied_sheets[6]

try:
    d1 = d1.loc[d1['Percentage Change'].isna()] 
except:
    ind = ind 

d1 = d1.loc[d1['CDID'] != 'YBHA'] # This is already in one of the other datasets
d1['Gross Domestic Product'].loc[d1['CDID'].isin(['CAER'])] = 'Gross operating surplus of corporations'
d1['Gross Domestic Product'].loc[d1['CDID'].isin(['CGBX','CGCB','CMVL','GIXQ'])] = 'Gross domestic product'

d1 = strip_superscripts(d1, 'Category of Income')

d1 = prefix_refperiod(d1, 'Period')

try:
    d1.drop(['Seasonal Adjustment','Percentage Change','measure','DATAMARKER'], axis=1, inplace=True)
except:
    ind = ind   

d1['Gross Domestic Product'] = d1['Gross Domestic Product'].apply(pathify)
d1['Category of Income'] = d1['Category of Income'].apply(pathify)

d1 = d1.rename(columns={'OBS':'Value', 'Gross Domestic Product':'Economic Concept'})

d1 = convet_dimension_to_int(d1, 'Value')

d1cdids = d1['CDID'].unique()
d1.head(5)
#d1['Gross Domestic Product'].unique()

# %%
scraper.dataset.title = mainTitle + ' - Gross domestic product: by category of income at current prices (D)'
scraper.dataset.comment = maincomme + ' - Gross domestic product: by category of income at current prices (D) - Seasonally Adjusted'
scraper.dataset.description = maindescr + """
Data has been seasonally adjusted.
Estimates are given to the nearest £ million but cannot be regarded as accurate to this degree.
Private. non-financial corporations: Quarterly alignment adjustment included in this series.
Gross operating surplus of corporations total includes the operating surplus of financial corporations, private non-financial corporations and public corporations.
Other income includes mixed income and the operating surplus of the non-corporate sector.
"""

with open("info.json", "r") as jsonFile:
    data = json.load(jsonFile)
    data["transform"]["columns"]["Value"]["measure"] = "http://gss-data.org.uk/def/measure/gdp"
    data["transform"]["columns"]["Value"]["unit"] = "http://gss-data.org.uk/def/concept/measurement-units/gbp-million"
    with open("info.json", "w") as jsonFile:
        json.dump(data, jsonFile)
       
cubes.add_cube(copy.deepcopy(scraper), d1, "gbp–data-tables-income", 'gbp–data-tables-income', data)
del d1

# %%
# E1
e1 = tidied_sheets[7]

try:
    e1 = e1.loc[e1['Percentage Change'].isna()] 
except:
    ind = ind 

e1['COICOP'] = 'CP' + e1['COICOP'].astype(str) 
e1['COICOP'].loc[e1['CDID'].isin(['ABJQ'])] = 'TOTAL'
e1['COICOP'].loc[e1['COICOP'] == 'CP0.0'] = 'CP00'
e1['COICOP'].loc[e1['CDID'].isin(['ABTF'])] = 'net-tourism'

e1['Expenditure Category'] = 'uk-national-domestic'
e1['Expenditure Category'].loc[e1['CDID'].isin(['ABJQ','ABTF'])] = 'uk-national'
e1['Economic Concept'] = 'current-price'

e1 = prefix_refperiod(e1, 'Period')

try:
    e1.drop(['Seasonal Adjustment','Percentage Change','measure','Household Expenditure'], axis=1, inplace=True)
except:
    ind = ind   

e1 = e1.rename(columns={'OBS':'Value'})

e1 = convet_dimension_to_int(e1, 'Value')

e1cdids = e1['CDID'].unique()
e1.head(50)

# %%
# E2
e2 = tidied_sheets[8]

try:
    e2 = e2.loc[e2['Percentage Change'].isna()] 
except:
    ind = ind 

#e2['COICOP'] = 'CP' + e2['COICOP'].astype(str) 
e2 = e2.loc[e2['CDID'] != 'ABJQ']
e2 = e2.loc[e2['CDID'] != 'ABTF']
e2 = e2.loc[e2['CDID'] != 'ZAKV']

e2['COICOP'].loc[e2['CDID'].isin(['UTIF'])] = 'total-goods'
e2['Economic Concept'] = 'current-price'

e2 = prefix_refperiod(e2, 'Period')

try:
    e2.drop(['Seasonal Adjustment','Percentage Change','measure','Household Expenditure'], axis=1, inplace=True)
except:
    ind = ind   

e2 = e2.rename(columns={'OBS':'Value'})

e2 = convet_dimension_to_int(e2, 'Value')

e2['Expenditure Category'] = 'uk-domestic'

e2cdids = e2['CDID'].unique()
e2.head(5)

# %%
# E3
e3 = tidied_sheets[9]

try:
    e3 = e3.loc[e3['Percentage Change'].isna()] 
except:
    ind = ind 

e3['COICOP'] = 'CP' + e3['COICOP'].astype(str) 
e3['COICOP'].loc[e3['CDID'].isin(['ABJR'])] = 'TOTAL'
e3['COICOP'].loc[e3['COICOP'] == 'CP0.0'] = 'CP00'
e3['COICOP'].loc[e3['CDID'].isin(['ABTH'])] = 'net-tourism'

e3['Expenditure Category'] = 'uk-national-domestic'
e3['Expenditure Category'].loc[e3['CDID'].isin(['ABJR','ABTH'])] = 'uk-national'
e3['Economic Concept'] = 'chained-volume-measure'

e3 = prefix_refperiod(e3, 'Period')

try:
    e3.drop(['Seasonal Adjustment','Percentage Change','measure','Household Expenditure'], axis=1, inplace=True)
except:
    ind = ind   

e3 = e3.rename(columns={'OBS':'Value'})

e3 = convet_dimension_to_int(e3, 'Value')

e3cdids = e3['CDID'].unique()
e3.head(50)

# %%
# E4
e4 = tidied_sheets[8]

try:
    e4 = e4.loc[e4['Percentage Change'].isna()] 
except:
    ind = ind 

#e4['COICOP'] = 'CP' + e4['COICOP'].astype(str) 
e4 = e4.loc[e4['CDID'] != 'ABJR']
e4 = e4.loc[e4['CDID'] != 'ABTH']
e4 = e4.loc[e4['CDID'] != 'ZAKW']

e4['COICOP'].loc[e4['CDID'].isin(['UTIH'])] = 'total-goods'
e4['Economic Concept'] = 'chained-volume-measure'

e4 = prefix_refperiod(e4, 'Period')

try:
    e4.drop(['Seasonal Adjustment','Percentage Change','measure','Household Expenditure'], axis=1, inplace=True)
except:
    ind = ind   

e4 = e4.rename(columns={'OBS':'Value'})

e4 = convet_dimension_to_int(e4, 'Value')

e4['Expenditure Category'] = 'uk-domestic'

e4cdids = e4['CDID'].unique()
e4.head(5)

# %%
#e1e2e3e4cdids = pd.concat([pd.DataFrame(e1cdids),pd.DataFrame(e2cdids),pd.DataFrame(e3cdids),pd.DataFrame(e4cdids)])
#del e1cdids, e2cdids, e3cdids, e4cdids

e1e2e3e4 = pd.concat([e1, e2, e3, e4])
e1e2e3e4.head(10)
e1e2e3e4['Expenditure Category'].unique()

# %%
scraper.dataset.title = mainTitle + ' - Household final consumption by purpose and goods and services at Current Prices & Chained Volume Measures (E1, E2, E3, E4)'
scraper.dataset.comment = maincomme + ' - Household final consumption by purpose and goods and services at Current Prices & Chained Volume Measures (E1, E2, E3, E4) - Seasonally Adjusted'
scraper.dataset.description = maindescr + """
Household final consumption by purpose and goods and services at Current Prices & Chained Volume Measures (E1, E2, E3, E4)
Data has been seasonally adjusted
COICOP: ESA 10 Classification of Individual Consumption by Purpose.
UK Domestic: Final consumption expenditure in the UK by UK & foreign households
UK National: Final consumption by UK Households in the UK & abroad.
UK National & Domestic: Final consumption expenditure in the UK by UK & foreign households and final consumption by UK Households in the UK & abroad.
"""

with open("info.json", "r") as jsonFile:
    data = json.load(jsonFile)
    data["transform"]["columns"]["Value"]["measure"] = "http://gss-data.org.uk/def/measure/hh-final-consumption"
    data["transform"]["columns"]["Value"]["unit"] = "http://gss-data.org.uk/def/concept/measurement-units/gbp-million"
    with open("info.json", "w") as jsonFile:
        json.dump(data, jsonFile)
       
cubes.add_cube(copy.deepcopy(scraper), e1e2e3e4, "gbp–data-tables-expenditure", 'gbp–data-tables-expenditure', data)
del e1e2e3e4

# %%
cubes.output_all()

# %%
#cids = pd.concat([pd.DataFrame(a2cdids),pd.DataFrame(b1b2cdids),pd.DataFrame(c1c2cdids),pd.DataFrame(d1cdids),pd.DataFrame(e1e2e3e4cdids)])
#print('Before: ' + str(cids[0].count()))
#cids = cids.drop_duplicates()
#print('After: ' + str(cids[0].count()))
#cids = cids.rename(columns={cids.columns[0]:'Label'})
#cids['Notation'] = cids['Label']
#cids['Parent Notation'] = ''
#cids['Sort Priority'] = np.arange(cids.shape[0]) + 6551
#cids.to_csv('cdids.csv', index=False)
#cids

# %%

# %%

# %%

# %%

# %%
#import dmtools as dm
#fldrpth = '/users/leigh/Development/family-trade/reference/codelists/'
#dm.search_for_codes_using_levenshtein_and_fuzzywuzzy(tidied_sheets[ind]['Sector'].unique(), fldrpth, 'Notation', 'sector', 3, 0.8)
#dm.search_codelists_for_codes(d1['Category of Income'].unique(), fldrpth, 'Notation', 'Category of Income')

# %%
