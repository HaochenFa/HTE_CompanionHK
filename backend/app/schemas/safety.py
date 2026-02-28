from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.chat import ChatRole

SafetyPolicyAction = Literal["allow", "supportive_refusal", "escalate_banner"]


class SafetyEvaluateRequest(BaseModel):
    user_id: str = Field(min_length=1)
    role: ChatRole = "companion"
    thread_id: str | None = Field(default=None, min_length=1)
    message: str = Field(min_length=1)


class SafetyEvaluateResponse(BaseModel):
    risk_level: Literal["low", "medium", "high"] = "low"
    show_crisis_banner: bool = False
    emotion_label: str | None = None
    emotion_score: float | None = Field(default=None, ge=0.0, le=1.0)
    policy_action: SafetyPolicyAction = "allow"
    monitor_provider: Literal["minimax", "rules"] = "rules"
    degraded: bool = False
    fallback_reason: str | None = None
    rationale: str | None = None
