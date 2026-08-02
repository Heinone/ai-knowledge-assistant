import re
import unicodedata
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from app.models.company_setup import CompanySetupRequest


def build_company_config(
    request: CompanySetupRequest,
) -> dict[str, Any]:
    company_id = generate_company_id(request.company_name)
    selected_mode = request.assistant.mode

    return {
        "company_id": company_id,
        "company_name": request.company_name,
        "description": request.company_details.description,
        "industry": request.industry,
        "default_mode": selected_mode,
        "assistant": {
            "name": request.assistant.name,
            "title": request.assistant.title,
            "default_language": request.assistant.default_language,
            "supported_languages": request.assistant.supported_languages,
        },
        "modes": {
            "customer_support": {
                "enabled": selected_mode == "customer_support",
                "default": selected_mode == "customer_support",
            },
            "internal_knowledge": {
                "enabled": selected_mode == "internal_knowledge",
                "default": selected_mode == "internal_knowledge",
            },
        },
        "branding": {
            "assets": {
                "logo": None,
                "favicon": None,
                "assistant_avatar": None,
            },
            "colors": request.branding.colors.model_dump(),
            "fonts": {
                "heading": "Inter",
                "body": "Inter",
            },
            "ui_theme": "professional",
        },
        "conversation": {
            "tone": request.conversation.tone,
            "response_length": request.conversation.response_length,
            "formality_level": "professional",
            "emoji_usage": "never",
            "greeting": {
                "enabled": True,
                "message": (
                    f"Hello, I'm {request.assistant.name}. "
                    "How can I help you today?"
                ),
            },
        },
        "customer_support": {
            "chat_headline": "Customer Support",
            "chat_description": (
                "Ask questions about our products, services, "
                "support, and policies."
            ),
            "placeholder": "Type your question...",
            "loading_message": "Searching the knowledge base...",
            "allowed_topics": [
                "products",
                "services",
                "support",
                "policies",
            ],
            "support_contacts": {
                "name": "Customer Support Team",
                "email": "",
                "phone": "",
            },
            "opening_hours": "",
            "fallback_message": (
                "I could not find enough information to answer "
                "that confidently."
            ),
        },
        "internal_knowledge": {
            "chat_headline": "Internal Knowledge Assistant",
            "chat_description": (
                "Ask questions about internal company information."
            ),
            "placeholder": "Ask a question...",
            "loading_message": "Searching the knowledge base...",
            "support_contacts": {
                "name": "Internal Helpdesk",
                "email": "",
                "phone": "",
            },
            "escalation_contacts": {
                "name": "",
                "email": "",
                "phone": "",
            },
            "fallback_message": (
                "I could not find enough information in the "
                "knowledge base to answer this confidently."
            ),
        },
        "prompts": {
            "customer_support": "",
            "internal_knowledge": "",
        },
        "knowledge_bases": {
            "customer_support": {
                "documents_path": "documents/customer_support",
            },
            "internal_knowledge": {
                "documents_path": "documents/internal_knowledge",
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