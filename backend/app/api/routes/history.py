from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import (
    AuthenticatedUser,
    get_app_settings,
    get_current_user,
    get_scan_service,
)
from app.core.config import Settings
from app.db.database import get_session
from app.db.models import ScanRecord
from app.db.repository import delete_scan, get_scan, list_scans
from app.models.history import ScanComparison, ScanComparisonFinding, ScanHistoryItem
from app.models.security import ScanResult
from app.services.crawler_service import ScanService
from app.services.report_store import delete_report_files

router = APIRouter(prefix="/scans", tags=["history"])

SEVERITY_RANK = {
    "CRITICO": 0,
    "ALTO": 1,
    "MEDIO": 2,
    "BAJO": 3,
    "INFO": 4,
}


def _history_item(record: ScanRecord) -> ScanHistoryItem:
    return ScanHistoryItem(
        scan_id=UUID(record.scan_id),
        domain=record.domain,
        created_at=record.created_at,
        finished_at=record.finished_at,
        status=record.status,
        engine_ia=record.engine_ia,
        severity_counts=record.severity_counts,
        findings_total=len(record.findings),
        subdomains_total=len(record.subdomains),
    )


def _comparison_finding(payload: dict[str, object]) -> ScanComparisonFinding:
    return ScanComparisonFinding(
        id=str(payload.get("id") or ""),
        title=str(payload.get("title") or ""),
        severity=str(payload.get("severity") or ""),
        category=str(payload.get("category") or ""),
        remediation=str(payload.get("remediation") or ""),
    )


def _sort_findings(items: list[ScanComparisonFinding]) -> list[ScanComparisonFinding]:
    return sorted(items, key=lambda item: SEVERITY_RANK.get(item.severity, 9))


@router.get("/history", response_model=list[ScanHistoryItem])
async def scan_history(
    user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[ScanHistoryItem]:
    return [_history_item(record) for record in list_scans(session, user.id)]


@router.get("/compare", response_model=ScanComparison)
async def compare_scans(
    base_id: UUID,
    target_id: UUID,
    user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ScanComparison:
    base = get_scan(session, base_id, user.id)
    target = get_scan(session, target_id, user.id)

    if base is None or target is None:
        raise HTTPException(status_code=404, detail="Escaneo no encontrado")
    if base.domain != target.domain:
        raise HTTPException(status_code=400, detail="Los escaneos pertenecen a dominios distintos")

    base_findings = {
        str(item.get("id") or ""): item
        for item in base.findings
        if isinstance(item, dict)
    }
    target_findings = {
        str(item.get("id") or ""): item
        for item in target.findings
        if isinstance(item, dict)
    }

    resolved = [
        _comparison_finding(item)
        for key, item in base_findings.items()
        if key not in target_findings
    ]
    created = [
        _comparison_finding(item)
        for key, item in target_findings.items()
        if key not in base_findings
    ]
    persistent = [
        _comparison_finding(item)
        for key, item in target_findings.items()
        if key in base_findings
    ]

    resolved = _sort_findings(resolved)
    created = _sort_findings(created)
    persistent = _sort_findings(persistent)

    return ScanComparison(
        base_id=base_id,
        target_id=target_id,
        domain=target.domain,
        resolved=resolved,
        new=created,
        persistent=persistent,
        counts={
            "resolved": len(resolved),
            "new": len(created),
            "persistent": len(persistent),
        },
    )


@router.get("/{scan_id}", response_model=ScanResult)
async def stored_scan(
    scan_id: UUID,
    user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ScanResult:
    record = get_scan(session, scan_id, user.id)
    if record is None or not record.result_json:
        raise HTTPException(status_code=404, detail="Escaneo guardado no encontrado")
    return ScanResult.model_validate(record.result_json)


@router.delete("/{scan_id}")
async def remove_scan(
    scan_id: UUID,
    user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_session),
    service: ScanService = Depends(get_scan_service),
    settings: Settings = Depends(get_app_settings),
) -> dict[str, bool]:
    record = get_scan(session, scan_id, user.id)
    if record is None:
        raise HTTPException(status_code=404, detail="Escaneo no encontrado")

    delete_report_files(scan_id, settings)
    service.forget(scan_id, user.id)
    delete_scan(session, record)
    return {"deleted": True}
