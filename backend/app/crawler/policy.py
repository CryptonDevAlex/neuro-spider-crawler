from dataclasses import dataclass


@dataclass(frozen=True)
class CrawlPolicy:
    max_depth: int = 2
    max_pages: int = 30
    respect_robots: bool = True
    delay_ms: int = 500
    timeout_ms: int = 15000
