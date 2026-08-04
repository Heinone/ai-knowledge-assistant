from fastapi import HTTPException, status

from app.config.company_config import resolve_assistant_mode
from app.models.assistant_mode import AssistantMode


def resolve_request_assistant_mode(
    requested_mode: AssistantMode | str | None,
) -> AssistantMode:
    try:
        return resolve_assistant_mode(requested_mode)
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error