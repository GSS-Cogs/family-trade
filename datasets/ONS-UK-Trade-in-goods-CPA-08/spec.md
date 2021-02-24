# Transformations

* Remove `International Trade Basis` column.
* Rename `Flow Directions` to `Flow Direction`.
* Remove `Price Classification` column. This information should go into the dataset description/comments.
* Remove `Seasonal Adjustment` column.
* `Product`
  * Scrap all of the mad logic that currently exists - most important `all` should not exist.
  * For all of the `Product`s down the side. Your new value is given by: `item.split(" ", 1)[0]`
    * i.e. `Total`, `A`, `01`, `01.1`, etc. all the way down to `Residual`.
    

