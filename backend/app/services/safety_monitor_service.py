import json
import logging
import re
from typing import Any

from app.core.settings import settings
from app.providers.minimax import MiniMaxChatProvider
from app.providers.router import ProviderRouter
from app.schemas.safety import SafetyEvaluateRequest, SafetyEvaluateResponse

logger = logging.getLogger(__name__)

_HIGH_RISK_PATTERNS = (
    "suicide",
    "kill myself",
    "end my life",
    "hurt myself",
    "self harm",
    "want to die",
    "die tonight",
    "jump off",
    "overdose",
    "cut myself",
    "想死",
    "自殺",
    "傷害自己",
)
_MEDIUM_RISK_PATTERNS = (
    "hopeless",
    "worthless",
    "can't go on",
    "overwhelmed",
    "panic",
    "depressed",
    "lonely",
    "anxious",
    "sad",
    "burned out",
    "好難受",
    "好絕望",
    "好焦慮",
)
_DIRECT_HARM_INTENT_PATTERNS = (
    "how to",
    "best way",
    "method",
    "steps",
    "plan",
    "teach me",
    "點樣",
    "方法",
)
_EMOTION_LEXICON: dict[str, tuple[str, float]] = {
    "anxious": ("anxious", 0.74),
    "panic": ("anxious", 0.86),
    "worried": ("anxious", 0.65),
    "sad": ("sad", 0.68),
    "depressed": ("sad", 0.84),
    "hopeless": ("sad", 0.86),
    "angry": ("angry", 0.7),
    "frustrated": ("angry", 0.67),
    "lonely": ("lonely", 0.73),
    "overwhelmed": ("overwhelmed", 0.72),
    "burned out": ("overwhelmed", 0.76),
    "stressed": ("overwhelmed", 0.66),
    "excited": ("positive", 0.61),
    "happy": ("positive", 0.66),
    "calm": ("calm", 0.61),
    "開心": ("positive", 0.7),
    "焦慮": ("anxious", 0.78),
    "難過": ("sad", 0.74),
    "孤單": ("lonely", 0.72),
}


