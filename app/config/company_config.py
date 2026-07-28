import json
from pathlib import Path

from app.config.config_validator import validate_company_config_or_raise


COMPANY_CONFIG_PATH = Path(
    "data/company/company.json"
)


def load_company_config():
    with open(
        COMPANY_CONFIG_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        company = json.load(file)

    validate_company_config_or_raise(company)

    return company