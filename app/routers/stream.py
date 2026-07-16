from collections.abc import AsyncIterator

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from app.schemas.chat import ChatRequest
from app.services import stream as stream_service

router = APIRouter()


@router.post("/chat/stream", summary="Stream a chat response via SSE")
async def stream_endpoint(payload: ChatRequest) -> EventSourceResponse:
    async def event_source() -> AsyncIterator[dict]:
        async for chunk in stream_service.stream_chat(payload.message):
            yield chunk

    return EventSourceResponse(event_source())