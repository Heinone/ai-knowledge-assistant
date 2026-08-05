import unittest

from app.config.company_config import (
    get_enabled_assistant_modes,
    resolve_assistant_mode,
)
from app.models.assistant_mode import AssistantMode


class AssistantModeResolverTests(
    unittest.TestCase
):
    def build_company(
        self,
        *,
        customer_support_enabled: bool,
        internal_knowledge_enabled: bool,
    ) -> dict:
        return {
            "modes": {
                "customer_support": {
                    "enabled": (
                        customer_support_enabled
                    ),
                    "default": False,
                },
                "internal_knowledge": {
                    "enabled": (
                        internal_knowledge_enabled
                    ),
                    "default": False,
                },
            },
        }

    def test_returns_enabled_modes(self):
        company = self.build_company(
            customer_support_enabled=True,
            internal_knowledge_enabled=False,
        )

        result = get_enabled_assistant_modes(
            company
        )

        self.assertEqual(
            result,
            (
                AssistantMode.CUSTOMER_SUPPORT,
            ),
        )

    def test_single_provisioned_mode_can_be_omitted(
        self,
    ):
        company = self.build_company(
            customer_support_enabled=True,
            internal_knowledge_enabled=False,
        )

        result = resolve_assistant_mode(
            company=company,
            available_modes=(
                AssistantMode.CUSTOMER_SUPPORT,
            ),
        )

        self.assertEqual(
            result,
            AssistantMode.CUSTOMER_SUPPORT,
        )

    def test_dual_mode_requires_explicit_mode(
        self,
    ):
        company = self.build_company(
            customer_support_enabled=True,
            internal_knowledge_enabled=True,
        )

        with self.assertRaisesRegex(
            ValueError,
            "required",
        ):
            resolve_assistant_mode(
                company=company,
                available_modes=(
                    AssistantMode.CUSTOMER_SUPPORT,
                    AssistantMode.INTERNAL_KNOWLEDGE,
                ),
            )

    def test_uses_requested_provisioned_mode(
        self,
    ):
        company = self.build_company(
            customer_support_enabled=True,
            internal_knowledge_enabled=True,
        )

        result = resolve_assistant_mode(
            AssistantMode.INTERNAL_KNOWLEDGE,
            company=company,
            available_modes=(
                AssistantMode.CUSTOMER_SUPPORT,
                AssistantMode.INTERNAL_KNOWLEDGE,
            ),
        )

        self.assertEqual(
            result,
            AssistantMode.INTERNAL_KNOWLEDGE,
        )

    def test_rejects_unavailable_requested_mode(
        self,
    ):
        company = self.build_company(
            customer_support_enabled=True,
            internal_knowledge_enabled=False,
        )

        with self.assertRaisesRegex(
            ValueError,
            "not available",
        ):
            resolve_assistant_mode(
                AssistantMode.INTERNAL_KNOWLEDGE,
                company=company,
                available_modes=(
                    AssistantMode.CUSTOMER_SUPPORT,
                ),
            )

    def test_rejects_unknown_requested_mode(
        self,
    ):
        company = self.build_company(
            customer_support_enabled=True,
            internal_knowledge_enabled=False,
        )

        with self.assertRaisesRegex(
            ValueError,
            "Unsupported assistant mode",
        ):
            resolve_assistant_mode(
                "unknown_mode",
                company=company,
                available_modes=(
                    AssistantMode.CUSTOMER_SUPPORT,
                ),
            )

    def test_rejects_company_and_deployment_mismatch(
        self,
    ):
        company = self.build_company(
            customer_support_enabled=False,
            internal_knowledge_enabled=True,
        )

        with self.assertRaisesRegex(
            ValueError,
            "do not match",
        ):
            resolve_assistant_mode(
                company=company,
                available_modes=(
                    AssistantMode.CUSTOMER_SUPPORT,
                ),
            )


if __name__ == "__main__":
    unittest.main()