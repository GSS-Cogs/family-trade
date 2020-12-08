# COGS Dataset Specification

[Family Home](https://gss-cogs.github.io/family-trade/datasets/specmenu.html)

[Family Transform Status](https://gss-cogs.github.io/family-trade/datasets/index.html)

## ONS UK Total Trade

[Landing Page](https://www.ons.gov.uk/businessindustryandtrade/internationaltrade/datasets/uktotaltradeallcountriesnonseasonallyadjusted)

#### Sheet: 1 Total Trade by Country - A

	Dimensions
		Period: row 4, format into year/{yr} (year/2020)
		Country: use the 2 letter code in column A as the value, codelist will have the country name as the Label
		Flow: rows 7 to 251 are Exports and rows 255 to 499 are Imports
		Trade Type: total

		Measure type = trade
		Unit = gbp-millions

#### Sheet: 2 Total Trade by Country - Q

	Dimensions
		Period: row 4, format into quarter/{qtr} (quarter/Q1)
		Country: use the 2 letter code in column A as the value, codelist will have the country name as the Label
		Flow: rows 7 to 251 are Exports and rows 255 to 499 are Imports
		Trade Type: total

		Measure type = trade
		Unit = gbp-millions

#### Sheet: 3 TIG by Country - A

	Dimensions
		Period: row 4, format into year/{yr} (year/2020)
		Country: use the 2 letter code in column A as the value, codelist will have the country name as the Label
		Flow: rows 7 to 251 are Exports and rows 255 to 499 are Imports
		Trade Type: goods

		Measure type = trade
		Unit = gbp-millions

#### Sheet: 3 TIG by Country - Q

	Dimensions
		Period: row 4, format into quarter/{qtr} (quarter/Q1)
		Country: use the 2 letter code in column A as the value, codelist will have the country name as the Label
		Flow: rows 7 to 251 are Exports and rows 255 to 499 are Imports
		Trade Type: goods

		Measure type = trade
		Unit = gbp-millions

#### Sheet: 3 TIS by Country - A

	Dimensions
		Period: row 4, format into year/{yr} (year/2020)
		Country: use the 2 letter code in column A as the value, codelist will have the country name as the Label
		Flow: rows 7 to 251 are Exports and rows 255 to 499 are Imports
		Trade Type: services

		Measure type = trade
		Unit = gbp-millions

#### Sheet: 3 TIS by Country - Q

	Dimensions
		Period: row 4, format into quarter/{qtr} (quarter/Q1)
		Country: use the 2 letter code in column A as the value, codelist will have the country name as the Label
		Flow: rows 7 to 251 are Exports and rows 255 to 499 are Imports
		Trade Type: services

		Measure type = trade
		Unit = gbp-millions

#### Join

	Join all 6 tables together into one datacube

	Marker
		Any N/A values put not-collated in cell . Description also explains the reason for this

	Scraper
		dataset_id: (only one dataset output so will probably not need changing)
		Title: (only one dataset output so will probably not need changing)
		Comment: UK total trade: all countries, non-seasonally adjusted - Annual and Q1, q2
		Description: scraper.dataset.description +
		These tables have been produced to provide an aggregated quarterly goods and services estimate and combines the most recent estimates for goods and services split by country.
		Data for goods and services is consistent for annual whole world totals and quarters (from Q1 2016) with the trade data published in the Quarterly National Accounts, Quarterly Sector Accounts and Quarterly Balance of Payments on 30th September 2020.
		These data are our best estimate of these bilateral UK trade flows. Users should note that alternative estimates are available, in some cases, via the statistical agencies for bilateral countries or through central databases such as:
		UN Comtrade.
		Some data for countries have been marked with N/A. This is because Trade in Goods do not collate data from these countries, therefore only Trade in Services is reflected within total trade for these countries
		The data within these tables are also consistent with the below releases:	
		For Trade in Goods the data is consistent with UK Trade: August 2020 publication on 9th October 2020
		For Trade in Services the data is consistent with UK Trade in services by partner country: April to June 2020 publication on 4th November 2020
		Family: trade

#### Table Structure

		Period, Country, Flow, Trade Type, Value

##### Footnotes

		footnotes

##### DM Notes

		notes

