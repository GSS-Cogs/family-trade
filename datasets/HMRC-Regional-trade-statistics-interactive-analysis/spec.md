# COGS Dataset Specification

[Family Home](https://gss-cogs.github.io/family-trade/datasets/specmenu.html)

[Family Transform Status](https://gss-cogs.github.io/family-trade/datasets/index.html)

## HMRC Regional trade statistics interactive analysis 

[Landing Page](https://www.gov.uk/government/statistical-data-sets/regional-trade-statistics-interactive-analysis-second-quarter-2020)

#### Sheets

	This assumes that the outputs from stage one relate to the following titles on the landing page

		data0 -> Q2 2020: Exports using proportional business count method
		data1 -> Q2 2020: Exports using whole number method
		data2 -> Q2 2020: Imports using proportional business count method
		data3 -> Q2 2020: Imports using whole number method

	With 4 sheets in each file
		Database (YR) -> column names are in row 0
		Database (QR) -> column names are in row 0
		Database (Regional Year)
		Database (Regional Qtr)

#### Output: data0 & data1

	Remove Code column as this detail is given in the other columns
	Rename Number Exporters column to Value
	Rename Year column to Period and format based on period type:
		Year -> year/{yr}
		Quarter -> quarter/{yr-qtr}
	Remove Quarter column

	Add Flow column with value export

	Measures
		Sheets: Database (YR) & Database (QR)
			Measure Type: exporters
			Unit: proportional count
		Sheets: Dataset (Regional Year) & Database (Regional Qtr)
			Measure Type: Metric columns becomes the Measure Type, change as follows:
				Average value per exporter (£ thousands) -> average-value-per-exporter
				Number of Exporters -> exporters
				Value of exports (£ billions) -> value-of-exports
			Unit: depending on the measure Type: gbp thousands, count, gbp billions

	Set Marker column to suppressed if Value = S and set Value column to 0

#### Sheet: data2 & data3

	Remove Code column as this detail is given in the other columns
	Rename Change to ONS Geography codes
	Rename Number Importers column to Value
	Rename Year column to Period and format based on period type:
		Year -> year/{yr}
		Quarter -> quarter/{yr-qtr}
	Remove Quarter column

	Add Flow column with value import

	Measures
		Sheets: Database (YR) & Database (QR)
			Measure Type: importers
			Unit: proportional count
		Sheets: Dataset (Regional Year) & Database (Regional Qtr)
			Measure Type: Metric columns becomes the Measure Type, change as follows:
				Average value per importer (£ thousands) -> average-value-per-importer
				Number of Importers -> number-of-importers
				Value of imports (£ billions) -> value-of-imports
			Unit: depending on the measure Type: gbp thousands, count, gbp billions
			
	Set Marker column to suppressed if Value = S and set Value column to 0
		
#### Table Structure

	Period, Region, Country, Flow, Measure Type, Unit, Marker, Value

#### Join

	This depends if we can do multi-measure cubes or not!!!!!
	If we can then join all datasets up into one cube and set meta-data as stated

	If not then create 2 datasets one for the business count method and one for the whole number count method:
	Dataset 1:
		data0 -> Q2 2020: Exports using proportional business count method
		data2 -> Q2 2020: Imports using proportional business count method

		Title: Regional trade statistics interactive analysis - importers, exporters - proportional business count method
		Comment:
		Description:
	Dataset 2
		data1 -> Q2 2020: Exports using whole number method
		data3 -> Q2 2020: Imports using whole number method

		Title: Regional trade statistics interactive analysis - importers, exporters - whole number count method
		Comment:
		Description:	
		
##### DM Notes

	Have created local codelists as their are some extra bits in the Region and Country columns (Stores and Provisions, Unallocated known). Have to start deciding how we are going to take care of this as the Country codelist would probably match up with the ONS Country codes and the Region codelist could have ONS Geography codes assigned. 
	Might get rid of the Flow column and maybe alter some of the Measure Type wording, will have a look when the data gets onto PMD4 as a draft
	Make sure to test for duplicate data
	Will sort the comments and description when we know how many output datasets we are going to have

