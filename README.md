# Student Skill Gap Analyzer (CMPSC 320)

Full-stack **Student Skill Gap Analyzer**: SvelteKit + Tailwind (frontend), Flask + Gunicorn (backend), Claude API for AI features, with optional PostgreSQL and Docker per the course requirements.

See [OUTLINE.md](./OUTLINE.md) for a development outline mapped to the requirements document (use cases, architecture, quality attributes, phased delivery).

## Repository layout

| Path | Purpose |
|------|---------|
| `frontend/` | SvelteKit app; dev server proxies `/api` → Flask on port 5000 |
| `backend/` | Flask app factory, REST API under `/api` |
| `OUTLINE.md` | Feature and implementation phases |

## Prerequisites

- Node.js 18+ (Node 20+ recommended if you use the `sv` CLI elsewhere)
- Python 3.9+

## Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # add ANTHROPIC_API_KEY when calling Claude
python wsgi.py              # http://127.0.0.1:5000 — try GET /api/health
pytest
```

Production-style serve: `gunicorn -w 2 -b 0.0.0.0:5000 wsgi:app` (from `backend/` with `PYTHONPATH=.` or run after `pip install -e .` — for now `python wsgi.py` is enough for dev).

## Frontend

```bash
cd frontend
npm install
npm run dev                 # http://127.0.0.1:5173 — API calls to /api are proxied to Flask
```

## Environment

- **Never commit** `.env` or API keys. Use `backend/.env.example` as a template.
- If your global npm cache has permission errors, you can use a project-local cache, for example:  
  `NPM_CONFIG_CACHE="$PWD/.npm-cache" npm install` (from `frontend/`).

## Next implementation steps

1. Authentication and student profile (UC-01) + database models.
2. Job description parser API and UI (UC-02).
3. Gap analysis report with validation and PDF export (UC-03).
4. Roadmap and milestone tracker (UC-04).
