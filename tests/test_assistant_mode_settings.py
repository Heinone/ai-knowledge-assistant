import unittest
from copy import deepcopy

from app.models.assistant_mode import AssistantMode
from app.models.company_setup import (
    AssistantModeSettingsUpdateRequest,
)
from app.services.company_config_migration_service import (
    migrate_company_config_to_v2,
)
from app.services.company_setup_service import (
    apply_assistant_mode_settings_update,
)


class AssistantModeSettingsTests(unittest.TestCase):
    def build_config(self) -> dict:
        return migrate_company_config_to_v2(
            {
                "company_id": "company-1",
                "company_name": "Example Company",
                "default_mode": "customer_support",
                "assistant": {
                    "name": "Alex",
                    "title": "Assistant",
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
                    "fallback_message": "No answer",
                    "allowed_topics": ["products"],
                },
                "internal_knowledge": {
                    "chat_headline": "Internal",
                    "chat_description": "Ask internally.",
                    "placeholder": "Ask a question",
                    "loading_message": "Searching",
                    "fallback_message": "No answer",
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
        name: str,
    ) -> AssistantModeSettingsUpdateRequest:
        return (
            AssistantModeSettingsUpdateRequest(
                display_name="Help Centre",
                assistant={
                    "name": name,
                    "title": "Customer Assistant",
                    "default_language": "English",
                    "supported_languages": [
                        "English",
                        "Finnish",
                    ],
                },
                conversation={
                    "tone": "friendly",
                    "response_length": "concise",
                    "greeting": {
                        "enabled": True,
                        "message": "How can I help?",
                    },
                },
                chat={
                    "chat_headline": "Customer Support",
                    "chat_description": (
                        "Ask about products and policies."
                    ),
                    "placeholder": "Type your question",
                    "loading_message": (
                        "Searching the knowledge base"
                    ),
                    "fallback_message": (
                        "I could not find that information."
                    ),
                },
                prompt_guide="Use product terminology.",
                show_citations=False,
            )
        )

    def test_updates_only_selected_mode(self):
        company = self.build_config()

        internal_before = deepcopy(
            company["modes"]["internal_knowledge"]
        )

        updated = (
            apply_assistant_mode_settings_update(
                company,
                mode=AssistantMode.CUSTOMER_SUPPORT,
                request=self.build_request("Maya"),
            )
        )

        support = updated["modes"][
            "customer_support"
        ]

        self.assertEqual(
            support["assistant"]["name"],
            "Maya",
        )

        self.assertTrue(support["enabled"])
        self.assertTrue(support["default"])

        self.assertEqual(
            updated["modes"]["internal_knowledge"],
            internal_before,
        )

        self.assertEqual(
            support["chat"]["allowed_topics"],
            ["products"],
        )

    def test_syncs_global_fields_for_default_mode(self):
        company = self.build_config()

        updated = (
            apply_assistant_mode_settings_update(
                company,
                mode=AssistantMode.CUSTOMER_SUPPORT,
                request=self.build_request("Maya"),
            )
        )

        self.assertEqual(
            updated["assistant"]["name"],
            "Maya",
        )

        self.assertEqual(
            updated["conversation"]["tone"],
            "friendly",
        )

    def test_does_not_replace_global_fields_for_non_default_mode(
        self,
    ):
        company = self.build_config()

        request = self.build_request("Atlas")

        updated = (
            apply_assistant_mode_settings_update(
                company,
                mode=AssistantMode.INTERNAL_KNOWLEDGE,
                request=request,
                available_modes=(
                    AssistantMode.CUSTOMER_SUPPORT,
                    AssistantMode.INTERNAL_KNOWLEDGE,
                ),
            )
        )

        self.assertEqual(
            updated["assistant"]["name"],
            "Alex",
        )

        self.assertEqual(
            updated["modes"]["internal_knowledge"][
                "assistant"
            ]["name"],
            "Atlas",
        )


if __name__ == "__main__":
    unittest.main()