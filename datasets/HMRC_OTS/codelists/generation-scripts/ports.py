"""
https://api.uktradeinfo.com/Port
"""

from pathlib import Path
import requests
import pandas as pd
from typing import List

api_url = "https://api.uktradeinfo.com/Port"
out_file = Path("../port.csv")


def get_api_data(url: str) -> List[dict]:
    json_response = requests.get(url).json()
    if "@odata.nextLink" in json_response:
        raise Exception("'@odata.nextLink' present in response. "
                        "This a paged response and this script has not yet been designed to support this.")

    return json_response["value"]


def main():
    ports_data = get_api_data(api_url)
    ports_codelist = pd.DataFrame({
        "Label": [f"{p['PortName']} ({p['PortCodeAlpha']})" for p in ports_data],
        "Notation": [p["PortId"] for p in ports_data],
        "Parent Notation": [None for _ in ports_data],
        "Sort Priority": range(1, len(ports_data) + 1)
    })
    ports_codelist.to_csv(out_file, index=False)


if __name__ == "__main__":
    main()
