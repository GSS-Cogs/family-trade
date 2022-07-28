# %%
from gssutils import *
import json
import copy 
import numpy as np

df = pd.DataFrame()
metadata = Scraper(seed = 'national_account_aggregates-info.json')
# %%
distribution = metadata.distribution(latest = True)
tabs = { tab.name: tab for tab in distribution.as_databaker() }
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
    print(not_blank_cells)
    for cell in indices_dimension.hbagset:
        # If a dimension cell is blank
        if cell.value == '': 
            # Is there a value 1 cells to the left? if so use that value
            cell_checked = [x for x in not_blank_cells if x.x == cell.x-1]
            if len(cell_checked) > 0:
                indices_dimension.AddCellValueOverride(cell, cell_checked[0].value)
            # Is there a value 1 cells to the right? if so use that value
            cell_checked = [x for x in not_blank_cells if x.x == cell.x+1]
            if len(cell_checked) > 0:
                indices_dimension.AddCellValueOverride(cell, cell_checked[0].value)
            # Is there a value two cells to the right? if so use that value
            cell_checked = [x for x in not_blank_cells if x.x == cell.x-2]
            if len(cell_checked) > 0:
                indices_dimension.AddCellValueOverride(cell, cell_checked[0].value)
            # Is there a value two cells to the left? if so use that value
            cell_checked = [x for x in not_blank_cells if x.x == cell.x+2]
            if len(cell_checked) > 0:
                indices_dimension.AddCellValueOverride(cell, cell_checked[0].value)   
                
    return indices_dimension


def with_sector_overrides(sector_dimension):
    not_blank_cells = [cell for cell in sector_dimension.hbagset if cell.value != '']
    for cell in sector_dimension.hbagset:
        if cell.value == '': 
            cell_checked = [x for x in not_blank_cells if x.x == cell.x-2]
            if len(cell_checked) > 0:
                sector_dimension.AddCellValueOverride(cell, cell_checked[0].value)
            cell_checked = [x for x in not_blank_cells if x.x == cell.x+2]
            if len(cell_checked) > 0:
                sector_dimension.AddCellValueOverride(cell, cell_checked[0].value)   
            cell_checked = [x for x in not_blank_cells if x.x == cell.x+4]
            if len(cell_checked) > 0:
                sector_dimension.AddCellValueOverride(cell, cell_checked[0].value)   
            cell_checked = [x for x in not_blank_cells if x.x == cell.x+6]
            if len(cell_checked) > 0:
                sector_dimension.AddCellValueOverride(cell, cell_checked[0].value)   
            cell_checked = [x for x in not_blank_cells if x.x == cell.x-4]
            if len(cell_checked) > 0:
                sector_dimension.AddCellValueOverride(cell, cell_checked[0].value) 
            cell_checked = [x for x in not_blank_cells if x.x == cell.x-6]
            if len(cell_checked) > 0:
                sector_dimension.AddCellValueOverride(cell, cell_checked[0].value)   
           #Check cell = "" and not been overriden already then add -8
            #Gross value added excluding oil & gas = Service industries 
                
    return sector_dimension


def with_expenditure_overrides(expenditure_dimension):
    not_blank_cells = [cell for cell in expenditure_dimension.hbagset if cell.value != '']
    for cell in expenditure_dimension.hbagset:
        if cell.value == '': 
            cell_checked = [x for x in not_blank_cells if x.x == cell.x+2]
            if len(cell_checked) > 0:
                expenditure_dimension.AddCellValueOverride(cell, cell_checked[0].value)   
            cell_checked = [x for x in not_blank_cells if x.x == cell.x+1]
            if len(cell_checked) > 0:
                expenditure_dimension.AddCellValueOverride(cell, cell_checked[0].value) 
            cell_checked = [x for x in not_blank_cells if x.x == cell.x-1]
            if len(cell_checked) > 0:
                expenditure_dimension.AddCellValueOverride(cell, cell_checked[0].value)   
            
                
    return expenditure_dimension


def with_gross_overrides(gross_dimension):
    not_blank_cells = [cell for cell in gross_dimension.hbagset if cell.value != '']
    for cell in gross_dimension.hbagset:
        if cell.value == '': 
            cell_checked = [x for x in not_blank_cells if x.x == cell.x-2]
            if len(cell_checked) > 0:
                gross_dimension.AddCellValueOverride(cell, cell_checked[0].value)   
            cell_checked = [x for x in not_blank_cells if x.x == cell.x+1]
            if len(cell_checked) > 0:
                gross_dimension.AddCellValueOverride(cell, cell_checked[0].value) 
            cell_checked = [x for x in not_blank_cells if x.x == cell.x-1]
            if len(cell_checked) > 0:
                gross_dimension.AddCellValueOverride(cell, cell_checked[0].value) 
    return gross_dimension


def with_analysis_by_overrides(analysis_by_dimension):
    not_blank_cells = [cell for cell in analysis_by_dimension.hbagset if cell.value != '']
    for cell in analysis_by_dimension.hbagset:
        if cell.value == '': 
            cell_checked = [x for x in not_blank_cells if x.x == cell.x-5]
            if len(cell_checked) > 0:
                analysis_by_dimension.AddCellValueOverride(cell, cell_checked[0].value)   
            cell_checked = [x for x in not_blank_cells if x.x == cell.x-4]
            if len(cell_checked) > 0:
                analysis_by_dimension.AddCellValueOverride(cell, cell_checked[0].value)  
            cell_checked = [x for x in not_blank_cells if x.x == cell.x-3]
            if len(cell_checked) > 0:
                analysis_by_dimension.AddCellValueOverride(cell, cell_checked[0].value)  
            cell_checked = [x for x in not_blank_cells if x.x == cell.x+1]
            if len(cell_checked) > 0:
                analysis_by_dimension.AddCellValueOverride(cell, cell_checked[0].value)  
            cell_checked = [x for x in not_blank_cells if x.x == cell.x+2]
            if len(cell_checked) > 0:
                analysis_by_dimension.AddCellValueOverride(cell, cell_checked[0].value) 
            cell_checked = [x for x in not_blank_cells if x.x == cell.x-1]
            if len(cell_checked) > 0:
                analysis_by_dimension.AddCellValueOverride(cell, cell_checked[0].value)
            cell_checked = [x for x in not_blank_cells if x.x == cell.x-2]
            if len(cell_checked) > 0:
                analysis_by_dimension.AddCellValueOverride(cell, cell_checked[0].value)
    return analysis_by_dimension


