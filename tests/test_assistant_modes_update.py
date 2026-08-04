import unittest

from pydantic import ValidationError

from app.models.company_setup import (
    AssistantModesUpdateRequest,
)
from app.services.company_config_migration_service import (
    migrate_company_config_to_v2,
)
from app.services.company_setup_service import (
    apply_assistant_modes_update,
)


class AssistantModesUpdateTests(unittest.TestCase):
    def build_config(self) -> dict:
        return migrate_company_config_to_v2(
            {
                "company_id": "company-1",
                "company_name": "Example Company",
                "default_mode": "customer_support",
                "assistant": {
                    "name": "Alex",
                    "title": "Customer Assistant",
                    "default_language": "English",
                    "supported_languages": [
                        "English",
                    ],
                },
                "conversation": {
                    "tone": "friendly",
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
                        "assistant": {
                            "name": "Alex",
                            "title": "Customer Assistant",
                            "default_language": "English",
                            "supported_languages": [
                                "English",
                            ],
                        },
                    },
                    "internal_knowledge": {
                        "enabled": False,
                        "default": False,
                        "assistant": {
                            "name": "Atlas",
                            "title": "Internal Assistant",
                            "default_language": "English",
                            "supported_languages": [
                                "English",
                            ],
                        },
                        "conversation": {
                            "tone": "professional",
                            "response_length": "detailed",
                            "greeting": {
                                "enabled": True,
                                "message": "How can I help?",
                            },
                        },
                    },
                },
                "customer_support": {},
                "internal_knowledge": {},
                "prompts": {},
                "visibility": {},
            }
        )

    def test_enables_both_modes(self):
        request = AssistantModesUpdateRequest(
            enabled_modes=[
                "customer_support",
                "internal_knowledge",
            ],
            default_mode="customer_support",
        )

        updated = apply_assistant_modes_update(
            self.build_config(),
            request,
        )

        self.assertTrue(
            updated["modes"]["customer_support"][
                "enabled"
            ]
        )

        self.assertTrue(
            updated["modes"]["internal_knowledge"][
                "enabled"
            ]
        )

        self.assertTrue(
            updated["modes"]["customer_support"][
                "default"
            ]
        )

        self.assertFalse(
            updated["modes"]["internal_knowledge"][
                "default"
            ]
        )

    def test_switches_default_and_global_compatibility_fields(
        self,
    ):
        request = AssistantModesUpdateRequest(
            enabled_modes=[
                "customer_support",
                "internal_knowledge",
            ],
            default_mode="internal_knowledge",
        )

        updated = apply_assistant_modes_update(
            self.build_config(),
            request,
        )

        self.assertEqual(
            updated["default_mode"],
            "internal_knowledge",
        )

        self.assertEqual(
            updated["assistant"]["name"],
            "Atlas",
        )

        self.assertEqual(
            updated["conversation"]["tone"],
            "professional",
        )

    def test_rejects_disabled_default_mode(self):
        with self.assertRaises(ValidationError):
            AssistantModesUpdateRequest(
                enabled_modes=[
                    "customer_support",
                ],
                default_mode="internal_knowledge",
            )

    def test_rejects_duplicate_modes(self):
        with self.assertRaises(ValidationError):
            AssistantModesUpdateRequest(
                enabled_modes=[
                    "customer_support",
                    "customer_support",
                ],
                default_mode="customer_support",
            )


if __name__ == "__main__":
    unittest.main()