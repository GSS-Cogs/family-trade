# ONS International Trade in Services by Subnational Areas of the UK

Very important related document with appendicies: <https://www.ons.gov.uk/businessindustryandtrade/internationaltrade/articles/internationaltradeinservicesbysubnationalareasoftheuk/latest>

## Footnotes

> An error has been found in the EU and Rest of the World estimates within the International trade in services by subnational areas of the UK: 2018 dataset. Please be aware of this if using this data. We are investigating the reason for this error and will update this notice as we have more information. We apologise for any inconvenience. Please contact Isabel Rogers for more information.

* Add one to represent '..'
  * `The symbol ".." denotes values that have been suppressed for reasons of confidentiality or reliability.`

## Directions for Data Engineer

* Remove all sheets except for `9. Tidy Data` and `8. Travel`.

### Travel Worksheet

* Add `Marker` column and set to `suppressed` if the value cell is `..`.
* Remove the `Measure Type` and `Unit` column and the untitled row number column (first one).
* Add new column `Location` with `http://data.europa.eu/nuts/code/{NUTS Code}`.
  * You will need to map the `NUTS1 Area` to the *NUTS Code*. Watch out because `NorthWest` is a typo, it should be `North West`.
  * Now you can remove the `NUTS1 Area` column.
* Map `Travel Type` values to local codelist identifiers [`total`, `personal`, `business`].
* Add `Includes Travel` column and set to `includes-travel`.
* Map `Origin` values to local code list identifiers.
* Add `Industry Grouping` column and set to `travel-related-trade`.
* Add `Flow` column and set to `imports`.
* Rename `Year` column to `Period`.

### Tidy Format Worksheet

* Add `Marker` column and set to `suppressed` if the value cell is `..`.
* Remove the `Measure Type` and `Unit` column and the untitled row number column (first one).
* Add `Travel Type` column.
  * If the `NUTS Level` is `NUTS1` *AND* the `Industry Grouping` is `Travel` - then the value of `Travel Type` should be `total`.
  * Else the value of `Travel Type` should be `na`.
* Add a column called `Includes Travel` column.
  * If the `NUTS Level` is `NUTS1` then the value of `Includes Travel` is `includes-travel`.
  * Otherwise set the value of `Travel` to `excludes-travel`.
* Remove `NUTS Level` column.
* Add new column `Location`.
  * Where a row has a valid `NUTS Code` value (i.e. not `N/A`), then populate `Location` with `http://data.europa.eu/nuts/code/{NUTS Code}` - making sure to replace the NUTS code with the value from the appropriate column.
  * Where a row does *not* have a valid `NUTS Code`, and the `NUTS Area Name` column is `United Kingdom` then populate the `Location` with `http://data.europa.eu/nuts/code/UK`.
  * Else the row represents a City. Populate `Location` with appropirate E47 combined authorities or W42 City Region geography URI, e.g. `http://statistics.data.gov.uk/id/statistical-geography/E47000008`. N.B. you must ensure the WHOLE URI is present in the cell.
    * Anything with 'combined authority' in the name should be E47 (you may need to remove 'combined authority' to do the name matching)
    * Most others should be W42. N.B. Some with 'city region' in them are actually combined authorities.
    * Greater London Authority - `http://statistics.data.gov.uk/id/statistical-geography/E61000001`
    * Inner/Outer London are E13 codes.
    * `Sheffield City Region, Inner London, Outer London and the Greater London Authority are not legally classified as Combined Authorities. However, they have been included as they are defined geographic boundaries headed by a Mayor for the purposes of this analysis.`
* Now remove the `NUTS Code`, `NUTS Area Name` and `NUTS Area Name` columns.
* Map `Industry Grouping` to local codelist.
* Rename `Country or Origin of Trade` to `Origin` to local codelist.
* Rename `Direction of Trade` to `Flow` and map to the `Flow` codelist [`imports`, `exports`, `balance`].
* Rename `Year` column to `Period`.

## Joins

Join the Travel & Tidy Format outputs together.
