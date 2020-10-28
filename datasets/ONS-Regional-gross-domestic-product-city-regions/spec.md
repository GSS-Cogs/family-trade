# COGS Dataset Specification
----------

## Regional gross domestic product city regions

[Landing Page](https://www.ons.gov.uk/economy/grossdomesticproductgdp/datasets/regionalgrossdomesticproductcityregions)

----------

### Stage 1. Transform

#### Sheet: Table 1 to Table 13 
    Period : cell D2 across
    Area Type : Cell A3 Down 
    Geo Code : Cell B3 Down
    Area Name : Cell C3 Down
    
    Dimension name unsure? : cell A1 (removing Table ??: City Regions: from string) 
    Marker '-' = ? assuming it means not-applicable as it is only in Table 13 for year 1999. 
   

#### Table Structure

		Period, Area Type, Area Name, Geo Code,  Value, Marker

#### DE Stage one notes 
    'Dimension name unsure' - Not sure what to call this dimension, it relates to the information on each sheet and needed to differentiate the data. 
    													
	Contents												
	Table 1		Gross value added (balanced) at current basic prices										
	Table 2		Value Added Tax on products										
	Table 3		Other taxes on products										
	Table 4		Subsidies on products										
	Table 5		Gross domestic product at current market prices										
	Table 6		Total resident population numbers										
	Table 7		Gross domestic product per head at current market prices										
	Table 8		Whole economy GVA implied deflators										
	Table 9		Gross domestic product chained volume measures index										
	Table 10	Gross domestic product chained volume measures in 2016 money value										
	Table 11	Gross domestic product chained volume measures per head										
	Table 12	Gross domestic product chained volume measures annual growth rates										
	Table 13	Gross domestic product chained volume measures per head annual growth rates										
    (Slighly different wording extracted in transformation of sheets but can change to the above.)
    
    There are 5 diffferent unit values:
    '£ million', 'persons', 'pounds', '2016=100', '%'
    
    Therefore will have to split datasets out into 5 seperate ones unless multiple Measure type issue has changed. 
    

#### Stage 2: Harmonisation


