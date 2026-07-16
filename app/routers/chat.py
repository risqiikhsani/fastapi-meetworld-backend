from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse
from app.services import chat as chat_service

router = APIRouter()


@router.post("/chat", response_model=ChatResponse, summary="Chat with AI")
async def chat_endpoint(payload: ChatRequest) -> ChatResponse:
    return ChatResponse(response=await chat_service.chat(payload.message))