"""
https://api.uktradeinfo.com/Commodity
"""

from pathlib import Path
import requests
import pandas as pd
from typing import List, Dict, Optional


sparql_endpoint = "https://staging.gss-data.org.uk/sparql"
api_url = "https://api.uktradeinfo.com/Commodity"
out_file = Path("../cn8.csv")
cn8_concept_scheme_uri = "http://gss-data.org.uk/def/trade/concept-scheme/combined-nomenclature-8/2021"


def map_sparql_json_results_to_sensible_format(results: dict) -> List[dict]:
    bindings = results["results"]["bindings"]
    results_out = []
    for result in bindings:
        result_out = {}
        for (key, value) in result.items():
            result_out[key] = value["value"]
        results_out.append(result_out)

    return results_out


def get_extend_codelist(concept_scheme_uri: str) -> pd.DataFrame:
    json_response = requests.post(
        sparql_endpoint,
        data={"query": f"""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX ui: <http://www.w3.org/ns/ui#>
            
            SELECT DISTINCT ?concept ?conceptNotation ?conceptLabel ?parentConceptNotation
            WHERE {{
                BIND(<{concept_scheme_uri}> as ?cs).
                ?cs a skos:ConceptScheme.
            
                ?concept skos:inScheme ?cs;
                         skos:notation ?conceptNotation;
                         rdfs:label ?conceptLabel.
            
                OPTIONAL {{
                    ?concept skos:broader [ skos:notation ?parentConceptNotation ].
                }}
            
                OPTIONAL {{
                    ?concept ui:sortPriority ?sortOrder.
                }}
            }}
            ORDER BY ASC(?sortOrder)
        """},
        headers={
            "Accept": "application/json"
        }).json()

    data = pd.DataFrame(map_sparql_json_results_to_sensible_format(json_response))
    data = pd.DataFrame({
        "Label": data["conceptLabel"],
        "Notation": data["conceptNotation"],
        "Parent Notation": data["parentConceptNotation"],
        "Sort Priority": range(1, len(data["conceptLabel"])+1),
        "Exact Match": data["concept"],
        "MatchedWithHMRC": [False for _ in data["conceptLabel"]]
    })
    return data


def get_api_data(url: str) -> List[dict]:
    json_response = requests.get(url).json()
    if "@odata.nextLink" in json_response:
        raise Exception("'@odata.nextLink' present in response. "
                        "This a paged response and this script has not yet been designed to support this.")

    return json_response["value"]


def merge_labels(merged_data: pd.DataFrame, existing_cn8_commodity_codes, hmrc_commodity_codes: Dict[str, str]):
    def get_best_label_for_code(code: str) -> str:
        hmrc_label = hmrc_commodity_codes.get(code)
        if hmrc_label is not None and hmrc_label != "-":
            return hmrc_label

        return existing_cn8_commodity_codes.get(code)

    merged_data["Label"] = merged_data["Notation"].map(get_best_label_for_code)


def get_hmrc_commodity_structure(map_code_to_parent: Dict[str, str]) -> (Dict[str, str], Dict[str, str]):
    def sanitise_notation(notation: Optional[str]) -> Optional[str]:
        if notation:
            # Ensure we generate valid URIs. `-` isn't okay in URIs, so replace with `+`.
            return notation.replace("-", "+")
        return None

    def get_hs_label(c: dict, i: int) -> str:
        concept = c[f"Hs{i}Code"]
        for j in range(i, 0, -2):
            desc = c[f"Hs{j}Description"]
            if desc:
                return desc if j == i else f"({concept}) {desc}"

        return concept

    hmrc_commodity_codes = get_api_data(api_url)

    map_code_to_description = {}
    for c in hmrc_commodity_codes:
        hmrc_code = sanitise_notation(c["Cn8Code"])
        hmrc_label = c["Cn8LongDescription"] \
            or f"({hmrc_code}) {c['Hs6Description'] or c['Hs4Description'] or c['Hs2Description']}" \
            or hmrc_code

        parent_codes = [ (a,b) for (a, b)
                         in [(sanitise_notation(c[f"Hs{i}Code"]), get_hs_label(c, i)) for i in range(6, 0, -2)]
                         if a != hmrc_code
                       ]

        hierarchy = [(hmrc_code, hmrc_label)] + parent_codes

        hierarchy = [(a, b) for (a, b) in hierarchy if a is not None and b is not None]

        for (p_code, p_description) in hierarchy:
            if p_code not in map_code_to_description or (p_description and p_description != '-'):
                map_code_to_description[p_code] = p_description

        for i in range(0, len(hierarchy)-1):
            (this_code, _) = hierarchy[i]
            (next_code, _) = hierarchy[i+1]
            map_code_to_parent[this_code] = next_code

    return map_code_to_description, map_code_to_parent


