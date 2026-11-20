from app.ai.client import LLMClient
from app.core.config import Settings, get_settings
from app.services.crawler_service import CrawlerService

_app_settings = get_settings()
_llm_client = LLMClient(
    api_key=_app_settings.llm_api_key,
    base_url=_app_settings.llm_base_url,
    model=_app_settings.llm_model,
)
_crawler_service = CrawlerService(settings=_app_settings, llm=_llm_client)


def get_app_settings() -> Settings:
    return _app_settings


def get_crawler_service() -> CrawlerService:
    return _crawler_service