def with_industry_overrides(industry_dimension):
    not_blank_cells = [cell for cell in industry_dimension.hbagset if cell.value != '']
    for cell in industry_dimension.hbagset:
        if cell.value == '': 
            cell_checked = [x for x in not_blank_cells if x.x == cell.x+2]
            if len(cell_checked) > 0:
                industry_dimension.AddCellValueOverride(cell, cell_checked[0].value)   
            cell_checked = [x for x in not_blank_cells if x.x == cell.x-2]
            if len(cell_checked) > 0:
                industry_dimension.AddCellValueOverride(cell, cell_checked[0].value)  
            cell_checked = [x for x in not_blank_cells if x.x == cell.x-1]
            if len(cell_checked) > 0:
                industry_dimension.AddCellValueOverride(cell, cell_checked[0].value)  
            cell_checked = [x for x in not_blank_cells if x.x == cell.x+1]
            if len(cell_checked) > 0:
                industry_dimension.AddCellValueOverride(cell, cell_checked[0].value)  
            #-3 = Distributive trades

    return industry_dimension


def with_flow_overrides(flow_dimension):
    not_blank_cells = [cell for cell in flow_dimension.hbagset if cell.value != '']
    for cell in flow_dimension.hbagset:
        if cell.value == '': 
            cell_checked = [x for x in not_blank_cells if x.x == cell.x-1]
            if len(cell_checked) > 0:
                flow_dimension.AddCellValueOverride(cell, cell_checked[0].value)   
            cell_checked = [x for x in not_blank_cells if x.x == cell.x+1]
            if len(cell_checked) > 0:
                flow_dimension.AddCellValueOverride(cell, cell_checked[0].value)  
    return flow_dimension

