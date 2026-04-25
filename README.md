# PostingPal

SvelteKit + Tailwind frontend, Flask API, SQLite. Google Gemini powers résumé/JD parsing, gap reports, and roadmaps — add `GEMINI_API_KEY` in `backend/.env`.

**Run:** `cd backend` → venv → `pip install -r requirements.txt` → copy `.env.example` to `.env` and set `SECRET_KEY` → `python wsgi.py`. Other terminal: `cd frontend` → `npm install` → `npm run dev` → **http://127.0.0.1:5173**

Flask config lives in `backend/.env`. You only need `frontend/.env` if you’re doing something non-default (see `frontend/.env.example`).

Tests: `cd backend`, venv on, `pytest`.
