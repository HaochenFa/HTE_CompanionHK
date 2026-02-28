from fastapi.testclient import TestClient

from app.api.routes import health as health_route
from app.main import app
from app.schemas.health import DependencyStatus


client = TestClient(app)


def test_health_endpoint_returns_service_status() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "companionhk-api"}


def test_health_dependencies_returns_ready_payload(monkeypatch) -> None:
    monkeypatch.setattr(
        health_route,
        "_collect_dependency_statuses",
        lambda: {
            "db": DependencyStatus(status="ok", detail="db_connected"),
            "redis": DependencyStatus(status="ok", detail="redis_connected"),
            "chat_provider": DependencyStatus(status="ok", detail="mock"),
            "safety_provider": DependencyStatus(status="ok", detail="rules"),
            "maps": DependencyStatus(status="degraded", detail="maps-stub"),
            "weather": DependencyStatus(status="ok", detail="open-meteo"),
            "exa": DependencyStatus(status="degraded", detail="retrieval-stub"),
            "voice": DependencyStatus(status="degraded", detail=None),
        },
    )
    response = client.get("/health/dependencies")

    assert response.status_code == 200
    body = response.json()
    assert body["ready"] is True
    assert body["dependencies"]["db"]["status"] == "ok"


def test_ready_returns_503_when_required_dependencies_fail(monkeypatch) -> None:
    monkeypatch.setattr(
        health_route,
        "_collect_dependency_statuses",
        lambda: {
            "db": DependencyStatus(status="failed", detail="db_unreachable"),
            "redis": DependencyStatus(status="ok", detail="redis_connected"),
            "chat_provider": DependencyStatus(status="ok", detail="mock"),
            "safety_provider": DependencyStatus(status="ok", detail="rules"),
            "maps": DependencyStatus(status="degraded", detail="maps-stub"),
            "weather": DependencyStatus(status="ok", detail="open-meteo"),
            "exa": DependencyStatus(status="degraded", detail="retrieval-stub"),
            "voice": DependencyStatus(status="degraded", detail=None),
        },
    )
    response = client.get("/ready")

    assert response.status_code == 503
    assert response.json()["ready"] is False
