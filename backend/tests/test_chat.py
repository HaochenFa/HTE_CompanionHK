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


def test_role_specific_chat_aliases_force_expected_role(monkeypatch) -> None:
    captured_roles: list[str] = []

    def fake_generate_reply(payload):
        captured_roles.append(payload.role)
        return {
            "request_id": "r-1",
            "thread_id": payload.thread_id or f"{payload.user_id}-{payload.role}-thread",
            "runtime": "simple",
            "provider": "mock",
            "reply": "ok",
            "safety": {
                "risk_level": "low",
                "show_crisis_banner": False,
                "policy_action": "allow",
                "monitor_provider": "rules",
                "degraded": False,
                "fallback_reason": None,
            },
        }

    monkeypatch.setattr(chat_route.orchestrator, "generate_reply", fake_generate_reply)

    common_payload = {
        "user_id": "test-user",
        "thread_id": "thread-1",
        "message": "hello",
    }
    assert client.post("/chat/companion", json=common_payload).status_code == 200
    assert client.post("/chat/guide", json=common_payload).status_code == 200
    assert client.post("/chat/study", json=common_payload).status_code == 200
    assert captured_roles == ["companion", "local_guide", "study_guide"]


def test_chat_history_endpoint_returns_turns(monkeypatch) -> None:
    def fake_get_history(*, user_id: str, role: str, thread_id: str | None, limit: int):
        _ = role, limit
        return {
            "user_id": user_id,
            "role": "companion",
            "thread_id": thread_id or "test-user-companion-thread",
            "turns": [
                {
                    "request_id": "turn-1",
                    "thread_id": thread_id or "test-user-companion-thread",
                    "created_at": "2026-02-28T00:00:00Z",
                    "user_message": "hi",
                    "assistant_reply": "hello",
                    "safety": {
                        "risk_level": "low",
                        "show_crisis_banner": False,
                        "policy_action": "allow",
                        "monitor_provider": "rules",
                        "degraded": False,
                        "fallback_reason": None,
                    },
                }
            ],
        }

    monkeypatch.setattr(chat_route.orchestrator, "get_history", fake_get_history)
    response = client.get("/chat/history", params={"user_id": "test-user", "role": "companion"})

    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == "test-user"
    assert body["role"] == "companion"
    assert len(body["turns"]) == 1
    assert body["turns"][0]["request_id"] == "turn-1"


def test_chat_guide_history_alias_forces_local_guide_role(monkeypatch) -> None:
    captured: dict[str, str] = {}

    def fake_get_history(*, user_id: str, role: str, thread_id: str | None, limit: int):
        _ = user_id, thread_id, limit
        captured["role"] = role
        return {
            "user_id": "test-user",
            "role": role,
            "thread_id": "test-user-local_guide-thread",
            "turns": [],
        }

    monkeypatch.setattr(chat_route.orchestrator, "get_history", fake_get_history)
    response = client.get("/chat/guide/history", params={"user_id": "test-user"})
    assert response.status_code == 200
    assert captured["role"] == "local_guide"
    assert response.json()["role"] == "local_guide"


def test_api_prefixed_chat_alias_reaches_backend(monkeypatch) -> None:
    captured_roles: list[str] = []

    def fake_generate_reply(payload):
        captured_roles.append(payload.role)
        return {
            "request_id": "r-api-1",
            "thread_id": payload.thread_id or f"{payload.user_id}-{payload.role}-thread",
            "runtime": "simple",
            "provider": "mock",
            "reply": "ok",
            "safety": {
                "risk_level": "low",
                "show_crisis_banner": False,
                "policy_action": "allow",
                "monitor_provider": "rules",
                "degraded": False,
                "fallback_reason": None,
            },
        }

    monkeypatch.setattr(chat_route.orchestrator, "generate_reply", fake_generate_reply)

    payload = {
        "user_id": "test-user",
        "thread_id": "thread-api-1",
        "message": "hello",
    }
    response = client.post("/api/chat/companion", json=payload)

    assert response.status_code == 200
    assert captured_roles == ["companion"]
