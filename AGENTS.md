# AGENTS.md

Reglas de desarrollo para NeuroSpider. Aplican a personas y agentes de IA.

## Principios generales

- NeuroSpider realiza reconocimiento **pasivo** y OSINT solo sobre alcances autorizados.
- Está prohibido implementar explotación activa, fuzzing intrusivo, escaneo de puertos o evasión de controles.
- El contrato de eventos SSE en `docs/api-contract.md` es la fuente de verdad entre backend y frontend.
- Código autodescriptivo: nombres claros antes que comentarios. No añadir comentarios obvios.
- Idioma: español para documentación y UI; inglés para identificadores de código y mensajes de commit.
- Un cambio, un propósito. Mantener los diffs pequeños y revisables.
- Nunca subir secretos. Solo `.env.example` con valores de ejemplo.
- La evidencia de posibles secretos debe mostrarse enmascarada.

## Git

- Usar **Conventional Commits**: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`, `ci:`.
- No hacer commit ni push salvo que el usuario lo pida explícitamente.
- El commit inicial acordado es `chore: initial project architecture and docs`.
- Nunca usar `--force`, reescribir historial ni cambiar la configuración de git del usuario.
- Cuando el usuario pida varios commits, agrupar por propósito: backend, frontend, documentación y configuración.

## Backend (`backend/`)

- Python 3.12+, async/await en toda la cadena HTTP → Playwright → análisis.
- FastAPI con modelos Pydantic v2 para request, response y eventos.
- El modo auditoría es obligatorio: `robots.txt` y `sitemap.xml` se leen como fuentes de descubrimiento, no como bloqueos.
- Respetar profundidad máxima, páginas máximas, delay entre navegaciones y timeout.
- Playwright se inicializa una sola vez por scan y se cierra en `finally`.
- Los hallazgos se clasifican con `CRITICO`, `ALTO`, `MEDIO`, `BAJO` o `INFO`.
- Los endpoints de SSE deben emitir eventos tipados: `status`, `node`, `finding`, `summary`, `error`, `done`.
- Errores controlados: timeout y fallo de navegación se convierten en eventos `error`, no en excepciones sin manejar.
- Antes de terminar: `ruff check .`, `mypy app` y `pytest`.

## Frontend (`frontend/`)

- Next.js App Router; componentes pequeños y centrados en una sola responsabilidad.
- Tailwind para estilos; tema oscuro tipo terminal financiera definido en `globals.css`.
- El estado del scan vive en un único store (Zustand). Los componentes no hacen fetch directo, salvo la descarga del informe.
- La conexión SSE se encapsula en `useScanStream`; los componentes solo consumen estado.
- Los eventos repetidos por reconexión SSE deben deduplicarse por identificador.
- La animación SVG debe degradarse con gracia y ser accesible (`aria-label`, `prefers-reduced-motion`).
- Evitar `any`. Usar los tipos de `src/lib/types.ts`.
- Antes de terminar: `npm run lint`, `npm run typecheck` y `npm run build`.

## Alcance por fases

1. **Fase 1:** estructura, documentación, contratos y stubs.
2. **Fase 2:** navegación, SSE y UI en vivo.
3. **Fase 3 (actual):** reconocimiento pasivo de seguridad, informe Markdown y pruebas.
4. **Fase 4:** robustez, persistencia opcional y despliegue.

No implementar fases futuras sin que el usuario lo solicite.
