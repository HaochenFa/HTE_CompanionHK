from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_orchestrator import ChatOrchestrator

router = APIRouter()
orchestrator = ChatOrchestrator()


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    return orchestrator.generate_reply(payload)
