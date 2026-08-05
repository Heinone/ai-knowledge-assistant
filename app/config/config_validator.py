from typing import Any

from app.config.env_config import AVAILABLE_MODES
from app.models.assistant_mode import AssistantMode


REQUIRED_FIELDS = [
    "company_id",
    "company_name",
    "assistant",
    "modes",
]


def validate_company_config(
    company: dict[str, Any],
    *,
    available_modes: tuple[
        AssistantMode,
        ...,
    ] = AVAILABLE_MODES,
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

            if (
                not isinstance(value, str)
                or not value.strip()
            ):
                errors.append(
                    f"Missing assistant field: {field}"
                )

    modes = company.get("modes")

    if not isinstance(modes, dict):
        errors.append(
            "Assistant modes configuration must be an object"
        )

        return errors

    enabled_modes: set[AssistantMode] = set()
    default_flags: list[AssistantMode] = []

    for mode in AssistantMode:
        mode_config = modes.get(mode.value)

        if not isinstance(mode_config, dict):
            errors.append(
                "Missing assistant mode configuration: "
                f"{mode.value}"
            )

            continue

        if mode_config.get("enabled") is True:
            enabled_modes.add(mode)

        if mode_config.get("default") is True:
            default_flags.append(mode)

    provisioned_modes = set(available_modes)

    missing_modes = (
        provisioned_modes - enabled_modes
    )

    unavailable_modes = (
        enabled_modes - provisioned_modes
    )

    if missing_modes:
        errors.append(
            "Provisioned assistant modes must be enabled: "
            + ", ".join(
                sorted(
                    mode.value
                    for mode in missing_modes
                )
            )
        )

    if unavailable_modes:
        errors.append(
            "Company configuration enables unavailable "
            "assistant modes: "
            + ", ".join(
                sorted(
                    mode.value
                    for mode in unavailable_modes
                )
            )
        )

    if len(default_flags) > 1:
        errors.append(
            "At most one assistant mode may be "
            "marked as the legacy default"
        )

    for default_mode in default_flags:
        if default_mode not in provisioned_modes:
            errors.append(
                "Legacy default assistant mode must "
                "be provisioned"
            )

    configured_default = company.get(
        "default_mode"
    )

    if configured_default is not None:
        try:
            legacy_default_mode = AssistantMode(
                configured_default
            )
        except (TypeError, ValueError):
            errors.append(
                "Legacy default assistant mode is invalid"
            )
        else:
            if (
                legacy_default_mode
                not in provisioned_modes
            ):
                errors.append(
                    "Legacy default assistant mode must "
                    "be provisioned"
                )

            if (
                default_flags
                and default_flags[0]
                != legacy_default_mode
            ):
                errors.append(
                    "Legacy default mode flag does not "
                    "match default_mode"
                )

    return errors


def validate_company_config_or_raise(
    company: dict[str, Any],
    *,
    available_modes: tuple[
        AssistantMode,
        ...,
    ] = AVAILABLE_MODES,
) -> None:
    errors = validate_company_config(
        company,
        available_modes=available_modes,
    )

    if errors:
        raise ValueError(
            "Invalid company configuration:\n"
            + "\n".join(errors)
        )