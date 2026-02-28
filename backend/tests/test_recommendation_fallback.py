from app.providers.google_maps import StubMapsProvider
from app.schemas.recommendations import RecommendationRequest
from app.schemas.weather import WeatherData, WeatherResponse
from app.services.recommendation_service import RecommendationService


class _FakeProviderRouter:
    def resolve_maps_provider(self):
        return StubMapsProvider()


class _FakeWeatherService:
    def get_current_weather(self, *, latitude: float, longitude: float, timezone: str = "auto"):
        _ = timezone
        return WeatherResponse(
            request_id="weather-request-1",
            weather=WeatherData(
                latitude=latitude,
                longitude=longitude,
                temperature_c=24.0,
                condition="cloudy",
                source="open-meteo",
            ),
            degraded=False,
            fallback_reason=None,
        )


def test_fallback_recommendations_use_realistic_hong_kong_places() -> None:
    service = RecommendationService(
        provider_router=_FakeProviderRouter(),
        weather_service=_FakeWeatherService(),
    )
    request = RecommendationRequest(
        user_id="test-user",
        role="local_guide",
        query="nice parks near hung hom",
        latitude=22.3030,
        longitude=114.1820,
        max_results=5,
        travel_mode="walking",
    )

    response = service.generate_recommendations(request)

    assert response.context.degraded is True
    assert response.context.fallback_reason in {
        "maps_provider_disabled_or_unavailable",
        "live_place_search_empty",
        "insufficient_live_place_results",
    }
    assert len(response.recommendations) >= 3
    assert response.recommendations[0].name != "Nearby Cafe Option"
    assert response.recommendations[0].maps_uri is not None
    assert "google.com/maps/search/" in response.recommendations[0].maps_uri
