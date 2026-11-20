from app.crawler.policy import CrawlPolicy
from app.models.crawl import PageNode


class Spider:
    def __init__(self, policy: CrawlPolicy) -> None:
        self.policy = policy
        self.visited: set[str] = set()

    async def crawl(self, start_url: str) -> list[PageNode]:
        raise NotImplementedError
