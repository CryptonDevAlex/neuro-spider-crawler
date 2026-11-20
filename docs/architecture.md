# Arquitectura

## Vista general

NeuroSpider es un sistema de dos procesos:

1. **Backend (FastAPI):** orquesta el crawl con Playwright, extrae datos, llama al LLM y emite eventos SSE.
2. **Frontend (Next.js):** consume eventos, dibuja el mapa de la araña y muestra resultados exportables.

No hay base de datos en la Fase 2: el resultado vive en memoria mientras dura el crawl. La exportación se genera al final.

## Componentes del backend

| Módulo | Responsabilidad |
| --- | --- |
| `app/api/routes` | HTTP: crear crawl, consultar estado, suscribirse a SSE |
| `app/services/crawler_service.py` | Orquestación del flujo y emisión de eventos |
| `app/crawler/policy.py` | robots.txt, profundidad, pages, delay, User-Agent |
| `app/crawler/browser.py` | Ciclo de vida del navegador Playwright |
| `app/crawler/spider.py` | Recorrido BFS y control de visitados |
| `app/crawler/extractors.py` | Texto, metadatos, enlaces y tablas |
| `app/ai/schemas.py` | Contrato de salida estructurada del LLM |
| `app/ai/client.py` | Cliente LLM configurable y reintentos |
| `app/services/export_service.py` | JSON y Markdown |

## Componentes del frontend

| Módulo | Responsabilidad |
| --- | --- |
| `src/app/page.tsx` | Layout dividido izquierda/derecha |
| `src/components/crawler/SpiderMap.tsx` | SVG animado de la araña y nodos |
| `src/components/results/*` | Métricas, resumen, tablas y exportación |
| `src/hooks/useCrawlStream.ts` | Suscripción SSE y reconexión |
| `src/store/crawl-store.ts` | Estado global del crawl |

## Decisiones

- **SSE en lugar de WebSockets:** el flujo es unidireccional (servidor → cliente) y SSE simplifica reconexión y proxies.
- **Playwright sobre requests:** permite ejecutar JavaScript y extraer páginas dinámicas.
- **Salida LLM validada:** se usa un esquema Pydantic para evitar respuestas no estructuradas.
- **Sin persistencia inicial:** reduce superficie; se añadirá en una fase posterior.

## Riesgos

- Sitios con protección anti-bot: se maneja con eventos `error` por página, sin detener el crawl completo.
- Coste/latencia del LLM: se resume una vez por crawl y se usa un modelo configurable.
- Páginas muy grandes: se limita el texto enviado al LLM por página.
