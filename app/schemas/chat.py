from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User input to send to the model.")


class ChatResponse(BaseModel):
    response: str