def define_sort_order(notation: str) -> str:
    if str.isdigit(notation):
        return f"b-{notation}"
    elif "+" in notation:
        # Stick the special `01---`/'HS2 Below Threshold Trade' elements after the real ones.
        # N.B. we have already replaced all instances of `-` with `+` earlier on.
        return f"b-{notation.replace('+', 'z')}"
    else:
        return f"a-section-header-{notation}"


def main():
    existing_cn8_data = get_extend_codelist(cn8_concept_scheme_uri)
    map_code_to_parent = dict(
        [(n, p) for (n, p) in zip(existing_cn8_data["Notation"], existing_cn8_data["Parent Notation"])
         if p is not None]
    )

    (hmrc_code_to_description, map_code_to_parent) = get_hmrc_commodity_structure(map_code_to_parent)

    existing_cn8_data["Parent Notation"] = existing_cn8_data["Notation"].map(map_code_to_parent.get)

    existing_cn8_data["MatchedWithHMRC"] = existing_cn8_data["Notation"]\
        .map(lambda x: x in hmrc_code_to_description.keys())

    merged_data = existing_cn8_data
    map_cn8_to_existing_label = dict(zip(existing_cn8_data["Notation"], existing_cn8_data["Label"]))
    merge_labels(merged_data, map_cn8_to_existing_label, hmrc_code_to_description)

    existing_cn8_codes = set(existing_cn8_data["Notation"])
    unmatched_cn8_codes = [c for c in hmrc_code_to_description.keys() if c not in existing_cn8_codes]

    merged_data = merged_data.append(pd.DataFrame({
        "Label": [hmrc_code_to_description[c] for c in unmatched_cn8_codes],
        "Notation": unmatched_cn8_codes,
        "Parent Notation": [map_code_to_parent.get(c) for c in unmatched_cn8_codes],
        "Sort Priority": [None for c in unmatched_cn8_codes],
        "Exact Match": [None for c in unmatched_cn8_codes],
        "MatchedWithHMRC": [None for c in unmatched_cn8_codes]
    }))

    merged_data = merged_data.append(pd.DataFrame({
        "Label": ["Unknown"],
        "Notation": ["unknown"],
        "Parent Notation": [None],
        "Sort Priority": [len(merged_data["Label"])],
        "Exact Match": [None],
        "MatchedWithHMRC": [None]
    }))

    # Get rid of data where there is no Notation specified.
    merged_data = merged_data[
        [r["Notation"] is not None and r["Notation"] != "00" for i, r in merged_data.iterrows()]
    ]

    # Get rid of data which is in the original CN8 codelist but not in HMRC's codelist.
    # This codelist is big enough as it is, we don't need to leave unnecessary nonsense in there.
    merged_data = merged_data[
        [not str.isdigit(r["Notation"]) or r["MatchedWithHMRC"] is None or r["MatchedWithHMRC"]
         for i, r in merged_data.iterrows()]
    ]

    merged_data["SortParam"] = merged_data["Notation"].map(define_sort_order)
    merged_data = merged_data.sort_values(by="SortParam")
    merged_data["Sort Priority"] = range(0, len(merged_data["Sort Priority"]))

    merged_data = merged_data.drop(columns=["MatchedWithHMRC", "SortParam"])

    merged_data.to_csv(out_file, index=False)


if __name__ == "__main__":
    main()