# %%
for name, tab in tabs.items():
    #shared dimensions across all tabs
    seasonal_adjustment = tab.excel_ref('A5').expand(DOWN).filter(contains_string('Seasonally'))
    period = tab.excel_ref('A6').expand(DOWN).is_not_blank() - seasonal_adjustment
    measure = tab.excel_ref('G1').expand(RIGHT).is_not_blank()
    p_change =  tab.excel_ref('A6').expand(DOWN).filter(contains_string('Percentage'))  | tab.excel_ref('A3')
    sheet = tab.name
   
    if name in national_account_aggregates:
        cdid = tab.excel_ref('B4').expand(RIGHT).is_not_blank() | p_change.shift(1,2).expand(RIGHT).is_not_blank()
        observations = cdid.fill(DOWN).is_not_blank().is_not_whitespace() - cdid
        gross = tab.excel_ref('C3').expand(RIGHT).is_not_blank()
        indices = gross.shift(UP)
        
        dimensions = [
            HDim(indices, "Indices", DIRECTLY, ABOVE), 
            HDim(gross, "Gross", DIRECTLY, ABOVE),
            HDim(period,'Period',DIRECTLY,LEFT),
            HDim(seasonal_adjustment,'Seasonal Adjustment',CLOSEST,ABOVE),
            HDim(p_change, 'Percentage Change',CLOSEST,ABOVE),
            HDim(cdid, 'CDID',DIRECTLY,ABOVE),
            HDim(measure, 'measure',CLOSEST,ABOVE),
        ]
        
        dimensions[0] = with_indices_overrides(dimensions[0])
        c1 = ConversionSegment(tab, dimensions, observations)  
        #savepreviewhtml(c1, fname=tab.name + "Preview.html")
        tidy_sheet = c1.topandas()
        tidy_sheet = tidy_sheet.replace(r'^\s*$', np.nan, regex=True)
        tidied_sheets.append(tidy_sheet)
        
    elif name in output_indicators:
        weights = tab.excel_ref('B4').expand(RIGHT).is_not_blank()
        cdid = tab.excel_ref('B5').expand(RIGHT).is_not_blank() | p_change.shift(1,1).expand(RIGHT).is_not_blank() - weights
        industry = tab.excel_ref('B3').expand(RIGHT).is_not_blank()
        observations = cdid.fill(DOWN).is_not_blank().is_not_whitespace() - cdid
        sector = industry.shift(UP)
        
        dimensions = [
            HDim(sector, 'Sector',DIRECTLY, ABOVE),
            HDim(period,'Period',DIRECTLY,LEFT),
            HDim(seasonal_adjustment,'Seasonal Adjustment',CLOSEST,ABOVE),
            HDim(p_change, 'Percentage Change',CLOSEST,ABOVE),
            HDim(cdid, 'CDID',DIRECTLY,ABOVE),
            HDim(weights, '2019 Weights',DIRECTLY,ABOVE),
            HDim(industry, 'Industry',DIRECTLY,ABOVE),
            HDim(measure, 'measure',CLOSEST,ABOVE)
            
        ]
        dimensions[0] = with_expenditure_overrides(dimensions[0])
        c1 = ConversionSegment(tab, dimensions, observations)   
        #savepreviewhtml(c1, fname=tab.name + "Preview.html")
        tidy_sheet = c1.topandas()
        tidy_sheet['Sector'] = tidy_sheet['Sector'].replace('', 'Service industries')
        tidy_sheet = tidy_sheet.replace(r'^\s*$', np.nan, regex=True)
        tidied_sheets.append(tidy_sheet)
        
    elif name in expenditure_indicators:
        p_change =  tab.excel_ref('A6').expand(DOWN).filter(contains_string('Percentage'))  | tab.excel_ref('C6')
        cdid = tab.excel_ref('B5').expand(RIGHT).is_not_blank() | p_change.shift(1,1).expand(RIGHT).is_not_blank() | p_change.shift(1,2).expand(RIGHT).is_not_blank().is_not_number()
        cdid = cdid - cdid.shift(0,1).expand(RIGHT)
        expenditure_cat = tab.excel_ref('C4').expand(RIGHT).is_not_blank()
        expenditure = expenditure_cat.shift(UP)
        
        observations = cdid.fill(DOWN).is_not_blank().is_not_whitespace() - cdid
        dimensions = [
            HDim(expenditure, 'Expenditure',CLOSEST,LEFT),
            HDim(period,'Period',DIRECTLY,LEFT),
            HDim(seasonal_adjustment,'Seasonal Adjustment',CLOSEST,ABOVE),
            HDim(p_change, 'Percentage Change',CLOSEST,ABOVE),
            HDim(cdid, 'CDID',DIRECTLY,ABOVE),
            HDim(measure, 'measure',CLOSEST,ABOVE),
            HDim(expenditure_cat, 'Expenditure Category',DIRECTLY,ABOVE),
        ]
        dimensions[0] = with_expenditure_overrides(dimensions[0])
        c1 = ConversionSegment(tab, dimensions, observations)   
       # savepreviewhtml(c1, fname=tab.name + "Preview.html")
        tidy_sheet = c1.topandas()
        tidy_sheet['Expenditure'] = tidy_sheet['Expenditure'].replace('', 'Gross capital formation')
        tidy_sheet = tidy_sheet.replace(r'^\s*$', np.nan, regex=True)
        tidied_sheets.append(tidy_sheet)
        
    elif name in income_indicators:
        cdid = tab.excel_ref('B4').expand(RIGHT).is_not_blank() | p_change.shift(1,2).expand(RIGHT).is_not_blank()
        cat_income = tab.excel_ref('A3').expand(RIGHT).is_not_blank()
        gross = cat_income.shift(UP)
        observations = cdid.fill(DOWN).is_not_blank() - cdid
        
        dimensions = [
            HDim(gross, 'Gross Domestic Product',DIRECTLY,ABOVE),
            HDim(period,'Period',DIRECTLY,LEFT),
            HDim(seasonal_adjustment,'Seasonal Adjustment',CLOSEST,ABOVE),
            HDim(p_change, 'Percentage Change',CLOSEST,ABOVE),
            HDim(cdid, 'CDID',DIRECTLY,ABOVE),
            HDim(measure, 'measure',CLOSEST,ABOVE),
            HDim(cat_income, 'Category of Income',DIRECTLY,ABOVE),
        ]
        dimensions[0] = with_gross_overrides(dimensions[0])
        c1 = ConversionSegment(tab, dimensions, observations)   
        #savepreviewhtml(c1, fname=tab.name + "Preview.html")
        tidy_sheet = c1.topandas()
        tidy_sheet['Gross Domestic Product'] = tidy_sheet['Gross Domestic Product'].replace('', 'Gross operating surplus of corporations')
        tidy_sheet = tidy_sheet.replace(r'^\s*$', np.nan, regex=True)
        tidied_sheets.append(tidy_sheet)

    elif name in household_expenditure_indicators:
        if name in household_expenditure_indicators[0] or name in household_expenditure_indicators[2]:
            COICOP = tab.excel_ref('B5').expand(RIGHT).is_not_blank()
            cdid = tab.excel_ref('B6').expand(RIGHT).is_not_blank() | p_change.shift(1,2).expand(RIGHT).is_not_blank() - COICOP
            measure = tab.excel_ref('G1').expand(RIGHT).is_not_blank()
            expenditure = tab.excel_ref('B4').expand(RIGHT).is_not_blank()
        else:
            p_change =  tab.excel_ref('A6').expand(DOWN).filter(contains_string('Percentage'))  | tab.excel_ref('B6')
            COICOP = tab.excel_ref('B7').expand(RIGHT)
            cdid = tab.excel_ref('B8').expand(RIGHT).is_not_blank() | p_change.shift(1,2).expand(RIGHT).is_not_blank() - COICOP
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
        observations = cdid.fill(DOWN).is_not_blank().is_not_whitespace() - cdid
        capitol_formation = tab.excel_ref('B4').expand(RIGHT).is_not_blank()
        analysis_by = capitol_formation.shift(0,-2)
        tab_name = tab.name
        
        dimensions = [
            HDim(analysis_by, 'Analysed by',DIRECTLY,ABOVE),
            HDim(period,'Period',DIRECTLY,LEFT),
            HDim(seasonal_adjustment,'Seasonal Adjustment',CLOSEST,ABOVE),
            HDim(p_change, 'Percentage Change',CLOSEST,ABOVE),
            HDim(cdid, 'CDID',DIRECTLY,ABOVE),
            HDim(capitol_formation, 'Capital Formation',DIRECTLY,ABOVE),
            HDim(measure, 'measure',CLOSEST,ABOVE),
        ]
        dimensions[0] = with_analysis_by_overrides(dimensions[0])
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
        industry = sector.shift(UP)
        dimensions = [
            HDim(industry,'Industry',DIRECTLY,ABOVE),
            HDim(period,'Period',DIRECTLY,LEFT),
            HDim(seasonal_adjustment,'Seasonal Adjustment',CLOSEST,ABOVE),
            HDim(p_change, 'Percentage Change',CLOSEST,ABOVE),
            HDim(cdid, 'CDID',DIRECTLY,ABOVE),
            HDim(sector, 'Sector',DIRECTLY,ABOVE),
            HDim(level_held, 'Level of inventories held at end-December 2019',DIRECTLY,ABOVE),
            HDim(measure, 'measure',CLOSEST,ABOVE),
        ]
        dimensions[0] = with_industry_overrides(dimensions[0])
        c1 = ConversionSegment(tab, dimensions, observations)   
        #savepreviewhtml(c1, fname=tab.name + "Preview.html")
        tidy_sheet = c1.topandas()
        tidy_sheet['Industry'] = tidy_sheet['Industry'].replace('', 'Distributive trades')
        tidy_sheet = tidy_sheet.replace(r'^\s*$', np.nan, regex=True)
        tidied_sheets.append(tidy_sheet)

    elif name in trade: 
        if name in trade[0]:
            goods_services = tab.excel_ref('B3').expand(RIGHT).is_not_blank() 
            cdid = tab.excel_ref('B5').expand(RIGHT).is_not_blank() | p_change.shift(1,2).expand(RIGHT).is_not_blank() - goods_services
            flow = goods_services.shift(UP) 
        else:
            goods_services = tab.excel_ref('B4').expand(RIGHT).is_not_blank() 
            cdid = tab.excel_ref('B6').expand(RIGHT).is_not_blank() | p_change.shift(1,1).expand(RIGHT).is_not_blank() - goods_services
            measure = tab.excel_ref('C2').expand(RIGHT).is_not_blank()
            flow = goods_services.shift(UP)
        observations = cdid.fill(DOWN).is_not_blank().is_not_whitespace() - cdid
        
        dimensions = [
            HDim(flow, 'Flow',DIRECTLY,ABOVE),
            HDim(period,'Period',DIRECTLY,LEFT),
            HDim(seasonal_adjustment,'Seasonal Adjustment',CLOSEST,ABOVE),
            HDim(p_change, 'Percentage Change',CLOSEST,ABOVE),
            HDim(cdid, 'CDID',DIRECTLY,ABOVE),
            HDim(goods_services, 'Goods or Services',DIRECTLY,ABOVE),
            HDim(measure, 'measure',CLOSEST,ABOVE),
        ]
        dimensions[0] = with_flow_overrides(dimensions[0])
        c1 = ConversionSegment(tab, dimensions, observations)   
        #savepreviewhtml(c1, fname=tab.name + "Preview.html")
        tidy_sheet = c1.topandas()
        tidy_sheet = tidy_sheet.replace(r'^\s*$', np.nan, regex=True)
        tidy_sheet['Goods or Services'] = tidy_sheet['Goods or Services'].replace('Total 1', 'Total')
        tidied_sheets.append(tidy_sheet)
    else:
        continue

