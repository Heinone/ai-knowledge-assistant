import json
from pathlib import Path
from typing import Any

from app.config.config_validator import validate_company_config_or_raise


PROJECT_ROOT = Path(__file__).resolve().parents[2]

ACTIVE_COMPANY_CONFIG_PATH = (
    PROJECT_ROOT / "data" / "company" / "company.json"
)


def has_active_company_config() -> bool:
    return ACTIVE_COMPANY_CONFIG_PATH.is_file()


def get_company_config_path() -> Path:
    if not ACTIVE_COMPANY_CONFIG_PATH.is_file():
        raise FileNotFoundError(
            "No active company configuration exists."
        )

    return ACTIVE_COMPANY_CONFIG_PATH


def load_company_config() -> dict[str, Any]:
    config_path = get_company_config_path()

    with config_path.open("r", encoding="utf-8") as file:
        company = json.load(file)

    validate_company_config_or_raise(company)

    return company