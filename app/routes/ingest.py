from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.ingestion_service import (
    build_index_from_directory,
    build_index_from_file,
)
from app.services.url_loader import fetch_url_to_text_file

router = APIRouter()


class IngestDirectoryRequest(BaseModel):
    path: str
    chunk_size: int = Field(default=512, ge=100, le=2000)
    chunk_overlap: int = Field(default=50, ge=0, le=500)


class IngestFileRequest(BaseModel):
    path: str
    chunk_size: int = Field(default=512, ge=100, le=2000)
    chunk_overlap: int = Field(default=50, ge=0, le=500)


class IngestUrlRequest(BaseModel):
    url: str
    chunk_size: int = Field(default=512, ge=100, le=2000)
    chunk_overlap: int = Field(default=50, ge=0, le=500)


@router.post("/ingest/directory")
def ingest_directory(request: IngestDirectoryRequest):
    documents_loaded = build_index_from_directory(
        path=request.path,
        chunk_size=request.chunk_size,
        chunk_overlap=request.chunk_overlap,
    )

    return {
        "documents_loaded": documents_loaded,
        "chunk_size": request.chunk_size,
        "chunk_overlap": request.chunk_overlap,
    }


@router.post("/ingest/file")
def ingest_file(request: IngestFileRequest):
    documents_loaded = build_index_from_file(
        path=request.path,
        chunk_size=request.chunk_size,
        chunk_overlap=request.chunk_overlap,
    )

    return {
        "documents_loaded": documents_loaded,
        "chunk_size": request.chunk_size,
        "chunk_overlap": request.chunk_overlap,
    }


@router.post("/ingest/url")
def ingest_url(request: IngestUrlRequest):
    saved_path = fetch_url_to_text_file(request.url)

    documents_loaded = build_index_from_file(
        path=saved_path,
        chunk_size=request.chunk_size,
        chunk_overlap=request.chunk_overlap,
    )

    return {
        "documents_loaded": documents_loaded,
        "saved_path": saved_path,
        "chunk_size": request.chunk_size,
        "chunk_overlap": request.chunk_overlap,
    }