# Tabs transformed and appended to tidied_sheets to make it easier to understand for a DM.. hopefully 
# Things to note, I have done no post processing atm due to this being a little annoying and want clarity from a DM first. 

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
# ##### Household Expenditure Indicators
#     tidied_sheets[7] (E1 Expenditure)
#     tidied_sheets[8] (E1 Expenditure)
#     tidied_sheets[9] (E1 Expenditure)
#     tidied_sheets[10](E1 Expenditure)
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
#     tidied_sheets[14](G1 Inventories)
#
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
#      'AD Annex D'
#      'AE Annex E',
#      'AF Annex F',
#      'AG Annex G'


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


# +

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


# -

def convet_dimension_to_int(dataset, dimension):
    try:
        dataset[dimension] = dataset[dimension].fillna(-1000000000000)
        dataset[dimension] = dataset[dimension].replace('',-1000000000000)
        dataset[dimension] = dataset[dimension].astype(int)
        dataset[dimension] = dataset[dimension].astype(str)
        dataset[dimension] = dataset[dimension].replace('-1000000000000', np.nan)
        return dataset
    except Exception as e:
        print('convet_dimension_to_int: ' + str(e))
        return dataset


# %%
a2 = tidied_sheets[1]

a2 = tidied_sheets[1]
# Only use the main value data for now
try:
    a2 = a2.loc[a2['Percentage Change'].isna()] 
except:
    print("something went wrong") 

a2 = prefix_refperiod(a2, 'Period')

a2['Gross'].loc[a2['CDID'] == 'YBHA'] = 'Gross domestic product at market prices'  
a2['Indices'].loc[a2['CDID'] == 'YBHA'] = 'Current prices'

a2 = strip_superscripts(a2, 'Gross')
    
a2['Indices'].loc[a2['Indices'] == 'Current prices'] = 'current-price'
a2['Indices'].loc[a2['Indices'] == 'Chained Volume Measure (Reference year 2019)'] = 'chained-volume-measure'

a2['Gross'] = a2['Gross'].apply(pathify)

a2 = a2.rename(columns={'OBS':'Value'})

a2 = convet_dimension_to_int(a2, 'Value')

try:
    a2.drop(['Seasonal Adjustment','Percentage Change','measure'], axis=1, inplace=True)
except:
    # ind = ind
    print("something went wrong")

a2 = a2.rename(columns={'Indices':'Estimate Type', 'Gross':'Aggregate'})

# # +
# Note - This change needs to be finalised

# a2["Estimate Type"] = a2["Estimate Type"].replace({"Chained Volume Measure (Reference year 2019)" : "chained-volume-measure"})
# a2["Estimate Type"].unique()

# %%
mainTitle = metadata.dataset.title
maincomme = metadata.dataset.comment
maindescr = metadata.dataset.description

metadata.dataset.title = mainTitle + ' - National Accounts aggregates (A2)'
metadata.dataset.comment = maincomme + ' - National Accounts aggregates (A2) - GDP and GVA in £ million. Seasonally Adjusted'
metadata.dataset.description = maindescr + """
Estimates are given to the nearest £ million but cannot be regarded as accurate to this degree. 
Data has been Seasonally Adjusted. 
Reference year is 2019. 
Less Basic price adjustment: Taxes on products less subsidies. 
Gross value added excluding oil & gas: Calculated by using gross value added at basic prices minus extraction of crude petroleum and natural gas.
"""
# -

a2.columns

a2["Estimate Type"].unique()

