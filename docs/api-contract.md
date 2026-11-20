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

### `GET /scan/{scan_id}/report.pdf`

Descarga un informe PDF corporativo con encabezado oscuro, resumen ejecutivo, tabla de severidades, WAF/CDN, subdominios por Certificate Transparency, detalle de hallazgos, guía técnica de remediación y aviso de reconocimiento pasivo autorizado.

### `GET /scans/history`

Devuelve el historial de escaneos persistidos en SQLite, ordenado del más reciente al más antiguo.

### `GET /scans/{scan_id}`

Devuelve un escaneo guardado con el mismo contrato que `GET /scan/{scan_id}` para recargarlo en pantalla.

### `GET /scans/compare?base_id=...&target_id=...`

Compara dos escaneos del mismo dominio y devuelve `resolved`, `new`, `persistent` y `counts`.

### `GET /monitoring/targets`

Lista los dominios en vigilancia continua.

### `POST /monitoring/targets`

Registra o actualiza un dominio vigilado con `domain`, `frequency` (`daily`/`weekly`) y `webhook_url` opcional.

### `PATCH /monitoring/targets/{target_id}`

Activa o pausa un dominio vigilado con `{ "active": true|false }`.

### `DELETE /monitoring/targets/{target_id}`

Elimina un dominio vigilado.

## Eventos

Todos los eventos llevan `event:` y un payload JSON con `type`, `scan_id` y `timestamp`.

| Evento | Payload | Momento |
| --- | --- | --- |
| `status` | `{ phase, pages_done, pages_total }` | Cambio de fase o progreso |
| `node` | `{ id, url, title, depth, links, forms, scripts, word_count }` | Página detectada y analizada |
| `finding` | `{ finding: { id, severity, category, title, description, evidence, remediation, target, source } }` | Hallazgo de seguridad detectado |
| `summary` | `{ executive_diagnosis, severity_counts, remediation_priorities, scope, engine, technologies, headers, subdomains, waf_detections }` | Análisis consolidado |
| `error` | `{ code, message, page_id? }` | Fallo parcial o fatal |
| `done` | `{ pages_scanned, findings_total, duration_ms, export_ready }` | Finalización |

Fases: `queued`, `discovering`, `analyzing`, `reporting`, `finished`.

Ejemplo:

```text
event: finding
data: {"type":"finding","scan_id":"...","finding":{"id":"tls-certificate-ejemplo-com","severity":"ALTO","category":"TLS/SSL","title":"Certificado TLS inválido detectado", ... }}

event: summary
data: {"type":"summary","scan_id":"...","engine":"openai","severity_counts":{...}, ...}

event: done
data: {"type":"done","scan_id":"...","pages_scanned":4,"findings_total":12,"duration_ms":4210,"export_ready":true}
```

## Códigos de error

| Código | Significado |
| --- | --- |
| `INVALID_URL` | URL mal formada o no http(s) |
| `NAVIGATION_TIMEOUT` | Playwright agotó el timeout |
| `NAVIGATION_ERROR` | No se pudo navegar a la página |
| `TLS_ERROR` | Fallo TLS al abrir la página |
| `CONNECTION_REFUSED` | El servidor rechazó la conexión |
| `DNS_ERROR` | No se pudo resolver el dominio |
| `HTTP_401` / `HTTP_403` | Acceso no autorizado; el scan continúa |
| `HTTP_429` | Límite de peticiones; el scan continúa |
| `HTTP_500`+ | Error del servidor; el scan continúa |
| `SCAN_FAILED` | Fallo general del reconocimiento |

Los errores por página son informativos y no detienen el escaneo. El evento `summary` incluye `engine`, con valor `local-rules`, `openai` o `gemini`.

## Notas de alcance

- No se realizan peticiones a puertos ni rutas fuera del host autorizado, salvo la descarga de scripts vinculados desde las páginas analizadas.
- La única consulta externa adicional es la API pública de Certificate Transparency en `crt.sh`, usada solo para enumerar subdominios publicados.
- No se envían payloads de ataque ni se intenta explotar ningún hallazgo.
- La evidencia se presenta de forma enmascarada cuando contiene posibles secretos.
