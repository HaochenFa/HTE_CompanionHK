from typing import Literal
from pydantic import BaseModel, Field

ChatRole = Literal["companion", "local_guide", "study_guide"]


class ChatRequest(BaseModel):
    user_id: str = Field(min_length=1)
    message: str = Field(min_length=1)
    thread_id: str | None = Field(default=None, min_length=1)
    role: ChatRole = "companion"


class SafetyResult(BaseModel):
    risk_level: Literal["low", "medium", "high"] = Field(
        default="low", exclude=True,
    )
    show_crisis_banner: bool = False


class ChatResponse(BaseModel):
    request_id: str
    thread_id: str
    runtime: str
    provider: str
    reply: str
    safety: SafetyResult
