from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field

ChatRole = Literal["companion", "local_guide", "study_guide"]


class ImageAttachment(BaseModel):
    mime_type: Literal["image/jpeg", "image/png", "image/webp"]
    base64_data: str = Field(min_length=1)
    filename: str | None = None
    size_bytes: int | None = Field(default=None, ge=0, le=5_242_880)


class ChatRequest(BaseModel):
    user_id: str = Field(min_length=1)
    message: str = Field(min_length=1)
    thread_id: str | None = Field(default=None, min_length=1)
    role: ChatRole = "companion"
    attachment: ImageAttachment | None = None


class RoleChatRequest(BaseModel):
    user_id: str = Field(min_length=1)
    message: str = Field(min_length=1)
    thread_id: str | None = Field(default=None, min_length=1)
    attachment: ImageAttachment | None = None


class SafetyResult(BaseModel):
    risk_level: Literal["low", "medium", "high"] = Field(
        default="low", exclude=True,
    )
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


class ClearHistoryRequest(BaseModel):
    user_id: str = Field(min_length=1)
    role: ChatRole
    thread_id: str | None = Field(default=None, min_length=1)


class ClearHistoryResponse(BaseModel):
    user_id: str
    role: ChatRole
    cleared_thread_id: str
    new_thread_id: str
    cleared_message_count: int = 0
    cleared_memory_count: int = 0
    cleared_recommendation_count: int = 0
