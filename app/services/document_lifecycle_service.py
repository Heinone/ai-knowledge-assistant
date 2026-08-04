import os
import shutil
from pathlib import Path
from threading import RLock
from uuid import uuid4

from app.config.company_config import PROJECT_ROOT
from app.config.env_config import VECTOR_STORE
from app.models.assistant_mode import AssistantMode
from app.services.document_registry_service import (
    delete_document_record,
    find_document_record_for_mode,
    list_document_records,
)
from app.services.ingestion_service import (
    build_local_index_snapshot_from_directory,
    reset_local_index,
)


class DocumentNotFoundError(Exception):
    pass


class DocumentStateConflictError(Exception):
    pass


_document_lifecycle_lock = RLock()


def _resolve_document_path(
    *,
    project_root: Path,
    mode: AssistantMode,
    stored_path: str,
) -> Path:
    mode_upload_directory = (
        project_root
        / "data"
        / "uploads"
        / mode.value
    ).resolve()

    document_path = (
        project_root
        / stored_path
    ).resolve()

    try:
        document_path.relative_to(mode_upload_directory)
    except ValueError as error:
        raise DocumentStateConflictError(
            "Document path is outside the assistant upload directory."
        ) from error

    return document_path


def _copy_or_link(
    source: Path,
    destination: Path,
) -> None:
    try:
        os.link(source, destination)
    except OSError:
        shutil.copy2(source, destination)


def _stage_remaining_documents(
    *,
    records: list[dict],
    excluded_document_id: str,
    source_directory: Path,
    project_root: Path,
    mode: AssistantMode,
) -> list[dict]:
    remaining_indexed_records = [
        record
        for record in records
        if (
            record["document_id"] != excluded_document_id
            and record["status"] == "indexed"
        )
    ]

    if not remaining_indexed_records:
        return []

    source_directory.mkdir(
        parents=True,
        exist_ok=False,
    )

    for record in remaining_indexed_records:
        document_path = _resolve_document_path(
            project_root=project_root,
            mode=mode,
            stored_path=record["stored_path"],
        )

        if not document_path.is_file():
            raise DocumentStateConflictError(
                "Registered document file is missing: "
                f"{record['filename']}."
            )

        staged_path = (
            source_directory
            / document_path.name
        )

        _copy_or_link(
            document_path,
            staged_path,
        )

    return remaining_indexed_records


def delete_document_and_rebuild(
    *,
    document_id: str,
    company_id: str,
    mode: AssistantMode,
    project_root: Path = PROJECT_ROOT,
) -> dict:
    if VECTOR_STORE != "local":
        raise DocumentStateConflictError(
            "Document deletion is not yet available for "
            "the configured vector store."
        )

    with _document_lifecycle_lock:
        record = find_document_record_for_mode(
            document_id=document_id,
            company_id=company_id,
            mode=mode,
        )

        if record is None:
            raise DocumentNotFoundError(
                f"Document '{document_id}' was not found."
            )

        all_records = list_document_records(
            company_id=company_id,
            mode=mode,
        )

        target_path = _resolve_document_path(
            project_root=project_root,
            mode=mode,
            stored_path=record["stored_path"],
        )

        operation_root = (
            project_root
            / "data"
            / "deletion_staging"
            / uuid4().hex
        )

        staged_source_directory = (
            operation_root
            / "remaining_documents"
        )

        staged_index_directory = (
            operation_root
            / "new_index"
        )

        deleted_file_backup = (
            operation_root
            / "deleted_file"
            / target_path.name
        )

        previous_index_backup = (
            operation_root
            / "previous_index"
        )

        runtime_index_directory = (
            project_root
            / "data"
            / "indexes"
            / mode.value
        )

        remaining_indexed_records = []

        if record["status"] == "indexed":
            if not target_path.is_file():
                raise DocumentStateConflictError(
                    "The registered document file is missing."
                )

            remaining_indexed_records = (
                _stage_remaining_documents(
                    records=all_records,
                    excluded_document_id=document_id,
                    source_directory=staged_source_directory,
                    project_root=project_root,
                    mode=mode,
                )
            )

            if remaining_indexed_records:
                build_local_index_snapshot_from_directory(
                    source_directory=staged_source_directory,
                    persist_directory=staged_index_directory,
                    chunk_size=1200,
                    chunk_overlap=150,
                )

        deleted_file_backup.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_was_moved = False
        previous_index_was_moved = False
        new_index_was_installed = False

        try:
            if target_path.exists():
                shutil.move(
                    str(target_path),
                    str(deleted_file_backup),
                )

                file_was_moved = True

            if runtime_index_directory.exists():
                shutil.move(
                    str(runtime_index_directory),
                    str(previous_index_backup),
                )

                previous_index_was_moved = True

            if staged_index_directory.exists():
                runtime_index_directory.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                shutil.move(
                    str(staged_index_directory),
                    str(runtime_index_directory),
                )

                new_index_was_installed = True

            reset_local_index(mode)

            deleted = delete_document_record(
                document_id=document_id,
                company_id=company_id,
                mode=mode,
            )

            if not deleted:
                raise DocumentNotFoundError(
                    f"Document '{document_id}' was not found."
                )

        except Exception:
            if new_index_was_installed:
                shutil.rmtree(
                    runtime_index_directory,
                    ignore_errors=True,
                )

            if previous_index_was_moved:
                shutil.move(
                    str(previous_index_backup),
                    str(runtime_index_directory),
                )

            if file_was_moved and deleted_file_backup.exists():
                target_path.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                shutil.move(
                    str(deleted_file_backup),
                    str(target_path),
                )

            reset_local_index(mode)

            shutil.rmtree(
                operation_root,
                ignore_errors=True,
            )

            raise

        shutil.rmtree(
            operation_root,
            ignore_errors=True,
        )

        return {
            "document_id": document_id,
            "mode": mode.value,
            "filename": record["filename"],
            "status": "deleted",
            "remaining_documents": len(all_records) - 1,
            "remaining_indexed_documents": len(
                remaining_indexed_records
            ),
        }