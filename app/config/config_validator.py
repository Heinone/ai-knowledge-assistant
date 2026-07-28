from typing import Any


REQUIRED_FIELDS = [
    "company_id",
    "company_name",
    "assistant",
    "modes",
]


def validate_company_config(company: dict[str, Any]) -> list[str]:
    errors = []

    for field in REQUIRED_FIELDS:
        if field not in company:
            errors.append(f"Missing required field: {field}")

    if "assistant" in company:
        assistant = company["assistant"]

        for field in ["name", "title"]:
            if field not in assistant:
                errors.append(
                    f"Missing assistant field: {field}"
                )

    if "modes" in company:
        modes = company["modes"]

        if not modes.get("customer_support", {}).get("enabled") and not modes.get("internal_knowledge", {}).get("enabled"):
            errors.append(
                "At least one assistant mode must be enabled"
            )

    return errors


def validate_company_config_or_raise(company: dict[str, Any]) -> None:
    errors = validate_company_config(company)

    if errors:
        raise ValueError(
            "Invalid company configuration:\n"
            + "\n".join(errors)
        )