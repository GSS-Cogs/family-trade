<!-- #region -->
# COGS Dataset Specification
----------

## UK tariffs

[Landing Page](https://www.gov.uk/guidance/uk-tariffs-from-1-january-2021)

----------

### Stage 1. Transform
#### DE Stage one notes :
    Due to having to use a temp scraper and the file format the data has been brought in as a pandas df consisiting of 9 columns of data type category. 


#### Sheet: Sheet 1
    Below is a list of the name of each column name, I assume commodity will be the observation value ?
    
    commodity                                                 
    description                                                    
    cet_duty_rate                                                  
    ukgt_duty_rate                                                 
    change                                                         
    trade_remedy_applies                                           
    cet_applies_until_trade_remedy_transition_reviews_concluded    
    suspension_applies                                             
    atq_applies                                                    


### Stage 2 - Harmonisation
    
    This is not a statisical dataset so this is a limited data to transform. it is simply meant for business to check tarffis of goods imported into the UK. 

    Upon investigation the dataset need to be split into two. based on the duty rate variables:
     cet_duty_rate                                                ukgt_duty_rate 
    both these duty rates need to be flattned so that a new dimension can be added called 'duty rate type' which will denote what the rate is e.g. cet or ukgt. 

    ##instructions for dataset1 duty rate type##
    measure type = duty rate change
    unit = % 

    ##instructions for dataset2 currency conversion##

    measure type = currency conversion 
    unit = tbc 


    #### Table construction ####
    I would suggest the table takes the following format: 
    commodity, duty rate type (new dimension), 
    change,	
    trade_remedy_applies,	
    cet_applies_until_trade_remedy_transition_reviews_concluded,
    suspension_applies,	
    atq_applies

    ######codelists########
    
   Commodity Codelist detailing the individual commodity codes

   description Codelist detailing the descriptions of each commodity

    A new codelist needs to be created for the change column cotaining the fields:
    'simpilified'
    'no change' 

    codelist duty rate type which will contain the different rate fields:
    cet_duty_rate,	
    ukgt_duty_rate

    addtional codeslists will need to be generated for 
    columns:
    trade_remedy_applies	cet_applies_until_trade_remedy_transition_reviews_concluded	suspension_applies	
    atq_applies





   


#### DM Notes
    ##title##
    'Tariffs on goods imported into the UK' 
    ##description## 
       The UK Global Tariff (UKGT) applies to all goods imported into the UK unless:

    the country you’re importing from has a trade agreement with the UK
    an exception applies, such as a relief or tariff suspension
    the goods come from developing countries covered by the Generalised Scheme of Preferences

    ##further information##

    'Importing goods covered by a tariff-rate quota'
    Some products are covered by a tariff-rate quota (TRQ).

If there’s a TRQ for your product, you can apply to import a limited amount at a zero or reduced rate of customs duty.  If this limit is exceeded, a higher tariff rate applies.

Some tariff-rate quotas are only applicable to products imported from a specified country.

Check the TRQs for specific products, including volume limits and authorised uses.


    ## How to check the tariff ##
   
    The tool shows the tariff rates that will be applied to goods at the border when they’re imported into the UK.

It does not cover:

other import duties, such as VAT
the precise details of trade remedy measures, such as anti-dumping, countervailing and safeguards.









<!-- #endregion -->

```python'

```
