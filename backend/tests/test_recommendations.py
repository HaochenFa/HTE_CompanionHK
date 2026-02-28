from fastapi.testclient import TestClient

from app.api.routes import recommendations as recommendations_route
from app.main import app
from app.schemas.recommendations import (
    Coordinates,
    RecommendationContext,
    RecommendationItem,
    RecommendationRequest,
    RecommendationResponse
)

client = TestClient(app)


def test_recommendations_endpoint_returns_ranked_results(monkeypatch) -> None:
    def fake_generate_recommendations(request: RecommendationRequest) -> RecommendationResponse:
        assert request.role == "local_guide"
        assert request.max_results == 5
        return RecommendationResponse(
            request_id="recommendation-request-1",
            recommendations=[
                RecommendationItem(
                    place_id="place-1",
                    name="Sample Cafe",
                    address="Central, Hong Kong",
                    rating=4.6,
                    user_ratings_total=800,
                    types=["cafe", "food"],
                    location=Coordinates(latitude=22.281, longitude=114.158),
                    photo_url=None,
                    maps_uri="https://www.google.com/maps/place/?q=place_id:place-1",
                    distance_text="1.1 km",
                    duration_text="15 mins",
                    fit_score=0.87,
                    rationale="Matches your cafe query with strong rating and convenient distance."
                ),
                RecommendationItem(
                    place_id="place-2",
                    name="Sample Park",
                    address="Admiralty, Hong Kong",
                    rating=4.4,
                    user_ratings_total=500,
                    types=["park", "point_of_interest"],
                    location=Coordinates(latitude=22.279, longitude=114.166),
                    photo_url=None,
                    maps_uri=None,
                    distance_text="1.8 km",
                    duration_text="24 mins",
                    fit_score=0.75,
                    rationale="A practical outdoor option for your route."
                ),
                RecommendationItem(
                    place_id="place-3",
                    name="Sample Museum",
                    address="Wan Chai, Hong Kong",
                    rating=4.3,
                    user_ratings_total=320,
                    types=["museum", "point_of_interest"],
                    location=Coordinates(latitude=22.277, longitude=114.175),
                    photo_url=None,
                    maps_uri=None,
                    distance_text="2.2 km",
                    duration_text="28 mins",
                    fit_score=0.71,
                    rationale="Indoor fallback that fits uncertain weather."
                )
            ],
            context=RecommendationContext(
                weather_condition="cloudy",
                temperature_c=26.5,
                degraded=False,
                fallback_reason=None
            )
        )

    monkeypatch.setattr(
        recommendations_route.recommendation_service,
        "generate_recommendations",
        fake_generate_recommendations
    )

    payload = {
        "user_id": "test-user",
        "role": "local_guide",
        "query": "quiet cafe in central",
        "latitude": 22.281,
        "longitude": 114.158,
        "max_results": 5,
        "travel_mode": "walking"
    }
    response = client.post("/recommendations", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["request_id"] == "recommendation-request-1"
    assert len(body["recommendations"]) == 3
    assert body["recommendations"][0]["fit_score"] >= body["recommendations"][1]["fit_score"]
    assert body["context"]["degraded"] is False


def test_recommendations_endpoint_validates_max_results_range() -> None:
    payload = {
        "user_id": "test-user",
        "role": "local_guide",
        "query": "food",
        "latitude": 22.281,
        "longitude": 114.158,
        "max_results": 2
    }
    response = client.post("/recommendations", json=payload)

    assert response.status_code == 422


def test_recommendations_endpoint_rejects_non_local_guide_role() -> None:
    payload = {
        "user_id": "test-user",
        "role": "companion",
        "query": "food",
        "latitude": 22.281,
        "longitude": 114.158,
    }
    response = client.post("/recommendations", json=payload)

    assert response.status_code == 422


def test_recommendations_endpoint_uses_chat_request_id_when_provided(monkeypatch) -> None:
    def fake_generate_recommendations(request: RecommendationRequest) -> RecommendationResponse:
        assert request.chat_request_id == "chat-turn-123"
        return RecommendationResponse(
            request_id=request.chat_request_id or "fallback-request-id",
            recommendations=[],
            context=RecommendationContext(
                weather_condition="unknown",
                temperature_c=None,
                degraded=False,
                fallback_reason=None,
            ),
        )

    monkeypatch.setattr(
        recommendations_route.recommendation_service,
        "generate_recommendations",
        fake_generate_recommendations,
    )
    response = client.post(
        "/recommendations",
        json={
            "user_id": "test-user",
            "role": "local_guide",
            "query": "cafe",
            "latitude": 22.281,
            "longitude": 114.158,
            "chat_request_id": "chat-turn-123",
        },
    )
    assert response.status_code == 200
    assert response.json()["request_id"] == "chat-turn-123"


def test_recommendation_history_endpoint_returns_batch(monkeypatch) -> None:
    def fake_get_history(*, user_id: str, role: str, request_ids: list[str]):
        assert user_id == "test-user"
        assert role == "local_guide"
        assert request_ids == ["turn-1", "turn-2"]
        return {
            "results": [
                {
                    "request_id": "turn-1",
                    "recommendations": [],
                    "context": {
                        "weather_condition": "cloudy",
                        "temperature_c": 26.2,
                        "degraded": False,
                        "fallback_reason": None,
                    },
                }
            ]
        }

    monkeypatch.setattr(recommendations_route.recommendation_service, "get_history", fake_get_history)
    response = client.post(
        "/recommendations/history",
        json={
            "user_id": "test-user",
            "role": "local_guide",
            "request_ids": ["turn-1", "turn-2"],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["results"]) == 1
    assert body["results"][0]["request_id"] == "turn-1"


def test_api_prefixed_recommendations_history_endpoint_returns_batch(monkeypatch) -> None:
    def fake_get_history(*, user_id: str, role: str, request_ids: list[str]):
        assert user_id == "test-user"
        assert role == "local_guide"
        assert request_ids == ["turn-1"]
        return {
            "results": [
                {
                    "request_id": "turn-1",
                    "recommendations": [],
                    "context": {
                        "weather_condition": "cloudy",
                        "temperature_c": 25.0,
                        "degraded": False,
                        "fallback_reason": None,
                    },
                }
            ]
        }

    monkeypatch.setattr(recommendations_route.recommendation_service, "get_history", fake_get_history)
    response = client.post(
        "/api/recommendations/history",
        json={
            "user_id": "test-user",
            "role": "local_guide",
            "request_ids": ["turn-1"],
        },
    )
    assert response.status_code == 200
    assert response.json()["results"][0]["request_id"] == "turn-1"
