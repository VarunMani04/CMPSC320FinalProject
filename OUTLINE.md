# PostingPal — Development Outline

Source: CMPSC 320 requirements (course project: Student Skill Gap Analyzer). This repo implements that spec as **PostingPal**. Stack: **SvelteKit + Tailwind** (frontend), **Flask + Gunicorn** (backend), **Claude API** (AI), **PostgreSQL** (optional), **Docker** (optional), **Pytest** (backend tests).

## 1. Product goals

- Structured career development for students and job seekers.
- Parse job descriptions, compare to student profile, produce validated gap analysis and learning roadmap with milestones.

## 2. Core features (use cases)

| ID | Feature | Summary |
|----|---------|---------|
| UC-01 | Student profile | Landing → create profile (skills, education, proficiency); validate; no duplicate email; redirect to dashboard. |
| UC-02 | Job description parser | Paste one or many JDs; extract skills/qualifications; hallucination checks; vague posting handling; multi-JD comparison table; rate-limit messaging. |
| UC-03 | Gap analysis report | Profile + parsed JDs → AI comparison (gap / partial / strong); validation; save report; optional PDF download; fallback rule-based report on API failure. |
| UC-04 | Roadmap & milestones | From gap report → prioritized missing skills, resources, estimates, tracker; complete milestones updates profile; new analysis resets path (with undo affordance); strong-fit path suggests adjacent roles. |

## 3. Architecture (MVC / packages)

- **Frontend**: UI, dashboard, forms, results display.
- **Backend (Flask API)**: Auth, orchestration, AI prompts, validation layer, persistence.
- **Database**: User accounts, profiles, skills, parsed jobs, reports, roadmaps, milestones.
- **External**: Claude API; credentials via environment (never commit secrets).

## 4. Quality attributes (priority)

- **High**: Performance (e.g. gap report in under ~10 seconds under normal conditions), security (auth, no cross-user access), usability (profile in ~5–10 min without help).
- **Medium**: Privacy (encryption at rest/in transit as appropriate), scalability, availability.

## 5. Implementation phases (suggested)

1. **Foundation**: Repo layout, env samples, health checks, CORS, local run docs.
2. **Auth & profile (UC-01)**: Registration/login, profile CRUD, skill proficiency model.
3. **Parser (UC-02)**: JD ingest API, Claude extraction + validation hooks, storage, comparison UI.
4. **Gap analysis (UC-03)**: Report generation, PDF export, retries and rule-based fallback.
5. **Roadmap (UC-04)**: Roadmap generation, resources validation, milestone completion sync to profile.
6. **Hardening**: Pytest coverage, rate-limit handling, security review, deployment story (optional Docker/PostgreSQL).

## 6. Testing (from requirements)

- **Pytest**: Unit/integration for Flask services and validation logic.
- **Prompts**: Iterative tuning against real JD samples; validation pipeline for AI outputs.
- Manual / system tests aligned with TS-01-01 … TS-01-04 in the requirements doc.

## 7. Constraints to remember

- Free/student-tier tools where possible; respect API rate limits.
- Agile/Scrum increments aligned with course deadlines.
- Document third-party ToS; academic integrity.
