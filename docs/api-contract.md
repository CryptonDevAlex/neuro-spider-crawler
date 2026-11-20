# Contrato de API y eventos SSE

Base URL: `http://localhost:8000`

## Endpoints

### `POST /crawl`

Request:

```json
{
  "url": "https://example.com",
  "max_depth": 2,
  "max_pages": 30,
  "respect_robots": true
}
```

Response `202`:

```json
{ "crawl_id": "uuid", "status": "queued" }
```

### `GET /crawl/{crawl_id}`

Devuelve el estado y el resultado parcial/final.

### `GET /crawl/{crawl_id}/stream`

`Content-Type: text/event-stream`.

## Eventos

Todos los eventos llevan `event:` y un payload JSON con `type`, `crawl_id` y `timestamp`.

| Evento | Payload | Momento |
| --- | --- | --- |
| `status` | `{ phase, pages_done, pages_total }` | Cambio de fase o progreso |
| `node` | `{ id, url, title, depth, links, word_count }` | Página extraída |
| `table` | `{ node_id, headers, rows }` | Tabla detectada |
| `summary` | `{ executive_summary, key_points, entities }` | LLM finalizado |
| `error` | `{ node_id?, code, message }` | Fallo parcial o fatal |
| `done` | `{ pages_crawled, duration_ms, export_ready }` | Finalización |

Ejemplo:

```text
event: node
data: {"type":"node","crawl_id":"...","id":"n1","url":"https://example.com","title":"Example","depth":0,"links":12,"word_count":340}

event: done
data: {"type":"done","crawl_id":"...","pages_crawled":8,"duration_ms":4210,"export_ready":true}
```

## Códigos de error

| Código | Significado |
| --- | --- |
| `INVALID_URL` | URL mal formada o no http(s) |
| `ROBOTS_BLOCKED` | robots.txt impide el acceso |
| `NAVIGATION_TIMEOUT` | Playwright agotó el timeout |
| `LLM_ERROR` | Fallo del proveedor de IA |
| `EXPORT_ERROR` | No se pudo generar la exportación |
