from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ScanHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    scan_id: UUID
    domain: str
    created_at: datetime
    finished_at: datetime | None
    status: str
    engine_ia: str
    severity_counts: dict[str, int]
    findings_total: int
    subdomains_total: int


class ScanComparisonFinding(BaseModel):
    id: str
    title: str
    severity: str
    category: str
    remediation: str


class ScanComparison(BaseModel):
    base_id: UUID
    target_id: UUID
    domain: str
    resolved: list[ScanComparisonFinding]
    new: list[ScanComparisonFinding]
    persistent: list[ScanComparisonFinding]
    counts: dict[str, int]


class MonitoredTargetCreate(BaseModel):
    domain: str = Field(min_length=1)
    frequency: Literal["daily", "weekly"] = "daily"
    webhook_url: str | None = None


class MonitoredTargetUpdate(BaseModel):
    active: bool


class MonitoredTargetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    domain: str
    frequency: str
    active: bool
    webhook_url: str | None
    last_run_at: datetime | None
    created_at: datetime
