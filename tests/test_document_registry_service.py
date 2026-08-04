import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.models.assistant_mode import AssistantMode
from app.services import document_registry_service


class DocumentRegistryServiceTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()

        database_path = (
            Path(self.temporary_directory.name)
            / "document_registry.sqlite3"
        )

        self.database_path_patch = patch.object(
            document_registry_service,
            "REGISTRY_DATABASE_PATH",
            database_path,
        )

        self.database_path_patch.start()

    def tearDown(self):
        self.database_path_patch.stop()
        self.temporary_directory.cleanup()

    def test_creates_and_lists_document(self):
        document_registry_service.create_document_record(
            document_id="document-1",
            company_id="company-1",
            mode=AssistantMode.CUSTOMER_SUPPORT,
            filename="refund-policy.pdf",
            stored_path=(
                "data/uploads/customer_support/"
                "document-1_refund-policy.pdf"
            ),
            size_bytes=1024,
        )

        documents = (
            document_registry_service.list_document_records(
                company_id="company-1",
                mode=AssistantMode.CUSTOMER_SUPPORT,
            )
        )

        self.assertEqual(len(documents), 1)
        self.assertEqual(
            documents[0]["document_id"],
            "document-1",
        )
        self.assertEqual(
            documents[0]["status"],
            "processing",
        )

    def test_marks_document_as_indexed(self):
        document_registry_service.create_document_record(
            document_id="document-1",
            company_id="company-1",
            mode=AssistantMode.CUSTOMER_SUPPORT,
            filename="refund-policy.pdf",
            stored_path="data/uploads/refund-policy.pdf",
            size_bytes=1024,
        )

        result = (
            document_registry_service.mark_document_indexed(
                document_id="document-1",
                documents_loaded=1,
            )
        )

        self.assertEqual(result["status"], "indexed")
        self.assertEqual(result["documents_loaded"], 1)
        self.assertIsNone(result["error_message"])

    def test_keeps_assistant_documents_separate(self):
        document_registry_service.create_document_record(
            document_id="support-document",
            company_id="company-1",
            mode=AssistantMode.CUSTOMER_SUPPORT,
            filename="support.txt",
            stored_path="data/uploads/support.txt",
            size_bytes=100,
        )

        document_registry_service.create_document_record(
            document_id="internal-document",
            company_id="company-1",
            mode=AssistantMode.INTERNAL_KNOWLEDGE,
            filename="internal.txt",
            stored_path="data/uploads/internal.txt",
            size_bytes=200,
        )

        support_documents = (
            document_registry_service.list_document_records(
                company_id="company-1",
                mode=AssistantMode.CUSTOMER_SUPPORT,
            )
        )

        self.assertEqual(len(support_documents), 1)
        self.assertEqual(
            support_documents[0]["document_id"],
            "support-document",
        )


if __name__ == "__main__":
    unittest.main()

def test_replaces_only_selected_mode_records(self):
    document_registry_service.create_document_record(
        document_id="old-support",
        company_id="company-1",
        mode=AssistantMode.CUSTOMER_SUPPORT,
        filename="old-support.txt",
        stored_path="data/uploads/customer_support/old-support.txt",
        size_bytes=100,
    )

    document_registry_service.create_document_record(
        document_id="internal-document",
        company_id="company-1",
        mode=AssistantMode.INTERNAL_KNOWLEDGE,
        filename="internal.txt",
        stored_path="data/uploads/internal_knowledge/internal.txt",
        size_bytes=200,
    )

    timestamp = "2026-08-04T12:00:00+00:00"

    document_registry_service.replace_document_records_for_mode(
        company_id="company-1",
        mode=AssistantMode.CUSTOMER_SUPPORT,
        documents=[
            {
                "document_id": "new-support",
                "filename": "new-support.txt",
                "stored_path": (
                    "data/uploads/customer_support/new-support.txt"
                ),
                "size_bytes": 300,
                "status": "indexed",
                "documents_loaded": 1,
                "error_message": None,
                "uploaded_at": timestamp,
                "updated_at": timestamp,
            }
        ],
    )

    support_documents = (
        document_registry_service.list_document_records(
            company_id="company-1",
            mode=AssistantMode.CUSTOMER_SUPPORT,
        )
    )

    internal_documents = (
        document_registry_service.list_document_records(
            company_id="company-1",
            mode=AssistantMode.INTERNAL_KNOWLEDGE,
        )
    )

    self.assertEqual(
        [document["document_id"] for document in support_documents],
        ["new-support"],
    )

    self.assertEqual(
        [document["document_id"] for document in internal_documents],
        ["internal-document"],
    )


