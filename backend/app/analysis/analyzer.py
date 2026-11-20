from collections import Counter
from dataclasses import dataclass, field

from app.analysis.executive_summary import build_executive_summary
from app.analysis.headers import analyze_headers
from app.analysis.secrets import scan_text
from app.analysis.technologies import analyze_cookies, detect_frameworks, detect_server
from app.analysis.waf import detect_waf
from app.core.config import Settings, get_settings
from app.models.security import (
    Finding,
    FormDetail,
    PageAsset,
    SecurityHeader,
    SecuritySummary,
    Severity,
    Technologies,
    WafDetection,
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
    subdomains: list[str] = field(default_factory=list)
    extra_findings: list[Finding] = field(default_factory=list)


@dataclass
class AnalysisOutput:
    headers: list[SecurityHeader]
    technologies: Technologies
    findings: list[Finding]
    summary: SecuritySummary
    subdomains: list[str] = field(default_factory=list)
    waf_detections: list[WafDetection] = field(default_factory=list)


class SecurityAnalyzer:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    async def analyze(self, data: AnalysisInput) -> AnalysisOutput:
        security_headers, findings = analyze_headers(data.headers, data.target)

        frameworks = detect_frameworks(
            " ".join(text for _, text in data.html), data.js_files
        )
        cookies, cookie_findings = analyze_cookies(data.cookies, data.target)
        findings.extend(cookie_findings)
        waf_detections = detect_waf(data.headers, data.cookies)
        findings.extend(self._waf_findings(waf_detections, data.target))

        for source, text in data.html:
            findings.extend(scan_text(text, source, data.target, "HTML"))
        for source, text in data.js:
            findings.extend(scan_text(text, source, data.target, "JavaScript"))

        findings.extend(self._recon_findings(data))
        findings.extend(data.extra_findings)
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

        narrative = await build_executive_summary(
            target=data.target,
            findings=findings,
            severity_counts=severity_counts,
            scope=scope,
            settings=self.settings,
        )

        technologies = Technologies(
            server=detect_server(data.headers),
            frameworks=frameworks,
            cookies=cookies,
            waf=waf_detections,
        )

        return AnalysisOutput(
            headers=security_headers,
            technologies=technologies,
            findings=findings,
            summary=SecuritySummary(
                executive_diagnosis=narrative.diagnosis,
                severity_counts=severity_counts,
                remediation_priorities=narrative.priorities,
                scope=scope,
                engine=narrative.engine,
            ),
            subdomains=data.subdomains,
            waf_detections=waf_detections,
        )

    @staticmethod
    def _waf_findings(detections: list[WafDetection], target: str) -> list[Finding]:
        return [
            Finding(
                id=f"waf-{item.name.lower().replace(' ', '-').replace('/', '-')}",
                severity=Severity.INFO,
                category=item.category,
                title=f"WAF/CDN detectado: {item.name}",
                description=(
                    "La huella de la capa de protección se identificó mediante cabeceras y cookies "
                    "expuestas durante el reconocimiento pasivo."
                ),
                evidence=item.evidence,
                remediation=(
                    "Documentar la capa de protección y verificar que no sustituye el endurecimiento "
                    "de la aplicación de origen."
                ),
                target=target,
                source=target,
            )
            for item in detections
        ]

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
