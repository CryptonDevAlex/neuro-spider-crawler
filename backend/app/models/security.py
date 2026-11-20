from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, field_validator

from app.crawler.url import normalize_target_input


class Severity(str, Enum):
    CRITICAL = "CRITICO"
    HIGH = "ALTO"
    MEDIUM = "MEDIO"
    LOW = "BAJO"
    INFO = "INFO"


class ScanStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ScanRequest(BaseModel):
    url: str = Field(min_length=1)
    max_depth: int = Field(default=2, ge=1, le=4)
    max_pages: int = Field(default=20, ge=1, le=100)
    audit_mode: bool = True

    @field_validator("url")
    @classmethod
    def normalize_url(cls, value: str) -> str:
        return normalize_target_input(value)


class ScanAccepted(BaseModel):
    scan_id: UUID
    status: ScanStatus = ScanStatus.QUEUED


class PageAsset(BaseModel):
    id: str
    url: HttpUrl
    title: str
    depth: int
    links: int
    forms: int
    scripts: int
    word_count: int


class SecurityHeader(BaseModel):
    name: str
    present: bool
    value: str | None = None
    severity: Severity


class FormInput(BaseModel):
    name: str
    type: str


class FormDetail(BaseModel):
    action: str
    method: str
    inputs: list[FormInput] = Field(default_factory=list)


class CookieInfo(BaseModel):
    name: str
    http_only: bool
    secure: bool
    same_site: str | None = None


class WafDetection(BaseModel):
    name: str
    evidence: str
    category: str = "WAF/CDN"


class Technologies(BaseModel):
    server: str | None = None
    frameworks: list[str] = Field(default_factory=list)
    cookies: list[CookieInfo] = Field(default_factory=list)
    waf: list[WafDetection] = Field(default_factory=list)


class Finding(BaseModel):
    id: str
    severity: Severity
    category: str
    title: str
    description: str
    evidence: str
    remediation: str
    target: str
    source: str | None = None


class SecuritySummary(BaseModel):
    executive_diagnosis: str
    severity_counts: dict[str, int] = Field(default_factory=dict)
    remediation_priorities: list[str] = Field(default_factory=list)
    scope: dict[str, int] = Field(default_factory=dict)
    engine: str = "local-rules"


class ScanResult(BaseModel):
    scan_id: UUID
    status: ScanStatus
    target: str
    started_at: datetime | None = None
    finished_at: datetime | None = None
    pages: list[PageAsset] = Field(default_factory=list)
    headers: list[SecurityHeader] = Field(default_factory=list)
    forms: list[FormDetail] = Field(default_factory=list)
    js_files: list[str] = Field(default_factory=list)
    technologies: Technologies = Field(default_factory=Technologies)
    findings: list[Finding] = Field(default_factory=list)
    robots_paths: list[str] = Field(default_factory=list)
    sitemap_paths: list[str] = Field(default_factory=list)
    subdomains: list[str] = Field(default_factory=list)
    waf_detections: list[WafDetection] = Field(default_factory=list)
    summary: SecuritySummary | None = None
