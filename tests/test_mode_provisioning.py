import unittest

from app.config.company_config import (
    resolve_assistant_mode,
)
from app.config.config_validator import (
    validate_company_config,
)
from app.models.assistant_mode import AssistantMode
from app.models.company_setup import (
    CompanySetupRequest,
)
from app.services.company_setup_service import (
    build_company_config,
)


class ModeProvisioningTests(unittest.TestCase):
    def build_setup_request(
    self,
    ) -> CompanySetupRequest:
        return CompanySetupRequest(
            company_name="Example Company",
            industry="Retail",
            customer_support={
                "assistant_name": "Alex",
                "chat_name": "Customer Service",
                "contact_email": (
                    "support@example.com"
                ),
                "contact_phone": "",
            },
        )

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
                },
                "internal_knowledge": {
                    "enabled": (
                        internal_knowledge_enabled
                    ),
                },
            },
        }

    def test_setup_uses_provisioned_modes(
        self,
    ):
        company = build_company_config(
            self.build_setup_request(),
            available_modes=(
                AssistantMode.CUSTOMER_SUPPORT,
            ),
        )

        self.assertTrue(
            company["modes"][
                "customer_support"
            ]["enabled"]
        )

        self.assertFalse(
            company["modes"][
                "internal_knowledge"
            ]["enabled"]
        )

    def test_setup_rejects_missing_provisioned_mode(
    self,
    ):
        with self.assertRaisesRegex(
            ValueError,
            "Missing setup",
        ):
            build_company_config(
                CompanySetupRequest(
                    company_name="Example Company",
                    industry="Technology",
                    customer_support={
                        "assistant_name": "Alex",
                        "chat_name": "Customer Service",
                    },
                ),
                available_modes=(
                    AssistantMode.CUSTOMER_SUPPORT,
                    AssistantMode.INTERNAL_KNOWLEDGE,
                ),
            )


    def test_setup_builds_contact_fallback(
        self,
    ):
        company = build_company_config(
            self.build_setup_request(),
            available_modes=(
                AssistantMode.CUSTOMER_SUPPORT,
            ),
        )

        fallback = company["modes"][
            "customer_support"
        ]["chat"]["fallback_message"]

        self.assertIn(
            "support@example.com",
            fallback,
        )

    def test_single_mode_can_be_omitted(self):
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

    def test_dual_mode_accepts_explicit_mode(
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

    def test_rejects_unprovisioned_mode(
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

    def test_validator_rejects_mode_mismatch(
        self,
    ):
        company = {
            "company_id": "company-1",
            "company_name": "Example",
            "assistant": {
                "name": "Alex",
                "title": "AI Assistant",
            },
            "modes": {
                "customer_support": {
                    "enabled": False,
                    "default": False,
                },
                "internal_knowledge": {
                    "enabled": True,
                    "default": True,
                },
            },
        }

        errors = validate_company_config(
            company,
            available_modes=(
                AssistantMode.CUSTOMER_SUPPORT,
            ),
        )

        self.assertTrue(
            any(
                "must be enabled" in error
                for error in errors
            )
        )

        self.assertTrue(
            any(
                "unavailable" in error
                for error in errors
            )
        )


if __name__ == "__main__":
    unittest.main()