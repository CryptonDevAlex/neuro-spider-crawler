from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, HttpUrl


class CrawlStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class CrawlRequest(BaseModel):
    url: HttpUrl
    max_depth: int = 2
    max_pages: int = 30
    respect_robots: bool = True


class CrawlAccepted(BaseModel):
    crawl_id: UUID
    status: CrawlStatus = CrawlStatus.QUEUED


class PageNode(BaseModel):
    id: str
    url: HttpUrl
    title: str
    depth: int
    links: int
    word_count: int
    text: str = ""


class TableData(BaseModel):
    node_id: str
    headers: list[str]
    rows: list[list[str]]


class KeyPoint(BaseModel):
    text: str
    weight: float = 0.0


class ExecutiveSummary(BaseModel):
    executive_summary: str
    key_points: list[KeyPoint]
    entities: list[str]


class CrawlResult(BaseModel):
    crawl_id: UUID
    status: CrawlStatus
    nodes: list[PageNode] = []
    tables: list[TableData] = []
    summary: ExecutiveSummary | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
