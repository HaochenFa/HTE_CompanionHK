from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field

ChatRole = Literal["companion", "local_guide", "study_guide"]


class ChatRequest(BaseModel):
    user_id: str = Field(min_length=1)
    message: str = Field(min_length=1)
    thread_id: str | None = Field(default=None, min_length=1)
    role: ChatRole = "companion"


class RoleChatRequest(BaseModel):
    user_id: str = Field(min_length=1)
    message: str = Field(min_length=1)
    thread_id: str | None = Field(default=None, min_length=1)


class SafetyResult(BaseModel):
    risk_level: Literal["low", "medium", "high"] = "low"
    show_crisis_banner: bool = False
    emotion_label: str | None = None
    emotion_score: float | None = Field(default=None, ge=0.0, le=1.0)
    policy_action: Literal["allow", "supportive_refusal", "escalate_banner"] = "allow"
    monitor_provider: Literal["minimax", "rules"] = "rules"
    degraded: bool = False
    fallback_reason: str | None = None


class ChatResponse(BaseModel):
    request_id: str
    thread_id: str
    runtime: str
    provider: str
    reply: str
    safety: SafetyResult


class ChatTurn(BaseModel):
    request_id: str
    thread_id: str
    created_at: datetime
    user_message: str
    assistant_reply: str
    safety: SafetyResult


class ChatHistoryResponse(BaseModel):
    user_id: str
    role: ChatRole
    thread_id: str
    turns: list[ChatTurn] = Field(default_factory=list)
