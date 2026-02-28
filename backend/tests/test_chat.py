from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_chat_endpoint_returns_mock_supportive_response() -> None:
    payload = {
        "user_id": "test-user",
        "thread_id": "test-user-main-thread",
        "message": "I had a hard day and feel overwhelmed."
    }

    response = client.post("/chat", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "mock"
    assert body["runtime"] == "simple"
    assert body["thread_id"] == "test-user-main-thread"
    assert body["safety"]["risk_level"] == "low"
    assert body["safety"]["show_crisis_banner"] is False
    assert "here with you" in body["reply"].lower()


def test_chat_endpoint_generates_default_thread_id_when_missing() -> None:
    payload = {
        "user_id": "test-user",
        "message": "Can you check in with me?"
    }

    response = client.post("/chat", json=payload)

    assert response.status_code == 200
    assert response.json()["thread_id"] == "test-user-default-thread"
