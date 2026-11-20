# NeuroSpider

Web Crawler visual con extracción estructurada y resumen ejecutivo impulsado por IA.

> **Estado actual:** Fase 1 — arquitectura base y documentación. La lógica completa de rastreo, IA y visualización en vivo se implementa en la Fase 2.

## Objetivo

El usuario ingresa una URL, un backend con **FastAPI + Playwright** rastrea el sitio (contenido, enlaces y tablas) y un **LLM** produce datos estructurados y un resumen ejecutivo. El frontend **Next.js + Tailwind** muestra en una vista dividida el mapa animado del rastreo y el panel de resultados con exportación a JSON/Markdown.

## Arquitectura

```mermaid
flowchart LR
    subgraph Client["Frontend · Next.js + Tailwind"]
        UI["URL Input / Terminal UI"]
        Hook["useCrawlStream (SSE)"]
        Map["SpiderMap SVG animado"]
        Panel["ResultsPanel"]
        Export["Export JSON / Markdown"]
        UI --> Hook
        Hook --> Map
        Hook --> Panel
        Panel --> Export
    end

    subgraph Server["Backend · FastAPI + Playwright"]
        API["POST /crawl"]
        Service["CrawlerService"]
        Policy["CrawlPolicy (robots, depth, delay)"]
        Browser["Playwright Browser Pool"]
        Extract["Extractors: contenido, enlaces, tablas"]
        LLM["LLM Client + prompts"]
        Summary["Resumen ejecutivo"]
        Stream["SSE Event Stream"]
        API --> Service
        Service --> Policy
        Service --> Browser
        Browser --> Extract
        Extract --> LLM
        LLM --> Summary
        Service --> Stream
    end

    Store[("Resultado del crawl")]

    UI -->|"URL + opciones"| API
    Stream -->|"text/event-stream"| Hook
    Extract --> Store
    Summary --> Store
    Store --> Panel
```

## Flujo de eventos (SSE)

```mermaid
sequenceDiagram
    participant UI as Frontend
    participant API as FastAPI
    participant SVC as CrawlerService
    participant PW as Playwright
    participant AI as LLM

    UI->>API: POST /crawl {url, max_depth, max_pages}
    API-->>UI: {crawl_id}
    UI->>API: GET /crawl/{crawl_id}/stream
    loop por cada página
        SVC->>PW: navegar y extraer
        PW-->>SVC: contenido + enlaces + tablas
        SVC-->>UI: event: node
        SVC->>AI: estructurar + resumir
        AI-->>SVC: JSON validado
        SVC-->>UI: event: summary
    end
    SVC-->>UI: event: done
```

## Estructura del repositorio

```text
neuro-spider-crawler/
├── backend/                 API, crawler, extracción, IA y modelos
│   ├── app/
│   │   ├── api/             rutas HTTP y dependencias
│   │   ├── core/            configuración, logging, eventos
│   │   ├── crawler/         Playwright, política, extractores
│   │   ├── ai/              cliente LLM, prompts, esquemas
│   │   ├── models/          contratos Pydantic
│   │   └── services/        orquestación y exportación
│   └── tests/
├── frontend/                App Router, componentes, hooks y store
├── docs/                    arquitectura, contrato de API, roadmap
├── AGENTS.md                reglas de desarrollo
└── README.md
```

## Stack

| Capa | Tecnologías |
| --- | --- |
| Backend | Python 3.12+, FastAPI, Playwright, Pydantic v2, pytest |
| IA | Cliente LLM configurable (OpenAI-compatible), salida validada con Pydantic |
| Frontend | Next.js (App Router), React, TypeScript, Tailwind CSS, Zustand |
| Tiempo real | Server-Sent Events (SSE) |
| Calidad | Conventional Commits, ruff/mypy (backend), ESLint/tsc (frontend) |

## Puesta en marcha (Fase 2)

```bash
# Backend
cd backend
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

Frontend: `http://localhost:3000` · Backend: `http://localhost:8000/docs`

## Convenciones

Los cambios deben seguir las reglas de [`AGENTS.md`](AGENTS.md) y los contratos de [`docs/api-contract.md`](docs/api-contract.md).
