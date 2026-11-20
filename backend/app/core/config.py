from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "NeuroSpider"
    environment: str = "development"
    debug: bool = True
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    llm_provider: str = "openai-compatible"
    llm_api_key: str = ""
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o-mini"

    max_depth: int = 2
    max_pages: int = 30
    request_delay_ms: int = 500
    navigation_timeout_ms: int = 15000


@lru_cache
def get_settings() -> Settings:
    return Settings()
