# ONS International Trade in Services by Subnational Areas of the UK

Initial Notes:

* The only key relevant sheets are
  * `9. Tidy Format` - Contains (almost) all the information in the other sheets in a tidy format.
  * `8. Travel` - has a breakdown by Personal/Business travel purposes
  * `5. NUTS3, destination` - has `Percentage to/from the EU` column. But this can be derived from the existing data.

## It's all NUTS

WATCH OUT FOR includes/excludes travel sheets!

* NUTS1 code => Includes travel
* Anything else => Excludes travel

## Footnotes

> An error has been found in the EU and Rest of the World estimates within the International trade in services by subnational areas of the UK: 2018 dataset. Please be aware of this if using this data. We are investigating the reason for this error and will update this notice as we have more information. We apologise for any inconvenience. Please contact Isabel Rogers for more information.

## Measures

* Imports
* Exports
* Balance
* EU Percentage (?)

## Units

* GBP Millions

## Dimensions

* Location
* NUTS Code
  * NUTS Codes available in RDF form here - http://nuts.geovocab.org/id/SE1.html
* NUTS Level - TODO: remove
* Industry Grouping - TODO: codelist
* Country or origin of trade - TODO: codelist
* Direction of Trade - TODO: codelist
* Including Travel or Not (secret dimension) - TODO: codelist
  * NUTS1 always includes travel, others always exclude travel
* Personal or Business Travel -- TODO: codelist

## Attributes

* Add one to represent '..'
  * `The symbol ".." denotes values that have been suppressed for reasons of confidentiality or reliability.`

## Directions for DE

* Remove all sheets except for `9. Tidy Data` and `8. Travel`.

### Travel Worksheet

* Add `Marker` column and set to `` if the value cell is `..`.
* Remove the `Measure Type` and `Unit` column and the untitled row number column (first one).
* Ensure the `Value` column values are all integers, not decimals/floats/doubles/etc.
* Add `NUTS Code` column and populate with NUTS code mapped from `NUTS1 Area` text value. Watch out because `NorthWest` is a typo, it should be `North West`.
  * Now you can remove the `NUTS1 Area` column.
* Map `Travel Type` values to local codelist identifiers.
* Map `Origin` values to local code list identifiers.
* Rename `Year` column to `Period`.

TODO: Should be in seperate datasets?

<!-- To be joined with the `Imports` data split out from the `9. Tidy Format` sheet. -->

### Tidy Format Worksheet

* Add `Marker` column and set to `` if the value cell is `..`.
* Remove the `Measure Type` and `Unit` column and the untitled row number column (first one).
* Add a column called `Travel` column.
  * If the `NUTS Level` is `NUTS1` then the value of `Travel` is the `Travel Included` mapped to the code-list identifier.
  * Otherwise set the value of `Travel` to `Travel Not Included` mapped to the code-list identifier.
* Remove `NUTS Level` column.
* Add new column `Location`.
  * Where a row has a valid `NUTS Code` value (i.e. not `N/A`), then populate `Location` with `http://data.europa.eu/nuts/code/{NUTS Code}` - making sure to replace the NUTS code with the value from the appropriate column.
  * Where a row does *not* have a valid `NUTS Code`, and the `NUTS Area Name` column is `United Kingdom` then populate the `Location` with `http://data.europa.eu/nuts/code/UK`.
  * Else the row represents a City. Populate `Location` with appropirate E47 combined authorities geography URI, e.g. `http://statistics.data.gov.uk/id/statistical-geography/E47000008`. N.B. you must ensure the WHOLE URI is present in the cell.
* Now remove the `NUTS Code`, `NUTS Area Name` and `NUTS Area Name` columns.
* Ensure that `Value` is an integer.
* Map `Industry Grouping`, `Country or Origin of Trade` and `Direction of Trade` to local codelists.
* Rename `Year` column to `Period`.
* Split the dataset on the `Direction of Trade`, i.e. one dataset for `Imports`, another for `Exports` and another for `Balance`.
* Remove the `Direction of Trade` column from the individual datasets.
