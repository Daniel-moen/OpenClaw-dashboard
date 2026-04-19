"""Application configuration loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = BACKEND_ROOT.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(REPO_ROOT / ".env", BACKEND_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    admin_password: str = Field("changeme-please", description="Single-user admin password.")
    session_secret: str = Field(
        "dev-only-secret-change-me",
        description="HMAC secret used to sign session cookies.",
    )
    frontend_origin: str = Field("http://localhost:5173")
    max_upload_mb: int = Field(25, ge=1, le=2048)
    data_dir: str = Field("data")

    jobcarver_stats_url: str | None = None
    jobcarver_stats_token: str | None = None

    # Optional LLM provider for the chat. OpenAI-compatible endpoint -- works
    # with OpenAI, OpenRouter, Together, local Ollama (with /v1), etc.
    # Leave empty to disable; chat will use a friendly offline reply.
    openai_api_key: str | None = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"
    assistant_name: str = "Mia"

    @property
    def data_path(self) -> Path:
        p = Path(self.data_dir)
        if not p.is_absolute():
            p = BACKEND_ROOT / p
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def uploads_path(self) -> Path:
        p = self.data_path / "uploads"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def db_path(self) -> Path:
        return self.data_path / "app.db"

    @property
    def cookie_secure(self) -> bool:
        return self.frontend_origin.startswith("https://")


@lru_cache
def get_settings() -> Settings:
    return Settings()
