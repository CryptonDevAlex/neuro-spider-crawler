import pytest

from app.analysis.analyzer import AnalysisInput, SecurityAnalyzer
from app.core.config import Settings
from app.models.security import Severity


def build_input() -> AnalysisInput:
    return AnalysisInput(
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


@pytest.mark.asyncio
async def test_analyzer_builds_executive_diagnosis() -> None:
    settings = Settings(
        _env_file=None,
        llm_provider="auto",
        llm_api_key="",
        openai_api_key="",
        gemini_api_key="",
    )

    output = await SecurityAnalyzer(settings).analyze(build_input())

    assert output.summary.executive_diagnosis
    assert output.summary.severity_counts[Severity.CRITICAL.value] == 0
    assert output.summary.severity_counts[Severity.HIGH.value] >= 1
    assert any("robots" in finding.title for finding in output.findings)
    assert any("sitemap" in finding.title for finding in output.findings)
    assert output.summary.remediation_priorities


@pytest.mark.asyncio
async def test_analyzer_falls_back_without_llm_keys() -> None:
    settings = Settings(
        _env_file=None,
        llm_provider="auto",
        llm_api_key="",
        openai_api_key="",
        gemini_api_key="",
    )

    output = await SecurityAnalyzer(settings).analyze(build_input())

    assert output.summary.engine == "local-rules"
    assert output.summary.executive_diagnosis
