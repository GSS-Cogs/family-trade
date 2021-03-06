# COGS Dataset Specification

[Family Home](https://gss-cogs.github.io/family-trade/datasets/specmenu.html)

[Family Transform Status](https://gss-cogs.github.io/family-trade/datasets/index.html)

## ONS Quarterly country and regional GDP 

[Landing Page](https://www.ons.gov.uk/economy/grossdomesticproductgdp/datasets/quarterlycountryandregionalgdp)

### Sheets:

	Key Figures
	North East
	North West
	Yorkshire and the Humber
	East Midlands
	West Midlands
	East of England
	London
	South East
	South West
	England
	Wales
	Extra-Regio

	All sheets to be joined and split into 2 datasets
		Indices (tables 1 & 2 per sheet)
		Percentage change (tables 3, 4 & 5 per sheet)
	All sheets have the same format, 2 tables, top 1 for year and bottom one for quarters. Main dimensions are Period, Region and Industry Section.
	Regions will have to stay as they are at the moment as their is not an ONS geography code for Extra-Regio. ONS do give it the code UKZ but this is not part of the statistical geography codelist 

	Industry Section: codelist should be defined in ref_common
	Change Type: codelist should be defined within main transform folder and referenced in info.json

### INDICES

#### Sheet (All sheets)

	Period (column A)
		format year values as year/{year} - year/2019
		format quarter values as quarter/{yr}-{qtr} - quarter/2019-Q1
	Region (sheet name) (codelist & pathify)
	Industry Section: use row 6 as the value (codelist from rows 5 & 6, pathify)
	info.json:
		Measure Type: indices
		Unit: gdp

	Scraper:
		dataset_id: ons-quarterly-country-and-regional-gdp/indices
		Title: Quarterly country and regional GDP - Indices
		Comment: Quarterly economic activity within Wales and the nine English regions (North East, North West, Yorkshire and The Humber, East Midlands, West Midlands, East of England, London, South East, and South West). Indices 2016 = 100.
		Description: same as comment + 
			Regional GDP is designated as experimental statistics.
			Indices reflect values measured at basic prices, which exclude taxes less subsidies on products.
			Estimates cannot be regarded as accurate to the last digit shown.
			Any apparent inconsistencies between the index numbers and the percentage change are due to rounding.
		Family: trade

#### Table Structure

		Period, Region, Industry Section, Value

### PERCENTAGE CHANGE

#### Sheets (All sheets)

	Period (column A)
		format year values as year/{year} - year/2019
		format quarter values as quarter/{yr}-{qtr} - quarter/2019-Q1
	Region (sheet name) (codelist & pathify)
	Industry Section: use row 6 as the value (codelist from rows 5 & 6, pathify)
	Change type (codelist & pathify):
		year-on-year
		quarter-on-previous-quarter
		quarter-on-same-quarter-a-year-ago
	info.json:
		Measure Type: percentage-change
		Unit: gdp

		Scraper:
		dataset_id: ons-quarterly-country-and-regional-gdp/percentagechange
		Title: Quarterly country and regional GDP - Percentage change
		Comment: Quarterly economic activity within Wales and the nine English regions (North East, North West, Yorkshire and The Humber, East Midlands, West Midlands, East of England, London, South East, and South West). Percentage change.
		Description: same as comment + 
			Regional GDP is designated as experimental statistics.
			Indices reflect values measured at basic prices, which exclude taxes less subsidies on products.
			Estimates cannot be regarded as accurate to the last digit shown.
			Any apparent inconsistencies between the index numbers and the percentage change are due to rounding.
		Family: trade

#### Table Structure

		Period, Region, Industry Section, Change Type, Value

##### DM Notes

		Industry section should eventually reference an all encompassing SITC4 hierarchical codelist

## TODO NEW:

* Map region column to the following codes:
  * http://statistics.data.gov.uk/id/statistical-geography/E92000001 - England
  * http://data.europa.eu/nuts/code/UKF - EAST MIDLANDS (ENGLAND)
  * http://data.europa.eu/nuts/code/UKG - WEST MIDLANDS (ENGLAND)
  * http://data.europa.eu/nuts/code/UKE - YORKSHIRE AND THE HUMBER
  * http://data.europa.eu/nuts/code/UKC - NORTH EAST (ENGLAND)
  * http://data.europa.eu/nuts/code/UKD - NORTH WEST (ENGLAND)
  * http://data.europa.eu/nuts/code/UKZ - EXTRA-REGIO NUTS 1
  * http://data.europa.eu/nuts/code/UKK - SOUTH WEST (ENGLAND)
  * http://data.europa.eu/nuts/code/UKL - WALES
  * http://data.europa.eu/nuts/code/UKJ - SOUTH EAST (ENGLAND)
  * http://data.europa.eu/nuts/code/UKH - EAST OF ENGLAND
  * http://data.europa.eu/nuts/code/UKI - LONDON
* Delete `Unit` column.
* Rename `Measure Type` column to `Unit`.
  * Rename all `percentage-change` values to `percentage`.
  * Leave `indices` as they are.
* Rename `Change Type` column to `Measure Type`. The following measures should be in place:   
  * Rename all `not-applicable` values to `gdp-from-gva`
  * Rename all `quarter-on-previous-quarter` values to `q-on-q-delta-gdp-from-gva`
  * Rename all `quarter-on-same-quarter-a-year-ago` values to `q-on-last-year-q-delta-gdp-from-gva`
  * Rename all `year-on-year` values to `y-on-y-delta-gdp-from-gva`
