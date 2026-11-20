# Roadmap

## Fase 1 — Arquitectura

- [x] Estructura `backend/` y `frontend/`
- [x] README con diagramas Mermaid
- [x] AGENTS.md
- [x] Contrato de API y eventos
- [x] Commit inicial y repositorio público

## Fase 2 — Crawler y UI en vivo

- [x] Configuración y app FastAPI
- [x] Política de navegación, profundidad, páginas y delay
- [x] Playwright: navegación y extracción
- [x] SSE end-to-end
- [x] UI terminal, SpiderMap animado y panel de resultados
- [x] Exportación JSON/Markdown
- [x] Ejecución en localhost
- [x] Corrección de CORS entre `127.0.0.1:3000` y `127.0.0.1:8000`

## Fase 3 — Reconocimiento pasivo de seguridad

- [x] Modo auditoría: `robots.txt` y `sitemap.xml` como descubrimiento
- [x] Análisis de cabeceras de seguridad
- [x] Inventario de formularios, inputs, endpoints y parámetros
- [x] Búsqueda de secretos, correos y rutas internas en HTML/JavaScript
- [x] Detección de tecnologías, frameworks y cookies
- [x] Diagnóstico ejecutivo con severidades y remediación
- [x] Métricas de seguridad y panel de hallazgos en el frontend
- [x] Botón MARKDOWN con informe profesional
- [x] Pruebas unitarias y verificaciones de calidad

## Fase 4 — Robustez para Internet real

- [x] Normalización `dominio.com` → `https://dominio.com` y redirecciones HTTP→HTTPS
- [x] User-Agent Chrome moderno en Playwright y `httpx`
- [x] Continuidad ante timeouts, `403`, `429` y errores por página
- [x] Hallazgo `ALTO` por certificado TLS vencido o autofirmado
- [x] Diagnóstico ejecutivo con OpenAI/Gemini opcional y fallback local
- [ ] Persistencia opcional de resultados
- [ ] Configuración de reglas por perfil de cliente
- [ ] Exportación PDF
- [ ] Docker Compose y despliegue
