import unittest
from unittest.mock import Mock, patch

from app.models.assistant_mode import AssistantMode
from app.services import ingestion_service


class LocalIndexModeTests(unittest.TestCase):
    def tearDown(self):
        ingestion_service.reset_local_index()

    def test_local_indexes_are_stored_separately(self):
        with (
            patch.object(
                ingestion_service,
                "_create_embedding_model",
            ),
            patch.object(
                ingestion_service,
                "VectorStoreIndex",
                side_effect=[
                    "customer-support-index",
                    "internal-knowledge-index",
                ],
            ),
            patch.object(
                ingestion_service,
                "_persist_local_index",
            ),
        ):
            ingestion_service._build_local_index_from_nodes(
                nodes=["support-node"],
                mode=AssistantMode.CUSTOMER_SUPPORT,
            )

            ingestion_service._build_local_index_from_nodes(
                nodes=["internal-node"],
                mode=AssistantMode.INTERNAL_KNOWLEDGE,
            )

        with patch.object(
            ingestion_service,
            "resolve_assistant_mode",
            side_effect=lambda mode: AssistantMode(mode),
        ):
            support_index = ingestion_service.get_index(
                AssistantMode.CUSTOMER_SUPPORT
            )

            internal_index = ingestion_service.get_index(
                AssistantMode.INTERNAL_KNOWLEDGE
            )

        self.assertEqual(
            support_index,
            "customer-support-index",
        )

        self.assertEqual(
            internal_index,
            "internal-knowledge-index",
        )

    def test_get_index_loads_persisted_index_when_cache_is_empty(self):
        persisted_index = Mock()

        with (
            patch.object(
                ingestion_service,
                "resolve_assistant_mode",
                return_value=AssistantMode.CUSTOMER_SUPPORT,
            ),
            patch.object(
                ingestion_service,
                "_load_local_index_from_disk",
                return_value=persisted_index,
            ) as load_index,
        ):
            result = ingestion_service.get_index(
                AssistantMode.CUSTOMER_SUPPORT
            )

        self.assertIs(
            result,
            persisted_index,
        )

        load_index.assert_called_once_with(
            AssistantMode.CUSTOMER_SUPPORT
        )

    def test_append_inserts_into_persisted_index(self):
        persisted_index = Mock()

        with (
            patch.object(
                ingestion_service,
                "_load_local_index_from_disk",
                return_value=persisted_index,
            ),
            patch.object(
                ingestion_service,
                "_persist_local_index",
            ) as persist_index,
        ):
            ingestion_service._build_local_index_from_nodes(
                nodes=["new-node"],
                mode=AssistantMode.CUSTOMER_SUPPORT,
                append=True,
            )

        persisted_index.insert_nodes.assert_called_once_with(
            ["new-node"]
        )

        persist_index.assert_called_once_with(
            index=persisted_index,
            mode=AssistantMode.CUSTOMER_SUPPORT,
        )

    def test_reset_removes_only_requested_mode_from_cache(self):
        ingestion_service._local_indexes[
            AssistantMode.CUSTOMER_SUPPORT
        ] = "customer-support-index"

        ingestion_service._local_indexes[
            AssistantMode.INTERNAL_KNOWLEDGE
        ] = "internal-knowledge-index"

        ingestion_service.reset_local_index(
            AssistantMode.CUSTOMER_SUPPORT
        )

        self.assertNotIn(
            AssistantMode.CUSTOMER_SUPPORT,
            ingestion_service._local_indexes,
        )

        self.assertIn(
            AssistantMode.INTERNAL_KNOWLEDGE,
            ingestion_service._local_indexes,
        )


if __name__ == "__main__":
    unittest.main()