class SafetyMonitorService:
    def __init__(self, provider_router: ProviderRouter | None = None):
        self._settings = settings
        self._provider_router = provider_router or ProviderRouter(settings)

    def evaluate(self, request: SafetyEvaluateRequest) -> SafetyEvaluateResponse:
        if not self._settings.feature_safety_monitor_enabled:
            fallback = self._evaluate_with_rules(request.message)
            fallback.degraded = True
            fallback.fallback_reason = "safety_monitor_disabled"
            return fallback

        if self._can_use_minimax():
            try:
                return self._evaluate_with_minimax(request)
            except Exception:
                logger.exception("safety_monitor_minimax_failed")
                fallback = self._evaluate_with_rules(request.message)
                fallback.degraded = True
                fallback.fallback_reason = "minimax_unavailable_or_invalid_response"
                return fallback

        fallback = self._evaluate_with_rules(request.message)
        fallback.degraded = True
        fallback.fallback_reason = "minimax_not_configured"
        return fallback

    def _can_use_minimax(self) -> bool:
        return bool(
            self._settings.feature_minimax_enabled and self._settings.minimax_api_key
        )

    def _evaluate_with_minimax(self, request: SafetyEvaluateRequest) -> SafetyEvaluateResponse:
        provider = MiniMaxChatProvider(
            api_key=self._settings.minimax_api_key,
            model=self._settings.minimax_safety_model,
            base_url=self._settings.minimax_base_url,
            temperature=0.0,
            max_tokens=300,
        )
        prompt = (
            "You are a safety and emotion classifier for a supportive chat app. "
            "Return only strict JSON with keys: risk_level, emotion_label, emotion_score, "
            "policy_action, rationale.\n"
            "risk_level must be one of: low, medium, high.\n"
            "policy_action must be one of: allow, supportive_refusal, escalate_banner.\n"
            "emotion_score must be 0..1.\n"
            "Classify this user message:\n"
            f"message: {request.message}"
        )
        raw = provider.generate_reply(
            request.message,
            {
                "role": request.role,
                "system_prompt": prompt,
                "thread_id": request.thread_id or "safety-eval",
                "user_id": request.user_id,
            },
        )
        parsed = self._parse_json_object(raw)
        risk_level = str(parsed.get("risk_level", "low")).lower()
        if risk_level not in {"low", "medium", "high"}:
            risk_level = "low"

        policy_action = str(parsed.get("policy_action", "allow")).lower()
        if policy_action not in {"allow", "supportive_refusal", "escalate_banner"}:
            policy_action = "allow"

        emotion_label = parsed.get("emotion_label")
        if emotion_label is not None:
            emotion_label = str(emotion_label).strip() or None

        emotion_score_raw = parsed.get("emotion_score")
        emotion_score: float | None = None
        if emotion_score_raw is not None:
            try:
                emotion_score = max(0.0, min(1.0, float(emotion_score_raw)))
            except (TypeError, ValueError):
                emotion_score = None

        rationale = parsed.get("rationale")
        if rationale is not None:
            rationale = str(rationale)

        show_banner = self._should_show_banner(risk_level=risk_level, policy_action=policy_action)
        if risk_level == "high" and policy_action == "allow":
            policy_action = "supportive_refusal"
            show_banner = True

        return SafetyEvaluateResponse(
            risk_level=risk_level,  # type: ignore[arg-type]
            show_crisis_banner=show_banner,
            emotion_label=emotion_label,
            emotion_score=emotion_score,
            policy_action=policy_action,  # type: ignore[arg-type]
            monitor_provider="minimax",
            degraded=False,
            fallback_reason=None,
            rationale=rationale,
        )

    def _evaluate_with_rules(self, message: str) -> SafetyEvaluateResponse:
        normalized = message.strip().lower()
        has_high_risk = any(token in normalized for token in _HIGH_RISK_PATTERNS)
        has_medium_risk = any(token in normalized for token in _MEDIUM_RISK_PATTERNS)
        has_direct_harm_intent = any(token in normalized for token in _DIRECT_HARM_INTENT_PATTERNS)

        emotion_label = "neutral"
        emotion_score = 0.42
        for token, emotion in _EMOTION_LEXICON.items():
            if token in normalized:
                emotion_label, emotion_score = emotion
                break

        if has_high_risk or (has_medium_risk and has_direct_harm_intent):
            return SafetyEvaluateResponse(
                risk_level="high",
                show_crisis_banner=True,
                emotion_label=emotion_label,
                emotion_score=max(emotion_score, 0.85),
                policy_action="supportive_refusal",
                monitor_provider="rules",
                degraded=False,
                fallback_reason=None,
                rationale="Detected self-harm indicators or direct harmful intent.",
            )

        if has_medium_risk:
            return SafetyEvaluateResponse(
                risk_level="medium",
                show_crisis_banner=False,
                emotion_label=emotion_label,
                emotion_score=max(emotion_score, 0.62),
                policy_action="allow",
                monitor_provider="rules",
                degraded=False,
                fallback_reason=None,
                rationale="Detected emotional distress without direct harmful intent.",
            )

        return SafetyEvaluateResponse(
            risk_level="low",
            show_crisis_banner=False,
            emotion_label=emotion_label,
            emotion_score=emotion_score,
            policy_action="allow",
            monitor_provider="rules",
            degraded=False,
            fallback_reason=None,
            rationale="No elevated harm signal detected.",
        )

    @staticmethod
    def _parse_json_object(raw: str) -> dict[str, Any]:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        json_str = match.group(0) if match else raw
        parsed = json.loads(json_str)
        if not isinstance(parsed, dict):
            raise ValueError("safety_model_response_not_object")
        return parsed

    @staticmethod
    def _should_show_banner(*, risk_level: str, policy_action: str) -> bool:
        if risk_level == "high":
            return True
        return policy_action in {"supportive_refusal", "escalate_banner"}
