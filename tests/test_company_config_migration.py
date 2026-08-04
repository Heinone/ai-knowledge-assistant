import unittest

from app.services.company_config_migration_service import (
    migrate_company_config_to_v2,
)


class CompanyConfigMigrationTests(unittest.TestCase):
    def build_legacy_config(self) -> dict:
        return {
            "company_id": "company-1",
            "company_name": "Example Company",
            "default_mode": "customer_support",
            "assistant": {
                "name": "Alex",
                "title": "AI Assistant",
                "default_language": "English",
                "supported_languages": ["English"],
            },
            "conversation": {
                "tone": "professional",
                "response_length": "concise",
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
                "chat_headline": "Customer Support",
                "fallback_message": "No answer found.",
            },
            "internal_knowledge": {
                "chat_headline": "Intranet Assistant",
                "fallback_message": "No internal answer found.",
            },
            "prompts": {
                "customer_support": "Use customer terminology.",
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

    def test_migrates_legacy_mode_settings(self):
        migrated = migrate_company_config_to_v2(
            self.build_legacy_config()
        )

        support = migrated["modes"]["customer_support"]
        internal = migrated["modes"]["internal_knowledge"]

        self.assertEqual(
            migrated["schema_version"],
            2,
        )

        self.assertEqual(
            support["display_name"],
            "Customer Support",
        )

        self.assertEqual(
            support["assistant"]["name"],
            "Alex",
        )

        self.assertEqual(
            support["conversation"]["tone"],
            "professional",
        )

        self.assertEqual(
            support["chat"]["fallback_message"],
            "No answer found.",
        )

        self.assertEqual(
            support["prompt_guide"],
            "Use customer terminology.",
        )

        self.assertFalse(
            support["show_citations"]
        )

        self.assertTrue(
            internal["show_citations"]
        )

    def test_preserves_existing_mode_specific_values(self):
        company = self.build_legacy_config()

        company["modes"]["customer_support"].update(
            {
                "display_name": "Help Centre",
                "assistant": {
                    "name": "Maya",
                },
                "conversation": {
                    "tone": "friendly",
                },
            }
        )

        migrated = migrate_company_config_to_v2(
            company
        )

        support = migrated["modes"]["customer_support"]

        self.assertEqual(
            support["display_name"],
            "Help Centre",
        )

        self.assertEqual(
            support["assistant"]["name"],
            "Maya",
        )

        self.assertEqual(
            support["assistant"]["title"],
            "AI Assistant",
        )

        self.assertEqual(
            support["conversation"]["tone"],
            "friendly",
        )

    def test_migration_is_idempotent(self):
        first = migrate_company_config_to_v2(
            self.build_legacy_config()
        )

        second = migrate_company_config_to_v2(
            first
        )

        self.assertEqual(
            first,
            second,
        )


if __name__ == "__main__":
    unittest.main()