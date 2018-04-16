# Reference Data for Trade

This repository contains reference data needed to support the publication of the International Trade dataset family.

The data is specified in tidy-format suitable for conversion as part of the [table2qb](https://github.com/swirrl/table2qb) process.

The [components.csv](/components.csv) file should be suitable to cover all of the components used across the various cubes we're creating. This may be loaded with the components pipeline.

The [codelists.csv](/codelists.csv) provides an index and notes to the various codelists in the sub-directory of the same name. This could be used to programmatically call the codelists pipeline.

It may also be instructive to look at the [columns.csv](https://github.com/Swirrl/table2qb/blob/master/resources/columns.csv) configuration for table2qb which specifies how data uploaded to the cube pipeline will be treated. The columns are identified according the `title` field and then the component is found in the corresponding  `property_template` and codes transformed with the `value_template`.
