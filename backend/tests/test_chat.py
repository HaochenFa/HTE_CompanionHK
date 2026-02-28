from fastapi.testclient import TestClient

from app.api.routes import chat as chat_route
from app.main import app
from app.schemas.safety import SafetyEvaluateResponse


client = TestClient(app)


def test_chat_endpoint_returns_mock_supportive_response() -> None:
    payload = {
        "user_id": "test-user",
        "thread_id": "test-user-companion-thread",
        "role": "companion",
        "message": "I had a hard day and feel overwhelmed."
    }

    response = client.post("/chat", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "mock"
    assert body["runtime"] == "simple"
    assert body["thread_id"] == "test-user-companion-thread"
    assert body["safety"]["risk_level"] in {"low", "medium"}
    assert body["safety"]["show_crisis_banner"] is False
    assert body["safety"]["monitor_provider"] in {"rules", "minimax"}
    assert "here with you" in body["reply"].lower()


def test_chat_endpoint_uses_companion_default_role_and_thread_when_missing() -> None:
    payload = {
        "user_id": "test-user",
        "message": "Can you check in with me?"
    }

    response = client.post("/chat", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["thread_id"] == "test-user-companion-thread"
    assert "here with you" in body["reply"].lower()


def test_chat_endpoint_generates_role_scoped_default_thread_id() -> None:
    payload = {
        "user_id": "test-user",
        "role": "local_guide",
        "message": "I want to explore Kowloon this afternoon."
    }

    response = client.post("/chat", json=payload)

    assert response.status_code == 200
    assert response.json()["thread_id"] == "test-user-local_guide-thread"


def test_chat_endpoint_rejects_unknown_role() -> None:
    payload = {
        "user_id": "test-user",
        "role": "unknown_role",
        "message": "hello"
    }

    response = client.post("/chat", json=payload)

    assert response.status_code == 422


def test_chat_endpoint_high_risk_returns_supportive_refusal_and_banner(monkeypatch) -> None:
    def fake_evaluate(_request) -> SafetyEvaluateResponse:
        return SafetyEvaluateResponse(
            risk_level="high",
            show_crisis_banner=True,
            emotion_label="sad",
            emotion_score=0.93,
            policy_action="supportive_refusal",
            monitor_provider="rules",
            degraded=False,
            fallback_reason=None,
            rationale="test",
        )

    monkeypatch.setattr(chat_route.orchestrator._safety_monitor_service, "evaluate", fake_evaluate)

    payload = {
        "user_id": "test-user",
        "thread_id": "test-user-companion-thread",
        "role": "companion",
        "message": "I want to kill myself.",
    }
    response = client.post("/chat", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["safety"]["risk_level"] == "high"
    assert body["safety"]["show_crisis_banner"] is True
    assert body["safety"]["policy_action"] == "supportive_refusal"
    assert "cannot help with anything that could harm you" in body["reply"].lower()
