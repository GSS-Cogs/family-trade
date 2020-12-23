# Requires python 3.8+

import sys
import json
import glob
from typing import List, Dict, Union, Optional, TypeVar, Callable
from datetime import datetime
import argparse

T = TypeVar("T")
def find(list: List[T], predicate: Callable[[T], bool]) -> Optional[T]:
    for item in list:
        if predicate(item):
            return item

    return None


def override(record: Dict, overrides: Dict):
    """
    Recusrively adds overrides to record. Overwrites existing fields where conflicts arise.
    """
    for key in overrides.keys():
        if key not in record:
            record[key] = overrides[key]
        else:
            existing_value = record[key]
            overwrite_value = overrides[key]
            if isinstance(existing_value, dict):
                override(existing_value, overwrite_value)
            else:
                record[key] = overwrite_value


def supplement(record: Dict, values: Dict):
    """
    Recursively adds values to record without overwriting existing fields.
    """
    for key in values.keys():
        if key not in record:
            record[key] = values[key]
        else:
            existing_value = record[key]
            supplemental_value = values[key]
            if isinstance(existing_value, dict):
                supplement(existing_value, supplemental_value)


def node_has_type(node: Dict, type_to_find: str) -> bool:
    if "@type" in node:
        t = node["@type"]
        return (isinstance(t, list) and find(t, lambda x: x == type_to_find)) or (isinstance(t, str) and t == type_to_find)
    return False


def is_dataset_node(node: Dict) -> bool:
    return node_has_type(node, "dcat:Dataset")


def get_dataset_node(
    csvw_mapping: Dict,
    allow_human_input: bool,
    rdfs_see_also: List[Dict],
    csv_url: str,
    concept_root_uri: str,
    dataset_uri: str,
    existing_label: str
) -> Dict:
    print(f"Processing '{existing_label}' code list ({csv_url})")

    maybe_existing_dataset_node = find(rdfs_see_also, is_dataset_node)

    dataset_node = maybe_existing_dataset_node if maybe_existing_dataset_node is not None else {}

    dataset_label = f"Dataset representing {existing_label} code list"
    override(dataset_node, {
        "@id": dataset_uri,
        "@type": [
            "dcat:Dataset",
            "http://publishmydata.com/pmdcat#Dataset"
        ],
        "rdfs:label": dataset_label,
        "dc:title": dataset_label,
        "http://publishmydata.com/pmdcat#datasetContents": {
            "@id": concept_root_uri
        }
    })

    if allow_human_input:
        # Get the user to provide some inputs:
        fields = [
            {
                "name": "dc:license",
                "input_request": "Please provide the license URI",
                "to_value": lambda input_value: {"@id": input_value}
            },
            {
                "name": "dc:creator",
                "input_request": "Creator Identifier URI",
                "to_value": lambda input_value: {"@id": input_value}
            },
            {
                "name": "dc:publisher",
                "input_request": "Publisher Identifier URI",
                "to_value": lambda input_value: {"@id": input_value}
            },
            {
                "name": "dcat:contactPoint",
                "input_request": "Contact Point URI (accepts 'mailto:email@address.com')",
                "to_value": lambda input_value: {"@id": input_value}
            },
            {
                "name": "dcat:accessURL",
                "input_request": "Access URL (user landing for Download)",
                "to_value": lambda creator_uri: {"@id": creator_uri}
            },
            {
                "name": "dcat:downloadURL",
                "input_request": "Direct Download URL: ",
                "to_value": lambda input_value: {"@id": input_value}
            },
            {
                "name": "dc:issued",
                "input_request": "Date issued/created/published (YYYY-mm-dd)",
                "to_value": lambda input_value: {"@type": "dateTime", "@value": datetime.strptime(dt_issued, "%Y-%m-%d").isoformat()}
            },
            {
                "name": "dc:modified",
                "input_request": "Date modified (YYYY-mm-dd)",
                "to_value": lambda input_value: {"@type": "dateTime", "@value": datetime.strptime(dt_issued, "%Y-%m-%d").isoformat()}
            }
        ]

        for field in fields:
            field_name = field["name"]
            to_value = field["to_value"]
            input_request = field["input_request"]
            if field_name not in dataset_node:
                input_value = input(f"{input_request}: ").strip()
                if len(input_value) > 0:
                    dataset_node[field_name] = to_value(input_value)

    return dataset_node


