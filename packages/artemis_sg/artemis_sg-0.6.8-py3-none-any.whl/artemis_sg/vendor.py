import logging
import os
from types import SimpleNamespace

from artemis_sg.config import CFG

MODULE = os.path.splitext(os.path.basename(__file__))[0]


def vendor(code: str, all_data: list[dict] = CFG["asg"]["vendors"]) -> SimpleNamespace:
    namespace = f"{MODULE}.{vendor.__name__}"
    vendor_data = {
        "code": "foo",
        "name": "",
        "isbn_key": "",
        "failover_scraper": "",
    }
    try:
        result = next((item for item in all_data if item["code"] == code), {})
    except KeyError:
        logging.warning(f"{namespace}: code {code} not found in data {all_data}")
        result = {}
    if "isbn_key" in result:
        result["isbn_key"] = result["isbn_key"].upper()
    data = vendor_data | result
    return SimpleNamespace(**data)
