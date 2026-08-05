import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from app.config.config_validator import (
    validate_company_config_or_raise,
)
from app.config.env_config import AVAILABLE_MODES
from app.models.assistant_mode import AssistantMode
from app.services.company_config_migration_service import (
    migrate_company_config_to_v2,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

ACTIVE_COMPANY_CONFIG_PATH = (
    PROJECT_ROOT
    / "data"
    / "company"
    / "company.json"
)

DEFAULT_FALLBACK_MESSAGE = (
    "I could not find enough information to answer that confidently."
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
        company = migrate_company_config_to_v2(
            json.load(file)
        )

    validate_company_config_or_raise(company)

    return company


def _get_mode_config(
    company: Mapping[str, Any],
    mode: AssistantMode,
) -> Mapping[str, Any]:
    modes = company.get("modes", {})

    if not isinstance(modes, Mapping):
        return {}

    mode_config = modes.get(mode.value, {})

    if not isinstance(mode_config, Mapping):
        return {}

    return mode_config


def get_enabled_assistant_modes(
    company: Mapping[str, Any],
) -> tuple[AssistantMode, ...]:
    configured_modes = company.get("modes")

    if not isinstance(configured_modes, Mapping):
        raise ValueError(
            "Company configuration must contain assistant modes."
        )

    enabled_modes: list[AssistantMode] = []

    for mode in AssistantMode:
        mode_config = configured_modes.get(
            mode.value,
            {},
        )

        if (
            isinstance(mode_config, Mapping)
            and mode_config.get("enabled") is True
        ):
            enabled_modes.append(mode)

    return tuple(enabled_modes)


def resolve_assistant_mode(
    requested_mode: AssistantMode | str | None = None,
    *,
    company: Mapping[str, Any] | None = None,
    available_modes: tuple[
        AssistantMode,
        ...,
    ] = AVAILABLE_MODES,
) -> AssistantMode:
    company_config = (
        load_company_config()
        if company is None
        else company
    )

    configured_modes = get_enabled_assistant_modes(
        company_config
    )

    if set(configured_modes) != set(available_modes):
        raise ValueError(
            "Company assistant modes do not match "
            "the provisioned AVAILABLE_MODES."
        )

    if requested_mode is not None:
        try:
            resolved_mode = AssistantMode(
                requested_mode
            )
        except ValueError as error:
            raise ValueError(
                f"Unsupported assistant mode: "
                f"{requested_mode}."
            ) from error

        if resolved_mode not in available_modes:
            raise ValueError(
                f"Assistant mode "
                f"'{resolved_mode.value}' is not "
                "available for this deployment."
            )

        return resolved_mode

    if len(available_modes) == 1:
        return available_modes[0]

    raise ValueError(
        "Assistant mode is required when multiple "
        "assistant modes are available."
    )


def get_mode_fallback_message(
    company: Mapping[str, Any],
    mode: AssistantMode | str,
) -> str:
    resolved_mode = AssistantMode(mode)

    mode_config = _get_mode_config(
        company,
        resolved_mode,
    )

    chat_config = mode_config.get("chat", {})

    if isinstance(chat_config, Mapping):
        fallback_message = chat_config.get(
            "fallback_message"
        )

        if (
            isinstance(fallback_message, str)
            and fallback_message.strip()
        ):
            return fallback_message.strip()

    legacy_mode_config = company.get(
        resolved_mode.value,
        {},
    )

    if isinstance(
        legacy_mode_config,
        Mapping,
    ):
        fallback_message = legacy_mode_config.get(
            "fallback_message"
        )

        if (
            isinstance(fallback_message, str)
            and fallback_message.strip()
        ):
            return fallback_message.strip()

    return DEFAULT_FALLBACK_MESSAGE


def get_mode_prompt_guide(
    company: Mapping[str, Any],
    mode: AssistantMode | str,
) -> str:
    resolved_mode = AssistantMode(mode)

    mode_config = _get_mode_config(
        company,
        resolved_mode,
    )

    prompt_guide = mode_config.get(
        "prompt_guide"
    )

    if isinstance(prompt_guide, str):
        return prompt_guide.strip()

    legacy_prompts = company.get(
        "prompts",
        {},
    )

    if not isinstance(legacy_prompts, Mapping):
        return ""

    legacy_prompt = legacy_prompts.get(
        resolved_mode.value
    )

    if not isinstance(legacy_prompt, str):
        return ""

    return legacy_prompt.strip()


def get_mode_show_citations(
    company: Mapping[str, Any],
    mode: AssistantMode | str,
) -> bool:
    resolved_mode = AssistantMode(mode)

    mode_config = _get_mode_config(
        company,
        resolved_mode,
    )

    show_citations = mode_config.get(
        "show_citations"
    )

    if isinstance(show_citations, bool):
        return show_citations

    visibility = company.get(
        "visibility",
        {},
    )

    if not isinstance(visibility, Mapping):
        return False

    legacy_visibility = visibility.get(
        resolved_mode.value,
        {},
    )

    if not isinstance(
        legacy_visibility,
        Mapping,
    ):
        return False

    return (
        legacy_visibility.get(
            "show_citations"
        )
        is True
    )