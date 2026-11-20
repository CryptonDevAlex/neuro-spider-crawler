from app.analysis.analyzer import AnalysisInput, SecurityAnalyzer
from app.models.security import Severity


def test_analyzer_builds_executive_diagnosis() -> None:
    data = AnalysisInput(
        target="http://127.0.0.1:8080",
        audit_mode=True,
        headers={"Server": "nginx"},
        cookies=[{"name": "session", "httpOnly": False, "secure": False}],
        pages=[],
        html=[("http://127.0.0.1:8080", "<form action='/login'><input name='user'></form>")],
        js=[],
        js_files=[],
        forms=[],
        endpoints=["http://127.0.0.1:8080/login"],
        params=["user"],
        robots_paths=["/hidden"],
        sitemap_paths=["http://127.0.0.1:8080/page1.html"],
    )

    output = SecurityAnalyzer().analyze(data)

    assert output.summary.executive_diagnosis
    assert output.summary.severity_counts[Severity.CRITICAL.value] == 0
    assert output.summary.severity_counts[Severity.HIGH.value] >= 1
    assert any("robots" in finding.title for finding in output.findings)
    assert any("sitemap" in finding.title for finding in output.findings)
    assert output.summary.remediation_priorities
