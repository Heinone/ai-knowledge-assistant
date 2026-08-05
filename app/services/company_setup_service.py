import re
import unicodedata
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any
from copy import deepcopy

from app.config.env_config import AVAILABLE_MODES
from app.models.company_setup import (
    AssistantModeSettingsUpdateRequest,
    BrandingSettingsUpdateRequest,
    CompanySettingsUpdateRequest,
    CompanySetupRequest,
    InitialAssistantSetupRequest,
)
from app.models.assistant_mode import AssistantMode
from app.services.company_config_migration_service import (
    migrate_company_config_to_v2,
)


def _get_initial_assistant_setup(
    request: CompanySetupRequest,
    mode: AssistantMode,
) -> InitialAssistantSetupRequest | None:
    if mode == AssistantMode.CUSTOMER_SUPPORT:
        return request.customer_support

    if mode == AssistantMode.INTERNAL_KNOWLEDGE:
        return request.internal_knowledge

    raise ValueError(
        f"Unsupported assistant mode: {mode.value}."
    )


def _build_fallback_message(
    *,
    base_message: str,
    email: str,
    phone: str,
    contact_name: str,
) -> str:
    normalized_email = email.strip()
    normalized_phone = phone.strip()

    if normalized_email and normalized_phone:
        return (
            f"{base_message} You can email our "
            f"{contact_name} at {normalized_email} "
            f"or call {normalized_phone}."
        )

    if normalized_email:
        return (
            f"{base_message} You can email our "
            f"{contact_name} at {normalized_email}."
        )

    if normalized_phone:
        return (
            f"{base_message} You can call our "
            f"{contact_name} at {normalized_phone}."
        )

    return base_message


