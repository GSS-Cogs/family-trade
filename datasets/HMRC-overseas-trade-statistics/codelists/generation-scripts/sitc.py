"""
https://api.uktradeinfo.com/Port
"""

from pathlib import Path
import requests
import pandas as pd
from typing import List, Optional
import re


api_url = "https://api.uktradeinfo.com/SITC"
out_file = Path("../sitc.csv")


def get_api_data(url: str) -> List[dict]:
    json_response = requests.get(url).json()
    if "@odata.nextLink" in json_response:
        raise Exception("'@odata.nextLink' present in response. "
                        "This a paged response and this script has not yet been designed to support this.")

    return json_response["value"]


def main():
    def get_parent_code(record: dict) -> Optional[str]:
        id = record["SitcCode"]

        if "-" in id:
            return re.sub("-+", "", id)
        else:
            parent_codes = record["ParentSitcCodes"]
            if len(parent_codes) > 0:
                return parent_codes[0]

        return None

    def map_to_standard_sitc(code: str) -> str:
        def place_decimal_point(c: str) -> str:
            if c is None:
                return None

            if len(c) in [1, 2, 3]:
                # Section, Divisional header or Group header
                return c
            elif len(c) in [4, 5]:
                # Either group header, sub-group header or final level SITCv4 code
                return f"{c[0:3]}.{c[3:]}"
            else:
                raise Exception(f"Unexpected length {len(c)} for code '{c}'")

        def trim_zeros(c: str) -> str:
            if c in ["0", "00"]:
                return c

            c = re.sub("0+$", "", c)
            c = re.sub("\\.$", "", c)

            return c

        if code is None:
            return None

        return trim_zeros(place_decimal_point(code))

    sitc_data = get_api_data(api_url)
    flattened_sitc_data = []
    for item in sitc_data:
        for i in range(1, 5):
            code_field_name = f"Sitc{i}Code"
            desc_field_name = f"Sitc{i}Desc"
            if code_field_name in item and item[code_field_name] is not None:
                flattened_sitc_data.append({
                    "SitcCode": item[code_field_name],
                    "SitcDesc": item[desc_field_name],
                    "ParentSitcCodes": [
                        item[f"Sitc{j}Code"] for j in range(i-1, 0, -1)
                        if f"Sitc{j}Code" in item and item[f"Sitc{j}Code"] is not None
                    ]
                })

        flattened_sitc_data.append({
            "SitcCode": item["SitcCode"],
            "SitcDesc": item["SitcDesc"],
            "ParentSitcCodes": [
                item[f"Sitc{i}Code"] for i in range(3, 0, -1)
                if f"Sitc{i}Code" in item and item[f"Sitc{i}Code"] is not None and item[f"Sitc{i}Code"] != item["SitcCode"]
            ]
        })

    code_mappings = set()
    unique_sitc_data = []
    for item in flattened_sitc_data:
        code = item["SitcCode"]
        if code in code_mappings:
            continue
        else:
            code_mappings.add(code)
            unique_sitc_data.append(item)

    ports_codelist = pd.DataFrame({
        "TrueSitcNotation": [map_to_standard_sitc(code) if len(code) <= 5 and "-" not in code else None for code in [p["SitcCode"] for p in unique_sitc_data]],
        "Label": [f"{p['SitcDesc']}" for p in unique_sitc_data],
        "Notation": [p["SitcCode"].replace("-", "+") for p in unique_sitc_data],
        "Parent Notation": [get_parent_code(s) for s in unique_sitc_data],
        "Sort Priority": range(1, len(unique_sitc_data) + 1)
    })

    parents_required = set([x for x in ports_codelist["Parent Notation"] if x is not None])
    sitc_present = set(ports_codelist["Notation"])
    unmatched_sitcs = parents_required - sitc_present
    if len(unmatched_sitcs) > 0:
        raise Exception(f"Could not find SITC values for expected parents: {unmatched_sitcs}")

    ports_codelist.to_csv(out_file, index=False)


if __name__ == "__main__":
    main()
