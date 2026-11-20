from typing import Self

import pytest

from app.analysis.subdomains import discover_subdomains
from app.analysis.waf import detect_waf


class FakeResponse:
    status_code = 200

    def json(self) -> list[dict[str, str]]:
        return [
            {"name_value": "api.example.com\n*.www.example.com\nother.org"},
            {"name_value": "cdn.example.com"},
        ]


class FakeClient:
    def __init__(self, *args: object, **kwargs: object) -> None:
        self.args = args
        self.kwargs = kwargs

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args: object) -> None:
        return None

    async def get(self, url: str) -> FakeResponse:
        assert url == "https://crt.sh/?q=%25.example.com&output=json"
        return FakeResponse()


@pytest.mark.asyncio
async def test_discover_subdomains_from_crtsh(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.analysis.subdomains.httpx.AsyncClient", FakeClient)

    result = await discover_subdomains("https://example.com", "neurospider-tests")

    assert result == ["api.example.com", "cdn.example.com", "www.example.com"]


def test_detect_waf_vendors_from_headers_and_cookies() -> None:
    detections = detect_waf(
        {
            "CF-RAY": "abc123",
            "Server": "cloudflare",
            "X-Amz-Cf-Id": "edge-1",
        },
        [{"name": "__cf_bm"}, {"name": "aws-waf-token"}],
    )

    names = [item.name for item in detections]

    assert "Cloudflare" in names
    assert "AWS CloudFront/WAF" in names
    assert all(item.evidence for item in detections)
