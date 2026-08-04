from pydantic import BaseModel, Field, field_validator

from app.models.assistant_mode import AssistantMode


class ChatRequest(BaseModel):
    question: str = Field(max_length=8_000)
    mode: AssistantMode | None = None

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("Question must not be empty.")

        return cleaned_value