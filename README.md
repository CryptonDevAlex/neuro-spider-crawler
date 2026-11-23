# 🕷️ NeuroSpider OSINT Crawler

**Multi-user passive security reconnaissance platform with live SSE streaming, JWT authentication, scheduled 24/7 monitoring, Markdown/PDF reports, and AI-powered executive diagnostics.**

> ⚠️ **Authorized use only.** NeuroSpider performs passive OSINT reconnaissance on authorized scopes. No active exploitation, port scanning, or intrusive testing. Use only on assets you own or have explicit permission to audit.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔐 **Multi-user SaaS** | Local registration + Google OIDC, JWT (7-day, httpOnly cookie), per-user isolated data |
| 🕷️ **Live Crawling** | FastAPI + Playwright (Chromium), controllable depth/pages/delay/audit-mode, SSE real-time stream |
| 🛡️ **Security Analysis** | Headers (CSP, HSTS, X-Frame-Options, etc.), forms/endpoints, JS/HTML comments, secrets/tokens, tech detection, cookies, TLS cert validation |
| 🌐 **Passive Recon** | Certificate Transparency subdomains (crt.sh), WAF/CDN fingerprinting (Cloudflare, AWS, Akamai, Imperva, Sucuri), robots.txt/sitemap.xml discovery |
| 📊 **Executive Diagnostics** | Local rule-based + optional AI (OpenAI/Groq/Gemini) generated security summary with severity classification (CRITICO/ALTO/MEDIO/BAJO/INFO) |
| 📈 **History & Diff** | Per-user scan history, side-by-side comparison (mitigated/new/persistent risks), one-click Markdown/PDF export, cached report cleanup |
| ⏰ **24/7 Monitoring** | APScheduler daily/weekly re-scans, per-target webhooks, HIGH/CRITICAL finding alerts |
| 🗄️ **Zero-External-DB** | SQLite local persistence (`backend/data/neurospider.db`), no external database required |
| 🎨 **Terminal-Style UI** | Next.js 15 App Router + Tailwind, dark Red Team aesthetic, animated SVG SpiderMap, real-time findings panel |

---

## 🏗️ Architecture (ASCII)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT (Next.js + Tailwind)                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐    │
│  │   Login     │──│  URL Input  │──│ useScanStream│──│  SpiderMap SVG  │    │
│  │  / Register │  │  Terminal   │  │   (SSE)      │  │  (Animated)     │    │
│  │  Google OIDC│  └──────┬──────┘  └──────┬──────┘  └────────┬────────┘    │
│  └─────────────┘         │                │                │             │
│                          ▼                ▼                ▼             │
│                   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│                   │ ResultsPanel│  │  Export     │  │  History &  │    │
│                   │ / Findings  │  │  MD / PDF   │  │  Diff       │    │
│                   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │
│                          │                │                │             │
│                          └────────────────┼────────────────┘             │
│                                           │                              │
│                                    ┌──────▼──────┐                        │
│                                    │ Monitoring  │                        │
│                                    │ 24/7 Tab    │                        │
│                                    └─────────────┘                        │
└─────────────────────────────────────│─────────────────────────────────────┘
                                      │ HTTPS + Cookie (SameSite=Lax)
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            SERVER (FastAPI + Playwright)                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐    │
│  │   Auth      │  │  POST /scan │  │ ScanService │──│  CrawlPolicy    │    │
│  │  (JWT/OIDC) │──│  (options)  │──│  (orchestr) │  │  (depth,delay)  │    │
│  └─────────────┘  └─────────────┘  └──────┬──────┘  └─────────────────┘    │
│                                           │                                 │
│                    ┌──────────────────────┼──────────────────────┐         │
│                    ▼                      ▼                      ▼         │
│             ┌─────────────┐        ┌─────────────┐        ┌─────────────┐  │
│             │ Playwright  │        │ Extractor   │        │  Analyzer   │  │
│             │ Browser     │───────▶│ (pages/forms│───────▶│ (headers/   │  │
│             │ (Chromium)  │        │  /scripts)  │        │  secrets/   │  │
│             └─────────────┘        └─────────────┘        │  tech/WAF)  │  │
│                                                           └──────┬──────┘  │
│                                                                  │         │
│                    ┌─────────────────────────────────────────────┘         │
│                    ▼                                                         │
│             ┌─────────────┐        ┌─────────────┐        ┌─────────────┐  │
│             │  Summary    │───────▶│  SQLite     │◀──────▶│  Scheduler  │  │
│             │  (AI/Local) │        │  (user_id)  │        │ (APScheduler)│ │
│             └──────┬──────┘        └─────────────┘        └──────┬──────┘  │
│                    │                                              │         │
│                    ▼                                              ▼         │
│             ┌─────────────┐                              ┌─────────────┐     │
│             │ SSE Stream  │                              │  Webhooks   │     │
│             │ (events)    │                              │ (alerts)    │     │
│             └─────────────┘                              └─────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.12+**
- **Node.js 20+** (for Next.js frontend)
- **Playwright Chromium** (auto-installed)

