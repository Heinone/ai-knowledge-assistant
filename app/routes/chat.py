import time

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.models.requests import ChatRequest
from app.models.responses import ChatResponse
from app.routes.mode_resolution import resolve_request_assistant_mode
from app.services.chat_service import answer_question

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    mode = resolve_request_assistant_mode(request.mode)

    result = answer_question(
        request.question,
        mode=mode,
    )

    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"],
        mode=mode,
    )


def fake_token_stream(question: str):
    words = [
        "Streaming ",
        "works. ",
        "You ",
        "asked: ",
        question,
    ]

    for word in words:
        yield word
        time.sleep(0.2)


@router.post("/chat/stream")
def chat_stream(request: ChatRequest):
    resolve_request_assistant_mode(request.mode)

    return StreamingResponse(
        fake_token_stream(request.question),
        media_type="text/plain",
    )