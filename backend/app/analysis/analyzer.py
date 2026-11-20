from collections import Counter
from dataclasses import dataclass

from app.analysis.headers import analyze_headers
from app.analysis.secrets import scan_text
from app.analysis.technologies import analyze_cookies, detect_frameworks, detect_server
from app.models.security import (
    Finding,
    FormDetail,
    PageAsset,
    SecurityHeader,
    SecuritySummary,
    Severity,
    Technologies,
)


@dataclass
class AnalysisInput:
    target: str
    audit_mode: bool
    headers: dict[str, str]
    cookies: list[dict[str, object]]
    pages: list[PageAsset]
    html: list[tuple[str, str]]
    js: list[tuple[str, str]]
    js_files: list[str]
    forms: list[FormDetail]
    endpoints: list[str]
    params: list[str]
    robots_paths: list[str]
    sitemap_paths: list[str]


@dataclass
class AnalysisOutput:
    headers: list[SecurityHeader]
    technologies: Technologies
    findings: list[Finding]
    summary: SecuritySummary


class SecurityAnalyzer:
    def analyze(self, data: AnalysisInput) -> AnalysisOutput:
        security_headers, findings = analyze_headers(data.headers, data.target)

        frameworks = detect_frameworks(
            " ".join(text for _, text in data.html), data.js_files
        )
        cookies, cookie_findings = analyze_cookies(data.cookies, data.target)
        findings.extend(cookie_findings)

        for source, text in data.html:
            findings.extend(scan_text(text, source, data.target, "HTML"))
        for source, text in data.js:
            findings.extend(scan_text(text, source, data.target, "JavaScript"))

        findings.extend(self._recon_findings(data))
        findings = self._dedupe(findings)

        counts = Counter(finding.severity.value for finding in findings)
        severity_counts = {
            severity.value: counts.get(severity.value, 0) for severity in Severity
        }
        risk_total = sum(
            severity_counts[severity.value]
            for severity in (Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM)
        )

        missing_headers = sum(1 for header in security_headers if not header.present)
        scope = {
            "pages": len(data.pages),
            "endpoints": len(data.endpoints),
            "forms": len(data.forms),
            "params": len(data.params),
            "js_files": len(data.js_files),
            "missing_headers": missing_headers,
            "risk_findings": risk_total,
            "robots_paths": len(data.robots_paths),
            "sitemap_paths": len(data.sitemap_paths),
        }

        if severity_counts[Severity.CRITICAL.value]:
            priority_note = (
                "Existen hallazgos críticos de exposición de credenciales: rotar y retirar antes de cualquier entrega."
            )
        elif risk_total:
            priority_note = (
                "No se detectaron credenciales críticas; priorizar la corrección de cabeceras y superficie expuesta."
            )
        else:
            priority_note = "No se detectaron riesgos altos en el alcance analizado."

        diagnosis = (
            f"Se analizaron {len(data.pages)} páginas y {len(data.endpoints)} endpoints dentro del alcance autorizado. "
            f"Se registraron {len(findings)} hallazgos, {risk_total} de ellos con severidad Media o superior. "
            f"{priority_note} El alcance fue pasivo y no se realizaron pruebas de explotación."
        )

        priorities: list[str] = []
        for severity in (Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM):
            for finding in findings:
                if finding.severity == severity and finding.remediation not in priorities:
                    priorities.append(finding.remediation)
            if len(priorities) >= 5:
                break

        technologies = Technologies(
            server=detect_server(data.headers),
            frameworks=frameworks,
            cookies=cookies,
        )

        return AnalysisOutput(
            headers=security_headers,
            technologies=technologies,
            findings=findings,
            summary=SecuritySummary(
                executive_diagnosis=diagnosis,
                severity_counts=severity_counts,
                remediation_priorities=priorities[:5],
                scope=scope,
            ),
        )

    @staticmethod
    def _dedupe(findings: list[Finding]) -> list[Finding]:
        seen: set[tuple[str, str, str | None]] = set()
        unique: list[Finding] = []

        for finding in findings:
            key = (finding.title, finding.evidence, finding.source)
            if key in seen:
                continue
            seen.add(key)
            unique.append(finding)

        return unique

    @staticmethod
    def _recon_findings(data: AnalysisInput) -> list[Finding]:
        findings: list[Finding] = []

        if data.audit_mode:
            findings.append(
                Finding(
                    id="mode-audit",
                    severity=Severity.INFO,
                    category="Alcance",
                    title="Modo auditoría activo",
                    description="robots.txt no se trató como una barrera: sus rutas y las de sitemap.xml se incorporaron al reconocimiento autorizado.",
                    evidence=f"audit_mode=true; rutas robots={len(data.robots_paths)}; rutas sitemap={len(data.sitemap_paths)}",
                    remediation="Documentar la autorización del alcance y conservar los archivos de descubrimiento como evidencia.",
                    target=data.target,
                    source=data.target,
                )
            )

        if data.robots_paths:
            findings.append(
                Finding(
                    id="robots-paths",
                    severity=Severity.INFO,
                    category="Descubrimiento",
                    title="Rutas declaradas en robots.txt",
                    description="robots.txt revela rutas que pueden ampliar el inventario del sitio.",
                    evidence=", ".join(data.robots_paths[:12])[:300],
                    remediation="No usar robots.txt como control de acceso; proteger las rutas sensibles con autenticación y autorización.",
                    target=data.target,
                    source=f"{data.target}/robots.txt",
                )
            )

        if data.sitemap_paths:
            findings.append(
                Finding(
                    id="sitemap-paths",
                    severity=Severity.INFO,
                    category="Descubrimiento",
                    title="Inventario expuesto en sitemap.xml",
                    description="El sitemap lista URLs públicas que ayudan a entender la estructura del sitio.",
                    evidence=", ".join(data.sitemap_paths[:8])[:300],
                    remediation="Publicar solo las URLs intencionadas y revisar periódicamente el inventario expuesto.",
                    target=data.target,
                    source=f"{data.target}/sitemap.xml",
                )
            )

        findings.append(
            Finding(
                id="attack-surface",
                severity=Severity.INFO,
                category="Superficie de ataque",
                title="Superficie de entrada identificada",
                description="Se inventariaron formularios, parámetros y enlaces como parte del reconocimiento pasivo.",
                evidence=(
                    f"endpoints={len(data.endpoints)}, forms={len(data.forms)}, "
                    f"params={len(data.params)}, js={len(data.js_files)}"
                ),
                remediation="Aplicar validación de entrada, control de CSRF y revisión de parámetros en cada punto de entrada.",
                target=data.target,
                source=data.target,
            )
        )

        return findings
