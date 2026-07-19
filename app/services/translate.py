from app.schemas.translate import Translation
from app.services.openai_client import get_async_client

MODEL = "gpt-4o-mini"


async def translate(text: str, source_lang: str | None, target_lang: str) -> Translation:
    """Translate `text` into `target_lang` using the Responses API.

    Uses strict structured output (`text_format=Translation`) so the model
    always returns a well-formed `{translated_text, detected_source_lang}`
    object. When `source_lang` is None, the model auto-detects and reports
    the source language; otherwise it leaves `detected_source_lang` null.
    """
    client = get_async_client()
    src_clause = f" from {source_lang}" if source_lang else " (auto-detect the source language)"
    detect_clause = (
        ""
        if source_lang
        else (
            " When the source is unspecified, populate `detected_source_lang` "
            "with the detected language; otherwise leave it null."
        )
    )
    instructions = (
        f"You are a translator. Translate the user's text{src_clause} into {target_lang}. "
        f"Return only the translation, with no additional commentary, quotes, or explanation.{detect_clause}"
    )
    response = await client.responses.parse(
        model=MODEL,
        instructions=instructions,
        input=[
            {
                "role": "user",
                "type": "message",
                "content": [{"type": "input_text", "text": text}],
            }
        ],
        text_format=Translation,
    )
    message = response.output[0]
    text_part = message.content[0]
    parsed: Translation | None = text_part.parsed
    if parsed is not None:
        return parsed
    # Strict parsing didn't yield a result — fall back to whatever raw text
    # came back so a model hiccup doesn't surface as a 500.
    return Translation(translated_text=(getattr(text_part, "text", "") or "").strip())