### Backend Setup
```bash
cd backend

# Create & activate virtual environment
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux/macOS:
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright Chromium
playwright install chromium

# Configure environment (optional AI, webhooks, admin user)
cp .env.example .env
# Edit .env with your keys (see Configuration below)

# Start server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
**Backend API:** `http://127.0.0.1:8000/docs` • **Health:** `http://127.0.0.1:8000/health`

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev -- --hostname 127.0.0.1 --port 3000
```
**Frontend:** `http://127.0.0.1:3000`

---

## ⚙️ Configuration (`.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_PATH` | `data/neurospider.db` | SQLite path relative to `backend/` |
| `JWT_SECRET_KEY` | *change in prod* | Secret for signing JWT tokens |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `10080` (7 days) | Token lifetime |
| `OPENAI_API_KEY` | — | Enable OpenAI-compatible diagnostics |
| `OPENAI_BASE_URL` | — | Custom endpoint (e.g., Groq: `https://api.groq.com/openai/v1`) |
| `OPENAI_MODEL` | — | Model name (e.g., `llama-3.1-8b-instant`) |
| `GEMINI_API_KEY` | — | Enable Google Gemini diagnostics |
| `LLM_PROVIDER` | `auto` | `auto` \| `openai` \| `gemini` \| `local` |
| `MONITORING_WEBHOOK_URL` | — | Global webhook for HIGH/CRITICAL alerts |
| `ADMIN_USER` / `ADMIN_EMAIL` / `ADMIN_PASSWORD` | — | Seed initial admin on first run |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | — | Enable Google OIDC login |
| `GOOGLE_REDIRECT_URI` | `http://127.0.0.1:8000/auth/google/callback` | OAuth callback |
| `FRONTEND_URL` | `http://127.0.0.1:3000` | Post-OAuth redirect |

> **No API keys?** The local rule engine generates full structured diagnostics automatically. Keys are never sent to frontend or included in reports.

---

## 📸 Screenshots / Demo

| View | Preview |
|------|---------|
| **Login / Terminal UI** | [INSERT_SCREENSHOT_LOGIN_HERE] |
| **Live SpiderMap + SSE Stream** | [INSERT_SCREENSHOT_MAP_HERE] |
| **Findings Panel + Severity Breakdown** | [INSERT_SCREENSHOT_FINDINGS_HERE] |
| **Executive Diagnostic (AI/Local)** | [INSERT_SCREENSHOT_DIAGNOSTIC_HERE] |
| **History & Diff Comparison** | [INSERT_SCREENSHOT_HISTORY_HERE] |
| **24/7 Monitoring Dashboard** | [INSERT_SCREENSHOT_MONITORING_HERE] |
| **Markdown / PDF Report Export** | [INSERT_SCREENSHOT_REPORT_HERE] |

---

## 🧪 Verification & Quality

```bash
# Backend
cd backend
pytest -q
ruff check .
mypy app

# Frontend
cd ../frontend
npm run lint
npm run typecheck
npm run build
```

---

## 📁 Repository Structure

```
neuro-spider-crawler/
├── backend/
│   ├── app/
│   │   ├── analysis/        # Security analyzers & recon
│   │   ├── api/             # HTTP routes & dependencies
│   │   ├── core/            # Config, logging, events
│   │   ├── crawler/         # Playwright, policy, extractors
│   │   ├── db/              # SQLAlchemy, repositories, SQLite
│   │   ├── models/          # Pydantic v2 contracts
│   │   └── services/        # Orchestration, SSE, export
│   ├── tests/
│   ├── requirements.txt
│   ├── pyproject.toml
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js App Router pages
│   │   ├── components/      # UI, SpiderMap, panels, suite
│   │   ├── hooks/           # useScanStream (SSE), state
│   │   └── lib/             # Types, API client
│   ├── package.json
│   ├── tailwind.config.ts
│   └── tsconfig.json
├── docs/                    # Architecture, API contract, roadmap
├── AGENTS.md                # Development rules for humans & AI
└── README.md
```

---

## 🛡️ Responsible Use

Before scanning, confirm you have **explicit authorization**. NeuroSpider is designed for:
- ✅ Authorized internal audits
- ✅ Bug bounty programs (within scope)
- ✅ Own assets / test environments

All reports include a passive-scope disclaimer, executive summary, severity table, and remediation guidance.

---

## 📜 License

**MIT License** — see [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch (`feat/amazing-feature`)
3. Follow [Conventional Commits](https://www.conventionalcommits.org/)
4. Run verification: `ruff check . && mypy app && pytest -q` (backend) / `npm run lint && npm run typecheck && npm run build` (frontend)
5. Open a PR

---

<div align="center">
  <sub>Built with ❤️ by <a href="https://github.com/CryptonDevAlex">CryptonDevAlex</a> • 
  <a href="https://www.linkedin.com/in/alex-alhuay-uquiche-191570308/">LinkedIn</a> • 
  Open to Work & Freelance 🟢</sub>
</div>