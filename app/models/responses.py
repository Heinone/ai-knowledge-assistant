from pydantic import BaseModel, Field

from app.models.assistant_mode import AssistantMode


class SourceChunk(BaseModel):
    id: str | None = None
    text: str
    score: float | None = None
    source: str | None = None


class ChatResponse(BaseModel):
    answer: str
    mode: AssistantMode
    sources: list[SourceChunk] = Field(default_factory=list)