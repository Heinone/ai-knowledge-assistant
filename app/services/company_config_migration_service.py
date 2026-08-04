from copy import deepcopy
from typing import Any

from app.models.assistant_mode import AssistantMode


CURRENT_COMPANY_CONFIG_SCHEMA_VERSION = 2

DEFAULT_DISPLAY_NAMES = {
    AssistantMode.CUSTOMER_SUPPORT: "Customer Service Chat",
    AssistantMode.INTERNAL_KNOWLEDGE: "Internal Knowledge Assistant",
}


def _copy_missing_values(
    target: dict[str, Any],
    defaults: dict[str, Any],
) -> None:
    for key, value in defaults.items():
        target.setdefault(
            key,
            deepcopy(value),
        )


def migrate_company_config_to_v2(
    company: dict[str, Any],
) -> dict[str, Any]:
    migrated = deepcopy(company)

    modes = migrated.setdefault("modes", {})

    shared_assistant = migrated.get("assistant", {})
    shared_conversation = migrated.get("conversation", {})
    legacy_prompts = migrated.get("prompts", {})
    legacy_visibility = migrated.get("visibility", {})

    if not isinstance(shared_assistant, dict):
        shared_assistant = {}

    if not isinstance(shared_conversation, dict):
        shared_conversation = {}

    if not isinstance(legacy_prompts, dict):
        legacy_prompts = {}

    if not isinstance(legacy_visibility, dict):
        legacy_visibility = {}

    for mode in AssistantMode:
        mode_name = mode.value

        mode_config = modes.setdefault(
            mode_name,
            {},
        )

        legacy_chat = migrated.get(mode_name, {})

        if not isinstance(legacy_chat, dict):
            legacy_chat = {}

        display_name = (
            legacy_chat.get("chat_headline")
            or DEFAULT_DISPLAY_NAMES[mode]
        )

        mode_config.setdefault(
            "display_name",
            display_name,
        )

        mode_assistant = mode_config.setdefault(
            "assistant",
            {},
        )

        mode_conversation = mode_config.setdefault(
            "conversation",
            {},
        )

        mode_chat = mode_config.setdefault(
            "chat",
            {},
        )

        if not isinstance(mode_assistant, dict):
            mode_assistant = {}
            mode_config["assistant"] = mode_assistant

        if not isinstance(mode_conversation, dict):
            mode_conversation = {}
            mode_config["conversation"] = mode_conversation

        if not isinstance(mode_chat, dict):
            mode_chat = {}
            mode_config["chat"] = mode_chat

        _copy_missing_values(
            mode_assistant,
            shared_assistant,
        )

        _copy_missing_values(
            mode_conversation,
            shared_conversation,
        )

        _copy_missing_values(
            mode_chat,
            legacy_chat,
        )

        prompt_guide = legacy_prompts.get(
            mode_name,
            "",
        )

        mode_config.setdefault(
            "prompt_guide",
            prompt_guide if isinstance(prompt_guide, str) else "",
        )

        mode_visibility = legacy_visibility.get(
            mode_name,
            {},
        )

        show_citations = (
            mode_visibility.get("show_citations", False)
            if isinstance(mode_visibility, dict)
            else False
        )

        mode_config.setdefault(
            "show_citations",
            bool(show_citations),
        )

    migrated["schema_version"] = (
        CURRENT_COMPANY_CONFIG_SCHEMA_VERSION
    )

    return migrated