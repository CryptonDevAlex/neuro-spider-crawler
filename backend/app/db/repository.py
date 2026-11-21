from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.domain import normalize_domain
from app.db.models import MonitoredTarget, ScanRecord, User
from app.models.security import ScanResult


def get_user(session: Session, user_id: int) -> User | None:
    return session.get(User, user_id)


def get_user_by_email(session: Session, email: str) -> User | None:
    return session.scalar(select(User).where(func.lower(User.email) == email.strip().lower()))


def get_user_by_identity(session: Session, identity: str) -> User | None:
    value = identity.strip().lower()
    return session.scalar(
        select(User).where(
            or_(func.lower(User.email) == value, func.lower(User.full_name) == value)
        )
    )


def get_user_by_google_id(session: Session, google_id: str) -> User | None:
    return session.scalar(select(User).where(User.google_id == google_id))


def create_user(
    session: Session,
    email: str,
    password_hash: str | None,
    full_name: str,
    google_id: str | None = None,
) -> User:
    user = User(
        email=email.strip().lower(),
        password_hash=password_hash,
        full_name=full_name.strip(),
        google_id=google_id,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def link_google_id(session: Session, user: User, google_id: str) -> User:
    user.google_id = google_id
    session.commit()
    session.refresh(user)
    return user


def save_scan(
    session: Session,
    result: ScanResult,
    user_id: int,
    domain: str | None = None,
) -> ScanRecord:
    record = ScanRecord(
        scan_id=str(result.scan_id),
        user_id=user_id,
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


def list_scans(session: Session, user_id: int, limit: int = 100) -> Sequence[ScanRecord]:
    return (
        session.execute(
            select(ScanRecord)
            .where(ScanRecord.user_id == user_id)
            .order_by(ScanRecord.created_at.desc())
            .limit(limit)
        )
        .scalars()
        .all()
    )


def get_scan(session: Session, scan_id: UUID | str, user_id: int | None = None) -> ScanRecord | None:
    statement = select(ScanRecord).where(ScanRecord.scan_id == str(scan_id))
    if user_id is not None:
        statement = statement.where(ScanRecord.user_id == user_id)
    return session.scalar(statement)


def delete_scan(session: Session, record: ScanRecord) -> None:
    session.delete(record)
    session.commit()


def latest_scan_for_domain(
    session: Session,
    domain: str,
    user_id: int,
) -> ScanRecord | None:
    return session.scalar(
        select(ScanRecord)
        .where(ScanRecord.user_id == user_id, ScanRecord.domain == normalize_domain(domain))
        .order_by(ScanRecord.created_at.desc())
    )


def upsert_monitored_target(
    session: Session,
    user_id: int,
    domain: str,
    frequency: str,
    webhook_url: str | None = None,
) -> MonitoredTarget:
    normalized = normalize_domain(domain)
    target = session.scalar(
        select(MonitoredTarget).where(
            MonitoredTarget.user_id == user_id,
            MonitoredTarget.domain == normalized,
        )
    )
    if target is None:
        target = MonitoredTarget(domain=normalized, user_id=user_id)
        session.add(target)

    target.frequency = frequency
    target.active = True
    target.webhook_url = webhook_url or None
    session.commit()
    session.refresh(target)
    return target


def list_monitored_targets(session: Session, user_id: int) -> Sequence[MonitoredTarget]:
    return (
        session.execute(
            select(MonitoredTarget)
            .where(MonitoredTarget.user_id == user_id)
            .order_by(MonitoredTarget.domain)
        )
        .scalars()
        .all()
    )


def get_monitored_target(
    session: Session,
    target_id: int,
    user_id: int,
) -> MonitoredTarget | None:
    return session.scalar(
        select(MonitoredTarget).where(
            MonitoredTarget.id == target_id,
            MonitoredTarget.user_id == user_id,
        )
    )


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
