from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse
from app.security import CurrentUserDep
from app.services import agent as agent_service

router = APIRouter()


@router.post("/agent", response_model=ChatResponse, summary="Run the History tutor agent")
async def agent_endpoint(
    payload: ChatRequest, user: CurrentUserDep
) -> ChatResponse:
    return ChatResponse(response=await agent_service.run_agent(payload.messages))