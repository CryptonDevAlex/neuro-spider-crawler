from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient
from fpdf import FPDF

from app.api.deps import get_scan_service
from app.main import app
from app.models.security import (
    Finding,
    ScanResult,
    ScanStatus,
    SecuritySummary,
    Severity,
)
from app.services.pdf_service import CONTENT_TOP_MM, ensure_space


def build_result() -> ScanResult:
    scan_id = uuid4()
    return ScanResult(
        scan_id=scan_id,
        status=ScanStatus.COMPLETED,
        target="https://example.com",
        started_at=datetime.now(UTC),
        finished_at=datetime.now(UTC),
        findings=[
            Finding(
                id="tls-invalid",
                severity=Severity.HIGH,
                category="TLS/SSL",
                title="Certificado TLS inválido detectado",
                description="El certificado no superó la verificación estricta.",
                evidence="[SSL: CERTIFICATE_VERIFY_FAILED]",
                remediation="Renovar el certificado y la cadena intermedia.",
                target="https://example.com",
                source="https://example.com",
            )
        ],
        summary=SecuritySummary(
            executive_diagnosis=(
                "Reconocimiento pasivo completado sobre example.com con un hallazgo de severidad alta."
            ),
            severity_counts={severity.value: 0 for severity in Severity},
            remediation_priorities=["Renovar el certificado y la cadena intermedia."],
            scope={"pages": 1, "endpoints": 2},
            engine="Groq (GPT-OSS 120B)",
        ),
    )


def test_pdf_report_endpoint() -> None:
    result = build_result()

    class FakeService:
        async def get(self, scan_id: object) -> ScanResult:
            return result

    app.dependency_overrides[get_scan_service] = lambda: FakeService()
    try:
        client = TestClient(app)
        response = client.get(f"/scan/{result.scan_id}/report.pdf")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")
    assert "attachment" in response.headers["content-disposition"]


def test_ensure_space_starts_new_page_below_header() -> None:
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(14, CONTENT_TOP_MM, 14)
    pdf.set_auto_page_break(auto=True, margin=24)
    pdf.add_page()
    pdf.set_y(265)

    ensure_space(pdf, 40)

    assert pdf.page_no() == 2
    assert pdf.get_y() == CONTENT_TOP_MM
