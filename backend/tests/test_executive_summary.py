from typing import Self

import pytest

from app.analysis.executive_summary import (
    _engine_label,
    _parse_response,
    _request_llm,
    _resolve_provider,
)
from app.core.config import Settings


class FakeResponse:
    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, object]:
        return {
            "choices": [
                {
                    "message": {
                        "content": (
                            '{"diagnosis":"Diagnóstico pasivo con evidencia suficiente para priorizar correcciones.","priorities":[]}'
                        )
                    }
                }
            ]
        }


def test_provider_auto_prefers_openai_compatible_key() -> None:
    settings = Settings(
        llm_provider="auto",
        llm_api_key="legacy-key",
        openai_api_key="",
        gemini_api_key="gemini-key",
    )

    assert _resolve_provider(settings) == ("openai", "legacy-key")


def test_provider_auto_uses_gemini_without_openai_key() -> None:
    settings = Settings(
        llm_provider="auto",
        llm_api_key="",
        openai_api_key="",
        gemini_api_key="gemini-key",
    )

    assert _resolve_provider(settings) == ("gemini", "gemini-key")


def test_settings_read_custom_openai_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "placeholder")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://api.groq.com/openai/v1")
    monkeypatch.setenv("OPENAI_MODEL", "llama-3.3-70b-versatile")

    settings = Settings(_env_file=None)

    assert settings.openai_api_key == "placeholder"
    assert settings.openai_base_url == "https://api.groq.com/openai/v1"
    assert settings.openai_model == "llama-3.3-70b-versatile"


def test_engine_label_uses_groq_display_name() -> None:
    settings = Settings(
        _env_file=None,
        openai_base_url="https://api.groq.com/openai/v1",
        openai_model="llama-3.3-70b-versatile",
    )

    assert _engine_label(settings, "openai") == "Groq (Llama 3.3)"


@pytest.mark.asyncio
async def test_request_llm_uses_custom_base_url_and_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    class CapturingClient:
        def __init__(self, *args: object, **kwargs: object) -> None:
            return None

        async def __aenter__(self) -> Self:
            return self

        async def __aexit__(self, *args: object) -> None:
            return None

        async def post(
            self,
            url: str,
            headers: dict[str, str],
            json: dict[str, object],
        ) -> FakeResponse:
            captured["url"] = url
            captured["headers"] = headers
            captured["model"] = json["model"]
            return FakeResponse()

    monkeypatch.setattr("app.analysis.executive_summary.httpx.AsyncClient", CapturingClient)
    settings = Settings(
        _env_file=None,
        openai_base_url="https://api.groq.com/openai/v1/",
        openai_model="llama-3.3-70b-versatile",
    )

    content = await _request_llm(
        provider="openai",
        api_key="placeholder",
        target="https://example.com",
        findings=[],
        severity_counts={},
        scope={},
        settings=settings,
    )

    assert captured["url"] == "https://api.groq.com/openai/v1/chat/completions"
    assert captured["model"] == "llama-3.3-70b-versatile"
    assert "diagnosis" in content


def test_parse_response_accepts_markdown_json_block() -> None:
    content = (
        "```json\n"
        '{"diagnosis":"Reconocimiento pasivo completado sobre example.com con hallazgos de severidad alta y prioridades claras.","priorities":["Renovar TLS"]}'
        "\n```"
    )

    narrative = _parse_response(content, engine="openai")

    assert narrative.engine == "openai"
    assert "example.com" in narrative.diagnosis
    assert narrative.priorities == ["Renovar TLS"]
