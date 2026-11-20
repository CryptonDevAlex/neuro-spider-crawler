from collections.abc import AsyncIterator
from uuid import UUID

from app.ai.client import LLMClient
from app.core.config import Settings
from app.crawler.policy import CrawlPolicy
from app.models.crawl import CrawlRequest, CrawlResult
from app.models.events import EventBase


class CrawlerService:
    def __init__(self, settings: Settings, llm: LLMClient) -> None:
        self.settings = settings
        self.llm = llm

    def policy_for(self, payload: CrawlRequest) -> CrawlPolicy:
        return CrawlPolicy(
            max_depth=payload.max_depth,
            max_pages=payload.max_pages,
            respect_robots=payload.respect_robots,
            delay_ms=self.settings.request_delay_ms,
            timeout_ms=self.settings.navigation_timeout_ms,
        )

    async def start(self, payload: CrawlRequest) -> tuple[UUID, CrawlResult]:
        raise NotImplementedError

    async def get(self, crawl_id: UUID) -> CrawlResult | None:
        raise NotImplementedError

    async def stream(self, crawl_id: UUID) -> AsyncIterator[EventBase]:
        raise NotImplementedError
        yield
