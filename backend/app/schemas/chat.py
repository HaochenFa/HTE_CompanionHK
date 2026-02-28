from typing import Literal
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    user_id: str = Field(min_length=1)
    message: str = Field(min_length=1)
    thread_id: str | None = Field(default=None, min_length=1)


class SafetyResult(BaseModel):
    risk_level: Literal["low", "medium", "high"] = "low"
    show_crisis_banner: bool = False


class ChatResponse(BaseModel):
    request_id: str
    thread_id: str
    runtime: str
    provider: str
    reply: str
    safety: SafetyResult
