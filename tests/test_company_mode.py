import unittest

from app.config.company_config import (
    get_enabled_assistant_modes,
    resolve_assistant_mode,
)
from app.models.assistant_mode import AssistantMode


class AssistantModeResolverTests(unittest.TestCase):
    def build_company(
        self,
        *,
        customer_support_enabled: bool = True,
        internal_knowledge_enabled: bool = False,
        default_mode: str | None = "customer_support",
    ) -> dict:
        return {
            "default_mode": default_mode,
            "modes": {
                "customer_support": {
                    "enabled": customer_support_enabled,
                    "default": default_mode == "customer_support",
                },
                "internal_knowledge": {
                    "enabled": internal_knowledge_enabled,
                    "default": default_mode == "internal_knowledge",
                },
            },
        }

    def test_returns_enabled_modes(self):
        company = self.build_company(
            customer_support_enabled=True,
            internal_knowledge_enabled=True,
        )

        result = get_enabled_assistant_modes(company)

        self.assertEqual(
            result,
            (
                AssistantMode.CUSTOMER_SUPPORT,
                AssistantMode.INTERNAL_KNOWLEDGE,
            ),
        )

    def test_uses_requested_enabled_mode(self):
        company = self.build_company(
            customer_support_enabled=True,
            internal_knowledge_enabled=True,
        )

        result = resolve_assistant_mode(
            "internal_knowledge",
            company=company,
        )

        self.assertEqual(
            result,
            AssistantMode.INTERNAL_KNOWLEDGE,
        )

    def test_rejects_disabled_requested_mode(self):
        company = self.build_company(
            internal_knowledge_enabled=False,
        )

        with self.assertRaisesRegex(
            ValueError,
            "is not enabled",
        ):
            resolve_assistant_mode(
                "internal_knowledge",
                company=company,
            )

    def test_rejects_unknown_requested_mode(self):
        company = self.build_company()

        with self.assertRaisesRegex(
            ValueError,
            "Unsupported assistant mode",
        ):
            resolve_assistant_mode(
                "unknown_mode",
                company=company,
            )

    def test_uses_configured_default_mode(self):
        company = self.build_company(
            customer_support_enabled=True,
            internal_knowledge_enabled=True,
            default_mode="internal_knowledge",
        )

        result = resolve_assistant_mode(company=company)

        self.assertEqual(
            result,
            AssistantMode.INTERNAL_KNOWLEDGE,
        )

    def test_falls_back_to_enabled_mode(self):
        company = self.build_company(
            customer_support_enabled=False,
            internal_knowledge_enabled=True,
            default_mode=None,
        )

        result = resolve_assistant_mode(company=company)

        self.assertEqual(
            result,
            AssistantMode.INTERNAL_KNOWLEDGE,
        )

    def test_rejects_configuration_without_enabled_modes(self):
        company = self.build_company(
            customer_support_enabled=False,
            internal_knowledge_enabled=False,
            default_mode=None,
        )

        with self.assertRaisesRegex(
            ValueError,
            "At least one assistant mode must be enabled",
        ):
            resolve_assistant_mode(company=company)


if __name__ == "__main__":
    unittest.main()