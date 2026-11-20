from datetime import UTC, datetime

from fpdf import FPDF
from fpdf.enums import XPos, YPos

from app.models.security import Finding, ScanResult, SecuritySummary, Severity

SEVERITY_ORDER = [
    Severity.CRITICAL,
    Severity.HIGH,
    Severity.MEDIUM,
    Severity.LOW,
    Severity.INFO,
]

SEVERITY_COLORS = {
    Severity.CRITICAL: (156, 21, 61),
    Severity.HIGH: (190, 69, 31),
    Severity.MEDIUM: (166, 116, 22),
    Severity.LOW: (31, 111, 139),
    Severity.INFO: (71, 85, 105),
}

CONTENT_TOP_MM = 36.0


class AuditReportPDF(FPDF):
    def header(self) -> None:
        self.set_fill_color(11, 18, 32)
        self.rect(0, 0, 210, 30, "F")
        self.set_xy(14, 8)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 14)
        self.cell(
            0,
            7,
            safe_text("NEUROSPIDER · INFORME DE AUDITORÍA DE SEGURIDAD PASIVA"),
            border=0,
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )
        self.set_x(14)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(148, 163, 184)
        self.cell(
            0,
            5,
            safe_text("RECONOCIMIENTO PASIVO AUTORIZADO / OSINT"),
            border=0,
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )

    def footer(self) -> None:
        self.set_y(-18)
        self.set_draw_color(226, 232, 240)
        self.line(14, self.get_y(), 196, self.get_y())
        self.ln(2)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(100, 116, 139)
        self.cell(
            0,
            4,
            safe_text(
                "Reconocimiento pasivo autorizado · Sin explotación activa ni escaneo de puertos"
            ),
            border=0,
            align="C",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )
        self.set_x(14)
        self.cell(
            0,
            4,
            safe_text(f"Página {self.page_no()}"),
            border=0,
            align="R",
            new_x=XPos.LMARGIN,
            new_y=YPos.TOP,
        )


