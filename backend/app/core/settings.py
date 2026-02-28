from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(str(REPO_ROOT / ".env"), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    app_name: str = "CompanionHK API"
    app_env: str = Field(default="development", alias="APP_ENV")
    backend_host: str = Field(default="0.0.0.0", alias="BACKEND_HOST")
    backend_port: int = Field(default=8000, alias="BACKEND_PORT")
    frontend_origin: str = Field(
        default="http://localhost:3000", alias="FRONTEND_ORIGIN")
    chat_provider: str = Field(default="mock", alias="CHAT_PROVIDER")
    feature_langgraph_enabled: bool = Field(
        default=False, alias="FEATURE_LANGGRAPH_ENABLED")
    langgraph_checkpointer_backend: str = Field(
        default="memory", alias="LANGGRAPH_CHECKPOINTER_BACKEND")

    feature_minimax_enabled: bool = Field(
        default=False, alias="FEATURE_MINIMAX_ENABLED")
    feature_elevenlabs_enabled: bool = Field(
        default=False, alias="FEATURE_ELEVENLABS_ENABLED")
    feature_cantoneseai_enabled: bool = Field(
        default=False, alias="FEATURE_CANTONESEAI_ENABLED")
    feature_exa_enabled: bool = Field(
        default=False, alias="FEATURE_EXA_ENABLED")
    feature_aws_enabled: bool = Field(
        default=True, alias="FEATURE_AWS_ENABLED")

    memory_long_term_strategy: str = Field(
        default="hybrid_profile_retrieval", alias="MEMORY_LONG_TERM_STRATEGY")
    memory_retrieval_top_k: int = Field(
        default=5, alias="MEMORY_RETRIEVAL_TOP_K")


settings = Settings()
