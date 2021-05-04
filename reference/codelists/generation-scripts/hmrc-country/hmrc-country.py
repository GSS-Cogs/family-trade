# CountryId,CountryCodeNumeric,RegionId,CountryName,CountryCodeAlpha,Area1,Area2,Area3,Area4,Area5,Area1a,Area2a,Area3a,Area4a,Area5a
# 1,001,001,France,FR,1,,,,,European Union,,,,

"""
https://api.uktradeinfo.com/Country
"""

from pathlib import Path
import requests
import pandas as pd
from typing import List, Dict, Optional


api_url = "https://api.uktradeinfo.com/Country"
out_file = Path("../../hmrc-country.csv")


def get_api_data(url: str) -> List[dict]:
    json_response = requests.get(url).json()
    if "@odata.nextLink" in json_response:
        raise Exception("'@odata.nextLink' present in response. "
                        "This a paged response and this script has not yet been designed to support this.")

    return json_response["value"]


def main():
    countries_data = get_api_data(api_url)

    countries = pd.DataFrame(countries_data)
    countries = countries.append({
        "CountryId": "unknown",
        "CountryCodeNumeric": None,
        "RegionId": None,
        "CountryName": "Unknown",
        "CountryCodeAlpha": "unknown",
        "Area1": None,
        "Area2": None,
        "Area3": None,
        "Area4": None,
        "Area5": None,
        "Area1a": None,
        "Area2a": None,
        "Area3a": None,
        "Area4a": None,
        "Area5a": None
    }, ignore_index=True)
    # CountryId,CountryCodeNumeric,RegionId,CountryName,CountryCodeAlpha,Area1,Area2,Area3,Area4,Area5,Area1a,Area2a,Area3a,Area4a,Area5a

    countries.to_csv(out_file, index=False)


if __name__ == "__main__":
    main()
