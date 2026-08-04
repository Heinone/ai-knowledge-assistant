import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.config.company_config import PROJECT_ROOT
from app.models.assistant_mode import AssistantMode
from app.models.documents import DocumentStatus


REGISTRY_DATABASE_PATH = (
    PROJECT_ROOT
    / "data"
    / "documents"
    / "document_registry.sqlite3"
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _connect() -> sqlite3.Connection:
    REGISTRY_DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(
        REGISTRY_DATABASE_PATH,
        timeout=10,
    )

    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 10000")
    connection.execute("PRAGMA journal_mode = WAL")

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
            document_id TEXT PRIMARY KEY,
            company_id TEXT NOT NULL,
            assistant_mode TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            stored_path TEXT NOT NULL UNIQUE,
            size_bytes INTEGER NOT NULL CHECK (size_bytes >= 0),
            status TEXT NOT NULL CHECK (
                status IN ('processing', 'indexed', 'failed')
            ),
            documents_loaded INTEGER,
            error_message TEXT,
            uploaded_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )

    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS
            idx_documents_company_mode_uploaded
        ON documents (
            company_id,
            assistant_mode,
            uploaded_at DESC
        )
        """
    )

    return connection


def _row_to_document(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "document_id": row["document_id"],
        "mode": row["assistant_mode"],
        "filename": row["original_filename"],
        "stored_path": row["stored_path"],
        "size_bytes": row["size_bytes"],
        "status": row["status"],
        "documents_loaded": row["documents_loaded"],
        "error_message": row["error_message"],
        "uploaded_at": row["uploaded_at"],
        "updated_at": row["updated_at"],
    }


def create_document_record(
    *,
    document_id: str,
    company_id: str,
    mode: AssistantMode,
    filename: str,
    stored_path: str,
    size_bytes: int,
    status: DocumentStatus = DocumentStatus.PROCESSING,
    documents_loaded: int | None = None,
    error_message: str | None = None,
    uploaded_at: datetime | None = None,
) -> dict[str, Any]:
    timestamp = uploaded_at or _utc_now()
    timestamp_text = timestamp.isoformat()

    with _connect() as connection:
        connection.execute(
            """
            INSERT INTO documents (
                document_id,
                company_id,
                assistant_mode,
                original_filename,
                stored_path,
                size_bytes,
                status,
                documents_loaded,
                error_message,
                uploaded_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                document_id,
                company_id,
                mode.value,
                filename,
                stored_path,
                size_bytes,
                status.value,
                documents_loaded,
                error_message,
                timestamp_text,
                timestamp_text,
            ),
        )

    return get_document_record(document_id)


def get_document_record(
    document_id: str,
) -> dict[str, Any]:
    with _connect() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM documents
            WHERE document_id = ?
            """,
            (document_id,),
        ).fetchone()

    if row is None:
        raise KeyError(
            f"Document '{document_id}' does not exist."
        )

    return _row_to_document(row)


def mark_document_indexed(
    *,
    document_id: str,
    documents_loaded: int,
) -> dict[str, Any]:
    updated_at = _utc_now().isoformat()

    with _connect() as connection:
        cursor = connection.execute(
            """
            UPDATE documents
            SET
                status = ?,
                documents_loaded = ?,
                error_message = NULL,
                updated_at = ?
            WHERE document_id = ?
            """,
            (
                DocumentStatus.INDEXED.value,
                documents_loaded,
                updated_at,
                document_id,
            ),
        )

        if cursor.rowcount != 1:
            raise KeyError(
                f"Document '{document_id}' does not exist."
            )

    return get_document_record(document_id)


def mark_document_failed(
    *,
    document_id: str,
    error_message: str,
) -> dict[str, Any]:
    updated_at = _utc_now().isoformat()

    with _connect() as connection:
        cursor = connection.execute(
            """
            UPDATE documents
            SET
                status = ?,
                error_message = ?,
                updated_at = ?
            WHERE document_id = ?
            """,
            (
                DocumentStatus.FAILED.value,
                error_message[:1000],
                updated_at,
                document_id,
            ),
        )

        if cursor.rowcount != 1:
            raise KeyError(
                f"Document '{document_id}' does not exist."
            )

    return get_document_record(document_id)


def list_document_records(
    *,
    company_id: str,
    mode: AssistantMode,
) -> list[dict[str, Any]]:
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM documents
            WHERE
                company_id = ?
                AND assistant_mode = ?
            ORDER BY uploaded_at DESC
            """,
            (
                company_id,
                mode.value,
            ),
        ).fetchall()

    return [
        _row_to_document(row)
        for row in rows
    ]


