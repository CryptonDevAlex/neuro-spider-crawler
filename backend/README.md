# Backend

FastAPI + Playwright + LLM. Contratos en `docs/api-contract.md`.

## Desarrollo

```bash
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
uvicorn app.main:app --reload --port 8000
```

## Calidad

```bash
ruff check .
mypy app
pytest
```
