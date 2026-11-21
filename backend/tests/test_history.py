from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.models import User
from app.db.repository import (
    create_user,
    list_monitored_targets,
    list_scans,
    save_scan,
)
from app.models.security import (
    Finding,
    ScanResult,
    ScanStatus,
    SecuritySummary,
    Severity,
)


def build_result(finding_id: str, domain: str = "example.com") -> ScanResult:
    scan_id = uuid4()
    return ScanResult(
        scan_id=scan_id,
        status=ScanStatus.COMPLETED,
        target=f"https://{domain}",
        started_at=datetime.now(UTC),
        finished_at=datetime.now(UTC),
        findings=[
            Finding(
                id=finding_id,
                severity=Severity.HIGH,
                category="TLS/SSL",
                title=f"Hallazgo {finding_id}",
                description="Descripción del hallazgo.",
                evidence="evidencia",
                remediation="Remediar el hallazgo.",
                target=f"https://{domain}",
                source=f"https://{domain}",
            )
        ],
        subdomains=[f"api.{domain}"],
        summary=SecuritySummary(
            executive_diagnosis="Diagnóstico pasivo autorizado sobre el objetivo.",
            severity_counts={"ALTO": 1},
            remediation_priorities=["Remediar el hallazgo."],
            engine="Groq (GPT-OSS 20B)",
        ),
    )


def test_save_and_list_scans(session: Session, user: User) -> None:
    result = build_result("tls-high")

    save_scan(session, result, user.id)

    assert len(list_scans(session, user.id)) == 1
    assert list_scans(session, user.id)[0].domain == "example.com"


def test_history_compare_and_ownership(
    session: Session,
    user: User,
    authorized_client: TestClient,
    client_for_user,
) -> None:
    base = build_result("old-high")
    target = build_result("new-high")
    save_scan(session, base, user.id)
    save_scan(session, target, user.id)
    other = create_user(
        session,
        email="other@neurospider.local",
        password_hash=hash_password("password123"),
        full_name="Otro operador",
    )
    other_client = client_for_user(other)

    history = authorized_client.get("/scans/history")
    comparison = authorized_client.get(
        "/scans/compare",
        params={"base_id": str(base.scan_id), "target_id": str(target.scan_id)},
    )
    stored = authorized_client.get(f"/scans/{target.scan_id}")
    foreign_stored = other_client.get(f"/scans/{target.scan_id}")
    foreign_delete = other_client.delete(f"/scans/{target.scan_id}")
    deleted = authorized_client.delete(f"/scans/{target.scan_id}")
    remaining = authorized_client.get("/scans/history")

    assert history.status_code == 200
    assert len(history.json()) == 2
    assert comparison.status_code == 200
    assert comparison.json()["counts"] == {"resolved": 1, "new": 1, "persistent": 0}
    assert stored.status_code == 200
    assert foreign_stored.status_code == 404
    assert foreign_delete.status_code == 404
    assert deleted.status_code == 200
    assert len(remaining.json()) == 1


def test_monitoring_targets_are_private(
    session: Session,
    user: User,
    authorized_client: TestClient,
    client_for_user,
) -> None:
    other = create_user(
        session,
        email="monitoring@neurospider.local",
        password_hash=hash_password("password123"),
        full_name="Monitor",
    )
    other_client = client_for_user(other)

    created = authorized_client.post(
        "/monitoring/targets",
        json={"domain": "https://example.com", "frequency": "weekly"},
    )
    foreign_created = other_client.post(
        "/monitoring/targets",
        json={"domain": "https://example.com", "frequency": "daily"},
    )
    listed = authorized_client.get("/monitoring/targets")
    foreign_listed = other_client.get("/monitoring/targets")

    assert created.status_code == 201
    assert foreign_created.status_code == 201
    assert len(listed.json()) == 1
    assert len(foreign_listed.json()) == 1
    assert len(list_monitored_targets(session, user.id)) == 1
