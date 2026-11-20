from app.analysis.executive_summary import _parse_response, _resolve_provider
from app.core.config import Settings


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
