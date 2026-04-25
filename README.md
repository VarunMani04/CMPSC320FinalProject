# PostingPal

Local full-stack app: **SvelteKit + Tailwind** (frontend) and **Flask + SQLite** (backend). Optional **Google Gemini** for résumé/JD parsing, gap reports, and roadmaps; heuristics work without an API key.

## Features

- Register / log in, student profile + skills (SQLite); optional PDF résumé parse (`POST /api/profile/parse-resume`)
- Job postings (paste JDs), analysis and stored skills
- Gap report vs profile + postings
- Roadmap with milestones and completion checkboxes
- Sage-inspired UI

## Layout

| Path | Purpose |
|------|---------|
| `frontend/` | SvelteKit app; dev server proxies `/api` → Flask |
| `backend/` | Flask API, SQLAlchemy models, LLM helpers |

## Prerequisites

- Node.js 18+
- Python 3.9+

## Run locally

**1. Backend**

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # set SECRET_KEY; optional GEMINI_API_KEY
python wsgi.py              # http://127.0.0.1:5000 — GET /api/health
```

**macOS:** AirPlay Receiver often uses port **5000**. Turn it off (*System Settings → General → AirDrop & Handoff → AirPlay Receiver*) **or** set `PORT=5001` in `backend/.env` and the same value as `FLASK_PORT` in `frontend/.env`.

With the venv active, from `backend/`: `pytest`

**2. Frontend** (separate terminal)

```bash
cd frontend
npm install
npm run dev                 # http://127.0.0.1:5173
```

Use **http://127.0.0.1:5173** (not mixed `localhost`) so cookies match backend CORS.

## Environment

| File | Purpose |
|------|---------|
| **`backend/.env`** | `SECRET_KEY`, optional `GEMINI_API_KEY` / `GOOGLE_API_KEY`, `GEMINI_MODEL`, `PORT`, `SESSION_COOKIE_SECURE`, `DATABASE_URL`, `CORS_ORIGINS` |
| **`frontend/.env`** | Usually omit. Optional `FLASK_PORT` if Flask is not on 5000; optional `API_ORIGIN` if the API is not local (see `frontend/.env.example`) |

Copy each folder’s `.env.example` → `.env`. Never commit secrets.

## Typical flow

1. Start Flask (`python wsgi.py`) and `npm run dev`.
2. Register → **Profile** → **Job postings** → **Gap report** → **Roadmap**.

If npm cache errors: `NPM_CONFIG_CACHE="$PWD/.npm-cache" npm install` from `frontend/`.
