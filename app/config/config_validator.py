from typing import Any

from app.models.assistant_mode import AssistantMode


REQUIRED_FIELDS = [
    "company_id",
    "company_name",
    "assistant",
    "modes",
    "default_mode",
]


def validate_company_config(
    company: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    for field in REQUIRED_FIELDS:
        if field not in company:
            errors.append(
                f"Missing required field: {field}"
            )

    assistant = company.get("assistant")

    if not isinstance(assistant, dict):
        errors.append(
            "Assistant configuration must be an object"
        )
    else:
        for field in ("name", "title"):
            value = assistant.get(field)

            if not isinstance(value, str) or not value.strip():
                errors.append(
                    f"Missing assistant field: {field}"
                )

    modes = company.get("modes")

    if not isinstance(modes, dict):
        errors.append(
            "Assistant modes configuration must be an object"
        )

        return errors

    enabled_modes: list[AssistantMode] = []
    default_flags: list[AssistantMode] = []

    for mode in AssistantMode:
        mode_config = modes.get(mode.value)

        if not isinstance(mode_config, dict):
            errors.append(
                f"Missing assistant mode configuration: "
                f"{mode.value}"
            )
            continue

        if mode_config.get("enabled") is True:
            enabled_modes.append(mode)

        if mode_config.get("default") is True:
            default_flags.append(mode)

    if not enabled_modes:
        errors.append(
            "At least one assistant mode must be enabled"
        )

    configured_default = company.get(
        "default_mode"
    )

    try:
        default_mode = AssistantMode(
            configured_default
        )
    except (TypeError, ValueError):
        default_mode = None

        errors.append(
            "Default assistant mode is invalid"
        )

    if (
        default_mode is not None
        and default_mode not in enabled_modes
    ):
        errors.append(
            "Default assistant mode must be enabled"
        )

    if len(default_flags) != 1:
        errors.append(
            "Exactly one assistant mode must be marked as default"
        )
    elif (
        default_mode is not None
        and default_flags[0] != default_mode
    ):
        errors.append(
            "Default mode flag does not match default_mode"
        )

    return errors


def validate_company_config_or_raise(
    company: dict[str, Any],
) -> None:
    errors = validate_company_config(company)

    if errors:
        raise ValueError(
            "Invalid company configuration:\n"
            + "\n".join(errors)
        )