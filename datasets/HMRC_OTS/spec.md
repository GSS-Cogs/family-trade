HMRC OTS data spec for initial conversion 

following the process of the RTS data flow i believe everything can be dropped bar the following:

FLowType differantes between EU and Non EU imports/Exports
OTS is the statistical list of all oversees trade
OTS Commodity - is a more indepth breakdown of commodities afor oversees trade compared with the SITC used for RTS.
Port - would need to be included idenitfy OTS countries point of origin 
Country - required to indentify OTS countries
SITC - required to idenitfy OTS and provide a more broader commodity code to aggregrate up to.
Creation of unit field to denote the numeric column alinged to 

statistical value is gbp thousands 
if the DE could return a list of the OTS commodity list as this would be handy to create a codelist for future use

create OTS codelist is more detailed that the SITC codelist used for RTS and is slightly different to the commodoity codelist used by ONS datasets

link to metadata so users can understand how these data are classifed https://www.uktradeinfo.com/trade-data/help-with-using-our-data/ 


# Rob stuff

Contact Point: <mailto:uktradeinfo@hmrc.gov.uk>

> Port data is only available for UK trade with non-EU countries. <https://www.uktradeinfo.com/trade-data/help-with-using-our-data/>

## Helpful Links

* <https://www.uktradeinfo.com/trade-data/help-with-using-our-data/>

## DE Actions

* Remove all columns EXCEPT the following:
  * `FlowTypeId`
  * `SuppressionIndex`
  * `CountryId`
  * `Value`
  * `NetMass`
  * `Cn8Code`
  * `PortCodeNumeric`
  * `Period`
* Map the `FlowTypeId` in the following fashion (<https://api.uktradeinfo.com/TradeType>)
  * `1` => `imports`
  * `2` => `exports`
* Add a `Measure Type` and `Unit Type` column. 
* Pivot the data so that every row now has two rows - one for each of these measures. (observed values for the measure go into the column called `Value`)
  * One row for the `Value` field which should have `Measure Type = monetary-value` and `Unit Type = http://gss-data.org.uk/def/concept/measurement-units/gbp` the value should end up in a column named `Value`
  * One row for the `NetMass` field which should have `Measure Type = net-mass` and `Unit Type = http://qudt.org/vocab/unit/KiloGM` the value should end up in a column named `Value`
  * Ensure the `NetMass` column doesn't exist anymore.
* Map the `SuppressionIndex` column in the following fashion: (<https://www.uktradeinfo.com/media/ie2p3tcj/current_suppressions.pdf>)
  * `1` => `complete-suppression`
  * `2` => `suppression-of-country-and-port`
  * `3` => `suppression-of-country-port-and-total-trade-quantity`