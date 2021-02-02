# COGS Dataset Specification

[Family Transform Status](https://gss-cogs.github.io/family-trade/datasets/index.html)

## HMRC alcohol-bulletin

### HM Revenue & Customs

[Landing Page](https://www.gov.uk/government/statistics/alcohol-bulletin/)

[Transform Flowchart](https://gss-cogs.github.io/family-trade/datasets/specflowcharts.html?HMRC-alcohol-bulletin/flowchart.ttl)

### Dataset One

#### Output Dataset Name:

	HMRC Alcohol Releases, Production and Clearances - NSA

#### Table Structure

		Period, Alcohol by Volume, Alcohol Type, Alcohol Origin, Production and Clearance, Measure Type, Unit, Marker, Value

#### Sheet: T1 Wine Duty (wine) statistics - Historic quantities released for consumption and revenue received

		B - Date - change to Period and format as required (Financial, Calendar and Monthly)
		E7, N7 - Statistic Type (Not needed)
			Quantities released for consumption
			Revenue
		D8, H8, G9 - Alcohol by Volume
			Not Exceeding 15%
			Over 15% ABV
			Composition by Origin above 5,5% ABV (This includes L9 as well, which is the total)
		E9:F9, H9:O9 - Alcohol Origin
			Still
			Sparkling
			Imported ex-ship
			Ex-Warehouse
			UK registered premises
			Total wine of fresh grape
			Total Wine
			Total Alcohol
		Add Alcohol Type column with value Wine
		Add Production and Clearances column with value N/A
		Add Measure Type column with value Released for Consumption
		Add Unit column with value Hectolitre and GBP Million

#### Sheet: T2 Wine Duty (made-wine) statistics - Historic quantities released for consumption and revenue

		B - Date - change to Period and format as required (Financial, Calendar and Monthly)
		E7, T7 - Statistic Type (Not needed)
			Quantities released for consumption
			Revenue
		E9, G8, K9, M9, R9 - Alcohol by Volume
			Above 1.2% but not exceeding 5.5% ABV
			Above 5.5% ABV but not exceeding 15%
			Over 15% ABV
			Composition by Origin above 5,5% ABV
			Total made wine
		G9:H9, M9:P9 - Alcohol Origin
			Still
			Sparkling
			Imported ex-ship
			Ex-Warehouse
			UK registered premises
			Total Wine
			Total Alcohol
		Add Alcohol Type column with value Made-Wine
		Add Production and Clearances column with value N/A
		Add Measure Type column with value Released for Consumption
		Add Unit column with value Hectolitre and GBP Million

#### Sheet: T3 Spirits Duty Statistics - Historic quantities released for consumption and revenue

		B - Date - change to Period and format as required (Financial, Calendar and Monthly)
		E7, T7 - Statistic Type (Not needed)
			Production and Quantities
			Revenue
		E8, G8 - Production and Clearances
			Production of Potable Spirits
			Net Quantities of Spirits Charged with Duty
		E10:P10 - Alcohol Origin
			Total
			Home Produced Whiskey Malt
			Home produced Whiskey Grain and Blended
			Home Produced Whiskey Total
			Spirits Based RTDs
			Imported and Other Spirits
			Total
			Total Sprits
			Total Alcohol
		Add Alcohol by Volume column with value All
		Add Alcohol Type column with value Spirits
		Add Measure Type column with value Released for Consumption
		Add Unit column with value Hectolitres of Pure Alcohol and GBP Million


#### Sheet: T4 Beer Duty and Cider Duty statistics - Historic clearances and revenue

		B - Date - change to Period and format as required (Financial, Calendar and Monthly)
		D7:M7 - Production and Clearances
			UK Beer Production
			Beer Clearances 
			Cider Clearances
		E9:R9 - Alcohol Origin
					Thousand Hectolitres - Total
					Thousand Hectolitres of alcohol (production) - Alcohol Production
					Uk Registered Premises
					Ex-warehouse and imports
					Total Beer Clearances
					Thousand hectolitres of alcohol (clearances) - Total
					Cider Thousand hectolitres - Total
					Total Beer
					Total Cider
					Total Alcohol
		Add Alcohol by Volume column with value All
		Add Alcohol Type column with value Beer and Cider 
		Add Measure Type column with value Clearances
		Add Unit column with value Thousand Hectolitres and GBP Million


### Dataset Two

#### Output Dataset Name:

	HMRC Alcohol Duty Rates

#### Table Structure

		Period, Alcohol Origin, Alcohol Type, Measure Type, Unit, Marker, Value

#### Sheet: R2 Historic alcohol duty rates

##### For all tables add following columns

		Measure Type with value GBP per Hectolitre of Product
		Unit GBP

##### Wine Duty (wine)

		B13:B39 - Date of Change - change to Period and format as required
		E7, J7 - Alcohol Origin
		D8:K8 - Alcohol by Volume
		Add Alcohol Type column with value Wine 
		Add Measure Type with value GBP per Hectolitre of Product
		Add Unit column with value GBP

##### Wine Duty (made-wine)

		B53:B79 - Date of Change - change to Period and format as required
		D47, G47, J47 - Alcohol Origin
		D49:K49 - Alcohol by Volume
		Add Alcohol Type column with value Made-Wine 
		Add Measure Type with value GBP per Hectolitre of Product
		Add Unit column with value GBP

##### Spirits Duty

		B94:B128 - Date of Change - change to Period and format as required
		D91, E91 - Alcohol Origin
		Add Alcohol by Volume column with value All
		Add Alcohol Type column with value Spirits 
		Add Measure Type with value GBP per Hectolitre of Product
		Add Unit column with value GBP

##### Beer Duty

		B141:B168 - Date of Change - change to Period and format as required
		D137:K138 - Alcohol Origin
		Add Alcohol by Volume column with value All
		Add Alcohol Type column with value Beer
		Add Measure Type with value GBP per 1% ABV per Hectolitre
		Add Unit column with value GBP

#### Cider Duty (Historic)

		B193:B221 - Date of Change - change to Period and format as required
		D187, G187 - Alcohol Origin
		D189:G190 - Alcohol by Volume
		Add Alcohol Type column with value Cider Historic
		Add Measure Type with value GBP per Hectolitre of Product
		Add Unit column with value GBP

#### Cider Duty (Current)

		B234:B234 - Date of Change - change to Period and format as required
		D228, I228 - Alcohol Origin
		D230:I232 - Alcohol by Volume
		Add Alcohol Type column with value Cider Current
		Add Measure Type with value GBP per Hectolitre of Product
		Add Unit column with value GBP
							
##### Footnotes

		Shed loads of Metadata in this spreadsheet. Sheets R1 and R3 hold loads of information. Not sure how this much information can de added. 

