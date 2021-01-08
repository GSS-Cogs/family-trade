
<!-- #region -->
# COGS Dataset Specification

# ONS UK trade in services by business characteristics
[Landing Page](https://www.ons.gov.uk/businessindustryandtrade/internationaltrade/datasets/uktradeingoodsbybusinesscharacteristics)

### Stage 1. Transform

#### Sheet: Sheet1

Transform notes

#### Table Structure (proposed by DM)

		Period // Business size // Ownership // Industry // Flow // // Value // Marker

#### DE Stage one notes
Notes go here.

### Stage 2 - Harmonisation

I think these six data tabs can be combined into a single cube: 2016, 2016 Industry Totals, 2017, 2017 Industry Totals, 2018, 2018 Industry Totals.
Exports (£) and Imports (£) should be combined into a 'Flow' dimension and the values should go in the 'Value' column.

A possible dataset structure would be:
Period // Business size // Ownership // Industry // Flow // // Value // Marker

The year tabs (2016, 2017 and 2018 at present) have one structure and the Industry Totals tabs another.

The year tabs have three summary tables on top of each other. Each is missing a dimension.
The first needs a 'Country' dimension with 'World' (i.e. all).
The second needs a 'Business size' dimension with 'any'.
The third needs an 'Ownership' dimension with 'All'.

The Industry totals tabs have two tables alongside each other.
The left one needs a 'Business size' dimension with 'All'.
The right one needs an 'Ownership' dimension with 'All'.

This way all the data have the same dimensions and can be combined 

The Industry Totals tabs have Ownership and Industry breakdowns and should have All for Business size.
The year totals have Ownership and Business size breakdowns and should have All for Industry.

Codelists:

Period: 

Business size: Change notation to '1-to-49', '11-to-249', '250-and-over', unknown-employees (also 'any' to represent total). Use codelist family-trade/reference/codelists/employment-size-bands

Ownership: Need to update family-trade/reference/codelists/countries-of-ownership.csv code list

Industry: 

Flow: add 'exports' and 'imports' as per instructions above and use codelist family-trade/reference/codelists/flow-directions

Value:

Marker: Change '..' to 'suppressed' and use codelist ref_common/markers

#### DM Notes

Nothing here yet.
<!-- #endregion -->}
