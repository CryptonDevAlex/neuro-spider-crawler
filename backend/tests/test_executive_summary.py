from typing import Self

import pytest

from app.analysis.executive_summary import (
    _engine_label,
    _parse_response,
    _request_llm,
    _resolve_provider,
)
from app.core.config import Settings

SUCCESS_CONTENT = (
    '{"diagnosis":"Diagnóstico pasivo con evidencia suficiente para priorizar correcciones.",'
    '"priorities":["Renovar certificado TLS"]}'
)


class FakeResponse:
    def __init__(self, status_code: int, payload: dict[str, object]) -> None:
        self.status_code = status_code
        self.payload = payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError("HTTP error")

    def json(self) -> dict[str, object]:
        return self.payload


class ScriptedClient:
    def __init__(self, responses: list[FakeResponse]) -> None:
        self.responses = responses
        self.calls: list[tuple[str, str, str | None]] = []

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
        self.calls.append(("post", url, str(json.get("model"))))
        return self.responses.pop(0)

    async def get(self, url: str, headers: dict[str, str]) -> FakeResponse:
        self.calls.append(("get", url, None))
        return self.responses.pop(0)


def test_provider_auto_prefers_openai_compatible_key() -> None:
    settings = Settings(
        _env_file=None,
        llm_provider="auto",
        llm_api_key="legacy-key",
        openai_api_key="",
        gemini_api_key="gemini-key",
    )

    assert _resolve_provider(settings) == ("openai", "legacy-key")


def test_provider_auto_uses_gemini_without_openai_key() -> None:
    settings = Settings(
        _env_file=None,
        llm_provider="auto",
        llm_api_key="",
        openai_api_key="",
        gemini_api_key="gemini-key",
    )

    assert _resolve_provider(settings) == ("gemini", "gemini-key")


def test_settings_read_custom_openai_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "placeholder")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://api.groq.com/openai/v1")
    monkeypatch.setenv("OPENAI_MODEL", "llama-3.1-8b-instant")

    settings = Settings(_env_file=None)

    assert settings.openai_api_key == "placeholder"
    assert settings.openai_base_url == "https://api.groq.com/openai/v1"
    assert settings.openai_model == "llama-3.1-8b-instant"


@pytest.mark.parametrize(
    ("model", "expected"),
    [
        ("llama-3.3-70b-versatile", "Groq (Llama 3.3)"),
        ("llama-3.1-8b-instant", "Groq (Llama 3.1)"),
        ("openai/gpt-oss-120b", "Groq (GPT-OSS 120B)"),
    ],
)
def test_engine_label_uses_groq_display_name(model: str, expected: str) -> None:
    settings = Settings(
        _env_file=None,
        openai_base_url="https://api.groq.com/openai/v1",
        openai_model=model,
    )

    assert _engine_label(settings, "openai", model) == expected


@pytest.mark.asyncio
async def test_request_llm_recovers_from_model_not_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = ScriptedClient(
        [
            FakeResponse(404, {"error": {"code": "model_not_found"}}),
            FakeResponse(
                200,
                {
                    "data": [
                        {
                            "id": "whisper-large-v3",
                            "input_modalities": ["audio"],
                            "output_modalities": ["transcription"],
                        },
                        {
                            "id": "openai/gpt-oss-20b",
                            "input_modalities": ["text"],
                            "output_modalities": ["text"],
                        },
                    ]
                },
            ),
            FakeResponse(
                200,
                {"choices": [{"message": {"content": SUCCESS_CONTENT}}]},
            ),
        ]
    )
    monkeypatch.setattr(
        "app.analysis.executive_summary.httpx.AsyncClient",
        lambda **kwargs: client,
    )
    settings = Settings(
        _env_file=None,
        openai_base_url="https://api.groq.com/openai/v1",
        openai_model="llama-3.1-8b-instant",
    )

    result = await _request_llm(
        provider="openai",
        api_key="placeholder",
        target="https://example.com",
        findings=[],
        severity_counts={},
        scope={},
        settings=settings,
    )

    assert result.model == "openai/gpt-oss-20b"
    assert client.calls[0][2] == "llama-3.1-8b-instant"
    assert client.calls[1][0] == "get"
    assert client.calls[2][2] == "openai/gpt-oss-20b"


def test_parse_response_accepts_markdown_json_block() -> None:
    content = (
        "```json\n"
        '{"diagnosis":"Reconocimiento pasivo completado sobre example.com con hallazgos de severidad alta y prioridades claras.","priorities":["Renovar TLS"]}'
        "\n```"
    )

    narrative = _parse_response(content, engine="Groq (Llama 3.1)")

    assert narrative.engine == "Groq (Llama 3.1)"
    assert "example.com" in narrative.diagnosis
    assert narrative.priorities == ["Renovar TLS"]
