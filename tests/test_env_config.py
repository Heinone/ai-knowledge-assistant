import unittest

from app.config.env_config import (
    EnvironmentConfigurationError,
    _parse_available_modes,
    _parse_vector_store,
)
from app.models.assistant_mode import AssistantMode


class EnvironmentConfigurationTests(
    unittest.TestCase
):
    def test_parses_single_available_mode(self):
        result = _parse_available_modes(
            "customer_support"
        )

        self.assertEqual(
            result,
            (
                AssistantMode.CUSTOMER_SUPPORT,
            ),
        )

    def test_parses_both_modes_in_configured_order(self):
        result = _parse_available_modes(
            "customer_support,internal_knowledge"
        )

        self.assertEqual(
            result,
            (
                AssistantMode.CUSTOMER_SUPPORT,
                AssistantMode.INTERNAL_KNOWLEDGE,
            ),
        )

    def test_rejects_missing_available_modes(self):
        with self.assertRaisesRegex(
            EnvironmentConfigurationError,
            "at least one",
        ):
            _parse_available_modes(None)

    def test_rejects_empty_available_mode_entry(self):
        with self.assertRaisesRegex(
            EnvironmentConfigurationError,
            "empty value",
        ):
            _parse_available_modes(
                "customer_support,"
            )

    def test_rejects_duplicate_available_modes(self):
        with self.assertRaisesRegex(
            EnvironmentConfigurationError,
            "duplicate",
        ):
            _parse_available_modes(
                "customer_support,customer_support"
            )

    def test_rejects_unknown_available_mode(self):
        with self.assertRaisesRegex(
            EnvironmentConfigurationError,
            "Unsupported assistant mode",
        ):
            _parse_available_modes(
                "sales_assistant"
            )

    def test_defaults_vector_store_to_local(self):
        self.assertEqual(
            _parse_vector_store(None),
            "local",
        )

    def test_rejects_unknown_vector_store(self):
        with self.assertRaisesRegex(
            EnvironmentConfigurationError,
            "local.*supabase",
        ):
            _parse_vector_store("pinecone")


if __name__ == "__main__":
    unittest.main()