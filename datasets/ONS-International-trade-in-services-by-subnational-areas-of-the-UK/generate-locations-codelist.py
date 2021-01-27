"""
Must be run after main.py has been run so that `./out/observations.csv` exists.
"""

import pandas as pd
from typing import List, Tuple, Iterable
import re


def split_namespace_and_notation(locations: Iterable[str]) -> Iterable[Tuple[str, str]]:
    re_pattern = re.compile("^(.*/)(.*)$")
    for location in locations:
        matches = re_pattern.match(location)
        namespace = matches.group(1)
        notation = matches.group(2)
        yield namespace, notation


def do_da_split():
    group_concept_base_uri = "http://gss-data.org.uk/data/gss_data/trade/international-trade-in-services-by" \
                             "-subnational-areas-of-the-uk#concept-scheme/location"
    nuts_group_notation = "nuts"
    stat_geog_group_notation = "statistical-geographies"
    nuts_group_uri = f"{group_concept_base_uri}/{nuts_group_notation}"
    stat_geog_group_uri = f"{group_concept_base_uri}/{stat_geog_group_notation}"

    group_codelist_values = pd.DataFrame({
        "URI": [nuts_group_uri, stat_geog_group_uri],
        "Notation": [nuts_group_notation, stat_geog_group_notation],
        "Label": ["NUTS", "UK Government Statistical Geographies"],
        "Parent URI": [None, None]
    })

    observations = pd.read_csv("./out/observations.csv")
    unique_locations = observations.Location.unique()

    namespace_and_notations = list(split_namespace_and_notation(unique_locations))
    notations = [notation for namespace, notation in namespace_and_notations]

    parent_uri = [
        nuts_group_uri if namespace == "http://data.europa.eu/nuts/code/" else stat_geog_group_uri
        for namespace, _ in namespace_and_notations
    ]

    codelist = pd.DataFrame({
        "URI": unique_locations,
        "Notation": notations,
        "Label": [None for x in namespace_and_notations],
        "Parent URI": parent_uri
    })

    codelist = pd.concat([group_codelist_values, codelist], axis=0)

    codelist["Sort Priority"] = range(0, len(codelist["URI"]))
    codelist.to_csv("./codelists/location.csv", index=False)


if __name__ == "__main__":
    do_da_split()
