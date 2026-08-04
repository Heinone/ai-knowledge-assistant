import hashlib
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.config.company_config import PROJECT_ROOT
from app.models.assistant_mode import AssistantMode
from app.services.document_registry_service import (
    replace_document_records_for_mode,
)
from app.services.ingestion_service import (
    build_local_index_snapshot_from_directory,
    reset_local_index,
)


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".md",
}

CURRENT_FILENAME_PATTERN = re.compile(
    r"^[0-9a-fA-F]{32}_(.+)$"
)

TIMESTAMP_FILENAME_PATTERN = re.compile(
    r"^\d{10,16}_[0-9a-fA-F]{12,32}_(.+)$"
)


def _digest(path: Path) -> str:
    hasher = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):
            hasher.update(chunk)

    return hasher.hexdigest()


def _original_filename(stored_filename: str) -> str:
    current_match = CURRENT_FILENAME_PATTERN.match(
        stored_filename
    )

    if current_match:
        return current_match.group(1)

    timestamp_match = TIMESTAMP_FILENAME_PATTERN.match(
        stored_filename
    )

    if timestamp_match:
        return timestamp_match.group(1)

    return stored_filename


def _collect_unique_documents(
    runtime_directory: Path,
) -> list[dict]:
    if not runtime_directory.is_dir():
        raise ValueError(
            f"Runtime directory does not exist: "
            f"'{runtime_directory}'."
        )

    files = sorted(
        path
        for path in runtime_directory.iterdir()
        if path.is_file()
    )

    if not files:
        raise ValueError(
            f"Runtime directory contains no documents: "
            f"'{runtime_directory}'."
        )

    unsupported = [
        path.name
        for path in files
        if path.suffix.lower() not in ALLOWED_EXTENSIONS
    ]

    if unsupported:
        raise ValueError(
            "Runtime directory contains unsupported files: "
            + ", ".join(unsupported)
        )

    groups: dict[str, list[Path]] = {}

    for path in files:
        groups.setdefault(
            _digest(path),
            [],
        ).append(path)

    unique_documents = []

    for file_hash, duplicate_paths in sorted(
        groups.items()
    ):
        names = sorted(
            {
                _original_filename(path.name)
                for path in duplicate_paths
            },
            key=lambda value: (
                len(value),
                value.lower(),
            ),
        )

        source_path = sorted(
            duplicate_paths,
            key=lambda path: path.name,
        )[0]

        uploaded_at = min(
            datetime.fromtimestamp(
                path.stat().st_mtime,
                tz=timezone.utc,
            )
            for path in duplicate_paths
        )

        unique_documents.append(
            {
                "hash": file_hash,
                "filename": names[0],
                "source_path": source_path,
                "uploaded_at": uploaded_at,
                "duplicate_count": len(duplicate_paths),
            }
        )

    return unique_documents


def rebuild_mode_runtime(
    *,
    company_id: str,
    mode: AssistantMode,
    project_root: Path = PROJECT_ROOT,
) -> dict:
    operation_id = uuid4().hex

    runtime_upload_directory = (
        project_root
        / "data"
        / "uploads"
        / mode.value
    )

    runtime_index_directory = (
        project_root
        / "data"
        / "indexes"
        / mode.value
    )

    staging_root = (
        project_root
        / "data"
        / "rebuild_staging"
        / operation_id
    )

    staged_upload_directory = (
        staging_root
        / "uploads"
        / mode.value
    )

    staged_index_directory = (
        staging_root
        / "indexes"
        / mode.value
    )

    backup_root = (
        project_root
        / "data"
        / "rebuild_backups"
        / operation_id
    )

    backup_upload_directory = (
        backup_root
        / "uploads"
        / mode.value
    )

    backup_index_directory = (
        backup_root
        / "indexes"
        / mode.value
    )

    unique_documents = _collect_unique_documents(
        runtime_upload_directory
    )

    staged_upload_directory.mkdir(
        parents=True,
        exist_ok=False,
    )

    registry_records = []

    for document in unique_documents:
        document_id = uuid4().hex
        filename = document["filename"]

        staged_path = (
            staged_upload_directory
            / f"{document_id}_{filename}"
        )

        shutil.copy2(
            document["source_path"],
            staged_path,
        )

        active_path = (
            runtime_upload_directory
            / staged_path.name
        )

        timestamp = document["uploaded_at"]

        registry_records.append(
            {
                "document_id": document_id,
                "filename": filename,
                "stored_path": active_path.relative_to(
                    project_root
                ).as_posix(),
                "size_bytes": staged_path.stat().st_size,
                "status": "indexed",
                "documents_loaded": None,
                "error_message": None,
                "uploaded_at": timestamp,
                "updated_at": timestamp,
            }
        )

    documents_loaded = (
        build_local_index_snapshot_from_directory(
            source_directory=staged_upload_directory,
            persist_directory=staged_index_directory,
            chunk_size=1200,
            chunk_overlap=150,
        )
    )

    backup_upload_directory.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    backup_index_directory.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    try:
        if runtime_upload_directory.exists():
            shutil.move(
                str(runtime_upload_directory),
                str(backup_upload_directory),
            )

        shutil.move(
            str(staged_upload_directory),
            str(runtime_upload_directory),
        )

        if runtime_index_directory.exists():
            shutil.move(
                str(runtime_index_directory),
                str(backup_index_directory),
            )

        shutil.move(
            str(staged_index_directory),
            str(runtime_index_directory),
        )

        replace_document_records_for_mode(
            company_id=company_id,
            mode=mode,
            documents=registry_records,
        )
    except Exception:
        shutil.rmtree(
            runtime_upload_directory,
            ignore_errors=True,
        )

        shutil.rmtree(
            runtime_index_directory,
            ignore_errors=True,
        )

        if backup_upload_directory.exists():
            shutil.move(
                str(backup_upload_directory),
                str(runtime_upload_directory),
            )

        if backup_index_directory.exists():
            shutil.move(
                str(backup_index_directory),
                str(runtime_index_directory),
            )

        raise
    finally:
        shutil.rmtree(
            staging_root,
            ignore_errors=True,
        )

    reset_local_index(mode)

    original_file_count = sum(
        document["duplicate_count"]
        for document in unique_documents
    )

    return {
        "mode": mode.value,
        "original_file_count": original_file_count,
        "unique_document_count": len(unique_documents),
        "duplicates_removed": (
            original_file_count - len(unique_documents)
        ),
        "documents_loaded": documents_loaded,
        "backup_directory": backup_root.relative_to(
            project_root
        ).as_posix(),
    }