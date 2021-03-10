"""
CN-2021 can be downloaded from https://ec.europa.eu/eurostat/ramon/nomenclatures/index.cfm?TargetUrl=LST_CLS_DLD&StrNom=CN_2021&StrLanguageCode=EN&StrLayoutCode=HIERARCHIC#
"""
from pathlib import Path
import requests as req
import pandas as pd
import math
import re

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
    csv_in["Description"] = csv_in["Description"].map(lambda x: re.sub(r"^[-\s]*", "", x))
    csv_in["Code.1"] = csv_in["Code.1"].map(lambda x: re.sub(r"\s+", "", x) if isinstance(x, str) else "")
    csv_in["Parent.1"] = csv_in["Parent.1"].map(lambda x: re.sub(r"\s+", "", x) if isinstance(x, str) else "")

    primary_cn_codelist = pd.DataFrame({
        "Label": csv_in["Description"],
        "Notation": csv_in["Code"],
        "Parent Notation": csv_in["Parent"].map(lambda x: str(int(x)) if x and not math.isnan(x) else ""),
        "CN8Mapping": csv_in["Code.1"],
        "Sort Priority": range(1, len(csv_in["Code"]) + 1),
        "Description": csv_in["Self-explanatory texts in English"]
    })
    primary_cn_codelist.to_csv(cn_codelist_file_out, index=False)

    # If the row in the csv_in is a string then it has a value, else it is a float(nan)
    cn_8_rows = csv_in[csv_in["Code.1"].map(lambda x: isinstance(x, str) and len(x.strip()) > 0)]
    cn_8_codelist = pd.DataFrame({
        "Label": cn_8_rows["Description"],
        "Notation": cn_8_rows["Code.1"],
        "Parent Notation": cn_8_rows["Parent.1"].map(lambda x: x if isinstance(x, str) else ""),
        "CNMapping": cn_8_rows["Code"],
        "Sort Priority": range(1, len(cn_8_rows["Code.1"]) + 1),
        "Description": cn_8_rows["Self-explanatory texts in English"]
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
