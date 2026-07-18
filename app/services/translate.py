from app.services.openai_client import get_async_client

MODEL = "gpt-4o-mini"


async def translate(text: str, source_lang: str | None, target_lang: str) -> str:
    """Translate `text` into `target_lang` using the Responses API.

    Returns just the translated string with no surrounding commentary.
    """
    client = get_async_client()
    src_clause = f" from {source_lang}" if source_lang else " (auto-detect the source language)"
    instructions = (
        f"You are a translator. Translate the user's text{src_clause} into {target_lang}. "
        "Return only the translation, with no additional commentary, quotes, or explanation."
    )
    response = await client.responses.create(
        model=MODEL,
        instructions=instructions,
        input=[
            {
                "role": "user",
                "type": "message",
                "content": [{"type": "input_text", "text": text}],
            }
        ],
    )
    return response.output_text.strip()
