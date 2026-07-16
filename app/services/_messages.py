"""Convert the wire-format message list into the typed input shape expected
by `client.responses.create` and `openai-agents` `Runner.run`.

User turns use the input-message shape with `input_text` content parts.
Prior assistant turns must be represented as historical output messages with
`output_text` content parts — the Responses API rejects `role="assistant"`
on the input side, so we reuse the output-message item shape instead.
"""
from app.schemas.chat import ChatMessage


def to_responses_input(messages: list[ChatMessage]) -> list[dict]:
    items: list[dict] = []
    for m in messages:
        if m.role == "user":
            items.append(
                {
                    "role": "user",
                    "type": "message",
                    "content": [{"type": "input_text", "text": m.content}],
                }
            )
        else:  # assistant — prior turn; use the output-message item shape
            items.append(
                {
                    "type": "message",
                    "role": "assistant",
                    "status": "completed",
                    "content": [{"type": "output_text", "text": m.content}],
                }
            )
    return items
