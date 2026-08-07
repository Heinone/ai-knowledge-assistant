import unittest

from app.models.assistant_mode import (
    AssistantMode,
)
from app.models.company_setup import (
    AssistantModeFallbackSettingsUpdateRequest,
)
from app.services.company_config_migration_service import (
    migrate_company_config_to_v2,
)
from app.services.company_setup_service import (
    apply_assistant_mode_fallback_settings_update,
)


class AssistantModeFallbackSettingsTests(
    unittest.TestCase
):
    CUSTOMER_SUPPORT_ONLY = (
        AssistantMode.CUSTOMER_SUPPORT,
    )

    def build_config(self) -> dict:
        return migrate_company_config_to_v2(
            {
                "company_id": "company-1",
                "company_name": "Example Company",
                "default_mode": "customer_support",
                "assistant": {
                    "name": "Alex",
                    "title": "AI Assistant",
                    "default_language": "English",
                    "supported_languages": [
                        "English",
                    ],
                },
                "conversation": {
                    "tone": "professional",
                    "response_length": "balanced",
                    "greeting": {
                        "enabled": True,
                        "message": "Hello",
                    },
                },
                "modes": {
                    "customer_support": {
                        "enabled": True,
                        "default": True,
                    },
                    "internal_knowledge": {
                        "enabled": False,
                        "default": False,
                    },
                },
                "customer_support": {
                    "chat_headline": "Support",
                    "chat_description": "Ask for help.",
                    "placeholder": "Ask a question",
                    "loading_message": "Searching",
                    "fallback_message": "No answer.",
                },
                "internal_knowledge": {
                    "chat_headline": "Internal",
                    "chat_description": "Ask internally.",
                    "placeholder": "Ask a question",
                    "loading_message": "Searching",
                    "fallback_message": (
                        "No internal answer."
                    ),
                },
                "prompts": {
                    "customer_support": "",
                    "internal_knowledge": "",
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
        )

    def build_request(
        self,
        *,
        email: str = "support@example.com",
        phone: str = "+358 40 123 4567",
        include_email: bool = True,
        include_phone: bool = False,
    ) -> (
        AssistantModeFallbackSettingsUpdateRequest
    ):
        return (
            AssistantModeFallbackSettingsUpdateRequest(
                contacts={
                    "email": email,
                    "phone": phone,
                },
                fallback={
                    "base_message": (
                        "I could not find enough "
                        "information."
                    ),
                    "include_email": include_email,
                    "include_phone": include_phone,
                },
            )
        )

    def test_builds_customer_support_fallback(
        self,
    ):
        updated = (
            apply_assistant_mode_fallback_settings_update(
                self.build_config(),
                mode=(
                    AssistantMode.CUSTOMER_SUPPORT
                ),
                request=self.build_request(),
                available_modes=(
                    self.CUSTOMER_SUPPORT_ONLY
                ),
            )
        )

        support = updated["modes"][
            "customer_support"
        ]

        self.assertEqual(
            support["contacts"]["email"],
            "support@example.com",
        )

        self.assertEqual(
            support["chat"]["fallback_message"],
            (
                "I could not find enough information. "
                "You can email our customer service "
                "at support@example.com."
            ),
        )

        self.assertEqual(
            updated["customer_support"][
                "support_contacts"
            ]["email"],
            "support@example.com",
        )

    def test_rejects_enabled_email_without_address(
        self,
    ):
        with self.assertRaisesRegex(
            ValueError,
            "Contact email is required",
        ):
            apply_assistant_mode_fallback_settings_update(
                self.build_config(),
                mode=(
                    AssistantMode.CUSTOMER_SUPPORT
                ),
                request=self.build_request(
                    email="",
                    include_email=True,
                ),
                available_modes=(
                    self.CUSTOMER_SUPPORT_ONLY
                ),
            )

    def test_rejects_unavailable_mode(self):
        with self.assertRaisesRegex(
            ValueError,
            "not available",
        ):
            apply_assistant_mode_fallback_settings_update(
                self.build_config(),
                mode=(
                    AssistantMode.INTERNAL_KNOWLEDGE
                ),
                request=self.build_request(),
                available_modes=(
                    self.CUSTOMER_SUPPORT_ONLY
                ),
            )


if __name__ == "__main__":
    unittest.main()