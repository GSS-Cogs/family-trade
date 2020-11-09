# COGS Dataset Specification
----------

## UK trade in services by industry, country and service type, exports

[Landing Page](https://www.ons.gov.uk/economy/nationalaccounts/balanceofpayments/datasets/uktradeinservicesbyindustrycountryandservicetypeexports)

----------

### Stage 1. Transform

#### Sheet: Sheet1 
    Period : cell E1 across
    Country : Cell A2 Down 
    Industry : Cell B2 Down
    Direction : Cell C2 Down
    Service Account : Cell D2 down
    
    Marker '..' = 'suppressed data'
   

#### Table Structure

		Period, Country, Industry, Direction, Service Account, Value, Marker

#### DE Stage one notes 
    
   NB: Imports data also avilable, it looks like we could pop them in a single cube with the addition of a flow dimension. https://www.ons.gov.uk/economy/nationalaccounts/balanceofpayments/articles/uktradeinservicesbyindustrycountryandservicetype/2016to2018/relateddata
    
    Unit = £ million
    Measure Type = Count 


#### Stage 2: Harmonisation

	Have looked at imports data and agree that it can be combined with exports. I have updated the issue cards to reflect this.
	Will also create a Trade folder in ref_common and start putting the codelists in there as some of the dimensions in this dataset have also Been used in others.
	The following applies to bot Import and Export data.

		'Direction': Change 'EX' to 'export' and 'IM' to 'import'. reference 'Flow' codelist in ref_common/trade
		'Country': Split string and only use first 2/3 character code. Reference 'ons-country' codelist in ref_common/trade (pathify)
		'Industry': Split string and only use initial number(s). Reference 'ons-industry' codelist in ref_common/trade              
		'Service Account': Split string and only use initial number(s). Reference 'ons-service-account' codelist in ref_common/trade             
		'Measure Type': current-prices
		'Unit': gbp-million
		'Marker': Change suppressed-data to suppressed. replace NaNs with empty string and replace empty Values with 0

	Scraper:
		Dataset-title: uktradeinservicesbyindustrycountryandservicetypeexport
		Title: UK trade in services by industry, country and service type, Imports & Exports
		Comment: Experimental dataset providing a breakdown of UK trade in services by industry, country and service type on a balance of payments basis. Data are subject to disclosure control, which means some data have been suppressed to protect confidentiality of individual traders.
		Description:  Experimental dataset providing a breakdown of UK trade in services by industry, country and service type on a balance of payments basis. Data are subject to disclosure control, which means some data have been suppressed to protect confidentiality of individual traders.

		Users should note the following:	
		Industry data has been produced using Standard Industrial Classification 2007 (SIC07).
	
		Service type data has been produced using Extended Balance of Payments (EBOPs).	
		Due to risks around disclosing data releated to individual firms we are only able to provide data for certain combinations of the dimensions included, i.e. country, service type and industry. This dataset therefore provides the following two combinations:	
		Industry (SIC07 2 digit), by service type (EBOPs 1 digit), by geographic region (world total, EU and non-EU)
		Industry (SIC07 2 digit), by total service type, by individual country
		Some data cells have been suppressed to protect confidentiality so that individual traders cannot be identified.
	
		Data
		All data is in £ million, current prices	

		Rounding
		Some of the totals within this release (e.g. EU, Non EU and world total) may not exactly match data published via other trade releases due to small rounding differences.
	
		Trade Asymmetries 
		These data are our best estimate of these bilateral UK trade flows. Users should note that alternative estimates are available, in some cases, via the statistical agencies for bilateral countries or through central databases such as UN Comtrade (https://comtrade.un.org/)

#### DM Notes

	Codelists that need to be created in ref_common:

		Country
		Industry
		Flow (Direction)
		Service Account
