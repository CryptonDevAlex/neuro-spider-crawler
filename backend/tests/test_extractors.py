from app.analysis.headers import analyze_headers
from app.analysis.secrets import scan_text
from app.crawler.policy import CrawlPolicy
from app.crawler.spider import normalize_url
from app.crawler.url import normalize_target_input
from app.models.security import ScanRequest, Severity


def test_policy_audit_mode_defaults() -> None:
    policy = CrawlPolicy()
    assert policy.max_depth == 2
    assert policy.max_pages == 30
    assert policy.respect_robots is False


def test_normalize_url() -> None:
    assert normalize_url("https://example.com/a", "/b#section") == "https://example.com/b"
    assert normalize_url("https://example.com", "mailto:x@y.com") == ""


def test_normalize_target_input_adds_https() -> None:
    assert normalize_target_input("dominio.com") == "https://dominio.com"
    assert normalize_target_input("127.0.0.1:8080") == "http://127.0.0.1:8080"
    assert ScanRequest(url="dominio.com/path#fragment").url == "https://dominio.com/path"


def test_missing_headers_generate_findings() -> None:
    headers, findings = analyze_headers({"Server": "nginx"}, "http://127.0.0.1:8080")
    assert len(headers) == 5
    assert all(not header.present for header in headers)
    assert any(finding.severity == Severity.HIGH for finding in findings)


def test_secret_patterns_are_masked() -> None:
    findings = scan_text(
        "const key = 'AKIA1234567890ABCDEF';",
        "http://127.0.0.1:8080/app.js",
        "http://127.0.0.1:8080",
        "JavaScript",
    )
    assert findings
    assert "AKIA" in findings[0].evidence
    assert "CDEF" in findings[0].evidence
    assert "1234567890" not in findings[0].evidence
