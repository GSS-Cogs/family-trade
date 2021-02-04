# COGS Dataset Specification

[Family Transform Status](https://gss-cogs.github.io/family-trade/datasets/index.html)

## HMRC alcohol-bulletin

### HM Revenue & Customs

[Landing Page](https://www.gov.uk/government/statistics/alcohol-bulletin/)

### Sheets: Wine_statistics & Made_wine_statistics

	Rename date column as "Period" and format as:
		Data by financial year (A) - format to financial year (forgot what the format is!)
		Data by calendar year (A) - format as year/{yr}
		Data by month (A) - format as month/{yr}-{mth} (remove provisional in last few rows and put in Marker column)

	"Bulletin Type" (row 6, columns B to J) (codelist/pathify) - remove (hectolitres), (£ millions) as this will be the unit. N/As change to 0 and put not-applicable in Marker column
	Add column "Alcohol Type" 
		Value "wine" for Wine sheet 
		Value: All for column J (same on all sheets so only pull in one)
		Value "made-wine" for Made wine sheet (ignore column J as same as all other sheets)

	Measures:
		Measure Type: clearances (cols B to H), duty-receipts (cols I)
		Unit: hectolitres (cols B to H), gbp-million (cols I and J)

	Table Structure:
		Period, Bulletin Type, Alcohol Type, Marker, Value

	Columns J and K are the same for both sheets so check for duplicates

### Sheet: Spirits_statistics

	Rename date column as "Period" and format as:
		Data by financial year (A) - format to financial year (forgot what the format is!)
		Data by calendar year (A) - format as year/{yr}
		Data by month (A) - format as month/{yr}-{mth} (remove provisional in last few rows and put in Marker column)

	"Bulletin Type" (row 6, columns B to J) (codelist/pathify) - remove (hectolitres of alcohol), (£ millions) as these will be the units. N/As change to 0 and put not-applicable in Marker column
	Add column "Alcohol Type" 
		Value "spirits" (ignore J column)

	Measures:
		Measure Type: production (col B) clearances (cols C to H), duty-receipts (cols I)
		Unit: hectolitres-of-alcohol (cols, B to H), gbp-million (cols I)

	Table Structure:
		Period, Bulletin Type, Alcohol Type, Marker, Value


### Sheet: Beer_and_Cider_statistics

	Rename date column as "Period" and format as:
		Data by financial year (A) - format to financial year (forgot what the format is!)
		Data by calendar year (A) - format as year/{yr}
		Data by month (A) - format as month/{yr}-{mth} (remove provisional in last few rows and put in Marker column)

	"Bulletin Type" (row 6, columns B to J) (codelist/pathify) - remove (hectolitres of alcohol), (£ millions) as these will be the units. N/As change to 0 and put not-applicable in Marker column
	Add column "Alcohol Type" 
		Value "beer-and-cider" (ignore K column)

	Measures:
		Measure Type: production (col B and C) clearances (cols D to H), duty-receipts (cols I)
		Unit: hectolitres (col B, D, E, F, H) hectolitres-of-alcohol (cols C, G), gbp-million (cols I and J)

	Table Structure:
		Period, Bulletin Type, Alcohol Type, Marker, Value
	

### SCRAPER
	Family: trade
	Title: Alcohol Bulletin
	Comment: Monthly statistics from the 4 different alcohol duty regimes administered by HM Revenue and Customs.
	Description:
	ALL METADATA FROM EACH SHEET NEEDS TO BE PULLED TOGETHER AND REWRITTEN.
	I WILL DO THIS SOON

### THIS IS A MULTI MEASURE CUBE
						
##### Footnotes

	Made-wine is any other drink that has alcohol made by fermentation apart from cider, not by distillation or any other process. For example, mead is a made-wine. Beer may be classed as made-wine if it's mixed with other products and has an ABV greater than 5.5%. In this guide, 'wine' refers to both wine and made-wine.

