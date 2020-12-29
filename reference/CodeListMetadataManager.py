"""
A script which aides in the creation and maintainance of `.csv-metadata.json` schema files.

Call with `--help` arg for further instructions.

Requires python 3.8+

"""

import re
import json
import glob
from typing import List, Dict, Union, Optional, TypeVar, Callable
from datetime import datetime
import argparse
from os import path
import csv

T = TypeVar("T")
reference_data_base_uri = "http://gss-data.org.uk/def"
pmdcat_base_uri = "http://publishmydata.com/pmdcat#"


def find(xs: List[T], predicate: Callable[[T], bool]) -> Optional[T]:
    for item in xs:
        if predicate(item):
            return item

    return None


def override(record: Dict, overrides: Dict):
    """
    Recursively adds overrides to record. Overwrites existing fields where conflicts arise.
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
        return (isinstance(t, list) and find(t, lambda x: x == type_to_find)) or (
                isinstance(t, str) and t == type_to_find)
    return False


def is_dataset_node(node: Dict) -> bool:
    return node_has_type(node, "dcat:Dataset")


def populate_dataset_node(
        dataset_node: Dict,
        allow_human_input: bool,
        csv_url: str,
        concept_root_uri: str,
        dataset_uri: str,
        existing_label: str
):
    print(f"Processing '{existing_label}' code list ({csv_url})")

    override(dataset_node, {
        "@id": dataset_uri,
        "@type": [
            "dcat:Dataset",
            f"{pmdcat_base_uri}Dataset"
        ],
        f"{pmdcat_base_uri}datasetContents": {
            "@id": concept_root_uri
        }
    })

    supplement(dataset_node, {
        "rdfs:label": existing_label,
        "dc:title": existing_label,
        "rdfs:comment": f"Dataset representing the '{existing_label}' code list."
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
                "name": "dcat:landingPage",
                "input_request": "Landing Page URL (user landing for Download)",
                "to_value": lambda landing_uri: {"@id": landing_uri}
            },
            {
                "name": "dc:issued",
                "input_request": "Date issued/created/published (YYYY-mm-dd)",
                "to_value": lambda input_value: {"@type": "dateTime",
                                                 "@value": datetime.strptime(input_value, "%Y-%m-%d").isoformat()}
            },
            {
                "name": "dc:modified",
                "input_request": "Date modified (YYYY-mm-dd)",
                "to_value": lambda input_value: {"@type": "dateTime",
                                                 "@value": datetime.strptime(input_value, "%Y-%m-%d").isoformat()}
            },
            {
                "name": f"{pmdcat_base_uri}markdownDescription",
                "input_request": "Markdown Description of Dataset",
                "to_value": lambda input_value: {
                    "@type": "https://www.w3.org/ns/iana/media-types/text/markdown#Resource",
                    "@value": input_value
                }
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


def map_file_path_to_label(file_path: str) -> str:
    file_name_without_ext = re.sub(".*?([^/]+)\\..*$", "\\1", file_path)
    return file_name_without_ext.replace("-", " ").title()


def refactor_structure_with_updates(csvw_mapping: Dict, allow_human_input: bool):
    """
    Applies schematic updates to the structure of `.csv-metadata.json` files.
    """
    # Populate our variables.
    dt_now = datetime.now().isoformat()
    prov_derivation_object = csvw_mapping["prov:hadDerivation"]
    concept_root_uri: str = csvw_mapping["@id"]
    csv_url: str = csvw_mapping["url"]
    existing_label: str = csvw_mapping.get("rdfs:label", prov_derivation_object.get("rdfs:label"))

    standardise_labels(csvw_mapping, prov_derivation_object, existing_label)

    populate_required_dcat_metadata(allow_human_input, concept_root_uri, csv_url, csvw_mapping,
                                    prov_derivation_object, dt_now, existing_label)


def standardise_labels(
        csvw_mapping: Dict,
        prov_derivation_object: Dict,
        existing_label: str
):
    # Historical place for rdfs:label doesn't make much sense, it's now outside of `prov:hadDerivation`
    if "rdfs:label" in prov_derivation_object:
        prov_derivation_object.pop("rdfs:label")
    # Ensure all labels are set in correct location.
    csvw_mapping["rdfs:label"] = existing_label
    csvw_mapping["dc:title"] = existing_label


def populate_required_dcat_metadata(
        allow_human_input: bool,
        concept_root_uri: str,
        csv_url: str,
        csvw_mapping: Dict,
        prov_derivation_object: Dict,
        dt_now: str,
        existing_label: str
):
    catalog_record_uri = concept_root_uri + "/catalog-record"
    dataset_uri = concept_root_uri + "/dataset"

    # Ensure that the skos:ConceptScheme is also of type pmdcat:DatasetContents
    existing_type: Union[str, List[str]] = prov_derivation_object["@type"]

    pmdcat_dataset_contents = f"{pmdcat_base_uri}DatasetContents"
    pmdcat_concept_scheme = f"{pmdcat_base_uri}ConceptScheme"
    if isinstance(existing_type, str):
        if existing_type != pmdcat_concept_scheme:
            prov_derivation_object["@type"] = [
                existing_type,
                pmdcat_concept_scheme
            ]
    elif isinstance(existing_type, list):
        if pmdcat_concept_scheme not in existing_type:
            existing_type.append(pmdcat_concept_scheme)

        if pmdcat_dataset_contents in existing_type:
            existing_type.remove(pmdcat_dataset_contents)
    else:
        raise Exception(
            f"Unexpected datatype found for '@types': {type(existing_type)}")

    # Ensure rdfs:seeAlso section is populated with dcat:CatalogRecord,
    # dcat:Dataset and a link between the top-level codelist catalog and the CatalogRecord for this codelist.
    rdfs_see_also: List[Dict] = csvw_mapping.get("rdfs:seeAlso", [])
    dataset_node = find(rdfs_see_also, is_dataset_node)
    if not dataset_node:
        dataset_node = {}
        rdfs_see_also.append(dataset_node)
    populate_dataset_node(
        dataset_node,
        allow_human_input,
        csv_url,
        concept_root_uri,
        dataset_uri,
        existing_label
    )
    catalog_record_catalog_link = find(rdfs_see_also, lambda x: "@id" in x and "dcat:record" in x)
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
        "foaf:primaryTopic": {
            "@id": dataset_uri
        }
    })
    supplement(catalog_record, {
        "dc:title": f"{existing_label} Catalog Record",
        "rdfs:label": f"{existing_label} Catalog Record",
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


def create_metadata_shell_for_csv(csv_file_path: str) -> str:
    """
    Returns the path for the metadata file which has been created.
    """
    metadata_file = f"{csv_file_path}-metadata.json"
    if path.exists(metadata_file):
        raise Exception(f"Metadata file {metadata_file} already exists.")
    if not path.exists(csv_file_path):
        raise Exception(f"CSV file {csv_file_path} does not exist.")

    label = map_file_path_to_label(csv_file_path)
    concept_scheme_uri = generate_concept_scheme_root_uri(label)

    # Just inserting basic structure at this point as already exists in standard files. Additional metadata will be
    # added as the script continues to run.
    metadata = {
        "@context": "http://www.w3.org/ns/csvw",
        "@id": concept_scheme_uri,
        "url": csv_file_path,
        "rdfs:label": label,
        "dc:title": label,
        "tableSchema": {
            "columns": [],
        },
        "prov:hadDerivation": {
            "@id": concept_scheme_uri,
            "@type": [
                "skos:ConceptScheme",
                f"{pmdcat_base_uri}DatasetContents"
            ]
        }
    }

    table_schema: Dict = metadata["tableSchema"]
    columns: List[Dict] = table_schema["columns"]

    with open(csv_file_path, newline="") as csv_file:
        reader = csv.reader(csv_file, delimiter=",", quotechar="\"")
        column_names: List[str] = next(reader)

    for column_name in column_names:
        column = generate_schema_for_column(column_name, concept_scheme_uri)
        columns.append(column)

    columns.append({
            "virtual": True,
            "propertyUrl": "rdf:type",
            "valueUrl": "skos:Concept"
    })
    columns.append({
            "virtual": True,
            "propertyUrl": "skos:inScheme",
            "valueUrl": concept_scheme_uri
    })

    if "notation" in [c.lower() for c in column_names]:
        override(table_schema, {
            "primaryKey": "notation",
            "aboutUrl": concept_scheme_uri + "/{notation}"
        })
    else:
        print("WARNING: could not determine primary key. As a result, `aboutUrl` property is not specified and " +
              "so each row will not have a true URI. This is basically required. Manual configuration required.")

    with open(metadata_file, 'w+') as file:
        file.write(json.dumps(metadata, indent=4))

    return str(metadata_file)


def generate_schema_for_column(column_name: str, concept_scheme_uri: str) -> Dict:
    """
    Generates column schema structure for a given column name.
    If the column name matches one of the standard GSS code-list column names then we link up the associated metadata.
    """
    column_name = column_name.strip()
    column_name_lower = column_name.lower()
    column_name_snake_case = re.sub("\\s+", "_", column_name_lower)
    column = {
        "titles": column_name,
        "name": column_name_snake_case
    }
    if column_name_lower == "label":
        override(column, {
            "datatype": "string",
            "required": True,
            "propertyUrl": "rdfs:label"
        })
    elif column_name_lower == "notation":
        override(column, {
            "datatype": {
                "base": "string",
                "format": "^-?[\\w\\.\\/\\+]+(-[\\w\\.\\/\\+]+)*$"
            },
            "required": True,
            "propertyUrl": "skos:notation"
        })
    elif column_name_lower == "parent notation":
        override(column, {
            "datatype": {
                "base": "string",
                "format": "^(-?[\\w\\.\\/\\+]+(-[\\w\\.\\/\\+]+)*|)$"
            },
            "required": False,
            "propertyUrl": "skos:broader",
            "valueUrl": concept_scheme_uri + "/{" + column_name_snake_case + "}"
        })
    elif column_name_lower == "sort priority":
        override(column, {
            "datatype": "integer",
            "required": False,
            "propertyUrl": "http://www.w3.org/ns/ui#sortPriority"
        })
    elif column_name_lower == "description":
        override(column, {
            "datatype": "string",
            "required": False,
            "propertyUrl": "rdfs:comment"
        })
    else:
        print(f"WARNING: Column '{column_name}' is not standard and so has not been fully mapped. " +
              "Please configure manually.")

    return column


def generate_concept_scheme_root_uri(label: str):
    def code_list_is_in_family() -> bool:
        global_family_response = input("Is the code list defined at the Global level or at the Family level? (G/f): ") \
            .strip().lower()
        is_global = len(global_family_response) == 0 or global_family_response == "g"
        if not is_global and global_family_response != "f":
            raise Exception(f"Invalid Global or family response '{global_family_response}'")

        return not is_global

    label_uri_format = re.sub("\\s+", "-", label.lower())

    if code_list_is_in_family():
        family_name = input("Please enter the family name (e.g. trade): ").strip().lower()
        if len(family_name) == 0:
            raise Exception("Family Name not provided.")

        return f"{reference_data_base_uri}/{family_name}/concept-scheme/{label_uri_format}"
    else:
        return f"{reference_data_base_uri}/concept-scheme/{label_uri_format}"


def main():
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument("-a", "--auto", help="Automatically process upgrades without human input.",
                        action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("-c", "--csv",
                        help="A CSV file. The script will create a corresponding `.csv-metadata.json` file.",
                        type=str, default=None)
    parser.add_argument("-s", "--schema", help="An individual schema file to upgrade.", type=str, default=None)
    parser.add_argument("-u", "--upgrade-all",
                        help="Finds all `.csv-metadata.json` files within the current directory (it recursively "
                             "searches through sub-directories) and applies any upgrades required.",
                        action=argparse.BooleanOptionalAction, default=False)
    args = parser.parse_args()

    metadata_files: List[str]
    if args.schema is not None:
        metadata_files = [args.schema]
    elif args.upgrade_all:
        metadata_files = glob.glob("**/*.csv-metadata.json", recursive=True) 
    elif args.csv is not None:
        if args.auto:
            raise Exception("Cannot create a new metadata file from an existing CSV without human input.")
        metadata_files = [create_metadata_shell_for_csv(args.csv)]
    else:
        parser.print_help()
        exit()

    for metadata_file in metadata_files:
        with open(metadata_file, 'r') as file:
            csvw_mapping = json.loads(file.read())

        refactor_structure_with_updates(csvw_mapping, not args.auto)

        config_json = json.dumps(csvw_mapping, indent=4)
        with open(metadata_file, 'w') as file:
            file.write(config_json)


if __name__ == "__main__":
    main()
