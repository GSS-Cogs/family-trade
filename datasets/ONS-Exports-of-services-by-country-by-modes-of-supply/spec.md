<!-- #region -->
# COGS Dataset Specification
----------

## Exports of services by country, by modes of supply (exports)

[Landing Page](https://www.ons.gov.uk/businessindustryandtrade/internationaltrade/datasets/exportsofservicesbycountrybymodesofsupply)

----------

### Stage 1. Transform

#### Sheet: Sheet1 
    Period : 2018 (Hardcoded, can be taken from cell "E1")
    Country : Cell A2 Down 
    Mode : Cell B2 Down
    Direction : Cell C2 Down
    Service Account : Cell D2 down
   

#### Table Structure

		Period, Country, Mode, Direction, Service Account, Value

#### DE Stage one notes 
easy one sheet dataset representing Exports. Data representing Imports can be found [here](https://www.ons.gov.uk/businessindustryandtrade/internationaltrade/articles/modesofsupplyukexperimentalestimates/2018/relateddata) and could easily be joined together with a "FLOW" dimension. Naming of dataset would need to be altered to reflect. 

Modes will need to be defined, mode information can be found [here](https://www.ons.gov.uk/businessindustryandtrade/internationaltrade/articles/modesofsupplyukexperimentalestimates/2018)
    
    Unit = ?? 
    Measure Type = Count 

<!-- #endregion -->

```python

```
