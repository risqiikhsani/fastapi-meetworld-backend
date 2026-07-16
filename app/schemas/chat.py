from typing import Literal

from pydantic import BaseModel, Field, model_validator


class ChatMessage(BaseModel):
    """A single message in a conversation.

    `role="assistant"` messages are history echoes — previous assistant
    replies that the client replays faithfully so the model can see prior
    turns. The server is stateless and does not store history.
    """

    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1, max_length=8000)


class ChatRequest(BaseModel):
    """Request body for chat endpoints. Send the full conversation history
    so the model can see prior turns; the server is stateless."""

    messages: list[ChatMessage] = Field(..., min_length=1, max_length=50)

    @model_validator(mode="after")
    def require_user_turns(self) -> "ChatRequest":
        if self.messages[-1].role != "user":
            raise ValueError("The final message must have role='user'.")
        if not any(m.role == "user" for m in self.messages):
            raise ValueError("At least one user message is required.")
        return self


class ChatResponse(BaseModel):
    response: str
