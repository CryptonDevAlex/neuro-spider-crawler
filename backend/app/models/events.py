from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.core.events import EventType
from app.models.security import Finding, SecurityHeader, Technologies, WafDetection


class EventBase(BaseModel):
    type: EventType
    scan_id: UUID
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
    forms: int
    scripts: int
    word_count: int


class FindingEvent(EventBase):
    type: EventType = EventType.FINDING
    finding: Finding


class SummaryEvent(EventBase):
    type: EventType = EventType.SUMMARY
    executive_diagnosis: str
    severity_counts: dict[str, int]
    remediation_priorities: list[str]
    scope: dict[str, int]
    engine: str
    technologies: Technologies
    headers: list[SecurityHeader]
    subdomains: list[str] = []
    waf_detections: list[WafDetection] = []


class ErrorEvent(EventBase):
    type: EventType = EventType.ERROR
    code: str
    message: str
    page_id: str | None = None


class DoneEvent(EventBase):
    type: EventType = EventType.DONE
    pages_scanned: int
    findings_total: int
    duration_ms: int
    export_ready: bool
