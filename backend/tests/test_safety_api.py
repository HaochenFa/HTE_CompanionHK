import pytest
from fastapi.testclient import TestClient

from app.api.routes import safety as safety_route
from app.main import app
from app.schemas.safety import SafetyEvaluateRequest, SafetyEvaluateResponse
from app.services.safety_monitor_service import SafetyMonitorService

client = TestClient(app)


def test_safety_evaluate_endpoint_returns_payload(monkeypatch) -> None:
    def fake_evaluate(_request: SafetyEvaluateRequest) -> SafetyEvaluateResponse:
        return SafetyEvaluateResponse(
            risk_level="medium",
            show_crisis_banner=False,
            emotion_label="anxious",
            emotion_score=0.71,
            policy_action="allow",
            monitor_provider="rules",
            degraded=False,
            fallback_reason=None,
            rationale="test",
        )

    monkeypatch.setattr(safety_route.safety_monitor_service, "evaluate", fake_evaluate)

    response = client.post(
        "/safety/evaluate",
        json={
            "user_id": "test-user",
            "role": "companion",
            "thread_id": "t-1",
            "message": "I feel overwhelmed today",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["risk_level"] == "medium"
    assert body["emotion_label"] == "anxious"
    assert body["policy_action"] == "allow"


def test_safety_monitor_rules_classifier_detects_high_risk() -> None:
    service = SafetyMonitorService()

    result = service.evaluate(
        SafetyEvaluateRequest(
            user_id="test-user",
            role="companion",
            message="I want to kill myself tonight.",
        )
    )

    assert result.risk_level == "high"
    assert result.show_crisis_banner is True
    assert result.policy_action == "supportive_refusal"


def test_safety_monitor_falls_back_to_rules_when_minimax_fails(monkeypatch) -> None:
    service = SafetyMonitorService()
    monkeypatch.setattr(service, "_can_use_minimax", lambda: True)

    def raise_error(_request: SafetyEvaluateRequest):
        raise RuntimeError("boom")

    monkeypatch.setattr(service, "_evaluate_with_minimax", raise_error)

    result = service.evaluate(
        SafetyEvaluateRequest(
            user_id="test-user",
            role="companion",
            message="I feel hopeless.",
        )
    )

    assert result.monitor_provider == "rules"
    assert result.degraded is True
    assert result.fallback_reason == "minimax_unavailable_or_invalid_response"


def test_safety_monitor_parse_json_object_handles_think_and_fenced_json() -> None:
    raw = (
        "<think>\n"
        "internal notes\n"
        "</think>\n"
        "```json\n"
        "{\"risk_level\":\"low\",\"policy_action\":\"allow\"}\n"
        "```"
    )
    parsed = SafetyMonitorService._parse_json_object(raw)
    assert parsed["risk_level"] == "low"
    assert parsed["policy_action"] == "allow"


def test_safety_monitor_parse_json_object_raises_for_non_json() -> None:
    with pytest.raises(ValueError):
        SafetyMonitorService._parse_json_object("<think>no json at all</think>")
