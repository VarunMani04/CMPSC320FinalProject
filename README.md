# PostingPal (CMPSC 320)

Full-stack app: **SvelteKit + Tailwind** (frontend), **Flask + Gunicorn + SQLite** (backend), **Google Gemini** optional for JD parsing, gap analysis, and roadmaps (heuristic fallbacks run without an API key).

See [OUTLINE.md](./OUTLINE.md) for how this maps to the course requirements.

## What’s implemented

- **UC-01:** Register / log in (email + password), student profile + skills (SQLite). Profile page can **optionally fill fields from a PDF résumé** (`POST /api/profile/parse-resume`); save still uses **Save profile**.
- **UC-02:** Paste one or many job descriptions (`---` separators); analyze and store parsed skills (LLM or heuristic).
- **UC-03:** Gap report vs profile + saved postings (LLM or rule-based fallback).
- **UC-04:** Roadmap with milestones; checkboxes PATCH completion.
- **UI:** Sage-inspired palette, “PP” mark in the nav, overview checklist on the dashboard.

## Repository layout

| Path | Purpose |
|------|---------|
| `frontend/` | SvelteKit UI; `vite` dev proxies `/api` → Flask `:5000` |
| `backend/` | Flask API, SQLAlchemy models, `app/services/llm.py` |
| `showcase/` | Streamlit console: signs into Flask API, design-system styling (`app.py`, `design-system.json`) |
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
cp .env.example .env        # set SECRET_KEY; add GEMINI_API_KEY to enable LLM features
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

## Environment (what goes where)

| File | Purpose |
|------|---------|
| **`backend/.env`** | **`SECRET_KEY`** (required for real sessions). Optional: **`GEMINI_API_KEY`** or **`GOOGLE_API_KEY`**, **`GEMINI_MODEL`**, **`SESSION_COOKIE_SECURE`**, **`DATABASE_URL`**. |
| **`frontend/.env`** | Usually **omit** — `/api` proxies to `http://127.0.0.1:5000`. Optional: **`API_ORIGIN`** if Flask is elsewhere (see `frontend/.env.example`). |
| **`showcase/.env`** | **`API_BASE_URL`** = Flask only (default `http://127.0.0.1:5000`). **Do not** use the Svelte URL (`:5173` / `:4173`); Streamlit talks to Flask, not Vite. **Do not** put Gemini keys here — those belong in **`backend/.env`**. |

Copy each folder’s **`.env.example`** → **`.env`** and fill in values. **Never commit** `.env` or API keys.

- **`GEMINI_MODEL`:** defaults to `gemini-2.0-flash` (set in `backend/.env` if you want another model id).
- **Production / poster QR:** deploy frontend + backend, use HTTPS, set `SESSION_COOKIE_SECURE=true`, and add your public site origin to the `origins` list in `backend/app/__init__.py` for CORS + credentials.

## Streamlit console (`showcase/`)

Alternate **PostingPal** UI that talks to the **same Flask API** (email + password sign-in, then a **step-by-step workflow**: profile → job postings → language hints → gap report → roadmap). Styling is driven by **`showcase/design-system.json`**. **spaCy** powers **Language hints** from job text already stored on the server.

**Prerequisites:** run the Flask backend (`python wsgi.py` from `backend/`, default `http://127.0.0.1:5000`).

**Local run**

```bash
cd showcase
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # optional: set API_BASE_URL if Flask is not on 127.0.0.1:5000
streamlit run app.py
```

**Streamlit Community Cloud:** the Streamlit host must reach your **public** API URL; set **`API_BASE_URL`** in app secrets to that origin. Cookie-based sessions are issued by Flask and held in the Streamlit server’s `requests` session (fine for demos; the primary product remains the SvelteKit app).

## Poster / hosting (full SvelteKit + Flask stack)

Pick a host pair (e.g. Vercel/Netlify for SvelteKit + Render/Fly/Railway for Flask), point the QR to the **public site URL**, and configure the SvelteKit **adapter** plus env vars so the browser calls your deployed API (same-site or CORS with credentials).

## Local flow

1. `python wsgi.py` and `npm run dev`.
2. Register → complete **Profile** → **Job postings** → **Gap report** → **Roadmap**.

If npm’s global cache errors on your machine:  
`NPM_CONFIG_CACHE="$PWD/.npm-cache" npm install` from `frontend/`.
