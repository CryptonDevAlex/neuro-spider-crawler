# Contrato de API y eventos SSE

Base URL: `http://127.0.0.1:8000`

Todas las operaciones están pensadas para reconocimiento pasivo sobre alcances autorizados.

Salvo `GET /health` y los endpoints públicos de `/auth`, los endpoints exigen `Authorization: Bearer <token>` o la cookie `httpOnly` emitida por el login. Todas las operaciones de escaneo, historial, informes y vigilancia filtran por el `user_id` del token; un usuario no puede ver, comparar ni borrar auditorías ajenas.

## Endpoints

### `POST /auth/register`

Request:

```json
{ "full_name": "Operador", "email": "operador@empresa.com", "password": "password123" }
```

Response `200`: JWT con expiración de 7 días y cookie `httpOnly`.

### `POST /auth/login`

Request:

```json
{ "email": "operador@empresa.com", "password": "password123" }
```

Response `200`:

```json
{ "access_token": "<jwt>", "token_type": "bearer", "expires_in": 604800 }
```

Además devuelve `Set-Cookie: neurospider_token=<jwt>; HttpOnly; SameSite=Lax`.

### `GET /auth/google/login`

Redirecciona a Google OIDC. Si `GOOGLE_CLIENT_ID` o `GOOGLE_CLIENT_SECRET` no están configurados, responde `503` con un mensaje informativo.

### `GET /auth/google/callback`

Valida `state`, intercambia el código, obtiene el perfil y crea o vincula la cuenta por correo/`google_id`, luego redirecciona a `FRONTEND_URL` con la cookie de sesión.

### `POST /auth/logout`

Elimina la cookie de sesión.

### `GET /auth/me`

Devuelve `{ "id": 1, "email": "...", "full_name": "...", "role": "admin" | "user" }` para el token vigente y la cuenta existente en SQLite.

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

Devuelve el historial del usuario autenticado, ordenado del más reciente al más antiguo.

### `GET /scans/{scan_id}`

Devuelve un escaneo guardado del usuario autenticado con el mismo contrato que `GET /scan/{scan_id}`. Un identificador ajeno responde `404`.

### `DELETE /scans/{scan_id}`

Elimina el registro SQLite, la entrada en memoria y cualquier PDF/Markdown cacheado asociado al escaneo, solo si pertenece al usuario autenticado.

### `GET /scans/compare?base_id=...&target_id=...`

Compara dos escaneos del usuario autenticado pertenecientes al mismo dominio y devuelve `resolved`, `new`, `persistent` y `counts`.

### `GET /monitoring/targets`

Lista los dominios en vigilancia continua del usuario autenticado.

### `POST /monitoring/targets`

Registra o actualiza un dominio vigilado del usuario autenticado con `domain`, `frequency` (`daily`/`weekly`) y `webhook_url` opcional. El mismo dominio puede ser vigilado por cuentas distintas.

### `PATCH /monitoring/targets/{target_id}`

Activa o pausa un dominio vigilado propio con `{ "active": true|false }`.

### `DELETE /monitoring/targets/{target_id}`

Elimina un dominio vigilado propio.

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
