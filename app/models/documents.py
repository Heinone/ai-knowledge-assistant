from datetime import datetime
from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field

from app.models.assistant_mode import AssistantMode


class DocumentStatus(str, Enum):
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"


class DocumentRecord(BaseModel):
    document_id: str
    mode: AssistantMode
    filename: str
    stored_path: str
    size_bytes: int = Field(ge=0)
    status: DocumentStatus
    documents_loaded: int | None = Field(default=None, ge=0)
    error_message: str | None = None
    uploaded_at: datetime
    updated_at: datetime


class DocumentListResponse(BaseModel):
    mode: AssistantMode
    total: int = Field(ge=0)
    documents: list[DocumentRecord] = Field(default_factory=list)

class DocumentDeleteResponse(BaseModel):
    document_id: str
    mode: AssistantMode
    filename: str
    status: Literal["deleted"]
    remaining_documents: int = Field(ge=0)
    remaining_indexed_documents: int = Field(ge=0)