def build_company_config(
    request: CompanySetupRequest,
    *,
    available_modes: tuple[
        AssistantMode,
        ...,
    ] = AVAILABLE_MODES,
) -> dict[str, Any]:
    if not available_modes:
        raise ValueError(
            "At least one assistant mode must be provisioned."
        )

    provisioned_modes = set(available_modes)

    provided_modes = {
        mode
        for mode in AssistantMode
        if _get_initial_assistant_setup(
            request,
            mode,
        )
        is not None
    }

    if provided_modes != provisioned_modes:
        missing_modes = (
            provisioned_modes - provided_modes
        )

        unavailable_modes = (
            provided_modes - provisioned_modes
        )

        problems: list[str] = []

        if missing_modes:
            problems.append(
                "Missing setup for provisioned modes: "
                + ", ".join(
                    sorted(
                        mode.value
                        for mode in missing_modes
                    )
                )
            )

        if unavailable_modes:
            problems.append(
                "Setup contains unavailable modes: "
                + ", ".join(
                    sorted(
                        mode.value
                        for mode in unavailable_modes
                    )
                )
            )

        raise ValueError(
            "; ".join(problems)
        )

    primary_mode = available_modes[0]

    primary_setup = _get_initial_assistant_setup(
        request,
        primary_mode,
    )

    if primary_setup is None:
        raise ValueError(
            "Primary assistant setup is missing."
        )

    company_id = generate_company_id(
        request.company_name
    )

    company_config: dict[str, Any] = {
        "company_id": company_id,
        "company_name": request.company_name,
        "description": "",
        "industry": request.industry,
        # Compatibility fields until schema v3 removes
        # the old global assistant representation.
        "default_mode": primary_mode.value,
        "assistant": {
            "name": primary_setup.assistant_name,
            "title": "AI Assistant",
            "default_language": "English",
            "supported_languages": [
                "English",
            ],
        },
        "conversation": {
            "tone": "professional",
            "response_length": "balanced",
            "formality_level": "professional",
            "emoji_usage": "never",
            "greeting": {
                "enabled": True,
                "message": (
                    f"Hello, I'm "
                    f"{primary_setup.assistant_name}. "
                    "How can I help you today?"
                ),
            },
        },
        "modes": {
            mode.value: {
                "enabled": (
                    mode in provisioned_modes
                ),
                "default": (
                    mode == primary_mode
                ),
            }
            for mode in AssistantMode
        },
        "branding": {
            "assets": {
                "logo": None,
                "favicon": None,
                "assistant_avatar": None,
            },
            "colors": {
                "primary": "#12343B",
                "secondary": "#F8F7F3",
                "accent": "#2EC4B6",
                "background": "#F8FAFC",
                "text": "#111827",
            },
            "fonts": {
                "heading": "Inter",
                "body": "Inter",
            },
            "ui_theme": "professional",
        },
        "customer_support": {
            "chat_headline": "Customer Service",
            "chat_description": (
                "Ask questions about our products, "
                "services, support, and policies."
            ),
            "placeholder": "Type your question...",
            "loading_message": (
                "Searching the knowledge base..."
            ),
            "allowed_topics": [
                "products",
                "services",
                "support",
                "policies",
            ],
            "support_contacts": {
                "name": "Customer Service",
                "email": "",
                "phone": "",
            },
            "opening_hours": "",
            "fallback_message": (
                "Sorry, I couldn't find enough "
                "information to answer that confidently."
            ),
        },
        "internal_knowledge": {
            "chat_headline": (
                "Internal Knowledge Assistant"
            ),
            "chat_description": (
                "Ask questions about internal "
                "company information."
            ),
            "placeholder": "Ask a question...",
            "loading_message": (
                "Searching the knowledge base..."
            ),
            "support_contacts": {
                "name": "Helpdesk",
                "email": "",
                "phone": "",
            },
            "escalation_contacts": {
                "name": "",
                "email": "",
                "phone": "",
            },
            "fallback_message": (
                "Sorry, I couldn't find enough "
                "information in the knowledge base "
                "to answer that confidently."
            ),
        },
        "prompts": {
            "customer_support": "",
            "internal_knowledge": "",
        },
        "knowledge_bases": {
            "customer_support": {
                "documents_path": (
                    "documents/customer_support"
                ),
            },
            "internal_knowledge": {
                "documents_path": (
                    "documents/internal_knowledge"
                ),
            },
        },
        "visibility": {
            "customer_support": {
                "show_citations": False,
            },
            "internal_knowledge": {
                "show_citations": True,
            },
        },
    }

    migrated = migrate_company_config_to_v2(
        company_config
    )

    for mode in available_modes:
        setup = _get_initial_assistant_setup(
            request,
            mode,
        )

        if setup is None:
            raise ValueError(
                f"Setup for '{mode.value}' is missing."
            )

        mode_config = migrated["modes"][
            mode.value
        ]

        is_internal = (
            mode
            == AssistantMode.INTERNAL_KNOWLEDGE
        )

        contact_name = (
            "helpdesk"
            if is_internal
            else "customer service"
        )

        base_fallback_message = (
            "Sorry, I couldn't find enough "
            "information in the knowledge base "
            "to answer that confidently."
            if is_internal
            else
            "Sorry, I couldn't find enough "
            "information to answer that confidently."
        )

        fallback_message = (
            _build_fallback_message(
                base_message=base_fallback_message,
                email=setup.contact_email,
                phone=setup.contact_phone,
                contact_name=contact_name,
            )
        )

        mode_config["display_name"] = (
            setup.chat_name
        )

        mode_config["assistant"] = {
            "name": setup.assistant_name,
            "title": "AI Assistant",
            "default_language": "English",
            "supported_languages": [
                "English",
            ],
        }

        mode_config["conversation"] = {
            "tone": "professional",
            "response_length": "balanced",
            "formality_level": "professional",
            "emoji_usage": "never",
            "greeting": {
                "enabled": True,
                "message": (
                    f"Hello, I'm "
                    f"{setup.assistant_name}. "
                    "How can I help you today?"
                ),
            },
        }

        chat = mode_config.setdefault(
            "chat",
            {},
        )

        chat["chat_headline"] = (
            setup.chat_name
        )

        chat["fallback_message"] = (
            fallback_message
        )

        mode_config["contacts"] = {
            "email": setup.contact_email,
            "phone": setup.contact_phone,
        }

        mode_config["fallback"] = {
            "base_message": (
                base_fallback_message
            ),
            "include_email": bool(
                setup.contact_email
            ),
            "include_phone": bool(
                setup.contact_phone
            ),
        }

        mode_config["show_citations"] = (
            is_internal
        )

        legacy_mode = migrated[
            mode.value
        ]

        legacy_mode["chat_headline"] = (
            setup.chat_name
        )

        legacy_mode["fallback_message"] = (
            fallback_message
        )

        legacy_contacts = (
            legacy_mode.setdefault(
                "support_contacts",
                {},
            )
        )

        legacy_contacts["name"] = (
            "Internal Helpdesk"
            if is_internal
            else "Customer Service"
        )

        legacy_contacts["email"] = (
            setup.contact_email
        )

        legacy_contacts["phone"] = (
            setup.contact_phone
        )

        migrated["visibility"][
            mode.value
        ]["show_citations"] = is_internal

    return migrated

