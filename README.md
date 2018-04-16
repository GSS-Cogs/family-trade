# Reference Data for Trade

This repository contains reference data needed to support the publication of the International Trade dataset family.

The data is specified in tidy-format suitable for conversion as part of the [table2qb](https://github.com/swirrl/table2qb) process.

The [components.csv](/components.csv) file should be suitable to cover all of the components used across the various cubes we're creating. This may be loaded with the components pipeline.

The [codelists.csv](/codelists.csv) provides an index and notes to the various codelists in the sub-directory of the same name. This could be used to programmatically call the codelists pipeline.
