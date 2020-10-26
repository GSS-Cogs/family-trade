<!-- #region -->
# COGS Dataset Specification
----------

## Exports of services by country, by modes of supply (exports)

[Landing Page](https://www.ons.gov.uk/businessindustryandtrade/internationaltrade/datasets/exportsofservicesbycountrybymodesofsupply)

----------

### Stage 1. Transform

#### Sheet: Sheet1 
    Period : 2018 (Hardcoded, can be taken from cell "E1")
    Country : Cell A2 Down 
    Mode : Cell B2 Down
    Direction : Cell C2 Down
    Service Account : Cell D2 down
   

#### Table Structure

		Period, Country, Mode, Direction, Service Account, Value

#### DE Stage one notes 
easy one sheet dataset representing Exports. Data representing Imports can be found [here](https://www.ons.gov.uk/businessindustryandtrade/internationaltrade/articles/modesofsupplyukexperimentalestimates/2018/relateddata) and could easily be joined together with a "FLOW" dimension. Naming of dataset would need to be altered to reflect. 

Modes will need to be defined, mode information can be found [here](https://www.ons.gov.uk/businessindustryandtrade/internationaltrade/articles/modesofsupplyukexperimentalestimates/2018)
    
    Unit = ?? 
    Measure Type = Count 

### Stage 2 - Harmonisation

	I have checked Imports file and agree that they should be joined up. Will ask BAs to possibly join up record in AirTable or record what we are doing. Codelists below will still apply for Imports file.

	Rename 'Direction' to 'Flow' and change value to 'exports' and reference back to column (info.json) in ref_common/codelists
	'Country':
		codelist needs to be created. Split string and use 2/3 alpha/numerical code for notation and the rest for Label:
			Label,       Notation, Parent Notation, Sort Priority
			World Total, W1,     ,                , 1
	'Mode':
		codelists needs to be created with the following values
			total: Total
			mode-1: Remote Trade
			mode-2: Consumption Abroad
			mode-3: Commercial Presence
			mode-4: Presence of Natural Persons
	'Service Account':
		codelist needs to be created. Split string and use numerical code for notation and the rest for Label:
			Label,       Notation, Parent Notation, Sort Priority
			Total services, 0,     ,                , 1


	Scraper:
		Dataset-Title: exportsofservicesbycountrybymodesofsupply

		Title: Imports and Exports of services by country, by modes of supply

		Comment: Country breakdown of trade in services values by mode of supply (imports/exports) for 2018. Countries include only total services data, while regions include top-level extended balance of payments (EBOPs) breakdown.

		Description: 
		New statistics presented in this article have been achieved as part of our ambitious trade development plan to provide more detail than ever before about the UK’s trading relationships, using improved data sources and methods enabled by our new trade IT systems.

		When thinking about trade, most people imagine lorries passing through ports. While this is true for trade in goods, this is not the case for trade in services, which are not physical. Trade in services statistics are by nature more challenging to measure, due largely to their intangible nature. While it is relatively straightforward to measure the number of cars that are imported and exported through UK ports, capturing the amount UK advertisers generate from providing services to overseas clients is much more challenging. Nevertheless, it is important that we continue to develop our trade in services statistics given the UK is an overwhelmingly services dominated economy.

		While our trade in services statistics already record the type of products being traded (for example, financial services) and who it is being traded with (for example, Germany), policymakers are increasingly interested in how that trade is conducted. This type of information is critical for understanding what barriers businesses face when looking to trade, and to assist policymakers engaged in trade negotiations.

		To increase the information available to users on how UK trade in services is conducted, we have been developing statistics on so-called “modes of supply”. The UK is one of the first countries to have developed such estimates.

		See report and methodology here:
		https://www.ons.gov.uk/businessindustryandtrade/internationaltrade/articles/modesofsupplyukexperimentalestimates/latest
	
#### DM Notes

	Country and Service Account codelists will probably be harmonised to a central reference at some point