def generate_company_id(company_name: str) -> str:
    normalized_name = unicodedata.normalize("NFKD", company_name)

    ascii_name = normalized_name.encode(
        "ascii",
        "ignore",
    ).decode("ascii")

    company_id = re.sub(
        r"[^a-zA-Z0-9]+",
        "_",
        ascii_name,
    )

    company_id = company_id.strip("_").lower()

    if not company_id:
        raise ValueError(
            "Company name could not be converted into a valid company ID."
        )

    return company_id

def apply_company_settings_update(
    existing_config: dict[str, Any],
    request: CompanySettingsUpdateRequest,
) -> dict[str, Any]:
    updated_config = migrate_company_config_to_v2(
    existing_config
)

    old_assistant_name = (
        updated_config.get("assistant", {}).get("name", "")
    )

    selected_mode = AssistantMode(
    request.assistant.mode
)

    if selected_mode not in AVAILABLE_MODES:
        raise ValueError(
        f"Assistant mode "
        f"'{selected_mode.value}' is not available "
        "for this deployment."
)

    selected_mode_key = selected_mode.value

    updated_config["company_name"] = request.company_name
    updated_config["industry"] = request.industry
    updated_config["description"] = request.company_details.description

    assistant = updated_config.setdefault("assistant", {})

    assistant["name"] = request.assistant.name
    assistant["title"] = request.assistant.title
    assistant["default_language"] = (
        request.assistant.default_language
    )
    assistant["supported_languages"] = (
        request.assistant.supported_languages
    )

    modes = updated_config.setdefault("modes", {})

    conversation = updated_config.setdefault(
        "conversation",
        {},
    )

    conversation["tone"] = request.conversation.tone
    conversation["response_length"] = (
        request.conversation.response_length
    )

    greeting = conversation.get("greeting")

    if isinstance(greeting, dict):
        old_default_greeting = (
            f"Hello, I'm {old_assistant_name}. "
            "How can I help you today?"
        )

        if greeting.get("message") == old_default_greeting:
            greeting["message"] = (
                f"Hello, I'm {request.assistant.name}. "
                "How can I help you today?"
            )

    selected_mode_config = modes.setdefault(
    selected_mode_key,
    {},
)

    selected_mode_config["assistant"] = deepcopy(
        assistant
    )

    selected_mode_config["conversation"] = deepcopy(
        conversation
    )

    # Global compatibility fields must always represent
    # the configured default mode.
    default_mode = updated_config.get(
        "default_mode"
    )

    if default_mode != selected_mode_key:
        default_mode_config = modes.get(
            default_mode,
            {},
        )

        default_assistant = default_mode_config.get(
            "assistant",
        )

        default_conversation = default_mode_config.get(
            "conversation",
        )

        if isinstance(default_assistant, dict):
            updated_config["assistant"] = deepcopy(
                default_assistant
            )

        if isinstance(default_conversation, dict):
            updated_config["conversation"] = deepcopy(
                default_conversation
            )

    return updated_config

