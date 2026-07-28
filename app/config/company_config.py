from pathlib import Path
import json


COMPANY_CONFIG_PATH = (
    Path(__file__).parent.parent.parent
    / "data"
    / "company"
    / "company.json"
)


def load_company_config():
    with open(COMPANY_CONFIG_PATH, "r") as file:
        return json.load(file)