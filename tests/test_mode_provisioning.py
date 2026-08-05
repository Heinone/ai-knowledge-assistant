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
            assistant={
                "name": "Alex",
                "title": "AI Assistant",
                # Deliberately conflicts with the
                # provisioned mode.
                "mode": "internal_knowledge",
                "default_language": "English",
                "supported_languages": [
                    "English",
                ],
            },
            conversation={
                "tone": "professional",
                "response_length": "concise",
            },
            company_details={
                "description": "",
            },
            branding={
                "colors": {
                    "primary": "#12343B",
                    "secondary": "#F8F7F3",
                    "accent": "#2EC4B6",
                    "background": "#F8FAFC",
                    "text": "#111827",
                },
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