def test_replacement_validation_does_not_delete_existing_records(self):
    document_registry_service.create_document_record(
        document_id="existing-document",
        company_id="company-1",
        mode=AssistantMode.CUSTOMER_SUPPORT,
        filename="existing.txt",
        stored_path="data/uploads/customer_support/existing.txt",
        size_bytes=100,
    )

    with self.assertRaisesRegex(
        ValueError,
        "Duplicate document ID",
    ):
        document_registry_service.replace_document_records_for_mode(
            company_id="company-1",
            mode=AssistantMode.CUSTOMER_SUPPORT,
            documents=[
                {
                    "document_id": "duplicate",
                    "filename": "one.txt",
                    "stored_path": (
                        "data/uploads/customer_support/one.txt"
                    ),
                    "size_bytes": 100,
                    "status": "indexed",
                    "documents_loaded": 1,
                    "error_message": None,
                    "uploaded_at": "2026-08-04T12:00:00+00:00",
                    "updated_at": "2026-08-04T12:00:00+00:00",
                },
                {
                    "document_id": "duplicate",
                    "filename": "two.txt",
                    "stored_path": (
                        "data/uploads/customer_support/two.txt"
                    ),
                    "size_bytes": 100,
                    "status": "indexed",
                    "documents_loaded": 1,
                    "error_message": None,
                    "uploaded_at": "2026-08-04T12:00:00+00:00",
                    "updated_at": "2026-08-04T12:00:00+00:00",
                },
            ],
        )

    documents = document_registry_service.list_document_records(
        company_id="company-1",
        mode=AssistantMode.CUSTOMER_SUPPORT,
    )

    self.assertEqual(
        [document["document_id"] for document in documents],
        ["existing-document"],
    )

def test_finds_document_only_for_correct_company_and_mode(self):
    document_registry_service.create_document_record(
        document_id="document-1",
        company_id="company-1",
        mode=AssistantMode.CUSTOMER_SUPPORT,
        filename="policy.txt",
        stored_path="data/uploads/customer_support/policy.txt",
        size_bytes=100,
    )

    found = (
        document_registry_service.find_document_record_for_mode(
            document_id="document-1",
            company_id="company-1",
            mode=AssistantMode.CUSTOMER_SUPPORT,
        )
    )

    wrong_mode = (
        document_registry_service.find_document_record_for_mode(
            document_id="document-1",
            company_id="company-1",
            mode=AssistantMode.INTERNAL_KNOWLEDGE,
        )
    )

    self.assertIsNotNone(found)
    self.assertIsNone(wrong_mode)


def test_deletes_document_only_for_correct_owner(self):
    document_registry_service.create_document_record(
        document_id="document-1",
        company_id="company-1",
        mode=AssistantMode.CUSTOMER_SUPPORT,
        filename="policy.txt",
        stored_path="data/uploads/customer_support/policy.txt",
        size_bytes=100,
    )

    deleted = document_registry_service.delete_document_record(
        document_id="document-1",
        company_id="company-1",
        mode=AssistantMode.CUSTOMER_SUPPORT,
    )

    self.assertTrue(deleted)

    remaining = (
        document_registry_service.list_document_records(
            company_id="company-1",
            mode=AssistantMode.CUSTOMER_SUPPORT,
        )
    )

    self.assertEqual(remaining, [])