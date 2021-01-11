
<!-- #region -->
# COGS Dataset Specification

# ONS UK trade in services by business characteristics
[Landing Page](https://www.ons.gov.uk/businessindustryandtrade/internationaltrade/datasets/uktradeingoodsbybusinesscharacteristics)

### Stage 1. Transform

#### Sheet: Sheet1

Transform notes

#### Table Structure (proposed by DM)

		Period // Business size // Country // Ownership // Industry // Flow // Measure type // Unit of Measure // Value // Marker

#### DE Stage one notes
Notes go here.

### Stage 2 - Harmonisation

I think these six data tabs can be combined into a single cube: 2016, 2016 Industry Totals, 2017, 2017 Industry Totals, 2018, 2018 Industry Totals.
Exports (£) and Imports (£) should be combined into a 'Flow' dimension and the values should go in the 'Value' column.

The year tabs (2016, 2017 and 2018 at present) have one structure and the Industry Totals tabs another.

The year tabs have three summary tables on top of each other. Each is missing a dimension.
The first down needs a 'Country' dimension with 'world'.
The second down needs a 'Business size' dimension with 'any'.
The third needs an 'Ownership' dimension with 'any'.

The Industry totals tabs have two tables alongside each other.
The left one needs a 'Business size' dimension with 'All' and a 'Country' dimension with 'world'.
The right one needs an 'Ownership' dimension with 'any' and a 'Country' dimension with 'world'.

This way all the data have the same dimensions and can be combined 

The Industry Totals tabs have Ownership and Industry breakdowns and should have All for Business size.
The year totals have Ownership and Business size breakdowns and should have All for Industry.

The Measure type dimension is 'Current Prices' and Unit of measure is 'gbp-million'.

### Codelists:

#### Period:

#### Business size:
Change notation to '1-to-49', '11-to-249', '250-and-over', unknown-employees (also 'any' to represent total). Use codelist family-trade/reference/codelists/employment-size-bands

#### Country:
Change 'World' to 'WW', 'Total EU28' to 'EU' and 'Non-EU' to 'RW'. Use family-trade/reference/codelists/eu-rw-ww

#### Ownership:
Change 'Domestic' to 'uk' and 'All' to 'any'. Use family-trade/reference/codelists/countries-of-ownership

#### Industry: 

#### Flow: 
add 'exports' and 'imports' as per instructions above and use codelist family-trade/reference/codelists/flow-directions

#### Measure type:
change 'Current prices' to 'CP'. Use code list: family-trade/reference/codelists/price-classifications

#### Unit of Measure:

#### Value:

#### Marker: 
Change '..' to 'suppressed' and use codelist ref_common/markers

### Scraper:

Dataset-title: uktradeingoodsbybusinesscharacteristics
Title: UK trade in goods by business characteristics
Comment: Trade in goods data, including breakdown of imports and exports by Standard Industrial Classification, region (EU and non-EU), business size and by domestic and foreign ownership.
Description: Trade in goods data, including breakdown of imports and exports by Standard Industrial Classification, region (EU and non-EU), business size and by domestic and foreign ownership.

Users should note the following:
Industry data has been produced using Standard Industrial Classification 2007 (SIC07).

Business size is defined using the following employment size bands:
   Small - 0-49 employees
   Medium - 50-249 employees
   Large - 250+ employees
   Unknown - number of employees cannot be determined via IDBR

Ownership status is defined as:
   Domestic - ultimate controlling parent company located in the UK
   Foreign - ultimate controlling parent company located outside the UK
   Unknown - location of ultimate controlling parent company cannot be determined via IDBR

Some data cells have been suppressed to protect confidentiality so that individual traders cannot be identified.

Data
All data is in £ million, current prices

Rounding
Some of the totals within this release (e.g. EU, Non EU and world total) may not exactly match data published via other trade releases due to small rounding differences.

Trade Asymmetries 
These data are our best estimate of these bilateral UK trade flows. Users should note that alternative estimates are available, in some cases, via the statistical agencies for bilateral countries or through central databases such as UN Comtrade

#### DM Notes

Nothing here yet.
<!-- #endregion -->}
