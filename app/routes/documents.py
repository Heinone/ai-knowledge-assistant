from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
)

from app.config.company_config import (
    PROJECT_ROOT,
    load_company_config,
)
from app.models.assistant_mode import AssistantMode
from app.models.documents import (
    DocumentDeleteResponse,
    DocumentListResponse,
)
from app.routes.mode_resolution import (
    resolve_request_assistant_mode,
)
from app.services.document_registry_service import (
    create_document_record,
    list_document_records,
    mark_document_failed,
    mark_document_indexed,
)
from app.services.ingestion_service import build_index_from_file

from app.services.document_lifecycle_service import (
    DocumentNotFoundError,
    DocumentStateConflictError,
    delete_document_and_rebuild,
)


router = APIRouter()

UPLOAD_ROOT = PROJECT_ROOT / "data" / "uploads"

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".md",
}

MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024


def _validate_filename(filename: str | None) -> str:
    if not filename:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file must have a filename.",
        )

    safe_name = Path(filename).name
    extension = Path(safe_name).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type for '{safe_name}'. "
                "Only PDF, TXT, and MD files are supported."
            ),
        )

    return safe_name


def _save_upload_file(
    file: UploadFile,
    mode: AssistantMode,
) -> tuple[str, Path, str, int]:
    safe_name = _validate_filename(file.filename)

    upload_directory = UPLOAD_ROOT / mode.value

    upload_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    document_id = uuid4().hex
    saved_path = upload_directory / f"{document_id}_{safe_name}"

    bytes_written = 0

    with saved_path.open("xb") as buffer:
        while True:
            chunk = file.file.read(1024 * 1024)

            if not chunk:
                break

            bytes_written += len(chunk)

            if bytes_written > MAX_FILE_SIZE_BYTES:
                saved_path.unlink(missing_ok=True)

                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"'{safe_name}' is too large. "
                        "Maximum file size is 15 MB."
                    ),
                )

            buffer.write(chunk)

    return (
        document_id,
        saved_path,
        safe_name,
        bytes_written,
    )


def _index_uploaded_file(
    file: UploadFile,
    mode: AssistantMode,
) -> dict:
    (
        document_id,
        saved_path,
        safe_name,
        bytes_written,
    ) = _save_upload_file(
        file=file,
        mode=mode,
    )

    company = load_company_config()

    stored_path = saved_path.relative_to(
        PROJECT_ROOT
    ).as_posix()

    try:
        create_document_record(
            document_id=document_id,
            company_id=company["company_id"],
            mode=mode,
            filename=safe_name,
            stored_path=stored_path,
            size_bytes=bytes_written,
        )
    except Exception:
        saved_path.unlink(missing_ok=True)
        raise

    try:
        documents_loaded = build_index_from_file(
            path=str(saved_path),
            chunk_size=1200,
            chunk_overlap=150,
            append=True,
            mode=mode,
        )
    except Exception as error:
        saved_path.unlink(missing_ok=True)

        mark_document_failed(
            document_id=document_id,
            error_message=str(error),
        )

        raise

    record = mark_document_indexed(
        document_id=document_id,
        documents_loaded=documents_loaded,
    )

    return {
        "document_id": record["document_id"],
        "filename": record["filename"],
        "saved_path": record["stored_path"],
        "bytes": record["size_bytes"],
        "documents_loaded": record["documents_loaded"],
        "status": record["status"],
        "uploaded_at": record["uploaded_at"],
    }


@router.get(
    "/documents",
    response_model=DocumentListResponse,
)
def get_documents(
    mode: Annotated[
        AssistantMode | None,
        Query(description="Assistant whose documents are requested"),
    ] = None,
):
    resolved_mode = resolve_request_assistant_mode(mode)
    company = load_company_config()

    documents = list_document_records(
        company_id=company["company_id"],
        mode=resolved_mode,
    )

    return {
        "mode": resolved_mode,
        "total": len(documents),
        "documents": documents,
    }

@router.delete(
    "/documents/{document_id}",
    response_model=DocumentDeleteResponse,
)
def delete_document(
    document_id: str,
    mode: Annotated[
        AssistantMode | None,
        Query(description="Assistant owning the document"),
    ] = None,
):
    resolved_mode = resolve_request_assistant_mode(mode)
    company = load_company_config()

    try:
        return delete_document_and_rebuild(
            document_id=document_id,
            company_id=company["company_id"],
            mode=resolved_mode,
        )
    except DocumentNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error
    except DocumentStateConflictError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error),
        ) from error

@router.post("/documents/upload")
async def upload_document(
    file: Annotated[
        UploadFile,
        File(description="PDF, TXT, or MD file"),
    ],
    mode: Annotated[
        AssistantMode | None,
        Form(description="Assistant receiving the document"),
    ] = None,
):
    resolved_mode = resolve_request_assistant_mode(mode)

    result = _index_uploaded_file(
        file=file,
        mode=resolved_mode,
    )

    return {
        "mode": resolved_mode.value,
        **result,
    }


@router.post("/documents/upload-batch")
async def upload_documents(
    files: Annotated[
        list[UploadFile],
        File(description="One or more PDF, TXT, or MD files"),
    ],
    mode: Annotated[
        AssistantMode | None,
        Form(description="Assistant receiving the documents"),
    ] = None,
):
    if not files:
        raise HTTPException(
            status_code=400,
            detail="At least one file is required.",
        )

    resolved_mode = resolve_request_assistant_mode(mode)

    results = []

    for file in files:
        result = _index_uploaded_file(
            file=file,
            mode=resolved_mode,
        )

        results.append(result)

    return {
        "mode": resolved_mode.value,
        "files_processed": len(results),
        "results": results,
        "status": "indexed",
    }