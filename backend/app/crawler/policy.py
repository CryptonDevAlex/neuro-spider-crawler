from dataclasses import dataclass


@dataclass(frozen=True)
class CrawlPolicy:
    max_depth: int = 2
    max_pages: int = 30
    respect_robots: bool = False
    delay_ms: int = 500
    timeout_ms: int = 15000
    user_agent: str = "NeuroSpider/0.2 (+https://github.com/CryptonDevAlex/neuro-spider-crawler)"
