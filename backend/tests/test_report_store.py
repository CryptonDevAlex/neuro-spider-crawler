from pathlib import Path
from uuid import uuid4

from app.core.config import Settings
from app.services.report_store import delete_report_files


def test_delete_report_files_removes_cached_pdf_and_markdown(tmp_path: Path) -> None:
    reports = tmp_path / "reports"
    reports.mkdir()
    scan_id = uuid4()
    pdf = reports / f"neurospider-audit-{scan_id}.pdf"
    markdown = reports / f"neurospider-{scan_id}.md"
    pdf.write_bytes(b"%PDF")
    markdown.write_text("informe", encoding="utf-8")

    delete_report_files(scan_id, Settings(database_path=str(tmp_path / "neurospider.db")))

    assert not pdf.exists()
    assert not markdown.exists()