a2.to_csv("national_account_aggregates-observations.csv", index = False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('national_account_aggregates-catalog-metadata.json')

# %%
b1 = tidied_sheets[2]
 # Only use the main value data for now, CVMs
try:
     b1 = b1.loc[b1['Percentage Change'].isna()] 
except:
     print("something went wrong")
    
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
    print("something went wrong while droping")  

b1['Sector'] = b1['Sector'].apply(pathify)
b1['Industry'] = b1['Industry'].apply(pathify)

 # b1 = b1.rename(columns={'OBS':'Value', '2018 Weights':'Weights 2018'})

b1 = convet_dimension_to_int(b1, 'Value')

# %%
b2 = tidied_sheets[3]
try:
    b2 = b2.loc[b2['Percentage Change'].isna()] 
except:
    print("something went wrong")
    
b2['Sector'] = 'Service industries'
b2 = strip_superscripts(b2, 'Industry')
b2 = prefix_refperiod(b2, 'Period')

try:
     b2.drop(['Seasonal Adjustment','Percentage Change','measure'], axis=1, inplace=True)
except:
     print("something went wrong while droping")   

b2['Sector'] = b2['Sector'].apply(pathify)
b2['Industry'] = b2['Industry'].apply(pathify)
# b2 = b2.rename(columns={'OBS':'Value', '2018 Weights':'Weights 2018'})
b2 = convet_dimension_to_int(b2, 'Value')
b1b2 = pd.concat([b1, b2])
b1b2 = b1b2.rename(columns={'OBS':'Value'})
b1b2 = b1b2[['Period','CDID','2019 Weights','Sector','Industry','Value']]
# # There are duplicates in this DataFrame.
duplicate_df = b1b2[b1b2.duplicated(['Period', 'CDID', '2019 Weights', 'Sector', 'Industry', 'Value'], keep = False)]
# # duplicate_df.sort_values(by = ['Value', '2019 Weights', 'Period', 'CDID']).to_csv("b1b2duplicates.csv")
# # duplicate_df
# # b1b2 = b1b2.drop_duplicates()
b1b2.drop_duplicates(subset = b1b2.columns.difference(['Value']), inplace = True)
# # There are duplicates in this DataFrame.
# duplicate_df = b1b2[b1b2.duplicated(['Period', 'CDID', '2019 Weights', 'Sector', 'Industry', 'Value'], keep = False)]
# # duplicate_df.sort_values(by = ['Value', '2019 Weights', 'Period', 'CDID']).to_csv("b1b2duplicates.csv")
# # duplicate_df
metadata.dataset.title = mainTitle + ' - Gross value added chained volume measures at basic prices, by category of output (B1 & B2)'
metadata.dataset.comment = maincomme + ' - Gross value added chained volume measures at basic prices, by category of output (B1 & B2) - Seasonally Adjusted'
metadata.dataset.description = maindescr + """
Estimates cannot be regarded as accurate to the last digit shown.
Data has been Seasonally Adjusted. 
Reference year is 2019.
Components of outputs are valued at basic prices, which excludes taxes and includes subsidies on products.
Weights may not sum to totals due to rounding.
This is a balanced index of UK GVA, taking into account data from the income and expenditure approaches. Thus it will not necessarily be the weighted sum of the industrial indices.
"""
b1b2.to_csv("output_indicators-observations.csv", index = False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('output_indicators-catalog-metadata.json')

# %%

c1 = tidied_sheets[4]

try:
    c1 = c1.loc[c1['Percentage Change'].isna()] 
except:
    print("something went wrong") 

c1 = c1.loc[c1['CDID'] != 'YBHA'] # This is already in one of the other datasets
c1['Expenditure'].loc[c1['CDID'].isin(['YBIL','IKBH','ABMF','IKBI','IKBJ','GIXM'])] = 'not-applicable'
c1['Expenditure'].loc[c1['CDID'].isin(['ABJQ'])] = 'Final consumption expenditure'
c1['Expenditure'].loc[c1['CDID'].isin(['NPQS','NPEK'])] = 'Gross capital formation'

c1 = strip_superscripts(c1, 'Expenditure Category')

c1 = prefix_refperiod(c1, 'Period')

try:
    c1.drop(['Seasonal Adjustment','Percentage Change','measure'], axis=1, inplace=True)
except:
    print("something went wrong while droping")   

c1['Expenditure Category'] = c1['Expenditure Category'].apply(pathify)
c1['Expenditure'] = c1['Expenditure'].apply(pathify)

c1 = c1.rename(columns={'OBS':'Value','Expenditure Category':'Expenditure Category','Expenditure':'Economic Concept'})

c1 = convet_dimension_to_int(c1, 'Value')

c1['Estimate Type'] = 'current-price'
# c1.head(5)

# # + endofcell="--"

c2 = tidied_sheets[5]

try:
   c2 = c2.loc[c2['Percentage Change'].isna()] 
except:
   print("something went wrong") 

c2 = c2.loc[c2['CDID'] != 'ABMI'] # This is already in one of the other datasets
c2['Expenditure'].loc[c2['CDID'].isin(['YBIM','IKBK','ABMG','IKBL','IKBM','GIXS'])] = 'not-applicable'
c2['Expenditure'].loc[c2['CDID'].isin(['ABJR'])] = 'Final consumption expenditure'
c2['Expenditure'].loc[c2['CDID'].isin(['NPQT','NPEL'])] = 'Gross capital formation'

c2 = strip_superscripts(c2, 'Expenditure Category')

c2 = prefix_refperiod(c2, 'Period')

try:
    c2.drop(['Seasonal Adjustment','Percentage Change','measure'], axis=1, inplace=True)
except:
    print("something went wrong while droping")   

c2['Expenditure Category'] = c2['Expenditure Category'].apply(pathify)
c2['Expenditure'] = c2['Expenditure'].apply(pathify)

c2 = c2.rename(columns={'OBS':'Value','Expenditure Category':'Expenditure Category','Expenditure':'Economic Concept'})

c2 = convet_dimension_to_int(c2, 'Value')
    
c2['Estimate Type'] = 'chained-volume-measure'
#c2.head(5)
# # -

c1c2 = pd.concat([c1, c2])
# c1c2cdids = c1c2['CDID'].unique()
# # del c1, c2

metadata.dataset.title = mainTitle + ' - Gross domestic product: expenditure at current prices and chained volume measures (C1 & C2)'
metadata.dataset.comment = maincomme + ' - Gross domestic product: expenditure at current prices and chained volume measures (C1 & C2) - Seasonally Adjusted'
metadata.dataset.description = maindescr + """
Data has been Seasonally Adjusted. 
Reference year is 2019.
Estimates are given to the nearest £ million but cannot be regarded as accurate to this degree.
Non-profit institutions: Non-profit institutions serving households.
Further breakdown of business investment can be found in the 'Business investment in the UK' bulletin
Changes in inventories: Quarterly alignment adjustment included in this series.
Acquisitions less disposals of valuables can be a volatile series, due to the inclusion of non-monetary gold, but any volatility is likely to be GDP neutral as this is offset in UK trade figures
Trade balance is calculated by using exports of goods and services minus imports of goods and services
Non-profit institutions: There is a small difference between the gross operating surplus of the NPISH sector in the SFA release, compared with the consumption of fixed capital for the NPISH sector published in the GDP release.  This affects 2019Q1 onwards. The latest figures for the affected series can be found in the SFA release.
"""
# # --

c1c2.to_csv("expenditure_indicators-observations.csv", index = False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('expenditure_indicators-catalog-metadata.json')


d1 = tidied_sheets[6]

try:
    d1 = d1.loc[d1['Percentage Change'].isna()] 
except:
    print("something went wrong") 

d1 = d1.loc[d1['CDID'] != 'YBHA'] # This is already in one of the other datasets
d1['Gross Domestic Product'].loc[d1['CDID'].isin(['CAER'])] = 'Gross operating surplus of corporations'
d1['Gross Domestic Product'].loc[d1['CDID'].isin(['CGBX','CGCB','CMVL','GIXQ'])] = 'Gross domestic product'

d1 = strip_superscripts(d1, 'Category of Income')

d1 = prefix_refperiod(d1, 'Period')

try:
    d1.drop(['Seasonal Adjustment','Percentage Change','measure'], axis=1, inplace=True)
except:
    print("something went wrong while droping")   

d1['Gross Domestic Product'] = d1['Gross Domestic Product'].apply(pathify)
d1['Category of Income'] = d1['Category of Income'].apply(pathify)

d1 = d1.rename(columns={'OBS':'Value', 'Gross Domestic Product':'Economic Concept'})

d1 = convet_dimension_to_int(d1, 'Value')

d1['Value'][d1['Value'].isna()] = ''
d1['Marker'] = ''
d1['Marker'][d1['Value'] == ''] = 'not-available'

d1cdids = d1['CDID'].unique()
d1.head(5)
#d1['Gross Domestic Product'].unique()
# -

metadata.dataset.title = mainTitle + ' - Gross domestic product: by category of income at current prices (D)'
metadata.dataset.comment = maincomme + ' - Gross domestic product: by category of income at current prices (D) - Seasonally Adjusted'
metadata.dataset.description = maindescr + """
Data has been seasonally adjusted.
Estimates are given to the nearest £ million but cannot be regarded as accurate to this degree.
Private. non-financial corporations: Quarterly alignment adjustment included in this series.
Gross operating surplus of corporations total includes the operating surplus of financial corporations, private non-financial corporations and public corporations.
Other income includes mixed income and the operating surplus of the non-corporate sector.
"""
# --

# +

d1.columns

# +

d1.to_csv("income_indicators-observations.csv", index = False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file('income_indicators-catalog-metadata.json')

# +

e1 = tidied_sheets[7]

e1.columns

# # +
e1 = tidied_sheets[7]

try:
    e1 = e1.loc[e1['Percentage Change'].isna()] 
except:
    print("something went wrong") 

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
    print("something went wrong")   

e1 = e1.rename(columns={'OBS':'Value'})

e1 = convet_dimension_to_int(e1, 'Value')

e1cdids = e1['CDID'].unique()
e1[e1['Expenditure Category'] == 'uk-national-domestic'].head(50)
e1[e1['CDID'] == 'ABJQ'].head(50)

# # +
e2 = tidied_sheets[8]

try:
    e2 = e2.loc[e2['Percentage Change'].isna()] 
except:
    print("something went wrong") 

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
    print("something went wrong")   

e2 = e2.rename(columns={'OBS':'Value'})

e2 = convet_dimension_to_int(e2, 'Value')

e2['Expenditure Category'] = 'uk-domestic'

e2cdids = e2['CDID'].unique()
e2.head(5)

# +
e3 = tidied_sheets[9]

try:
    e3 = e3.loc[e3['Percentage Change'].isna()] 
except:
    print("something went wrong") 

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
    print("something went wrong")   

e3 = e3.rename(columns={'OBS':'Value'})

e3 = convet_dimension_to_int(e3, 'Value')

e3cdids = e3['CDID'].unique()
e3.head(50)

# +
e4 = tidied_sheets[10]

try:
    e4 = e4.loc[e4['Percentage Change'].isna()] 
except:
    print("something went wrong") 

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
    print("something went wrong")   

e4 = e4.rename(columns={'OBS':'Value'})

e4 = convet_dimension_to_int(e4, 'Value')

e4['Expenditure Category'] = 'uk-domestic'

e4cdids = e4['CDID'].unique()
e4.head(5)

# +

e1e2e3e4 = pd.concat([e1, e2, e3, e4])
e1e2e3e4.head(10)

# +

metadata.dataset.title = mainTitle + ' - Household final consumption by purpose and goods and services at Current Prices & Chained Volume Measures (E1, E2, E3, E4)'
metadata.dataset.comment = maincomme + ' - Household final consumption by purpose and goods and services at Current Prices & Chained Volume Measures (E1, E2, E3, E4) - Seasonally Adjusted'
metadata.dataset.description = maindescr + """
Household final consumption by purpose and goods and services at Current Prices & Chained Volume Measures (E1, E2, E3, E4)
Data has been seasonally adjusted
COICOP: ESA 10 Classification of Individual Consumption by Purpose.
UK Domestic: Final consumption expenditure in the UK by UK & foreign households
UK National: Final consumption by UK Households in the UK & abroad.
UK National & Domestic: Final consumption expenditure in the UK by UK & foreign households and final consumption by UK Households in the UK & abroad.
"""

# +

e1e2e3e4.columns

# +

e1e2e3e4["Expenditure Category"].unique()

# +

e1e2e3e4.to_csv("household_expenditure_indicators-observations.csv", index = False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file("household_expenditure_indicators-catalog-metadata.json")



f1 = tidied_sheets[11]

try:
    f1 = f1.loc[f1['Percentage Change'].isna()] 
except:
    ind = 11 

f1['Capital Formation'].loc[f1['CDID'].isin(['L62R'])] = 'Public Corporations - Dwellings'
f1['Capital Formation'].loc[f1['CDID'].isin(['L62S'])] = 'Public Corporations - Costs of transfer of ownership of non-produced assests'
f1['Capital Formation'].loc[f1['CDID'].isin(['L62T'])] = 'Private Sector - Dwellings'
f1['Capital Formation'].loc[f1['CDID'].isin(['L62U'])] = 'Private Sector - Costs of transfer of ownership of non-produced assests'

f1['Analysed by'].loc[f1['CDID'].isin(['NPEK','RPZG'])] = 'Analysis by sector'

f1 = strip_superscripts(f1, 'Capital Formation')

f1['Economic Concept'] = 'current-price'

f1 = prefix_refperiod(f1, 'Period')

try:
    f1.drop(['Seasonal Adjustment','Percentage Change','measure'], axis=1, inplace=True)
except:
    ind = 11   

f1 = f1.rename(columns={'OBS':'Value', 'Analysed by':'Analysis'})

f1 = convet_dimension_to_int(f1, 'Value')

f1['Capital Formation'] = f1['Capital Formation'].apply(pathify)
f1['Analysis'] = f1['Analysis'].apply(pathify)

f1cdids = f1['CDID'].unique()
f1.head(5)


f2 = tidied_sheets[12]

try:
    f2 = f2.loc[f2['Percentage Change'].isna()] 
except:
    ind = 12 

f2['Capital Formation'].loc[f2['CDID'].isin(['L634'])] = 'Public Corporations - Dwellings'
f2['Capital Formation'].loc[f2['CDID'].isin(['L635'])] = 'Public Corporations - Costs of transfer of ownership of non-produced assests'
f2['Capital Formation'].loc[f2['CDID'].isin(['L636'])] = 'Private Sector - Dwellings'
f2['Capital Formation'].loc[f2['CDID'].isin(['L637'])] = 'Private Sector - Costs of transfer of ownership of non-produced assests'

f2['Analysed by'].loc[f2['CDID'].isin(['NPEL','DLWF'])] = 'Analysis by sector'

f2 = strip_superscripts(f2, 'Capital Formation')

f2['Economic Concept'] = 'chained-volume-measure'

f2 = prefix_refperiod(f2, 'Period')

try:
    f2.drop(['Seasonal Adjustment','Percentage Change','measure'], axis=1, inplace=True)
except:
    ind = 12   

f2 = f2.rename(columns={'OBS':'Value', 'Analysed by':'Analysis'})
f2["Analysis"] = f2["Analysis"].loc[f2['Analysis'] == "analysis-by-sector-7"] = "analysis-by-sector"
f2 = convet_dimension_to_int(f2, 'Value')

f2['Capital Formation'] = f2['Capital Formation'].apply(pathify)
f2['Analysis'] = f2['Analysis'].apply(pathify)

f2cdids = f2['CDID'].unique()
f2.head(5)
# -

f1["Analysis"].unique()

f2["Analysis"].unique()

f1f2 = pd.concat([f1,f2])
#f1f2['Analysis'] = f1f2['Analysis'].str.replace('analysis-by-','')
f1f2cdids = pd.concat([pd.DataFrame(f1cdids),pd.DataFrame(f2cdids)])

metadata.dataset.title = mainTitle + ' - Gross fixed capital formation by sector and type of asset at current prices and chained volume measures (F1, F2)'
metadata.dataset.comment = maincomme + ' - Gross fixed capital formation by sector and type of asset at current prices and chained volume measures (F1, F2) - Seasonally Adjusted'
metadata.dataset.description = maindescr + """
Gross fixed capital formation by sector and type of asset at current prices and chained volume measures (F1, F2)
Data has been seasonally adjusted
Business Investment: Not including expenditure on dwellings, land and existing buildings and costs associated with the transfer of ownership of non-produced assets.
Public Corporations: Remaining investment by public non-financial corporations included within business investment.
ICT equipment and other machinery and equipment: Includes cultivated biological resources (AN.115) and weapons (AN.114)
Dwellings: Includes new dwellings and improvements to dwellings.
Other buildings and structures: Including costs associated with the transfer of ownership of buildings, dwellings and non-produced assets.
"""

# +

f1f2.columns

# +

f1f2["Analysis"].unique()

# +

# There are duplicates in this DataFrame.
duplicate_df_f1f2 = f1f2[f1f2.duplicated(['Value', 'CDID', 'Analysis', 'Period', 'Capital Formation','Economic Concept'], keep = False)]
# duplicate_df_f1f2.sort_values(by = ['Value']).to_csv("f1f2duplicates.csv")
# duplicate_df_f1f2
# -

f1f2.drop_duplicates(subset = f1f2.columns.difference(['Value']), inplace = True)

duplicate_df_f1f2 = f1f2[f1f2.duplicated(['Value', 'CDID', 'Analysis', 'Period', 'Capital Formation','Economic Concept'], keep = False)]
duplicate_df_f1f2

f1f2.head(5)

f1f2.to_csv("gross_fixed_capitol-observations.csv", index = False)
catalog_metadata = metadata.as_csvqb_catalog_metadata()
catalog_metadata.to_json_file("gross_fixed_capitol-catalog-metadata.json")

# # +

# g1 = tidied_sheets[13]

# try:
#     g1 = g1.loc[g1['Percentage Change'].isna()] 
# except:
#     ind = 13 

# g1 = strip_superscripts(g1, 'Sector')

# g1['Sector'].loc[g1['CDID'].isin(['FAGF','FADY','FALR','NZTP'])] = 'Manufacturing - ' + g1['Sector'].loc[g1['CDID'].isin(['FAGF','FADY','FALR','NZTP'])].astype(str)
# g1['Sector'].loc[g1['CDID'].isin(['FBHE','FAHA'])] = 'Distributive trades - ' + g1['Sector'].loc[g1['CDID'].isin(['FBHE','FAHA'])].astype(str)
# g1['Sector'].loc[g1['CDID'].isin(['CAEX'])] = 'Total' 


# g1['Economic Concept'] = 'current-price'

# g1 = prefix_refperiod(g1, 'Period')

# try:
#     g1.drop(['Seasonal Adjustment','Percentage Change','measure'], axis=1, inplace=True)
# except:
#     ind = 13   

# g1 = g1.rename(columns={'OBS':'Value'})

# g1 = convet_dimension_to_int(g1, 'Value')
# g1['Level of inventories held at end-December 2019'] = g1['Level of inventories held at end-December 2019'].str.replace('.0','')

# g1['Sector'] = g1['Sector'].apply(pathify)
# g1['Industry'] = g1['Industry'].apply(pathify)

# g1cdids = g1['CDID'].unique()
# g1.head(5)

# # +

# g2 = tidied_sheets[14]

# try:
#     g2 = g2.loc[g2['Percentage Change'].isna()] 
# except:
#     ind = 14

# g2 = strip_superscripts(g2, 'Sector')

# g2['Sector'].loc[g2['CDID'].isin(['FBNF','FBNG','FBNH','DHBM'])] = 'Manufacturing - ' + g2['Sector'].loc[g2['CDID'].isin(['FBNF','FBNG','FBNH','DHBM'])].astype(str)
# g2['Sector'].loc[g2['CDID'].isin(['FAJX','FBYN'])] = 'Distributive trades - ' + g2['Sector'].loc[g2['CDID'].isin(['FAJX','FBYN'])].astype(str)
# g2['Sector'].loc[g2['CDID'].isin(['CAFU'])] = 'Total' 


# g2['Economic Concept'] = 'chained-volume-measure'

# g2 = prefix_refperiod(g2, 'Period')

# try:
#     g2.drop(['Seasonal Adjustment','Percentage Change','measure'], axis=1, inplace=True)
# except:
#     ind = 14  

# g2 = g2.rename(columns={'OBS':'Value'})

# g2 = convet_dimension_to_int(g2, 'Value')
# g2['Level of inventories held at end-December 2019'] = g2['Level of inventories held at end-December 2019'].str.replace('.0','')

# g2['Sector'] = g2['Sector'].apply(pathify)
# g2['Industry'] = g2['Industry'].apply(pathify)

# g2cdids = g2['CDID'].unique()
# g2.head(5)
# # -

# g1g2 = pd.concat([g1,g2])
# del g1g2['Industry']

# # +

# metadata.dataset.title = mainTitle + ' - Change in inventories at current prices and chained volume measures (G1, G2)'
# metadata.dataset.comment = maincomme + ' - Change in inventories at current prices and chained volume measures (G1, G2) - Seasonally Adjusted'
# metadata.dataset.description = maindescr + """
# Change in inventories at current prices and chained volume measures (G1, G2)
# Data has been seasonally adjusted
# Estimates are given to the nearest £ million but cannot be regarded as accurate to this degree.
# Wholesaling and retailing estimates exclude the motor trades.
# Total change in inventories: Quarterly alignment adjustment included in this series.
# Please note, inventories estimates for 2020 Q4 at this stage face additional uncertainty due to the lower data content. 
# """
# # -

# g1g2.columns

# g1g2.head(5)

# # +

# g1g2.to_csv("inventories-observations.csv", index = False)
# catalog_metadata = metadata.as_csvqb_catalog_metadata()
# catalog_metadata.to_json_file("inventories-catalog-metadata.json")

# # +

# h1 = tidied_sheets[15]

# try:
#     h1 = h1.loc[h1['Percentage Change'].isna()] 
# except:
#     ind = 15 

# h1['Flow'].loc[h1['CDID'].isin(['BOKG','IKBB','IKBH'])] = 'Exports'
# h1['Flow'].loc[h1['CDID'].isin(['BOKH','IKBC','IKBI'])] = 'Imports'
# h1['Flow'].loc[h1['CDID'].isin(['BOKI','IKBO','IKBJ'])] = 'Balance'


# h1['Economic Concept'] = 'current-price'

# h1 = prefix_refperiod(h1, 'Period')

# try:
#     h1.drop(['Seasonal Adjustment','Percentage Change','measure'], axis=1, inplace=True)
# except:
#     ind = 15  

# h1 = h1.rename(columns={'OBS':'Value'})

# h1 = convet_dimension_to_int(h1, 'Value')

# h1['Goods or Services'] = h1['Goods or Services'].apply(pathify)
# h1['Flow'] = h1['Flow'].apply(pathify)

# h1cdids = h1['CDID'].unique()
# h1.head(5)

# # +

# h2 = tidied_sheets[16]

# try:
#     h2 = h2.loc[h2['Percentage Change'].isna()] 
# except:
#     ind = 16

# h2['Flow'].loc[h2['CDID'].isin(['BQKQ','IKBE','IKBK'])] = 'Exports'
# h2['Flow'].loc[h2['CDID'].isin(['BQKO','IKBF','IKBL'])] = 'Imports'
# h2['Flow'].loc[h2['CDID'].isin(['IKBM'])] = 'Balance'

# h2['Economic Concept'] = 'chained-volume-measure'

# h2 = prefix_refperiod(h2, 'Period')

# try:
#     h2.drop(['Seasonal Adjustment','Percentage Change','measure'], axis=1, inplace=True)
# except:
#     ind = 16

# h2 = h2.rename(columns={'OBS':'Value'})

# h2 = convet_dimension_to_int(h2, 'Value')

# h2['Goods or Services'] = h2['Goods or Services'].apply(pathify)
# h2['Flow'] = h2['Flow'].apply(pathify)

# h2cdids = h2['CDID'].unique()
# h2.head(5)

# # +

# h1h2 = pd.concat([h1,h2])
# h1h2cdids = pd.concat([pd.DataFrame(h1cdids),pd.DataFrame(h2cdids)])
# h1h2['Goods or Services'][h1h2['Goods or Services'] == 'total-1'] = 'total'

# # +
# #h1h2['Goods or Services'].unique()

# h1h2.columns

# # +

# metadata.dataset.title = mainTitle + ' - Exports and Imports of goods and services at current prices and chained volume measures (H1, H2)'
# metadata.dataset.comment = maincomme + ' - Exports and Imports of goods and services at current prices and chained volume measures (H1, H2) - Seasonally Adjusted'
# metadata.dataset.description = maindescr + """
# Exports and Imports of goods and services at current prices and chained volume measures (H1, H2)
# Data has been seasonally adjusted
# Trade balance is calculated by using exports of goods and services minus imports of goods and services
# """
# # -

# h1h2.to_csv("trade-observations.csv", index = False)
# catalog_metadata = metadata.as_csvqb_catalog_metadata()
# catalog_metadata.to_json_file("trade-catalog-metadata.json")

# # +

# # # +
# #cids = pd.concat([pd.DataFrame(f1f2cdids),pd.DataFrame(g1g2cdids),pd.DataFrame(h1h2cdids)])
# #print('Before: ' + str(cids[0].count()))
# #cids = cids.drop_duplicates()
# #print('After: ' + str(cids[0].count()))
# #cids = cids.rename(columns={cids.columns[0]:'Label'})
# #cids['Notation'] = cids['Label']
# #cids['Parent Notation'] = ''
# #cids['Sort Priority'] = np.arange(cids.shape[0]) + 6654
# #cids.to_csv('cdids.csv', index=False)
# #cids

# # # +
# #import dmtools as dm
# #fldrpth = '/users/leigh/Development/family-trade/reference/codelists/'
# #dm.search_for_codes_using_levenshtein_and_fuzzywuzzy(tidied_sheets[ind]['Sector'].unique(), fldrpth, 'Notation', 'sector', 3, 0.8)
# #dm.search_codelists_for_codes(d1['Category of Income'].unique(), fldrpth, 'Notation', 'Category of Income')
# %%
