from app.services.openai_client import get_async_client

MODEL = "gpt-4o-mini"


async def chat(message: str) -> str:
    """One-shot chat with web_search tool enabled (mirrors the original chat.py)."""
    client = get_async_client()
    response = await client.responses.create(
        model=MODEL,
        # tools=[{"type": "web_search"}],
        input=message,
    )
    return response.output_text