from app.schemas.grammar import GrammarRepair
from app.services.openai_client import get_async_client

MODEL = "gpt-4o-mini"


async def repair_grammar(text: str) -> GrammarRepair:
    """Detect the language of `text` and return a grammar-repaired version.

    Uses strict structured output (`text_format=GrammarRepair`). When the
    model cannot reliably detect a natural language it populates `error`
    and leaves `repaired_text` / `detected_language` as null.
    """
    client = get_async_client()
    instructions = (
        "You are a grammar repair assistant. Follow these steps:\n"
        "1. Detect the language of the user's text. The detection must be reliable.\n"
        "2. If you CANNOT reliably detect a natural language — for example the "
        "text is whitespace-only, gibberish, only emojis/symbols/numbers, or "
        "mixes unrelated scripts without forming a coherent message — set "
        "`error` to a short reason and leave `repaired_text` and "
        "`detected_language` as null.\n"
        "3. Otherwise, repair the grammar (spelling, punctuation, agreement, "
        "word order) in place while preserving the user's original meaning, "
        "tone, and language. Do NOT translate. Do NOT paraphrase aggressively. "
        "If the text is already correct, return it unchanged.\n"
        "4. Set `detected_language` to the language you identified "
        "(e.g. 'English', 'Spanish', 'Japanese').\n"
        "5. Set `repaired_text` to the repaired text.\n"
        "Do not include any extra commentary, quotes, or explanation."
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
        text_format=GrammarRepair,
    )
    message = response.output[0]
    text_part = message.content[0]
    parsed: GrammarRepair | None = text_part.parsed
    if parsed is not None:
        return parsed
    # Strict parsing didn't yield a result — surface as a structured error
    # rather than guessing. This differs from translate.py's fallback because
    # grammar repair needs both `repaired_text` and `detected_language`, which
    # we can't reliably extract from raw text.
    return GrammarRepair(error="Model returned an unparseable response.")