# COGS Dataset Specification
----------

## Regional Gross Domestic Product city regions

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
	Table 5		Gross Domestic Product at current market prices										
	Table 6		Total resident population numbers										
	Table 7		Gross Domestic Product per head at current market prices										
	Table 8		Whole economy GVA implied deflators										
	Table 9		Gross Domestic Product chained volume measures index										
	Table 10	Gross Domestic Product chained volume measures in 2016 money value										
	Table 11	Gross Domestic Product chained volume measures per head										
	Table 12	Gross Domestic Product chained volume measures annual growth rates										
	Table 13	Gross Domestic Product chained volume measures per head annual growth rates										
    (Slighly different wording extracted in transformation of sheets but can change to the above.)
    
    There are 5 diffferent unit values:
    '£ million', 'persons', 'pounds', '2016=100', '%'
    
    Therefore will have to split datasets out into 5 seperate ones unless multiple Measure type issue has changed. 
    

#### Stage 2: Harmonisation

	Rename column 'Period' to 'Year'
	Geo Code
		Greater London Authority: According to http://statistics.data.gov.uk/atlas/search, the code this is E61000001. Replace 'Not available' with this code.
		reference http://statistics.data.gov.uk/id/statistical-geography/ in info.json
	Area Type
		change values to 'city-region' and 'local-authority' and reference geography-level in ref_common
	Remove columns: 'Area name' and 'Unit' (will de defined in info.json)
	Dimension name unsure?
		remove superscripts from strings (1,2 etc.)
		rename: 'GDP Estimate Type'. Needs to be pathified and a codelist created 
	Marker
		all 2018 values need to have 'provisional' in the Marker column set bans to empty string

	Scraper
	IF WE STILL CANNOT DO MULTL-MEASURE CUBES THEN THE DATA WILL NEED TO BE SPLIT INTO 8 DATASETS
		1. Tables 1 to 5
			Title: Regional Gross Domestic Product city regions - GDP in Current Prices 
			Comment: Annual estimates of balanced UK regional Gross Domestic Product (GDP). Current price estimates for combined authorities and city regions.
			Measure: cp, Unit: gbp-million, Datatype: integer, dataset_path: dataset_path + /cp
		2. Table 6
			Title: Regional Gross Domestic Product city regions - Total resident Population numbers
			Comment: Annual estimates of balanced UK regional Gross Domestic Product (GDP). Total resident population numbers for combined authorities and city regions.
			Measure: count, Unit: persons, Datatype: integer, dataset_path: dataset_path + /pop
		3. Table 7
			Title: Regional Gross Domestic Product city regions - GDP per Head at Current Market Prices
			Comment: Annual estimates of balanced UK regional Gross Domestic Product (GDP). CGDP per Head at Current Market Prices for combined authorities and city regions..
			Measure: amp, Unit: gbp, Datatype: integer, dataset_path: dataset_path + /cmp
		4. Table 8
			Title: Regional Gross Domestic Product city regions - Whole Economy GVA Implied Deflators
			Comment: Annual estimates of balanced UK regional Gross Domestic Product (GDP). Whole Economy GVA Implied Deflators for combined authorities and city regions.
			Measure: gva, Unit: deflators, Datatype: double, dataset_path: dataset_path + /deflate
		5. Table 9
			Title: Regional Gross Domestic Product city regions - Chained Volume Measures index
			Comment: Annual estimates of balanced UK regional Gross Domestic Product (GDP). Chained Volume Measures index for combined authorities and city regions.
			Measure: cvm, Unit: index, Datatype: double, dataset_path: dataset_path + /cvmindex
		6. Table 10
			Title: Regional Gross Domestic Product city regions - Chained Volume Measures in 2016 money value
			Comment: Annual estimates of balanced UK regional Gross Domestic Product (GDP). Chained Volume Measures in 2016 money value for combined authorities and city regions.
			Measure: cvm, Unit: gbp-million, Datatype: integer, dataset_path: dataset_path + /cvmmoney
		7. Table 11
			Title: Regional Gross Domestic Product city regions - Chained Volume Measures per head
			Comment: Annual estimates of balanced UK regional Gross Domestic Product (GDP). Chained Volume Measures per head for combined authorities and city regions.
			Measure: cvm, Unit: gbp, Datatype: integer, dataset_path: dataset_path + /cvmhead
		8. Table 12 & 13
			Title: Regional Gross Domestic Product city regions - Chained Volume Measures annual growth rates
			Comment: Annual estimates of balanced UK regional Gross Domestic Product (GDP). Chained Volume Measures annual growth rates for combined authorities and city regions.
			Measure: cvm, Unit: rate, Datatype: double, dataset_path: dataset_path + /cvmrate

		Description: (see footnotes)
		Family: trade
			
### Footnotes

	These tables are part of the regional economic activity by Gross Domestic Product release

	The data herein are based on the balanced measure of regional gross value added (GVA(B)), which combines estimates produced using the income and production approaches to create a single best estimate of GVA for each industry in each region.	
	We have now included the effects of taxes and subsidies on products to derive annual estimates of regional GDP for the first time. GDP is equivalent to GVA plus Value Added Tax (VAT) plus other taxes on products less subsidies on products.	
	This is part of several datasets that give the full picture of Gross Domestic Product
	Current Price data
		Regional Gross Domestic Product city regions - GDP in Current Prices
			Gross Value Added (Balanced) at current basic prices
 			Value Added Tax (VAT) on products
 			Other taxes on products
 			Subsidies on products
 			Gross Domestic Product (GDP) at current market prices

	Used to calculate GDP per head:
		Regional Gross Domestic Product city regions - Total resident Population numbers
 		Regional Gross Domestic Product city regions - GDP per Head at Current Market Prices

	The implied deflators from the GVA(B) dataset:
		Regional Gross Domestic Product city regions - Whole Economy GVA Implied Deflators

	The deflators are used to remove the effect of price inflation and derive volume measures of regional GDP:
		Regional Gross Domestic Product city regions - Chained Volume Measures index
 		Regional Gross Domestic Product city regions - Chained Volume Measures in 2016 money value

	Volume GDP per head is given in:
		Regional Gross Domestic Product city regions - Chained Volume Measures per head
		
	And the annual growth rates of volume GDP and volume GDP per head are given in:
		Regional Gross Domestic Product city regions - Chained Volume Measures annual growth rates
			Snnual growth rates
 			Per head annual growth rates
 
	All calculations are carried out using unrounded data.		

	Workplace-based estimates are allocated to the region in which the economic activity takes place. 
	Components may not sum to totals as a result of rounding.
	Implied deflators are derived from whole economy current price and chained volume measures of GVA. 
	Use of implied deflators duplicates the effect of chain-linking, though technically this results in constant price volume measures.
	Components will not sum to totals since chain-linking produces non-additive volume estimates.						

### DM Notes

	Will have to check with data producer that they are happy with text in description	