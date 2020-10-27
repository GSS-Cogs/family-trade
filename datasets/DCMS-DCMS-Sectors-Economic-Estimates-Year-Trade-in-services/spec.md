# COGS Dataset Specification
----------

## DCMS Sectors Economic Estimates 2018: Trade in services

[Landing Page](https://www.gov.uk/government/statistics/dcms-sectors-economic-estimates-2018-trade-in-services)

----------

### Stage 1. Transform

#### Sheet: Imports 
    Period : 2018 (Hardcoded)
    Country : Cell A5 Down 
    Sector : A3 across
    Sector Type : B4 across
    Flow : Imports (Hardcoded)
    
#### Sheet: Exports 
    Period : 2018 (Hardcoded)
    Country : Cell A5 Down 
    Sector : A3 across
    Sector Type : B4 across
    Flow : Exports (Hardcoded)

#### Table Structure

		Period, Country, Sector, Sector Type, Flow, Measure Type, Unit, Value, Marker

#### DE Stage one notes 
    Marker "-" cannot easily find exactly what this translates to therefore have made it "n/a" for now. 
    Unsure if Sector and Sub Sector are the best naming conventions for those dimensions 
    
    I have applied the following to Unit and Measure type, might not be correct. 
    
    Unit = Millions (pounds)
    Measure Type = Count 
    
    Is it still OK to use "Flow" to represent Imports and Exports Marker "-" cannot easily find exactly what this translates to therefore have made it "n/a" for now. 
    	Unsure if Sector and Sub Sector are the best naming conventions for those dimensions 
    
    	I have applied the following to Unit and Measure type, might not be correct. 
    
    	Unit = Millions (pounds)
    	Measure Type = Count 
    
    	Is it still OK to use "Flow" to represent Imports and Exports together?


### Stage 2: Harmonisation

#### Output dataset

	Replace empty cells in Value column with 0. Some do not have n/a in the Marker column?
	It is unclear what "-" means but probably is N/A, have asked Dave Hull to clarify. Can you change it to "not-applicable" as this is defined in the Marker file in ref_common/codelists.
    
    Have spoken to BAs who have contacted the publisher with the following answer:
    '-' is used to denote a value that has been suppressed as part of the disclosure control procedure.
    So can we make the 'Marker' column = 'suppressed' where the 'Value' column is '-' please and change 'Value' to 0?
	
    Need to define the following codelists:
		Country
		Sector
		Sector Type (some values have super-script numbers at the end (Crafts4), need to remove)
		Flow (ok to use but define in ref_common/codelists and reference in info.json as will probably be used by a few pipelines)
		pathify once codelists have been created
	Change "Unit" to "gbp-million"" as this is defined in the measurements-unit.csv in ref_common

	Scraper
		Dataset Title: dcms-sectors-economic-estimates-2018-trade-in-services
		
		Title: Sectors Economic Estimates 2018: Trade in services
		
		Comment: Official Statistics used to provide an estimate of the contribution of DCMS Sectors to the UK economy, measured by imports and exports of services.
		
		Description: DCMS Sector Economic Estimates 2018: Trade in Services is an official statistic and has been produced to the standards set out in the Code of Practice for Statistics.
		DCMS Sectors Economic Estimates 2018: Trade in services report:
		https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/863862/DCMS_Sectors_Economic_Estimates_2018_Trade_In_Services.pdf
		
		This release provides estimates of exports and imports of services by businesses in DCMS Sectors excluding Tourism and Civil Society2) in current prices. Any changes between years may reflect changes in the absolute value of the £ (affected by the domestic rate of inflation and by exchange rates), as well as changes in actual trade volume. These statistics are further broken down by selected countries, regions and continents.The latest year for which these estimates are available is 2018. Estimates of trade in services have been constructed from ONS official statistics using international classifications (StandardIndustrial Classification (SIC) codes). For further information see Annex A and the quality assurance (QA) document accompanying this report.Data are available for each DCMS Sector (excluding Tourism and Civil Society) and sub-sectors within the Creative Industries, Digital Sector, and Cultural Sector. There is significant overlap between DCMS Sectors so users should be aware that the estimate for “DCMSSectors Total” is lower than the sum of the individual sectors.
		
		The World totals are calculated on the same basis as previous years. However, the list of individual countries used in the calculation of the (world) regional and continental statistics (e.g. European Union, Latin America and Caribbean, Asia) is slightly different to the previous (August 2019) release. Therefore, these statistics in particular are not directly comparable with previous years. In particular: 
               -The Bailiwick of Guernsey, the Bailiwick of Jersey and Timor-Leste form part of the Europe, Rest of Europe and    Asia totals for the first time.
               -Gibraltar is included, and now forms part of the European Union total, in line with the Balance of Payments Vademecum. The EU Institutions total is also included on its own for the first time.     
               -Latin America & Caribbean no longer includes America Unallocated as part of its calculation.	
            A revised backseries of calculations on the current basis is expected to be provided in the summer.	

#### DM Notes

		I think that's it!
