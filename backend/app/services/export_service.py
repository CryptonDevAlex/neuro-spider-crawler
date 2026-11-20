from app.models.crawl import CrawlResult


def to_json(result: CrawlResult) -> str:
    raise NotImplementedError


def to_markdown(result: CrawlResult) -> str:
    raise NotImplementedError
