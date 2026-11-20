# Arquitectura

## Vista general

NeuroSpider es un sistema de dos procesos:

1. **Backend (FastAPI):** orquesta la navegación con Playwright, extrae superficie expuesta y analiza hallazgos de seguridad pasiva.
2. **Frontend (Next.js):** consume eventos SSE, dibuja el mapa de la araña y muestra métricas, hallazgos e informe exportable.

El resultado vive en memoria mientras dura el escaneo. No hay base de datos ni persistencia de evidencia sensible.

## Componentes del backend

| Módulo | Responsabilidad |
| --- | --- |
| `app/api/routes/crawl.py` | HTTP: crear scan, consultar resultado, suscribirse a SSE y descargar Markdown |
| `app/services/crawler_service.py` | Orquestación del flujo, modo auditoría y emisión de eventos |
| `app/crawler/policy.py` | Profundidad, páginas, delay, timeout y User-Agent |
| `app/crawler/browser.py` | Ciclo de vida del navegador Playwright |
| `app/crawler/spider.py` | Recorrido BFS y control de visitados |
| `app/crawler/extractors.py` | Formularios, inputs, enlaces, scripts, parámetros y HTML |
| `app/analysis/discovery.py` | Lectura de `robots.txt` y `sitemap.xml` como recon |
| `app/analysis/headers.py` | Comprobación de cabeceras de seguridad |
| `app/analysis/secrets.py` | Búsqueda enmascarada de tokens, claves, correos y rutas internas |
| `app/analysis/technologies.py` | Servidor, frameworks y cookies |
| `app/analysis/analyzer.py` | Consolidación de hallazgos, severidades y diagnóstico |
| `app/services/export_service.py` | Informe Markdown profesional |

## Componentes del frontend

| Módulo | Responsabilidad |
| --- | --- |
| `src/app/page.tsx` | Layout dividido izquierda/derecha |
| `src/components/crawler/SpiderMap.tsx` | SVG animado de la araña y nodos |
| `src/hooks/useScanStream.ts` | Suscripción SSE y deduplicación de eventos |
| `src/store/scan-store.ts` | Estado global del escaneo |
| `src/components/results/MetricsGrid.tsx` | Endpoints/formularios, JS, cabeceras y riesgo |
| `src/components/results/FindingsReport.tsx` | Panel de severidades y remediación |
| `src/components/results/TechPanel.tsx` | Tecnologías, cookies y cabeceras |
| `src/components/results/ExportBar.tsx` | Descarga del informe Markdown |

## Decisiones

- **SSE en lugar de WebSockets:** el flujo es unidireccional (servidor → cliente) y SSE simplifica reconexión y proxies.
- **Playwright:** permite ejecutar JavaScript y extraer superficie en páginas dinámicas.
- **Modo auditoría:** `robots.txt` y `sitemap.xml` no bloquean; amplían el inventario del reconocimiento autorizado.
- **Reglas locales:** el análisis de secretos y configuración se hace sin enviar contenido a proveedores externos.
- **Evidencia enmascarada:** los posibles secretos se truncan para no exponerlos en pantalla ni en el informe.
- **Deduplicación en cliente:** evita duplicados cuando EventSource se reconecta y reproduce eventos previos.

## Riesgos y límites

- Sitios con protección anti-bot: se maneja con eventos `error` por página, sin detener el resto del reconocimiento.
- Falsos positivos: los patrones de secretos son heurísticos; la evidencia debe validarse manualmente.
- Páginas muy grandes: el HTML y los scripts se limitan antes de analizarse.
- Alcance: está prohibido usar la herramienta sin autorización explícita sobre el objetivo.
