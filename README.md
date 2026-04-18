# Student Skill Gap Analyzer (CMPSC 320)

Full-stack app: **SvelteKit + Tailwind** (frontend), **Flask + Gunicorn + SQLite** (backend), **OpenAI** optional for JD parsing, gap analysis, and roadmaps (heuristic fallbacks run without an API key to save credits).

See [OUTLINE.md](./OUTLINE.md) for how this maps to the course requirements.

## What’s implemented

- **UC-01:** Register / log in (email + password), student profile + skills (SQLite).
- **UC-02:** Paste one or many job descriptions (`---` separators); analyze and store parsed skills (LLM or heuristic).
- **UC-03:** Gap report vs profile + saved postings (LLM or rule-based fallback).
- **UC-04:** Roadmap with milestones; checkboxes PATCH completion.
- **UI:** Neutral stone palette, simple “SG” mark, overview checklist on the dashboard.

## Repository layout

| Path | Purpose |
|------|---------|
| `frontend/` | SvelteKit UI; `vite` dev proxies `/api` → Flask `:5000` |
| `backend/` | Flask API, SQLAlchemy models, `app/services/llm.py` |
| `OUTLINE.md` | Requirements-aligned outline |

## Prerequisites

- Node.js 18+
- Python 3.9+

## Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # set SECRET_KEY; add OPENAI_API_KEY to enable LLM
python wsgi.py              # http://127.0.0.1:5000 — GET /api/health
pytest
```

Gunicorn (from `backend/`): `gunicorn -w 2 -b 127.0.0.1:5000 wsgi:app`

SQLite file default: `backend/instance/app.db`.

## Frontend

```bash
cd frontend
npm install
npm run dev                 # http://127.0.0.1:5173 — /api proxied to Flask
```

Use the same host as in backend CORS (`localhost` vs `127.0.0.1`) so session cookies match; the README defaults assume **127.0.0.1**.

## Environment

- **Never commit** `.env` or API keys.
- **`OPENAI_MODEL`:** defaults to `gpt-4o-mini` (set in `.env` if you want another small/cheap model).
- **Production / poster QR:** deploy frontend + backend, use HTTPS, set `SESSION_COOKIE_SECURE=true`, and add your public site origin to the `origins` list in `backend/app/__init__.py` for CORS + credentials.

## Poster / hosting (next step for you)

Pick a host pair (e.g. Vercel/Netlify for SvelteKit + Render/Fly/Railway for Flask), point the QR to the **public site URL**, and configure the SvelteKit **adapter** plus env vars so the browser calls your deployed API (same-site or CORS with credentials).

## Local flow

1. `python wsgi.py` and `npm run dev`.
2. Register → complete **Profile** → **Job postings** → **Gap report** → **Roadmap**.

If npm’s global cache errors on your machine:  
`NPM_CONFIG_CACHE="$PWD/.npm-cache" npm install` from `frontend/`.
