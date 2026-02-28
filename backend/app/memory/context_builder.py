from typing import Any

from app.core.settings import Settings
from app.schemas.chat import ChatRole


class ConversationContextBuilder:
    """
    Foundation memory context builder.

    This defines a single context shape that future memory adapters
    (Redis, Postgres profile memory, pgvector retrieval) can populate.
    """

    def __init__(self, settings: Settings):
        self._settings = settings

    def build(
        self,
        *,
        user_id: str,
        thread_id: str,
        role: ChatRole,
        message: str
    ) -> dict[str, Any]:
        _ = message
        return {
            "user_id": user_id,
            "thread_id": thread_id,
            "role": role,
            "memory": {
                "strategy": self._settings.memory_long_term_strategy,
                "short_term": {
                    "source": "redis",
                    "status": "stubbed"
                },
                "long_term_profile": {
                    "source": "postgres",
                    "status": "stubbed"
                },
                "long_term_retrieval": {
                    "source": "pgvector",
                    "top_k": self._settings.memory_retrieval_top_k,
                    "status": "stubbed"
                }
            }
        }