def safe_text(value: object) -> str:
    text = str(value)
    replacements = {
        "’": "'",
        "“": '"',
        "”": '"',
        "–": "-",
        "—": "-",
        "•": "-",
        "\u00a0": " ",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return text.encode("latin-1", errors="replace").decode("latin-1")


def to_pdf(result: ScanResult) -> bytes:
    pdf = AuditReportPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(14, 36, 14)
    pdf.set_auto_page_break(auto=True, margin=24)
    pdf.set_title(safe_text(f"NeuroSpider · {result.scan_id}"))
    pdf.set_author("NeuroSpider")
    pdf.set_creator("NeuroSpider Audit Reporting")
    pdf.add_page()

    summary = result.summary
    generated = result.finished_at or result.started_at or datetime.now(UTC)
    engine = summary.engine if summary and summary.engine != "local-rules" else "Reglas locales"

    add_section(pdf, "Datos de la auditoría")
    add_meta(pdf, "Objetivo", result.target)
    add_meta(pdf, "ID de escaneo", str(result.scan_id))
    add_meta(pdf, "Fecha", generated.strftime("%Y-%m-%d %H:%M UTC"))
    add_meta(pdf, "Estado", result.status.value.upper())
    add_meta(pdf, "Motor de diagnóstico", engine)
    add_meta(pdf, "Páginas analizadas", len(result.pages))
    pdf.ln(4)

    add_section(pdf, "Resumen ejecutivo")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(30, 41, 59)
    diagnosis = (
        summary.executive_diagnosis
        if summary
        else "Informe en proceso; el diagnóstico ejecutivo aún no está disponible."
    )
    write_paragraph(pdf, diagnosis, 5.5)
    pdf.ln(3)

    if summary and summary.remediation_priorities:
        add_section(pdf, "Prioridades de remediación")
        for index, priority in enumerate(summary.remediation_priorities, start=1):
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(190, 69, 31)
            pdf.cell(
                8,
                5,
                f"{index}.",
                border=0,
                new_x=XPos.RIGHT,
                new_y=YPos.TOP,
            )
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(30, 41, 59)
            write_paragraph(pdf, priority, 5)
        pdf.ln(3)

    add_section(pdf, "Distribución por severidad")
    add_severity_table(pdf, summary)
    pdf.ln(4)

    add_section(pdf, "Superficie identificada")
    scope = summary.scope if summary else {}
    add_meta(pdf, "Endpoints inventariados", scope.get("endpoints", 0))
    add_meta(pdf, "Formularios detectados", scope.get("forms", 0))
    add_meta(pdf, "Parámetros detectados", scope.get("params", 0))
    add_meta(pdf, "Archivos JavaScript", scope.get("js_files", 0))
    add_meta(pdf, "Cabeceras ausentes", scope.get("missing_headers", 0))
    pdf.ln(4)

    add_section(pdf, "WAF/CDN identificado")
    if result.waf_detections:
        for detection in result.waf_detections:
            add_meta(pdf, detection.name, detection.evidence)
    else:
        write_paragraph(pdf, "No se identificó huella de WAF o CDN en el alcance analizado.", 5)
    pdf.ln(4)

    add_section(pdf, "Subdominios por Certificate Transparency")
    if result.subdomains:
        for index in range(0, len(result.subdomains), 8):
            group = result.subdomains[index : index + 8]
            write_paragraph(pdf, ", ".join(group), 5)
    else:
        write_paragraph(pdf, "No se publicaron subdominios adicionales en certificados.", 5)
    pdf.ln(4)

    for severity in SEVERITY_ORDER:
        findings = [item for item in result.findings if item.severity == severity]
        if not findings:
            continue
        add_section(pdf, f"Hallazgos {severity.value} ({len(findings)})")
        for finding in findings:
            add_finding(pdf, finding)

    if not result.findings:
        add_section(pdf, "Hallazgos")
        pdf.set_font("Helvetica", "", 10)
        write_paragraph(pdf, "No se registraron hallazgos en el alcance analizado.", 5)

    return bytes(pdf.output())


def ensure_space(pdf: FPDF, height: float) -> None:
    if pdf.get_y() + height <= pdf.page_break_trigger:
        return
    pdf.add_page()
    pdf.set_y(CONTENT_TOP_MM)


def add_section(pdf: FPDF, title: str) -> None:
    ensure_space(pdf, 24)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(
        0,
        7,
        safe_text(title),
        border=0,
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.set_draw_color(190, 69, 31)
    pdf.set_line_width(0.5)
    pdf.line(14, pdf.get_y(), 196, pdf.get_y())
    pdf.ln(3)


def add_meta(pdf: FPDF, label: str, value: object) -> None:
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(
        42,
        5,
        safe_text(label),
        border=0,
        new_x=XPos.RIGHT,
        new_y=YPos.TOP,
    )
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(30, 41, 59)
    write_paragraph(pdf, str(value), 5)


def add_severity_table(pdf: FPDF, summary: SecuritySummary | None) -> None:
    counts = summary.severity_counts if summary else {}
    width = 36.4

    for severity in SEVERITY_ORDER:
        color = SEVERITY_COLORS[severity]
        pdf.set_fill_color(*color)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(
            width,
            8,
            safe_text(severity.value),
            border=1,
            align="C",
            fill=True,
            new_x=XPos.RIGHT,
            new_y=YPos.TOP,
        )

    pdf.ln()
    pdf.set_text_color(30, 41, 59)
    for severity in SEVERITY_ORDER:
        pdf.set_fill_color(248, 250, 252)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(
            width,
            9,
            str(counts.get(severity.value, 0)),
            border=1,
            align="C",
            fill=True,
            new_x=XPos.RIGHT,
            new_y=YPos.TOP,
        )
    pdf.ln()


def add_finding(pdf: FPDF, finding: Finding) -> None:
    ensure_space(pdf, 34)

    color = SEVERITY_COLORS[finding.severity]
    pdf.set_fill_color(*color)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(
        28,
        6,
        safe_text(finding.severity.value),
        border=0,
        align="C",
        fill=True,
        new_x=XPos.RIGHT,
        new_y=YPos.TOP,
    )
    pdf.set_text_color(15, 23, 42)
    pdf.set_font("Helvetica", "B", 10)
    write_paragraph(pdf, finding.title, 6)
    pdf.ln(1)

    add_meta(pdf, "Categoría", finding.category)
    add_meta(pdf, "Fuente", finding.source or "No declarada")
    ensure_space(pdf, 16)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(
        0,
        5,
        safe_text("Descripción"),
        border=0,
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(30, 41, 59)
    write_paragraph(pdf, finding.description, 5)
    pdf.ln(1)
    ensure_space(pdf, 16)

    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(
        0,
        5,
        safe_text("Evidencia"),
        border=0,
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.set_font("Courier", "", 8)
    pdf.set_text_color(55, 65, 81)
    write_paragraph(pdf, finding.evidence[:600], 4.5)
    pdf.ln(1)
    ensure_space(pdf, 16)

    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(
        0,
        5,
        safe_text("Guía técnica de remediación"),
        border=0,
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(30, 41, 59)
    write_paragraph(pdf, finding.remediation, 5)
    pdf.ln(5)


def write_paragraph(pdf: FPDF, value: object, line_height: float) -> None:
    pdf.multi_cell(
        0,
        line_height,
        safe_text(value),
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
