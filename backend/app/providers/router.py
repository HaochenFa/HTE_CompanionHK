from app.core.settings import Settings
from app.providers.base import ChatProvider
from app.providers.minimax import MiniMaxChatProvider
from app.providers.mock import MockChatProvider


class ProviderRouter:
    def __init__(self, settings: Settings):
        self._settings = settings

    def resolve_chat_provider(self) -> ChatProvider:
        if self._settings.chat_provider == "minimax" and self._settings.feature_minimax_enabled:
            return MiniMaxChatProvider()
        return MockChatProvider()
