from app.core.settings import Settings
from app.providers.router import ProviderRouter


def test_provider_router_falls_back_to_mock_when_minimax_disabled() -> None:
    settings = Settings(CHAT_PROVIDER="minimax", FEATURE_MINIMAX_ENABLED=False)
    router = ProviderRouter(settings)

    provider = router.resolve_chat_provider()

    assert provider.provider_name == "mock"


def test_provider_router_uses_minimax_when_enabled() -> None:
    settings = Settings(CHAT_PROVIDER="minimax", FEATURE_MINIMAX_ENABLED=True)
    router = ProviderRouter(settings)

    provider = router.resolve_chat_provider()

    assert provider.provider_name == "minimax"
