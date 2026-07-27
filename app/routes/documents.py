from pathlib import Path
from typing import Annotated
import time

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.ingestion_service import build_index_from_file


router = APIRouter()

UPLOAD_DIR = Path("data/uploads")
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}
MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB demo limit


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


def _save_upload_file(file: UploadFile) -> tuple[Path, str, int]:
    safe_name = _validate_filename(file.filename)

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = int(time.time() * 1000)
    saved_path = UPLOAD_DIR / f"{timestamp}_{safe_name}"

    bytes_written = 0

    with saved_path.open("wb") as buffer:
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
                        "Maximum file size is 15 MB for this demo."
                    ),
                )

            buffer.write(chunk)

    return saved_path, safe_name, bytes_written


def _index_uploaded_file(file: UploadFile) -> dict:
    saved_path, safe_name, bytes_written = _save_upload_file(file)

    documents_loaded = build_index_from_file(
        path=str(saved_path),
        chunk_size=1200,
        chunk_overlap=150,
        append=True,
    )

    return {
        "filename": safe_name,
        "saved_path": str(saved_path),
        "bytes": bytes_written,
        "documents_loaded": documents_loaded,
        "status": "indexed",
    }


@router.post("/documents/upload")
async def upload_document(
    file: Annotated[UploadFile, File(description="PDF, TXT, or MD file")]
):
    return _index_uploaded_file(file)


@router.post("/documents/upload-batch")
async def upload_documents(
    files: Annotated[
        list[UploadFile],
        File(description="One or more PDF, TXT, or MD files"),
    ]
):
    if not files:
        raise HTTPException(
            status_code=400,
            detail="At least one file is required.",
        )

    results = []

    for file in files:
        result = _index_uploaded_file(file)
        results.append(result)

    return {
        "files_processed": len(results),
        "results": results,
        "status": "indexed",
    }