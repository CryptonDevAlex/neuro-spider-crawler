from app.models.security import ScanResult, Severity

SEVERITY_ORDER = [
    Severity.CRITICAL,
    Severity.HIGH,
    Severity.MEDIUM,
    Severity.LOW,
    Severity.INFO,
]


def to_json(result: ScanResult) -> str:
    return result.model_dump_json(indent=2)


def to_markdown(result: ScanResult) -> str:
    summary = result.summary
    counts = summary.severity_counts if summary else {}
    scope = summary.scope if summary else {}
    technologies = result.technologies

    lines = [
        "# Informe de Reconocimiento Pasivo de Seguridad",
        "",
        f"**Objetivo:** {result.target}",
        f"**ID de escaneo:** `{result.scan_id}`",
        f"**Estado:** {result.status.value}",
        f"**Generado:** {result.finished_at.isoformat() if result.finished_at else 'Pendiente'}",
        "",
        (
            "> Este informe corresponde a reconocimiento pasivo/OSINT sobre un alcance autorizado. "
            "No incluye explotación activa, escaneo de puertos ni pruebas intrusivas."
        ),
        "",
        "## Resumen ejecutivo",
        "",
        summary.executive_diagnosis if summary else "Informe aún en proceso.",
        "",
        (
            f"**Motor de diagnóstico:** "
            f"{'IA configurada' if summary and summary.engine != 'local-rules' else 'Reglas locales'}"
        ),
        "",
        "## Distribución por severidad",
        "",
        "| Severidad | Hallazgos |",
        "| --- | ---: |",
    ]
    lines.extend(
        f"| {severity.value} | {counts.get(severity.value, 0)} |"
        for severity in SEVERITY_ORDER
    )

    lines.extend(["", "## Superficie identificada", ""])
    if scope:
        lines.extend(
            [
                f"- Páginas analizadas: {scope.get('pages', 0)}",
                f"- Endpoints inventariados: {scope.get('endpoints', 0)}",
                f"- Formularios detectados: {scope.get('forms', 0)}",
                f"- Parámetros detectados: {scope.get('params', 0)}",
                f"- Archivos JavaScript analizados: {scope.get('js_files', 0)}",
                f"- Cabeceras de seguridad ausentes: {scope.get('missing_headers', 0)}",
                f"- Hallazgos de riesgo medio o superior: {scope.get('risk_findings', 0)}",
            ]
        )
    else:
        lines.append("- No disponible")

    lines.extend(["", "## Tecnologías detectadas", ""])
    lines.append(f"- Servidor/framework HTTP: {technologies.server or 'No identificado'}")
    if technologies.frameworks:
        lines.extend(f"- Framework frontend: {framework}" for framework in technologies.frameworks)
    else:
        lines.append("- Frameworks frontend: No identificados")
    if technologies.cookies:
        lines.extend(
            f"- Cookie `{cookie.name}`: HttpOnly={'sí' if cookie.http_only else 'no'}, "
            f"Secure={'sí' if cookie.secure else 'no'}, SameSite={cookie.same_site or 'no declarado'}"
            for cookie in technologies.cookies
        )
    else:
        lines.append("- Cookies: No detectadas")

    lines.extend(["", "## Hallazgos", ""])
    for severity in SEVERITY_ORDER:
        findings = [item for item in result.findings if item.severity == severity]
        if not findings:
            continue
        lines.extend([f"### {severity.value} ({len(findings)})", ""])
        for finding in findings:
            lines.extend(
                [
                    f"#### {finding.title}",
                    "",
                    f"- **Categoría:** {finding.category}",
                    f"- **Objetivo:** {finding.target}",
                    f"- **Fuente:** {finding.source}",
                    f"- **Descripción:** {finding.description}",
                    f"- **Evidencia:** `{finding.evidence}`",
                    f"- **Recomendación:** {finding.remediation}",
                    "",
                ]
            )

    if not result.findings:
        lines.append("No se registraron hallazgos.")

    lines.extend(["", "## Rutas de descubrimiento", ""])
    lines.append(
        f"- robots.txt: {', '.join(result.robots_paths) if result.robots_paths else 'No disponible o sin rutas'}"
    )
    lines.append(
        f"- sitemap.xml: {', '.join(result.sitemap_paths[:10]) if result.sitemap_paths else 'No disponible o sin rutas'}"
    )

    if summary and summary.remediation_priorities:
        lines.extend(["", "## Prioridades de remediación", ""])
        lines.extend(
            f"{index}. {priority}"
            for index, priority in enumerate(summary.remediation_priorities, start=1)
        )

    lines.extend(
        [
            "",
            "---",
            "",
            "Generado por NeuroSpider · Reconocimiento web pasivo y OSINT autorizado.",
        ]
    )

    return "\n".join(lines)
