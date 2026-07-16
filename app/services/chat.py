from app.schemas.chat import ChatMessage
from app.services._messages import to_responses_input
from app.services.openai_client import get_async_client

MODEL = "gpt-4o-mini"


async def chat(messages: list[ChatMessage]) -> str:
    """One-shot chat with the model, threading the full conversation history."""
    client = get_async_client()
    response = await client.responses.create(
        model=MODEL,
        # tools=[{"type": "web_search"}],
        input=to_responses_input(messages),
    )
    return response.output_text
