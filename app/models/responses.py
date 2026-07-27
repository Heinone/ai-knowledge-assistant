from pydantic import BaseModel


class SourceChunk(BaseModel):
    id: str | None = None
    text: str
    score: float | None = None
    source: str | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceChunk] = []