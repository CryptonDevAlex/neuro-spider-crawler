from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.domain import normalize_domain
from app.db.models import MonitoredTarget, ScanRecord
from app.models.security import ScanResult


def save_scan(
    session: Session,
    result: ScanResult,
    domain: str | None = None,
) -> ScanRecord:
    record = ScanRecord(
        scan_id=str(result.scan_id),
        domain=domain or normalize_domain(result.target),
        target=result.target,
        status=result.status.value,
        engine_ia=result.summary.engine if result.summary else "local-rules",
        created_at=result.started_at or datetime.now(UTC),
        finished_at=result.finished_at,
        severity_counts=result.summary.severity_counts if result.summary else {},
        findings=[finding.model_dump(mode="json") for finding in result.findings],
        subdomains=list(result.subdomains),
        waf_detections=[item.model_dump(mode="json") for item in result.waf_detections],
        result_json=result.model_dump(mode="json"),
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def list_scans(session: Session, limit: int = 100) -> Sequence[ScanRecord]:
    return (
        session.execute(
            select(ScanRecord).order_by(ScanRecord.created_at.desc()).limit(limit)
        )
        .scalars()
        .all()
    )


def get_scan(session: Session, scan_id: UUID | str) -> ScanRecord | None:
    return session.scalar(select(ScanRecord).where(ScanRecord.scan_id == str(scan_id)))


def latest_scan_for_domain(session: Session, domain: str) -> ScanRecord | None:
    return session.scalar(
        select(ScanRecord)
        .where(ScanRecord.domain == normalize_domain(domain))
        .order_by(ScanRecord.created_at.desc())
    )


def upsert_monitored_target(
    session: Session,
    domain: str,
    frequency: str,
    webhook_url: str | None = None,
) -> MonitoredTarget:
    normalized = normalize_domain(domain)
    target = session.scalar(
        select(MonitoredTarget).where(MonitoredTarget.domain == normalized)
    )
    if target is None:
        target = MonitoredTarget(domain=normalized)
        session.add(target)

    target.frequency = frequency
    target.active = True
    target.webhook_url = webhook_url or None
    session.commit()
    session.refresh(target)
    return target


def list_monitored_targets(session: Session) -> Sequence[MonitoredTarget]:
    return (
        session.execute(select(MonitoredTarget).order_by(MonitoredTarget.domain))
        .scalars()
        .all()
    )


def get_monitored_target(session: Session, target_id: int) -> MonitoredTarget | None:
    return session.get(MonitoredTarget, target_id)


def set_monitored_active(
    session: Session,
    target: MonitoredTarget,
    active: bool,
) -> MonitoredTarget:
    target.active = active
    session.commit()
    session.refresh(target)
    return target


def delete_monitored_target(session: Session, target: MonitoredTarget) -> None:
    session.delete(target)
    session.commit()


def mark_monitored_run(session: Session, target: MonitoredTarget) -> None:
    target.last_run_at = datetime.now(UTC).replace(tzinfo=None)
    session.commit()


def due_monitored_targets(session: Session) -> list[MonitoredTarget]:
    now = datetime.now(UTC).replace(tzinfo=None)
    targets = session.scalars(
        select(MonitoredTarget).where(MonitoredTarget.active.is_(True))
    ).all()
    due: list[MonitoredTarget] = []

    for target in targets:
        days = 7 if target.frequency == "weekly" else 1
        if target.last_run_at is None or target.last_run_at <= now - timedelta(days=days):
            due.append(target)

    return due
