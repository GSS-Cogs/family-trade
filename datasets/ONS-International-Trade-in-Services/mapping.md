# Adding a mapping

Look at the existing Tidy CSV file, either by running the transform locally or looking on Jenkins. The
[output files from the recent build are collected together](https://ci.floop.org.uk/job/GSS_data/job/Trade/job/ONS-International-Trade-in-Services/107/)
and provide a [page for the Tidy CSV file](https://ci.floop.org.uk/job/GSS_data/job/Trade/job/ONS-International-Trade-in-Services/107/artifact/datasets/ONS-International-Trade-in-Services/out/international-trade-in-services.csv/*view*/).

The table looks like:

| Marker | Flow Directions | ITIS Industry | ITIS Service | International Trade Basis | Measure Type | ONS Trade Areas ITIS | Unit | Value | Year |
| ------ | --------------- | ------------- | ------------ | ------------------------- | ------------ | -------------------- | ---- | ----- | ---- |
| | exports | all | total-international-trade-in-services-excluding-travel-transport-and-banking | BOP | GBP Total | itis/austria | gbp-million | 365.0 | 2013 |
| ... |

The headers are the things we need to add mappings for in the `info.json` file. Previously, this was done using a family-wide
mapping declared in [`columns.csv`](https://github.com/GSS-Cogs/family-trade/blob/master/reference/columns.csv).

A mapping is used to declare how we want the CSV file to be turned into RDF triples. Remember that for Tidy data, each
row is an observation and most of the columns represent a dimension or attribute. As a graph, the structure
looks like:

![Observation graph](obs-graph.svg)

In RDF, everything is represented using URIs, so the mapping is used to turn the CSV column headings into the URIs used
for each dimension, and the values under those headings into the URIs used for the eventual codes.

We need to edit the `info.json` file and add a `columns` object to the `transform` section:

```json
{
    "title": "International trade in services",
    ...
    "transform": {
        ...
        "main_issue": 4,
        "columns": {
        }
    }
    ...
```

If you're using a JSON editor or IDE such as IntelliJ, you should be able to associate [dataset JSON Schema](https://gss-cogs.github.io/family-schemas/dataset-schema.json)
with this file in order to provide some hints about the structure, validation and autocomplete. In IntelliJ, click
on the toolbar at the bottom right where it says "JSON" and then on "Edit Schema Mappings". The schema URL to use
is https://gss-cogs.github.io/family-schemas/dataset-schema.json.

Each column header in the source Tidy CSV file needs a declaration in the `info.json` file. We'll start with *Marker*:

## Marker

This column represents the "data marker" and is used to annotate the status of the observation. It is an attribute, 
rather than a dimension, and we can declare it as follows:

```json
{
    ...
    "columns": {
        "Marker": {
            "attribute": "http://purl.org/linked-data/sdmx/2009/attribute#obsStatus",
            "value": "http://gss-data.org.uk/def/concept/marker/{marker}"
        },
```

Here, the `"Marker"` column is declared as an attribute, using one of the core [SDMX "content oriented guidelines"
vocabularies](https://www.w3.org/TR/vocab-data-cube/#dsd-cog), there's an attribute [Observation Status](http://purl.org/linked-data/sdmx/2009/attribute#obsStatus)
for recording "Information on the quality of a value or an unusual or missing value".

We've previously set up a [codelist](https://github.com/GSS-Cogs/ref_common/blob/pmd4/codelists/markers.csv)
to denote the values that this attribute can take. It's taken from a [GSS policy document on harmonising the
use of symbols in tables](https://gss.civilservice.gov.uk/wp-content/uploads/2018/03/GSS-Website-Harmonised-Symbols-Supporting-Documentation_Feb-2018-7.pdf).

The URIs used for the values for these markers are given by `http://gss-data.org.uk/def/concept/marker/{marker}`,
e.g. if an observation is marked as "not-applicable", the URI would end up being `http://gss-data.org.uk/def/concept/marker/not-applicable`.

## Flow Directions

This column represents whether the trade is an import or export.
