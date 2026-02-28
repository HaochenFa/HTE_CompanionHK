import logging

from fastapi import APIRouter, HTTPException

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_orchestrator import ChatOrchestrator

logger = logging.getLogger(__name__)
router = APIRouter()
orchestrator = ChatOrchestrator()


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    try:
        return orchestrator.generate_reply(payload)
    except Exception:
        logger.exception("chat_endpoint_error user_id=%s role=%s", payload.user_id, payload.role)
        raise HTTPException(status_code=500, detail="Internal error processing chat request.")
