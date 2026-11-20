from datetime import UTC, datetime
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db.database import Base, get_session
from app.db.repository import get_scan, list_scans, save_scan, upsert_monitored_target
from app.main import app
from app.models.security import (
    Finding,
    ScanResult,
    ScanStatus,
    SecuritySummary,
    Severity,
)


@pytest.fixture
def session() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        yield db


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


def test_save_and_list_scans(session: Session) -> None:
    result = build_result("tls-high")

    save_scan(session, result)
    stored = get_scan(session, result.scan_id)

    assert stored is not None
    assert stored.domain == "example.com"
    assert stored.engine_ia == "Groq (GPT-OSS 20B)"
    assert stored.subdomains == ["api.example.com"]
    assert len(list_scans(session)) == 1


def test_history_and_compare_endpoints(session: Session) -> None:
    base = build_result("old-high")
    target = build_result("new-high")
    save_scan(session, base)
    save_scan(session, target)
    app.dependency_overrides[get_session] = lambda: session

    try:
        client = TestClient(app)
        history = client.get("/scans/history")
        comparison = client.get(
            "/scans/compare",
            params={"base_id": str(base.scan_id), "target_id": str(target.scan_id)},
        )
        stored = client.get(f"/scans/{target.scan_id}")
    finally:
        app.dependency_overrides.clear()

    assert history.status_code == 200
    assert len(history.json()) == 2
    assert comparison.status_code == 200
    payload = comparison.json()
    assert payload["counts"] == {"resolved": 1, "new": 1, "persistent": 0}
    assert stored.status_code == 200
    assert stored.json()["scan_id"] == str(target.scan_id)


def test_monitoring_target_endpoints(session: Session) -> None:
    app.dependency_overrides[get_session] = lambda: session

    try:
        client = TestClient(app)
        created = client.post(
            "/monitoring/targets",
            json={"domain": "https://example.com", "frequency": "weekly"},
        )
        listed = client.get("/monitoring/targets")
        updated = client.patch(
            f"/monitoring/targets/{created.json()['id']}",
            json={"active": False},
        )
    finally:
        app.dependency_overrides.clear()

    assert created.status_code == 201
    assert created.json()["domain"] == "example.com"
    assert listed.status_code == 200
    assert updated.json()["active"] is False
    assert len(list_scans(session)) == 0
    assert upsert_monitored_target(session, "example.com", "daily").active is True
