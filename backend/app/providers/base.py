from abc import ABC, abstractmethod
from typing import Any


class ChatProvider(ABC):
    provider_name: str

    @abstractmethod
    def generate_reply(self, message: str, context: dict[str, Any] | None = None) -> str:
        """Generate a supportive chat reply."""


class VoiceProvider(ABC):
    provider_name: str

    @abstractmethod
    def synthesize(self, text: str) -> bytes:
        """Return synthesized audio bytes."""


class RetrievalProvider(ABC):
    provider_name: str

    @abstractmethod
    def retrieve(self, query: str) -> list[dict[str, Any]]:
        """Return retrieval results for freshness/context enrichment."""
