import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.config.company_config import PROJECT_ROOT
from app.models.assistant_mode import AssistantMode
from app.models.documents import DocumentStatus
from app.services.document_registry_service import (
    create_document_record,
    is_stored_path_registered,
)


UPLOAD_ROOT = PROJECT_ROOT / "data" / "uploads"

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".md",
}

OLD_UPLOAD_NAME_PATTERN = re.compile(
    r"^\d{10,16}_[0-9a-fA-F]{12,32}_(.+)$"
)

CURRENT_UPLOAD_NAME_PATTERN = re.compile(
    r"^([0-9a-fA-F]{32})_(.+)$"
)


def _infer_original_filename(stored_filename: str) -> str:
    old_match = OLD_UPLOAD_NAME_PATTERN.match(stored_filename)

    if old_match:
        return old_match.group(1)

    current_match = CURRENT_UPLOAD_NAME_PATTERN.match(
        stored_filename
    )

    if current_match:
        return current_match.group(2)

    return stored_filename


def _infer_document_id(stored_filename: str) -> str:
    current_match = CURRENT_UPLOAD_NAME_PATTERN.match(
        stored_filename
    )

    if current_match:
        return current_match.group(1)

    return uuid4().hex


def _file_uploaded_at(path: Path) -> datetime:
    modified_timestamp = path.stat().st_mtime

    return datetime.fromtimestamp(
        modified_timestamp,
        tz=timezone.utc,
    )


def backfill_document_registry(
    *,
    company_id: str,
    upload_root: Path = UPLOAD_ROOT,
    project_root: Path = PROJECT_ROOT,
) -> dict:
    summary = {
        "scanned": 0,
        "registered": 0,
        "already_registered": 0,
        "unsupported": 0,
        "modes": {},
    }

    for mode in AssistantMode:
        mode_directory = upload_root / mode.value

        mode_summary = {
            "scanned": 0,
            "registered": 0,
            "already_registered": 0,
            "unsupported": 0,
        }

        summary["modes"][mode.value] = mode_summary

        if not mode_directory.is_dir():
            continue

        for file_path in sorted(mode_directory.iterdir()):
            if not file_path.is_file():
                continue

            summary["scanned"] += 1
            mode_summary["scanned"] += 1

            extension = file_path.suffix.lower()

            if extension not in ALLOWED_EXTENSIONS:
                summary["unsupported"] += 1
                mode_summary["unsupported"] += 1
                continue

            try:
                stored_path = file_path.relative_to(
                project_root
                ).as_posix()
            except ValueError as error:
                    raise ValueError(
                    f"Upload file '{file_path}' is outside "
                    f"project root '{project_root}'."
                ) from error

            if is_stored_path_registered(stored_path):
                summary["already_registered"] += 1
                mode_summary["already_registered"] += 1
                continue

            try:
                create_document_record(
                    document_id=_infer_document_id(
                        file_path.name
                    ),
                    company_id=company_id,
                    mode=mode,
                    filename=_infer_original_filename(
                        file_path.name
                    ),
                    stored_path=stored_path,
                    size_bytes=file_path.stat().st_size,
                    status=DocumentStatus.INDEXED,
                    documents_loaded=None,
                    uploaded_at=_file_uploaded_at(file_path),
                )
            except sqlite3.IntegrityError:
                # Another process may have registered the same file
                # between the existence check and the insert.
                summary["already_registered"] += 1
                mode_summary["already_registered"] += 1
                continue

            summary["registered"] += 1
            mode_summary["registered"] += 1

    return summary