def is_stored_path_registered(
    stored_path: str,
) -> bool:
    with _connect() as connection:
        row = connection.execute(
            """
            SELECT 1
            FROM documents
            WHERE stored_path = ?
            """,
            (stored_path,),
        ).fetchone()

    return row is not None

def _datetime_to_text(value: datetime | str) -> str:
    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, str) and value.strip():
        return value.strip()

    raise ValueError("Document timestamp must not be empty.")

def replace_document_records_for_mode(
    *,
    company_id: str,
    mode: AssistantMode,
    documents: list[dict[str, Any]],
) -> None:
    """
    Atomically replace every registry record for one company and mode.

    Existing records remain untouched if validation or insertion fails.
    """

    required_fields = {
        "document_id",
        "filename",
        "stored_path",
        "size_bytes",
        "status",
        "uploaded_at",
        "updated_at",
    }

    seen_document_ids: set[str] = set()
    seen_stored_paths: set[str] = set()

    for document in documents:
        missing_fields = required_fields - document.keys()

        if missing_fields:
            missing = ", ".join(sorted(missing_fields))

            raise ValueError(
                f"Document record is missing required fields: {missing}"
            )

        document_id = str(document["document_id"])
        stored_path = str(document["stored_path"])
        size_bytes = document["size_bytes"]

        if document_id in seen_document_ids:
            raise ValueError(
                f"Duplicate document ID in replacement set: "
                f"{document_id}"
            )

        if stored_path in seen_stored_paths:
            raise ValueError(
                f"Duplicate stored path in replacement set: "
                f"{stored_path}"
            )

        if not isinstance(size_bytes, int) or size_bytes < 0:
            raise ValueError(
                f"Invalid size for document '{document_id}'."
            )

        try:
            status = DocumentStatus(document["status"])
        except ValueError as error:
            raise ValueError(
                f"Invalid status for document '{document_id}': "
                f"{document['status']}"
            ) from error

        seen_document_ids.add(document_id)
        seen_stored_paths.add(stored_path)

        document["status"] = status.value

    with _connect() as connection:
        connection.execute(
            """
            DELETE FROM documents
            WHERE
                company_id = ?
                AND assistant_mode = ?
            """,
            (
                company_id,
                mode.value,
            ),
        )

        connection.executemany(
            """
            INSERT INTO documents (
                document_id,
                company_id,
                assistant_mode,
                original_filename,
                stored_path,
                size_bytes,
                status,
                documents_loaded,
                error_message,
                uploaded_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    document["document_id"],
                    company_id,
                    mode.value,
                    document["filename"],
                    document["stored_path"],
                    document["size_bytes"],
                    document["status"],
                    document.get("documents_loaded"),
                    document.get("error_message"),
                    _datetime_to_text(document["uploaded_at"]),
                    _datetime_to_text(document["updated_at"]),
                )
                for document in documents
            ],
        )

def find_document_record_for_mode(
    *,
    document_id: str,
    company_id: str,
    mode: AssistantMode,
) -> dict[str, Any] | None:
    with _connect() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM documents
            WHERE
                document_id = ?
                AND company_id = ?
                AND assistant_mode = ?
            """,
            (
                document_id,
                company_id,
                mode.value,
            ),
        ).fetchone()

    if row is None:
        return None

    return _row_to_document(row)


def delete_document_record(
    *,
    document_id: str,
    company_id: str,
    mode: AssistantMode,
) -> bool:
    with _connect() as connection:
        cursor = connection.execute(
            """
            DELETE FROM documents
            WHERE
                document_id = ?
                AND company_id = ?
                AND assistant_mode = ?
            """,
            (
                document_id,
                company_id,
                mode.value,
            ),
        )

    return cursor.rowcount == 1
