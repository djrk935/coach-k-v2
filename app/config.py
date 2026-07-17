from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    anthropic_api_key: str
    llama_cloud_api_key: str | None = None
    openai_api_key: str | None = None

    chat_model: str = "claude-opus-4-8"
    fast_model: str = "claude-haiku-4-5-20251001"  # router + memory extraction
    embed_model: str = "text-embedding-3-small"
    embed_dim: int = 1536


settings = Settings()
