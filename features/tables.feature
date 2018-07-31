Feature: Preserve table information

  As a QA tester, I would like to check that the resulting information
  in PMD corresponds to the information in the original spreadsheet.

  Scenario: Check a table
    Given the "ONS ABS" dataset is published in PMD
    When I lock dimension "age-of-business" to "age-of-business/any"
    And I lock dimension "employment" to "employment-size-bands/any"
    And I lock dimension "product" to "ons-abs-trades/goods-and-services"
    And I lock dimension "turnover" to "turnover-size-bands/any"
    And I lock the measure type to "count"
    And I lock the reference period to "year/2016"
    And download the resulting table
    Then the table should look like
      | Ownership | Businesses | Exporters | Importers | Exporter and Importer | Exporter and/or Importer |
      | UK        | 2,331,800  | 193,600   | 200,700   | 105,700               | 288,600                  |
      | Foreign   | 27,300	   | 13,200    | 13,300    | 9,900                 | 16,700                   |
