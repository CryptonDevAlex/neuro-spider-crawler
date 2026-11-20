import json
import logging

import httpx
from pydantic import BaseModel, Field

from app.core.config import Settings
from app.models.security import Finding, Severity

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "Eres un auditor senior de seguridad. Redactas diagnósticos ejecutivos para reconocimiento "
    "pasivo y OSINT autorizado. No afirmes explotación, no inventes evidencia y mantén un tono "
    "profesional, claro y accionable. Responde únicamente JSON válido."
)


class ExecutiveNarrative(BaseModel):
    diagnosis: str = Field(min_length=40)
    priorities: list[str] = Field(default_factory=list)
    engine: str = "local-rules"


async def build_executive_summary(
    target: str,
    findings: list[Finding],
    severity_counts: dict[str, int],
    scope: dict[str, int],
    settings: Settings,
) -> ExecutiveNarrative:
    provider, api_key = _resolve_provider(settings)

    if provider and api_key:
        try:
            content = await _request_llm(
                provider=provider,
                api_key=api_key,
                target=target,
                findings=findings,
                severity_counts=severity_counts,
                scope=scope,
                settings=settings,
            )
            return _parse_response(content, engine=_engine_label(settings, provider))
        except Exception as exc:
            logger.warning(
                "LLM summary failed with %s; falling back to local rules",
                type(exc).__name__,
            )

    return local_executive_summary(target, findings, severity_counts, scope)


def local_executive_summary(
    target: str,
    findings: list[Finding],
    severity_counts: dict[str, int],
    scope: dict[str, int],
) -> ExecutiveNarrative:
    critical = severity_counts.get(Severity.CRITICAL.value, 0)
    high = severity_counts.get(Severity.HIGH.value, 0)
    medium = severity_counts.get(Severity.MEDIUM.value, 0)
    risk_total = critical + high + medium

    if critical:
        priority_note = (
            "Hay exposición crítica de credenciales o secretos: revocar, retirar y rotar antes de cualquier entrega."
        )
    elif high:
        priority_note = (
            "Hay debilidades de severidad alta: corregir TLS, cabeceras y superficie expuesta antes de publicar."
        )
    elif risk_total:
        priority_note = (
            "No se detectaron riesgos críticos ni altos; priorizar el endurecimiento de cabeceras y superficie."
        )
    else:
        priority_note = "No se detectaron riesgos medios o superiores en el alcance analizado."

    diagnosis = (
        f"Reconocimiento pasivo completado sobre {target}. Se revisaron "
        f"{scope.get('pages', 0)} páginas, {scope.get('endpoints', 0)} endpoints y "
        f"{scope.get('js_files', 0)} archivos JavaScript, con {len(findings)} hallazgos en total. "
        f"Distribución: {critical} críticos, {high} altos y {medium} medios. {priority_note} "
        "El análisis fue no intrusivo y se realizó dentro del alcance autorizado."
    )

    priorities: list[str] = []
    for severity in (Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM):
        for finding in findings:
            if finding.severity == severity and finding.remediation not in priorities:
                priorities.append(finding.remediation)
        if len(priorities) >= 5:
            break

    return ExecutiveNarrative(
        diagnosis=diagnosis,
        priorities=priorities[:5],
        engine="local-rules",
    )


def _resolve_provider(settings: Settings) -> tuple[str | None, str]:
    provider = settings.llm_provider.strip().lower()

    if provider in ("openai", "openai-compatible"):
        return "openai", settings.openai_api_key or settings.llm_api_key
    if provider == "gemini":
        return "gemini", settings.gemini_api_key
    if provider == "auto":
        if settings.openai_api_key or settings.llm_api_key:
            return "openai", settings.openai_api_key or settings.llm_api_key
        if settings.gemini_api_key:
            return "gemini", settings.gemini_api_key

    return None, ""


def _engine_label(settings: Settings, provider: str) -> str:
    if provider != "openai":
        return provider

    base_url = settings.openai_base_url.lower()
    model = (settings.llm_model or settings.openai_model).lower()
    if "groq" in base_url:
        if "llama-3.3" in model:
            return "Groq (Llama 3.3)"
        return "Groq"
    return "openai"


async def _request_llm(
    provider: str,
    api_key: str,
    target: str,
    findings: list[Finding],
    severity_counts: dict[str, int],
    scope: dict[str, int],
    settings: Settings,
) -> str:
    user_prompt = _build_prompt(target, findings, severity_counts, scope)

    async with httpx.AsyncClient(timeout=30.0) as client:
        if provider == "openai":
            model = settings.llm_model or settings.openai_model
            response = await client.post(
                f"{settings.openai_base_url.rstrip('/')}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0.2,
                },
            )
            response.raise_for_status()
            return str(
                response.json()["choices"][0]["message"]["content"]
            )

        model = settings.llm_model or settings.gemini_model
        response = await client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            headers={
                "x-goog-api-key": api_key,
                "Content-Type": "application/json",
            },
            json={
                "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
                "generationConfig": {
                    "responseMimeType": "application/json",
                    "temperature": 0.2,
                },
            },
        )
        response.raise_for_status()
        return str(response.json()["candidates"][0]["content"]["parts"][0]["text"])


def _build_prompt(
    target: str,
    findings: list[Finding],
    severity_counts: dict[str, int],
    scope: dict[str, int],
) -> str:
    summary = [
        {
            "severity": finding.severity.value,
            "title": finding.title,
            "description": finding.description,
            "remediation": finding.remediation,
        }
        for finding in findings[:20]
    ]

    context = {
        "target": target,
        "severity_counts": severity_counts,
        "scope": scope,
        "findings": summary,
    }

    payload = json.dumps(context, ensure_ascii=False)[:18000]

    return (
        f"Redacta un diagnóstico ejecutivo de seguridad pasiva y hasta cinco prioridades de "
        f"remediación usando exclusivamente este contexto:\n{payload}\n\n"
        'Devuelve JSON con la forma {"diagnosis":"...","priorities":["..."]}. '
        "El diagnóstico debe tener entre 200 y 500 caracteres, mencionar el alcance autorizado "
        "y no incluir recomendaciones que no aparezcan en el contexto."
    )


def _parse_response(content: str, engine: str) -> ExecutiveNarrative:
    data = json.loads(_extract_json(content))
    diagnosis = data.get("diagnosis") or data.get("diagnostico")
    priorities = data.get("priorities") or data.get("prioridades") or []

    if not isinstance(diagnosis, str) or len(diagnosis.strip()) < 40:
        raise ValueError("Diagnóstico inválido")
    if not isinstance(priorities, list):
        raise TypeError("Prioridades inválidas")

    clean_priorities = [str(item).strip() for item in priorities if str(item).strip()][:5]

    return ExecutiveNarrative(
        diagnosis=diagnosis.strip()[:2000],
        priorities=clean_priorities,
        engine=engine,
    )


def _extract_json(content: str) -> str:
    text = content.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]

    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("Respuesta sin JSON")

    return text[start : end + 1]
