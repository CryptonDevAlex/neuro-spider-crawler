# AGENTS.md

Reglas de desarrollo para NeuroSpider. Aplican a personas y agentes de IA.

## Principios generales

- El contrato de eventos SSE en `docs/api-contract.md` es la fuente de verdad entre backend y frontend.
- Código autodescriptivo: nombres claros antes que comentarios. No añadir comentarios obvios.
- Idioma: español para documentación y UI; inglés para identificadores de código y mensajes de commit.
- Un cambio, un propósito. Mantener los diffs pequeños y revisables.
- Nunca subir secretos. Solo `.env.example` con valores de ejemplo.

## Git

- Usar **Conventional Commits**: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`, `ci:`.
- No hacer commit ni push salvo que el usuario lo pida explícitamente.
- El commit inicial acordado es `chore: initial project architecture and docs`.
- Nunca usar `--force`, reescribir historial ni cambiar la configuración de git del usuario.

## Backend (`backend/`)

- Python 3.12+, async/await en toda la cadena HTTP → Playwright → LLM.
- FastAPI con modelos Pydantic v2 para request, response y eventos.
- El crawler debe respetar `robots.txt`, profundidad máxima, pages máximas y delay entre requests.
- Playwright se inicializa una sola vez por crawl y se cierra en `finally`.
- El LLM devuelve siempre JSON validado por un esquema Pydantic; nunca texto libre sin validar.
- Los endpoints de SSE deben emitir eventos tipados: `status`, `node`, `table`, `summary`, `error`, `done`.
- Errores controlados: timeout, página bloqueada y fallo de LLM se convierten en eventos `error`, no en excepciones sin manejar.
- Antes de terminar: `ruff check .`, `mypy app` y `pytest`.

## Frontend (`frontend/`)

- Next.js App Router; componentes pequeños y centrados en una sola responsabilidad.
- Tailwind para estilos; tema oscuro tipo terminal financiera definido en `globals.css`.
- El estado del crawl vive en un único store (Zustand). Los componentes no hacen fetch directo.
- La conexión SSE se encapsula en `useCrawlStream`; los componentes solo consumen estado.
- La animación SVG debe degradarse con gracia y ser accesible (`aria-label`, `prefers-reduced-motion`).
- Evitar `any`. Usar los tipos de `src/lib/types.ts`.
- Antes de terminar: `npm run lint`, `npx tsc --noEmit` y `npm run build`.

## Alcance por fases

1. **Fase 1 (actual):** estructura, documentación, contratos y stubs. Sin lógica de negocio.
2. **Fase 2:** implementación del crawler, extracción, IA, SSE y UI en vivo.
3. **Fase 3:** exportación, métricas avanzadas, tests de integración y despliegue.

No implementar fases futuras sin que el usuario lo solicite.
