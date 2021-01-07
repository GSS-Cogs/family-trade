
<!-- #region -->
# COGS Dataset Specification

# ONS UK trade in services by business characteristics
[Landing Page](https://www.ons.gov.uk/businessindustryandtrade/internationaltrade/datasets/uktradeingoodsbybusinesscharacteristics)

### Stage 1. Transform

#### Sheet: Sheet1

Transform notes

#### Table Structure

		Columns go here

#### DE Stage one notes
Notes go here.

### Stage 2 - Harmonisation

Exports (£) and Imports (£) should be combined into a dimension and the values should go in the \'91Value\'92 column.\

I think these six data tabs can be combined into a single cube: 2016, 2016 Industry Totals, 2017, 2017 Industry Totals, 2018, 2018 Industry Totals.

A possible dataset structure would be:
Business size // Ownership // Industry // Flow // Data Marking // Value

The Industry Totals tabs have Ownership and Industry breakdowns and should have Total for Business size.
The year totals have Ownership and Business size breakdowns and should have Total for Industry.


#### DM Notes

Nothing here yet.
<!-- #endregion -->}
