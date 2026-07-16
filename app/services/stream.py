import json
from collections.abc import AsyncIterator

from app.schemas.chat import ChatMessage
from app.services._messages import to_responses_input
from app.services.openai_client import get_async_client

MODEL = "gpt-4o-mini"


async def stream_chat(messages: list[ChatMessage]) -> AsyncIterator[dict]:
    """Yield SSE-shaped dicts for a streaming Responses API call.

    Each text delta is emitted as:
        {"event": "delta", "data": "<json: {text: ...}>"}
    A terminal event is emitted when the stream completes:
        {"event": "done", "data": "[DONE]"}
    """
    client = get_async_client()
    stream = await client.responses.create(
        model=MODEL,
        input=to_responses_input(messages),
        stream=True,
    )
    async for event in stream:
        event_type = getattr(event, "type", "")
        if event_type.endswith("output_text.delta"):
            payload = json.dumps({"text": getattr(event, "delta", "")})
            yield {"event": "delta", "data": payload}
        # All other event types (created, in_progress, completed, etc.)
        # are intentionally ignored — we only forward text deltas.

    yield {"event": "done", "data": "[DONE]"}
