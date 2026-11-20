from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.core.events import EventType


class EventBase(BaseModel):
    type: EventType
    crawl_id: UUID
    timestamp: datetime


class StatusEvent(EventBase):
    type: EventType = EventType.STATUS
    phase: str
    pages_done: int
    pages_total: int


class NodeEvent(EventBase):
    type: EventType = EventType.NODE
    id: str
    url: str
    title: str
    depth: int
    links: int
    word_count: int


class TableEvent(EventBase):
    type: EventType = EventType.TABLE
    node_id: str
    headers: list[str]
    rows: list[list[str]]


class SummaryEvent(EventBase):
    type: EventType = EventType.SUMMARY
    executive_summary: str
    key_points: list[str]
    entities: list[str]


class ErrorEvent(EventBase):
    type: EventType = EventType.ERROR
    code: str
    message: str
    node_id: str | None = None


class DoneEvent(EventBase):
    type: EventType = EventType.DONE
    pages_crawled: int
    duration_ms: int
    export_ready: bool
