# Contrato de API y eventos SSE

Base URL: `http://127.0.0.1:8000`

Todas las operaciones están pensadas para reconocimiento pasivo sobre alcances autorizados.

## Endpoints

### `POST /scan`

Request:

```json
{
  "url": "http://127.0.0.1:8080/index.html",
  "max_depth": 2,
  "max_pages": 20,
  "audit_mode": true
}
```

`audit_mode=true` habilita el modo auditoría: `robots.txt` y `sitemap.xml` se consumen como fuentes de descubrimiento y no bloquean el análisis.

Response `202`:

```json
{ "scan_id": "uuid", "status": "running" }
```

### `GET /scan/{scan_id}`

Devuelve el resultado parcial o final: páginas, cabeceras, formularios, tecnologías, hallazgos, rutas descubiertas y resumen.

### `GET /scan/{scan_id}/stream`

`Content-Type: text/event-stream`. Emite eventos tipados mientras avanza el reconocimiento.

### `GET /scan/{scan_id}/report.md`

Descarga el informe Markdown profesional con diagnóstico ejecutivo, severidades, evidencia, superficie identificada y prioridades de remediación.

## Eventos

Todos los eventos llevan `event:` y un payload JSON con `type`, `scan_id` y `timestamp`.

| Evento | Payload | Momento |
| --- | --- | --- |
| `status` | `{ phase, pages_done, pages_total }` | Cambio de fase o progreso |
| `node` | `{ id, url, title, depth, links, forms, scripts, word_count }` | Página detectada y analizada |
| `finding` | `{ finding: { id, severity, category, title, description, evidence, remediation, target, source } }` | Hallazgo de seguridad detectado |
| `summary` | `{ executive_diagnosis, severity_counts, remediation_priorities, scope, technologies, headers }` | Análisis consolidado |
| `error` | `{ code, message, page_id? }` | Fallo parcial o fatal |
| `done` | `{ pages_scanned, findings_total, duration_ms, export_ready }` | Finalización |

Fases: `queued`, `discovering`, `analyzing`, `reporting`, `finished`.

Ejemplo:

```text
event: finding
data: {"type":"finding","scan_id":"...","finding":{"id":"header-content-security-policy","severity":"ALTO","category":"Cabeceras HTTP","title":"Cabecera ausente: Content-Security-Policy", ... }}

event: done
data: {"type":"done","scan_id":"...","pages_scanned":4,"findings_total":12,"duration_ms":4210,"export_ready":true}
```

## Códigos de error

| Código | Significado |
| --- | --- |
| `INVALID_URL` | URL mal formada o no http(s) |
| `NAVIGATION_TIMEOUT` | Playwright agotó el timeout |
| `NAVIGATION_ERROR` | No se pudo navegar a la página |
| `SCAN_FAILED` | Fallo general del reconocimiento |

## Notas de alcance

- No se realizan peticiones a puertos ni rutas fuera del host autorizado, salvo la descarga de scripts vinculados desde las páginas analizadas.
- No se envían payloads de ataque ni se intenta explotar ningún hallazgo.
- La evidencia se presenta de forma enmascarada cuando contiene posibles secretos.
