from app.core.settings import Settings
from app.runtime.base import ConversationRuntime
from app.runtime.langgraph_runtime import LangGraphConversationRuntime
from app.runtime.simple_runtime import SimpleConversationRuntime


def build_runtime(settings: Settings) -> ConversationRuntime:
    if settings.feature_langgraph_enabled:
        return LangGraphConversationRuntime(
            checkpointer_backend=settings.langgraph_checkpointer_backend
        )
    return SimpleConversationRuntime()
