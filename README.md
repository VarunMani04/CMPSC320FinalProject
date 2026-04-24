# PostingPal (CMPSC 320)

Full-stack app: **SvelteKit + Tailwind** (frontend), **Flask + Gunicorn + SQLite** (backend), **OpenAI** optional for JD parsing, gap analysis, and roadmaps (heuristic fallbacks run without an API key to save credits).

See [OUTLINE.md](./OUTLINE.md) for how this maps to the course requirements.

## What’s implemented

- **UC-01:** Register / log in (email + password), student profile + skills (SQLite).
- **UC-02:** Paste one or many job descriptions (`---` separators); analyze and store parsed skills (LLM or heuristic).
- **UC-03:** Gap report vs profile + saved postings (LLM or rule-based fallback).
- **UC-04:** Roadmap with milestones; checkboxes PATCH completion.
- **UI:** Sage-inspired palette, “PP” mark in the nav, overview checklist on the dashboard.

## Repository layout

| Path | Purpose |
|------|---------|
| `frontend/` | SvelteKit UI; `vite` dev proxies `/api` → Flask `:5000` |
| `backend/` | Flask API, SQLAlchemy models, `app/services/llm.py` |
| `showcase/` | Streamlit demo: PDF + spaCy + Gemini (`app.py`, `requirements.txt`) |
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

## Streamlit showcase (PDF + spaCy + Gemini, one URL for a QR code)

For a **single free public URL** (good for a poster QR) without deploying the SvelteKit + Flask pair, use the Streamlit app under `showcase/`. It uses **pdfplumber** for PDF job text, **spaCy** (`en_core_web_sm`) for linguistic hints, and **Google Gemini** (free tier via AI Studio) for structured parse / gap / roadmap. Heuristics still work if the key is missing.

**Local run**

```bash
cd showcase
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Or from the repo root: `streamlit run showcase/app.py` (then set working directory if imports fail; prefer `cd showcase` as above).

For a **persistent local key** (recommended for daily use), copy `showcase/.env.example` to **`showcase/.env`**, add `GEMINI_API_KEY=...`, and restart Streamlit. That file is **gitignored** so it stays on your machine only. You can still use `export GEMINI_API_KEY=...` or the sidebar if you prefer.

**Streamlit Community Cloud (free hosting + QR)**

1. Push this repository to GitHub.
2. In [Streamlit Community Cloud](https://streamlit.io/cloud), create a new app from the repo.
3. Under **Advanced settings**: set **Main file path** to `showcase/app.py` and **Requirements file** to `showcase/requirements.txt`.
4. Add a secret **`GEMINI_API_KEY`** (value from [Google AI Studio](https://aistudio.google.com/apikey)).
5. Deploy, copy the `*.streamlit.app` URL, and encode it in your poster QR.

If the default model errors in your region, set secret **`GEMINI_MODEL`** to `gemini-1.5-flash` or change the model field in the sidebar.

## Poster / hosting (full SvelteKit + Flask stack)

Pick a host pair (e.g. Vercel/Netlify for SvelteKit + Render/Fly/Railway for Flask), point the QR to the **public site URL**, and configure the SvelteKit **adapter** plus env vars so the browser calls your deployed API (same-site or CORS with credentials).

## Local flow

1. `python wsgi.py` and `npm run dev`.
2. Register → complete **Profile** → **Job postings** → **Gap report** → **Roadmap**.

If npm’s global cache errors on your machine:  
`NPM_CONFIG_CACHE="$PWD/.npm-cache" npm install` from `frontend/`.
