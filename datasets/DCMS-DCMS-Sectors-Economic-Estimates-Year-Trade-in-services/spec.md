# COGS Dataset Specification
----------

## DCMS Sectors Economic Estimates 2018: Trade in services

[Landing Page](https://www.gov.uk/government/statistics/dcms-sectors-economic-estimates-2018-trade-in-services)

----------

### Stage 1. Transform

#### Sheet: Imports 
    Period : 2018 (Hardcoded)
    Country : Cell A5 Down 
    Sector : A3 across
    Sector Type : B4 across
    Flow : Imports (Hardcoded)
    
#### Sheet: Exports 
    Period : 2018 (Hardcoded)
    Country : Cell A5 Down 
    Sector : A3 across
    Sector Type : B4 across
    Flow : Exports (Hardcoded)

#### Table Structure

		Period, Country, Sector, Sector Type, Flow, Measure Type, Unit, Value, Marker

#### DE Stage one notes 
    Marker "-" cannot easily find exactly what this translates to therefore have made it "n/a" for now. 
    Unsure if Sector and Sub Sector are the best naming conventions for those dimensions 
    
    I have applied the following to Unit and Measure type, might not be correct. 
    
    Unit = Millions (pounds)
    Measure Type = Count 
    
    Is it still OK to use "Flow" to represent Imports and Exports Marker "-" cannot easily find exactly what this translates to therefore have made it "n/a" for now. 
    Unsure if Sector and Sub Sector are the best naming conventions for those dimensions 
    
    I have applied the following to Unit and Measure type, might not be correct. 
    
    Unit = Millions (pounds)
    Measure Type = Count 
    
    Is it still OK to use "Flow" to represent Imports and Exports together?
