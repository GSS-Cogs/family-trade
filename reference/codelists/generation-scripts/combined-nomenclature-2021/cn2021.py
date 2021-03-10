"""
CN-2021 can be downloaded from https://ec.europa.eu/eurostat/ramon/nomenclatures/index.cfm?TargetUrl=LST_CLS_DLD&StrNom=CN_2021&StrLanguageCode=EN&StrLayoutCode=HIERARCHIC#
"""
from pathlib import Path
import requests as req
import pandas as pd
import math
import re
from typing import List

csv_file_url = "https://ec.europa.eu/eurostat/ramon/nomenclatures/index.cfm?TargetUrl=ACT_OTH_CLS_DLD&StrNom=CN_2021&" \
               "StrFormat=CSV&StrLanguageCode=EN&IntKey=&IntLevel=&bExport="


def main():
    # Out directory used to hide raw CSV from git.
    out_directory = Path("out")
    if not out_directory.exists():
        out_directory.mkdir()

    csv_file_in = Path(out_directory / "cn-2021-input.csv")
    cn_codelist_file_out = Path("../../combined-nomenclature-2021.csv")
    cn_8_codelist_file_out = Path("../../combined-nomenclature-8-2021.csv")
    ensure_input_csv_exists(csv_file_in)

    csv_in = pd.read_csv(csv_file_in, sep=";")

    # Remove dashes from start of label.
    csv_in["Code"] = csv_in["Code"].map(lambda x: str(int(x)) if x and not math.isnan(x) else "")
    csv_in["Parent"] = csv_in["Parent"].map(lambda x: str(int(x)) if x and not math.isnan(x) else "")
    csv_in["Description"] = csv_in["Description"].map(lambda x: re.sub(r"^[-\s]*", "", x))
    csv_in["Code.1"] = csv_in["Code.1"].map(lambda x: re.sub(r"\s+", "", x) if isinstance(x, str) else "")
    csv_in["Parent.1"] = csv_in["Parent.1"].map(lambda x: re.sub(r"\s+", "", x) if isinstance(x, str) else "")

    primary_cn_codelist = pd.DataFrame({
        "Label": csv_in["Description"],
        "Notation": csv_in["Code"],
        "Parent Notation": csv_in["Parent"],
        "CN8Mapping": csv_in["Code.1"],
        "Sort Priority": range(1, len(csv_in["Code"]) + 1),
        "Description": csv_in["Self-explanatory texts in English"]
    })
    primary_cn_codelist.to_csv(cn_codelist_file_out, index=False)

    # def get_standard_parents_required_to_root(data_included: pd.DataFrame) -> pd.DataFrame:
    #     """
    #     Pull out the parent hierarchy (to the root) where there are parent nodes which don't have CN8 codes.
    #     Instead, use their standard CN code inside this mis-mash hierarchy.
    #     Instead, use their standard CN code inside this mis-mash hierarchy.
    #     """
    #     already_existing_codes = set(data_included["Code"])
    #     standard_parent_ids_required = set([
    #         row[1]["Parent"]
    #         for row in data_included.iterrows()
    #         if not (isinstance(row[1]["Parent.1"], str) and len(row[1]["Parent.1"].strip()) > 0)
    #            and len(row[1]["Parent"]) > 0 and row[1]["Parent"] not in already_existing_codes
    #     ])
    #     if len(standard_parent_ids_required) == 0:
    #         return data_included
    #
    #     standard_parents_required = csv_in[csv_in["Code"].isin(standard_parent_ids_required)]
    #     return get_standard_parents_required_to_root(data_included.append(standard_parents_required))
    #
    # # If the row in the csv_in is a string then it has a value, else it is a float(nan)
    # cn_8_hierarchy = get_standard_parents_required_to_root(
    #     csv_in[csv_in["Code.1"].map(lambda x: isinstance(x, str) and len(x.strip()) > 0)]
    # )

    cn_8_codelist = pd.DataFrame({
        "Label": csv_in["Description"],
        "Notation": [row[1]["Code.1"] if len(row[1]["Code.1"]) > 0 else row[1]["Code"] for row in csv_in.iterrows()],
        "Parent Notation": [row[1]["Parent.1"] if len(row[1]["Parent.1"]) > 0 else row[1]["Parent"] for row in csv_in.iterrows()],
        "CNMapping": csv_in["Code"],
        "Sort Priority": range(1, len(csv_in["Code"]) + 1),
        "Description": csv_in["Self-explanatory texts in English"]
    })
    cn_8_codelist.to_csv(cn_8_codelist_file_out, index=False)


def ensure_input_csv_exists(csv_file_in):
    if not csv_file_in.exists():
        print(f"Could not find {csv_file_in}. Downloading from {csv_file_url}.")
        response = req.get(csv_file_url)
        with open(csv_file_in, "w+") as f:
            f.write(response.text)
        print("Download complete.")


if __name__ == "__main__":
    main()
