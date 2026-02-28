from typing import Any

from app.providers.base import ChatProvider


class MiniMaxChatProvider(ChatProvider):
    provider_name = "minimax"

    def generate_reply(self, message: str, context: dict[str, Any] | None = None) -> str:
        _ = message
        role = (context or {}).get("role", "companion")
        _system_prompt = (context or {}).get("system_prompt")
        _ = _system_prompt

        if role == "local_guide":
            return (
                "MiniMax adapter stub is active for Local Guide. Share your preferred district and"
                " pace, and I can suggest nearby options."
            )
        if role == "study_guide":
            return (
                "MiniMax adapter stub is active for Study Guide. I can help you structure revision,"
                " prioritize topics, and track progress."
            )
        return (
            "MiniMax adapter stub is active. I hear what you are going through, and I am here to"
            " support you."
        )
