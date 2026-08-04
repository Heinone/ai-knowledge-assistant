import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.models.assistant_mode import AssistantMode
from app.services import (
    document_backfill_service,
    document_registry_service,
)


class DocumentBackfillServiceTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)

        self.upload_root = self.root / "data" / "uploads"
        self.database_path = (
            self.root / "document_registry.sqlite3"
        )

        self.database_path_patch = patch.object(
            document_registry_service,
            "REGISTRY_DATABASE_PATH",
            self.database_path,
        )

        self.database_path_patch.start()

    def tearDown(self):
        self.database_path_patch.stop()
        self.temporary_directory.cleanup()

    def test_registers_existing_uploads_without_duplicates(self):
        support_directory = (
            self.upload_root
            / AssistantMode.CUSTOMER_SUPPORT.value
        )

        internal_directory = (
            self.upload_root
            / AssistantMode.INTERNAL_KNOWLEDGE.value
        )

        support_directory.mkdir(parents=True)
        internal_directory.mkdir(parents=True)

        old_support_file = (
            support_directory
            / "1720000000000_abcdef123456_refund_policy.txt"
        )

        current_internal_file = (
            internal_directory
            / (
                "0123456789abcdef0123456789abcdef_"
                "employee_handbook.md"
            )
        )

        old_support_file.write_text(
            "Refund policy",
            encoding="utf-8",
        )

        current_internal_file.write_text(
            "Employee handbook",
            encoding="utf-8",
        )

        first_result = (
            document_backfill_service.backfill_document_registry(
                company_id="company-1",
                upload_root=self.upload_root,
                project_root=self.root,
            )
        )

        second_result = (
            document_backfill_service.backfill_document_registry(
                company_id="company-1",
                upload_root=self.upload_root,
                project_root=self.root,
            )
        )

        self.assertEqual(first_result["registered"], 2)
        self.assertEqual(second_result["registered"], 0)
        self.assertEqual(
            second_result["already_registered"],
            2,
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
            support_documents[0]["filename"],
            "refund_policy.txt",
        )

        self.assertEqual(
            internal_documents[0]["filename"],
            "employee_handbook.md",
        )

        self.assertEqual(
            support_documents[0]["status"],
            "indexed",
        )


if __name__ == "__main__":
    unittest.main()