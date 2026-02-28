from abc import ABC, abstractmethod
from typing import Any

from app.providers.base import ChatProvider


class ConversationRuntime(ABC):
    runtime_name: str

    @abstractmethod
    def generate_reply(
        self,
        *,
        message: str,
        provider: ChatProvider,
        context: dict[str, Any]
    ) -> str:
        """Generate a model response using the configured orchestration runtime."""
