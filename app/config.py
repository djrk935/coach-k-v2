from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def normalize_database_url(url: str) -> str:
    """App Platform and Heroku often use postgres://; drivers expect postgresql://."""
    u = url.strip()
    if u.startswith("postgres://"):
        return "postgresql://" + u[len("postgres://") :]
    return u


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str

    @field_validator("database_url", mode="before")
    @classmethod
    def _normalize_database_url(cls, v: str) -> str:
        return normalize_database_url(v)
    anthropic_api_key: str
    llama_cloud_api_key: str | None = None
    openai_api_key: str | None = None

    chat_model: str = "claude-opus-4-8"
    fast_model: str = "claude-haiku-4-5-20251001"  # router + memory extraction

    # Deployment
    app_password: str | None = None  # set in prod: gates /api/* behind x-app-key
    # Comma-separated. Production serves the UI from the same origin — localhost
    # is only for Vite dev. Set CORS_ORIGINS=https://your-app.ondigitalocean.app
    # if you split frontend and API.
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Push notifications (web push / VAPID)
    vapid_public_key: str | None = None
    vapid_private_key: str | None = None
    vapid_subject: str = "mailto:coach@coach-k.local"
    embed_model: str = "BAAI/bge-base-en-v1.5"  # local via fastembed — free, private
    embed_dim: int = 768


settings = Settings()
