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

    llm_provider: str = "auto"
    llm_api_key: str = ""
    llm_model: str = ""
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    max_depth: int = 2
    max_pages: int = 30
    request_delay_ms: int = 500
    navigation_timeout_ms: int = 15000

    database_path: str = "data/neurospider.db"
    monitoring_webhook_url: str = ""

    admin_user: str = "CryptonDevAlex"
    admin_email: str = "admin@neurospider.local"
    admin_password: str = "admin1234"
    jwt_secret_key: str = "cambia-esta-clave-secreta"
    access_token_expire_minutes: int = 10080

    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://127.0.0.1:8000/auth/google/callback"
    frontend_url: str = "http://127.0.0.1:3000"


@lru_cache
def get_settings() -> Settings:
    return Settings()
