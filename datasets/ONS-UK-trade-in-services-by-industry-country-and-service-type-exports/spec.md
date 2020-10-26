# COGS Dataset Specification
----------

## UK trade in services by industry, country and service type, exports

[Landing Page](https://www.ons.gov.uk/economy/nationalaccounts/balanceofpayments/datasets/uktradeinservicesbyindustrycountryandservicetypeexports)

----------

### Stage 1. Transform

#### Sheet: Sheet1 
    Period : cell E1 across
    Country : Cell A2 Down 
    Industry : Cell B2 Down
    Direction : Cell C2 Down
    Service Account : Cell D2 down
    
    Marker '..' = 'suppressed data'
   

#### Table Structure

		Period, Country, Industry, Direction, Service Account, Value, Marker

#### DE Stage one notes 
    
   NB: Imports data also avilable, it looks like we could pop them in a single cube with the addition of a flow dimension. https://www.ons.gov.uk/economy/nationalaccounts/balanceofpayments/articles/uktradeinservicesbyindustrycountryandservicetype/2016to2018/relateddata
    
    Unit = £ million
    Measure Type = Count 


```python

```
