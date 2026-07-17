from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    anthropic_api_key: str
    llama_cloud_api_key: str | None = None
    openai_api_key: str | None = None

    chat_model: str = "claude-opus-4-8"
    fast_model: str = "claude-haiku-4-5-20251001"  # router + memory extraction

    # Deployment
    app_password: str | None = None  # set in prod: gates /api/* behind x-app-key
    cors_origins: str = "http://localhost:5173"  # comma-separated
    embed_model: str = "BAAI/bge-base-en-v1.5"  # local via fastembed — free, private
    embed_dim: int = 768


settings = Settings()