def apply_assistant_mode_settings_update(
    existing_config: dict[str, Any],
    *,
    mode: AssistantMode,
    request: AssistantModeSettingsUpdateRequest,
    available_modes: tuple[
        AssistantMode,
        ...,
    ] = AVAILABLE_MODES,
) -> dict[str, Any]:

    if mode not in available_modes:
        raise ValueError(
            f"Assistant mode '{mode.value}' is not "
            "available for this deployment."
        )

    updated_config = migrate_company_config_to_v2(
        existing_config
    )

    modes = updated_config.setdefault(
        "modes",
        {},
    )

    mode_config = modes.setdefault(
        mode.value,
        {},
    )

    mode_config["display_name"] = (
        request.display_name
    )

    assistant = mode_config.setdefault(
        "assistant",
        {},
    )

    assistant.update(
        request.assistant.model_dump()
    )

    conversation = mode_config.setdefault(
        "conversation",
        {},
    )

    conversation.update(
        request.conversation.model_dump()
    )

    chat = mode_config.setdefault(
        "chat",
        {},
    )

    chat.update(
        request.chat.model_dump()
    )

    mode_config["prompt_guide"] = (
        request.prompt_guide
    )

    mode_config["show_citations"] = (
        request.show_citations
    )

    # Keep legacy mode-specific fields synchronized until
    # the current frontend has been migrated to schema v2.
    legacy_chat = updated_config.setdefault(
        mode.value,
        {},
    )

    legacy_chat.update(
        request.chat.model_dump()
    )

    prompts = updated_config.setdefault(
        "prompts",
        {},
    )

    prompts[mode.value] = request.prompt_guide

    visibility = updated_config.setdefault(
        "visibility",
        {},
    )

    mode_visibility = visibility.setdefault(
        mode.value,
        {},
    )

    mode_visibility["show_citations"] = (
        request.show_citations
    )

    # Global assistant/conversation fields are temporary
    # compatibility fields representing the default mode.
    if updated_config.get("default_mode") == mode.value:
        updated_config["assistant"] = deepcopy(
            assistant
        )

        updated_config["conversation"] = deepcopy(
            conversation
        )

    return updated_config

def apply_company_branding_update(
    existing_config: dict[str, Any],
    request: BrandingSettingsUpdateRequest,
) -> dict[str, Any]:
    updated_config = deepcopy(existing_config)

    branding = updated_config.setdefault("branding", {})
    branding.setdefault(
        "assets",
        {
            "logo": None,
            "favicon": None,
            "assistant_avatar": None,
        },
    )

    branding["colors"] = request.colors.model_dump()

    return updated_config

def save_company_config(
    company_config: dict[str, Any],
    config_path: Path,
) -> None:
    config_directory = config_path.parent.resolve()
    config_directory.mkdir(parents=True, exist_ok=True)

    resolved_config_path = config_path.resolve()

    if not resolved_config_path.is_relative_to(config_directory):
        raise ValueError("Invalid company configuration path.")

    temporary_path: Path | None = None

    try:
        with NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=config_directory,
            prefix=".company.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)

            json.dump(
                company_config,
                temporary_file,
                indent=2,
                ensure_ascii=False,
            )

            temporary_file.write("\n")
            temporary_file.flush()
            os.fsync(temporary_file.fileno())

        os.replace(
            temporary_path,
            resolved_config_path,
        )
    finally:
        if temporary_path and temporary_path.exists():
            temporary_path.unlink()
