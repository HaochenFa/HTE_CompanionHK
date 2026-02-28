from app.core.settings import Settings
from app.providers.router import ProviderRouter


def test_provider_router_falls_back_to_mock_when_minimax_disabled() -> None:
    settings = Settings(CHAT_PROVIDER="minimax", FEATURE_MINIMAX_ENABLED=False)
    router = ProviderRouter(settings)

    provider = router.resolve_chat_provider()

    assert provider.provider_name == "mock"


def test_provider_router_uses_minimax_when_enabled() -> None:
    settings = Settings(
        CHAT_PROVIDER="minimax",
        FEATURE_MINIMAX_ENABLED=True,
        MINIMAX_API_KEY="test-minimax-key",
    )
    router = ProviderRouter(settings)

    provider = router.resolve_chat_provider()

    assert provider.provider_name == "minimax"


def test_provider_router_falls_back_to_mock_when_minimax_key_missing() -> None:
    settings = Settings(CHAT_PROVIDER="minimax", FEATURE_MINIMAX_ENABLED=True)
    router = ProviderRouter(settings)

    provider = router.resolve_chat_provider()

    assert provider.provider_name == "mock"


def test_provider_router_uses_open_meteo_when_weather_enabled() -> None:
    settings = Settings(FEATURE_WEATHER_ENABLED=True)
    router = ProviderRouter(settings)

    provider = router.resolve_weather_provider()

    assert provider.provider_name == "open-meteo"


def test_provider_router_uses_weather_stub_when_weather_disabled() -> None:
    settings = Settings(FEATURE_WEATHER_ENABLED=False)
    router = ProviderRouter(settings)

    provider = router.resolve_weather_provider()

    assert provider.provider_name == "weather-stub"


def test_provider_router_uses_google_maps_when_enabled_and_key_available() -> None:
    settings = Settings(
        FEATURE_GOOGLE_MAPS_ENABLED=True,
        GOOGLE_MAPS_API_KEY="test-key"
    )
    router = ProviderRouter(settings)

    provider = router.resolve_maps_provider()

    assert provider.provider_name == "google-maps"


def test_provider_router_uses_maps_stub_when_key_missing() -> None:
    settings = Settings(
        FEATURE_GOOGLE_MAPS_ENABLED=True,
        GOOGLE_MAPS_API_KEY=""
    )
    router = ProviderRouter(settings)

    provider = router.resolve_maps_provider()

    assert provider.provider_name == "maps-stub"


def test_provider_router_uses_exa_when_enabled_and_key_available() -> None:
    settings = Settings(
        FEATURE_EXA_ENABLED=True,
        EXA_API_KEY="exa-key",
    )
    router = ProviderRouter(settings)

    provider = router.resolve_retrieval_provider()

    assert provider.provider_name == "exa"


def test_provider_router_uses_stub_retrieval_when_exa_disabled() -> None:
    settings = Settings(
        FEATURE_EXA_ENABLED=False,
        EXA_API_KEY="",
    )
    router = ProviderRouter(settings)

    provider = router.resolve_retrieval_provider()

    assert provider.provider_name == "retrieval-stub"


def test_provider_router_safety_uses_minimax_model_when_available() -> None:
    settings = Settings(
        FEATURE_MINIMAX_ENABLED=True,
        MINIMAX_API_KEY="test-minimax-key",
        MINIMAX_SAFETY_MODEL="MiniMax-M2",
    )
    router = ProviderRouter(settings)

    provider = router.resolve_safety_provider()

    assert provider.provider_name == "minimax"


def test_provider_router_safety_falls_back_to_mock_when_unavailable() -> None:
    settings = Settings(
        FEATURE_MINIMAX_ENABLED=False,
        MINIMAX_API_KEY="",
    )
    router = ProviderRouter(settings)

    provider = router.resolve_safety_provider()

    assert provider.provider_name == "mock"