def augmentWithDCat(csvw_mapping: Dict, allow_human_input: bool):
    # Populate our variables.
    dt_now = datetime.now().isoformat()
    derivation_object = csvw_mapping["prov:hadDerivation"]

    concept_root_uri: str = csvw_mapping["@id"]
    csv_url: str = csvw_mapping["url"]
    existing_type: Union[str, List[str]] = derivation_object["@type"]
    existing_label: str = derivation_object.get(
        "rdfs:label", csvw_mapping.get("rdfs:label"))

    catalog_record_uri = concept_root_uri + "/catalog-record"
    dataset_uri = concept_root_uri + "/dataset"

    # Historical place for rdfs:label doesn't make much sense, it's now outside of `prov:hadDerivation`
    if "rdfs:label" in derivation_object:
        derivation_object.pop("rdfs:label")

    # Ensure that the skos:ConceptScheme is also of type pmdcat:DatasetContents
    pmdcat_dataset_contents = "http://publishmydata.com/pmdcat#DatasetContents"
    if isinstance(existing_type, str):
        if existing_type != pmdcat_dataset_contents:
            derivation_object["@type"] = [
                existing_type,
                pmdcat_dataset_contents
            ]
    elif isinstance(existing_type, list):
        if not find(existing_type, lambda x: x == pmdcat_dataset_contents):
            existing_type.append(pmdcat_dataset_contents)
    else:
        raise Exception(
            f"Unexpected datatype found for '@types': {type(existing_type)}")

    # Ensure all labels are set in correct location.
    csvw_mapping["rdfs:label"] = existing_label
    csvw_mapping["dc:title"] = existing_label

    # Ensure rdfs:seeAlso section is populated with dcat:CatalogRecord,
    # dcat:Dataset and a link between the top-level codelist catalog and the CatalogRecord for this codelist.
    rdfs_see_also: List[Dict] = csvw_mapping.get("rdfs:seeAlso", [])

    dataset_node = get_dataset_node(
        csvw_mapping,
        allow_human_input,
        rdfs_see_also,
        csv_url,
        concept_root_uri,
        dataset_uri,
        existing_label
    )

    if not find(rdfs_see_also, is_dataset_node):
        rdfs_see_also.append(dataset_node)

    catalog_record_catalog_link = find(
        rdfs_see_also, lambda x: "@id" in x and "dcat:record" in x)

    if not catalog_record_catalog_link:
        catalog_record_catalog_link = {}
        rdfs_see_also.append(catalog_record_catalog_link)

    override(catalog_record_catalog_link, {
        "@id": "http://gss-data.org.uk/catalog/vocabularies",
        "dcat:record": {"@id": catalog_record_uri}
    })

    catalog_record = find(
        rdfs_see_also, lambda x: "@id" in x and node_has_type(x, "dcat:CatalogRecord"))

    if not catalog_record:
        catalog_record = {}
        rdfs_see_also.append(catalog_record)

    override(catalog_record, {
        "@id": catalog_record_uri,
        "@type": "dcat:CatalogRecord",
        "dc:title": f"{existing_label} Catalog Record",
        "rdfs:label": f"{existing_label} Catalog Record",
        "foaf:primaryTopic": {
            "@id": dataset_uri
        }
    })

    supplement(catalog_record, {
        "dc:issued": {
            "@type": "dateTime",
            "@value": dt_now
        },
        "dc:modified": {
            "@type": "dateTime",
            "@value": dt_now
        }
    })

    csvw_mapping["rdfs:seeAlso"] = rdfs_see_also


def main():
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument("-a", "--auto", help="Automatically process without human input.",
                        action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument(
        "-f", "--file", help="An individual file to process", type=str, default=None)
    args = parser.parse_args()

    metadata_files: List[str] = glob.glob(
        "*.csv-metadata.json") if args.file is None else [args.file]

    for metadata_file in metadata_files:
        csvw_mapping: Dict = None

        with open(metadata_file, 'r') as file:
            csvw_mapping = json.loads(file.read())

        augmentWithDCat(csvw_mapping, not(args.auto))

        config_json = json.dumps(csvw_mapping, indent=4)
        with open(metadata_file, 'w') as file:
            file.write(config_json)


if __name__ == "__main__":
    main()
