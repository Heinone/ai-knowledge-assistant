import json
from pathlib import Path


COMPANY_CONFIG_PATH = Path(
    "data/company/company.json"
)


def load_company_config():
    with open(
        COMPANY_CONFIG_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)