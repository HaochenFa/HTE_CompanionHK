import logging

from fastapi import APIRouter, HTTPException, Query

from app.schemas.chat import (
    ChatHistoryResponse,
    ChatRequest,
    ChatResponse,
    ChatRole,
    RoleChatRequest,
)
from app.services.chat_orchestrator import ChatOrchestrator

logger = logging.getLogger(__name__)
router = APIRouter()
orchestrator = ChatOrchestrator()


def _chat_forced_role(payload: RoleChatRequest, *, role: ChatRole) -> ChatResponse:
    request = ChatRequest(
        user_id=payload.user_id,
        role=role,
        thread_id=payload.thread_id,
        message=payload.message,
    )
    return orchestrator.generate_reply(request)


def _history_forced_role(
    *,
    user_id: str,
    role: ChatRole,
    thread_id: str | None,
    limit: int,
) -> ChatHistoryResponse:
    return orchestrator.get_history(
        user_id=user_id,
        role=role,
        thread_id=thread_id,
        limit=limit,
    )


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    try:
        return orchestrator.generate_reply(payload)
    except Exception:
        logger.exception("chat_endpoint_error user_id=%s role=%s", payload.user_id, payload.role)
        raise HTTPException(status_code=500, detail="Internal error processing chat request.")


@router.post("/chat/companion", response_model=ChatResponse)
def chat_companion(payload: RoleChatRequest) -> ChatResponse:
    try:
        return _chat_forced_role(payload, role="companion")
    except Exception:
        logger.exception("chat_companion_endpoint_error user_id=%s", payload.user_id)
        raise HTTPException(status_code=500, detail="Internal error processing companion chat request.")


@router.post("/chat/guide", response_model=ChatResponse)
def chat_guide(payload: RoleChatRequest) -> ChatResponse:
    try:
        return _chat_forced_role(payload, role="local_guide")
    except Exception:
        logger.exception("chat_guide_endpoint_error user_id=%s", payload.user_id)
        raise HTTPException(status_code=500, detail="Internal error processing guide chat request.")


@router.post("/chat/study", response_model=ChatResponse)
def chat_study(payload: RoleChatRequest) -> ChatResponse:
    try:
        return _chat_forced_role(payload, role="study_guide")
    except Exception:
        logger.exception("chat_study_endpoint_error user_id=%s", payload.user_id)
        raise HTTPException(status_code=500, detail="Internal error processing study chat request.")


@router.get("/chat/history", response_model=ChatHistoryResponse)
def chat_history(
    user_id: str = Query(min_length=1),
    role: ChatRole = "companion",
    thread_id: str | None = Query(default=None, min_length=1),
    limit: int = Query(default=50, ge=1, le=200),
) -> ChatHistoryResponse:
    try:
        return orchestrator.get_history(
            user_id=user_id,
            role=role,
            thread_id=thread_id,
            limit=limit,
        )
    except Exception:
        logger.exception("chat_history_endpoint_error user_id=%s role=%s", user_id, role)
        raise HTTPException(status_code=500, detail="Internal error fetching chat history.")


@router.get("/chat/companion/history", response_model=ChatHistoryResponse)
def chat_companion_history(
    user_id: str = Query(min_length=1),
    thread_id: str | None = Query(default=None, min_length=1),
    limit: int = Query(default=50, ge=1, le=200),
) -> ChatHistoryResponse:
    try:
        return _history_forced_role(
            user_id=user_id,
            role="companion",
            thread_id=thread_id,
            limit=limit,
        )
    except Exception:
        logger.exception("chat_companion_history_endpoint_error user_id=%s", user_id)
        raise HTTPException(status_code=500, detail="Internal error fetching companion history.")


@router.get("/chat/guide/history", response_model=ChatHistoryResponse)
def chat_guide_history(
    user_id: str = Query(min_length=1),
    thread_id: str | None = Query(default=None, min_length=1),
    limit: int = Query(default=50, ge=1, le=200),
) -> ChatHistoryResponse:
    try:
        return _history_forced_role(
            user_id=user_id,
            role="local_guide",
            thread_id=thread_id,
            limit=limit,
        )
    except Exception:
        logger.exception("chat_guide_history_endpoint_error user_id=%s", user_id)
        raise HTTPException(status_code=500, detail="Internal error fetching guide history.")


@router.get("/chat/study/history", response_model=ChatHistoryResponse)
def chat_study_history(
    user_id: str = Query(min_length=1),
    thread_id: str | None = Query(default=None, min_length=1),
    limit: int = Query(default=50, ge=1, le=200),
) -> ChatHistoryResponse:
    try:
        return _history_forced_role(
            user_id=user_id,
            role="study_guide",
            thread_id=thread_id,
            limit=limit,
        )
    except Exception:
        logger.exception("chat_study_history_endpoint_error user_id=%s", user_id)
        raise HTTPException(status_code=500, detail="Internal error fetching study history.")
