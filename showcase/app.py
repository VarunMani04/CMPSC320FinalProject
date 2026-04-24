"""
PostingPal — Streamlit console for the Flask API (design-system aligned).
Run from this folder: streamlit run app.py
Requires the Flask backend (default http://127.0.0.1:5000).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pandas as pd
import requests
import streamlit as st


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    p = Path(__file__).resolve().parent / ".env"
    if p.is_file():
        load_dotenv(p)


def _design_system_path() -> Path:
    return Path(__file__).resolve().parent / "design-system.json"


def _load_design_system() -> dict[str, Any]:
    p = _design_system_path()
    if not p.is_file():
        return {}
    with p.open(encoding="utf-8") as f:
        return json.load(f)


def _css_variables_block(ds: dict[str, Any]) -> str:
    if not ds:
        return """:root {
  --color-canvas: #ECEAE4;
  --color-card: #FFFFFF;
  --color-card-alt: #F5F4F0;
  --color-accent: #4A6741;
  --color-text-heading: #1A1A1A;
  --color-text-body: #3A3A3A;
  --color-text-muted: #8A8A8A;
  --color-text-on-dark: #FFFFFF;
  --radius-card: 20px;
  --radius-button: 12px;
  --shadow-card: 0 2px 12px rgba(0,0,0,0.06);
  --shadow-button: 0 2px 8px rgba(74,103,65,0.25);
  --spacing-card-pad: 24px;
  --font-family: 'Inter', system-ui, sans-serif;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
}"""
    tpl = (ds.get("designSystem") or {}).get("cssVariablesTemplate") or {}
    variables = (tpl.get("variables") or {}) if isinstance(tpl, dict) else {}
    lines = [f"  {k}: {v};" for k, v in variables.items()]
    return ":root {\n" + "\n".join(lines) + "\n}"


def _inject_design_system_css(ds: dict[str, Any]) -> None:
    root = _css_variables_block(ds)
    st.markdown(
        f"""
<link rel="preconnect" href="https://fonts.googleapis.com" crossorigin>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
{root}
  html, body, .stApp {{
    font-family: var(--font-family) !important;
    color: var(--color-text-body);
  }}
  .stApp {{
    background-color: var(--color-canvas) !important;
  }}
  .main .block-container {{
    max-width: 52rem;
    padding-top: var(--spacing-card-pad);
    padding-bottom: 48px;
  }}
  h1, h2, h3 {{
    color: var(--color-text-heading) !important;
    font-weight: var(--font-weight-bold) !important;
    letter-spacing: -0.02em !important;
  }}
  [data-testid="stSidebar"] {{
    background-color: var(--color-card) !important;
    border-right: 1px solid #e8e6e0 !important;
    box-shadow: var(--shadow-card);
  }}
  .stButton > button[kind="primary"] {{
    background-color: var(--color-accent) !important;
    color: var(--color-text-on-dark) !important;
    border: none !important;
    border-radius: var(--radius-button) !important;
    font-weight: var(--font-weight-semibold) !important;
    box-shadow: var(--shadow-button) !important;
  }}
  .stButton > button[kind="primary"]:hover {{
    filter: brightness(1.06);
  }}
  .stButton > button[kind="secondary"] {{
    border-radius: var(--radius-button) !important;
    border: 1px solid #dddddd !important;
    background: transparent !important;
    color: var(--color-text-body) !important;
    font-weight: var(--font-weight-semibold) !important;
  }}
  .stTextInput input, .stTextArea textarea {{
    border-radius: var(--radius-button) !important;
    border: none !important;
    box-shadow: var(--shadow-card) !important;
    color: var(--color-text-body) !important;
  }}
  div[data-testid="stExpander"] {{
    background: var(--color-card);
    border-radius: var(--radius-card) !important;
    box-shadow: var(--shadow-card);
    border: none !important;
  }}
  div[data-testid="stAlert"] {{
    border-radius: var(--radius-button) !important;
  }}
  [data-testid="stHeader"] {{
    background: color-mix(in srgb, var(--color-canvas) 92%, transparent);
    border-bottom: 1px solid #e0ddd6;
  }}
</style>
        """,
        unsafe_allow_html=True,
    )


def _api_base() -> str:
    return (os.environ.get("API_BASE_URL") or "http://127.0.0.1:5000").rstrip("/")


def _http() -> requests.Session:
    if "http_client" not in st.session_state:
        st.session_state.http_client = requests.Session()
    return st.session_state.http_client


def _reset_http() -> None:
    st.session_state.http_client = requests.Session()


def _current_user(http: requests.Session) -> dict[str, Any] | None:
    try:
        r = http.get(f"{_api_base()}/api/auth/me", timeout=20)
        if r.status_code != 200:
            return None
        u = r.json().get("user")
        return u if isinstance(u, dict) else None
    except requests.RequestException:
        return None


def _render_brand_header() -> None:
    st.markdown(
        """
<div style="display:flex;align-items:center;gap:14px;margin-bottom:8px;">
  <div style="width:44px;height:44px;border-radius:9999px;background:var(--color-accent-ghost,#E8EFE7);color:var(--color-accent,#4A6741);display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px;">PP</div>
  <div>
    <div style="font-size:1.5rem;font-weight:700;letter-spacing:-0.03em;color:var(--color-text-heading,#1a1a1a);">PostingPal</div>
    <div style="font-size:12px;color:var(--color-text-muted,#8a8a8a);margin-top:2px;">Skill gap analysis</div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def _render_auth(ds: dict[str, Any]) -> None:
    _inject_design_system_css(ds)
    panel = st.session_state.get("auth_panel", "login")
    _, c, _ = st.columns([1, 2, 1])
    with c:
        _render_brand_header()
        st.caption(
            f"API: `{_api_base()}` · Set `API_BASE_URL` in `showcase/.env` if your backend runs elsewhere."
        )

        if panel == "login":
            st.markdown("#### Sign in")
            st.caption("Your email is your account name.")
            with st.form("signin_form"):
                email = st.text_input("Email", autocomplete="email")
                password = st.text_input("Password", type="password", autocomplete="current-password")
                submitted = st.form_submit_button("Sign in", type="primary", use_container_width=True)
                if submitted:
                    if not email.strip() or not password:
                        st.error("Enter email and password.")
                    else:
                        http = _http()
                        try:
                            r = http.post(
                                f"{_api_base()}/api/auth/login",
                                json={"email": email.strip().lower(), "password": password},
                                timeout=60,
                            )
                        except requests.RequestException as exc:
                            st.error(f"Cannot reach API: {exc!s}. Is the Flask server running?")
                            submitted = False
                        if submitted:
                            if r.status_code == 200:
                                st.success("Signed in.")
                                st.rerun()
                            else:
                                try:
                                    err = r.json().get("error", r.text)
                                except Exception:
                                    err = r.text or "Sign-in failed"
                                st.error(err)
            if st.button("Create an account", use_container_width=True):
                st.session_state.auth_panel = "register"
                st.rerun()
        else:
            st.markdown("#### Create account")
            st.caption("Password must be at least 8 characters.")
            with st.form("register_form"):
                email = st.text_input("Email", key="reg_email", autocomplete="email")
                password = st.text_input("Password", type="password", key="reg_pw", autocomplete="new-password")
                submitted = st.form_submit_button("Create account", type="primary", use_container_width=True)
                if submitted:
                    if len(password) < 8:
                        st.error("Password must be at least 8 characters.")
                    else:
                        http = _http()
                        try:
                            r = http.post(
                                f"{_api_base()}/api/auth/register",
                                json={"email": email.strip().lower(), "password": password},
                                timeout=60,
                            )
                        except requests.RequestException as exc:
                            st.error(f"Cannot reach API: {exc!s}")
                            submitted = False
                        if submitted:
                            if r.status_code == 201:
                                st.success("Account created. You are signed in.")
                                st.session_state.auth_panel = "login"
                                st.rerun()
                            else:
                                try:
                                    err = r.json().get("error", r.text)
                                except Exception:
                                    err = r.text or "Registration failed"
                                st.error(err)
            if st.button("Back to sign in", use_container_width=True):
                st.session_state.auth_panel = "login"
                st.rerun()


def _load_profile_into_editor(http: requests.Session) -> None:
    r = http.get(f"{_api_base()}/api/profile", timeout=30)
    if r.status_code != 200:
        st.session_state.pf_skills_df = pd.DataFrame([{"name": "", "proficiency": "beginner"}])
        return
    p = r.json()
    st.session_state.pf_name = p.get("full_name") or ""
    st.session_state.pf_edu = p.get("education") or ""
    st.session_state.pf_exp = p.get("experience") or ""
    skills = p.get("skills") or []
    rows = [{"name": s.get("name", ""), "proficiency": s.get("proficiency", "beginner")} for s in skills if isinstance(s, dict)]
    st.session_state.pf_skills_df = pd.DataFrame(rows if rows else [{"name": "", "proficiency": "beginner"}])


def _save_profile(http: requests.Session) -> bool:
    skills_df: pd.DataFrame = st.session_state.get("pf_skills_df", pd.DataFrame())
    skills_out: list[dict[str, str]] = []
    for _, row in skills_df.iterrows():
        name = str(row.get("name") or "").strip()
        if not name:
            continue
        prof = str(row.get("proficiency") or "beginner").lower()
        if prof not in ("beginner", "intermediate", "advanced"):
            prof = "beginner"
        skills_out.append({"name": name[:120], "proficiency": prof})
    body = {
        "full_name": (st.session_state.get("pf_name") or "")[:200],
        "education": st.session_state.get("pf_edu") or "",
        "experience": st.session_state.get("pf_exp") or "",
        "skills": skills_out,
    }
    r = http.put(f"{_api_base()}/api/profile", json=body, timeout=60)
    if r.status_code != 200:
        try:
            st.error(r.json().get("error", r.text))
        except Exception:
            st.error(r.text or "Save failed")
        return False
    st.success("Profile saved.")
    return True


@st.cache_resource
def _load_nlp():
    import spacy

    return spacy.load("en_core_web_sm")


_WORKFLOW_STEPS: list[tuple[str, str, str]] = [
    ("profile", "Profile", "Your background and skills"),
    ("jobs", "Job postings", "Paste and analyze target roles"),
    ("nlp", "Language hints", "spaCy signals from saved postings"),
    ("gap", "Gap report", "Compare profile to requirements"),
    ("roadmap", "Roadmap", "Learning milestones"),
]


def _workflow_init() -> None:
    if "workflow_step" not in st.session_state:
        st.session_state.workflow_step = 0


def _workflow_render_sidebar_nav() -> None:
    st.markdown("**Workflow**")
    st.caption("Move through each step in order.")
    step = int(st.session_state.workflow_step)
    for i, (slug, title, sub) in enumerate(_WORKFLOW_STEPS):
        label = f"{i + 1}. {title}"
        is_here = i == step
        if st.button(
            label,
            key=f"wf_nav_{slug}",
            use_container_width=True,
            type="primary" if is_here else "secondary",
            help=sub,
        ):
            if i != step:
                st.session_state.workflow_step = i
                st.rerun()


def _workflow_footer_nav() -> None:
    step = int(st.session_state.workflow_step)
    last = len(_WORKFLOW_STEPS) - 1
    st.divider()
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.button("← Back", disabled=step <= 0, use_container_width=True):
            st.session_state.workflow_step = max(0, step - 1)
            st.rerun()
    with c2:
        slug, title, _sub = _WORKFLOW_STEPS[step]
        st.caption(f"Step {step + 1} of {len(_WORKFLOW_STEPS)} · **{title}**")
    with c3:
        if step >= last:
            if st.button("Finish", use_container_width=True):
                st.session_state.workflow_step = 0
                st.rerun()
        else:
            if st.button("Continue →", type="primary", use_container_width=True):
                st.session_state.workflow_step = min(last, step + 1)
                st.rerun()


def _page_profile(http: requests.Session) -> None:
    st.markdown("### Profile")
    st.caption("This data is saved to your PostingPal account when you click Save.")
    st.session_state.pf_name = st.text_input("Full name", value=st.session_state.get("pf_name", ""))
    st.session_state.pf_edu = st.text_area("Education", value=st.session_state.get("pf_edu", ""), height=100)
    st.session_state.pf_exp = st.text_area(
        "Experience and projects", value=st.session_state.get("pf_exp", ""), height=140
    )
    st.markdown("#### Skills")
    st.session_state.pf_skills_df = st.data_editor(
        st.session_state.pf_skills_df,
        column_config={
            "name": st.column_config.TextColumn("Skill", required=True),
            "proficiency": st.column_config.SelectColumn(
                "Level",
                options=["beginner", "intermediate", "advanced"],
                required=True,
            ),
        },
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
    )
    up = st.file_uploader("Import from PDF résumé (optional)", type=["pdf"])
    if up is not None and st.button("Extract into form", type="secondary"):
        try:
            files = {"file": (up.name, up.getvalue(), "application/pdf")}
            pr = http.post(f"{_api_base()}/api/profile/parse-resume", files=files, timeout=120)
        except requests.RequestException as exc:
            st.error(f"Request failed: {exc!s}")
            pr = None
        if pr is not None:
            if pr.status_code != 200:
                try:
                    st.error(pr.json().get("error", pr.text))
                except Exception:
                    st.error(pr.text)
            else:
                data = pr.json()
                if data.get("full_name"):
                    st.session_state.pf_name = data["full_name"]
                if data.get("education"):
                    st.session_state.pf_edu = data["education"]
                if data.get("experience"):
                    st.session_state.pf_exp = data["experience"]
                sk = data.get("skills") or []
                rows = [
                    {"name": s.get("name", ""), "proficiency": s.get("proficiency", "beginner")}
                    for s in sk
                    if isinstance(s, dict) and (s.get("name") or "").strip()
                ]
                st.session_state.pf_skills_df = pd.DataFrame(
                    rows if rows else [{"name": "", "proficiency": "beginner"}]
                )
                st.success("Extracted — review fields, then save.")
                st.rerun()
    if st.button("Save profile", type="primary"):
        _save_profile(http)
    if st.button("Reload from server", type="secondary"):
        _load_profile_into_editor(http)
        st.rerun()


def _page_jobs(http: requests.Session) -> None:
    st.markdown("### Job postings")
    st.caption("Separate multiple postings with a line containing only ---")
    jd = st.text_area("Job description text", height=260, key="jd_batch")
    if st.button("Analyze and save to account", type="primary"):
        parts = [p.strip() for p in jd.split("---") if p.strip()]
        if not parts:
            st.warning("Paste at least one job description.")
        else:
            try:
                r = http.post(f"{_api_base()}/api/jobs/analyze", json={"postings": parts}, timeout=180)
            except requests.RequestException as exc:
                st.error(f"Request failed: {exc!s}")
                r = None
            if r is not None:
                if r.status_code != 201:
                    try:
                        st.error(r.json().get("error", r.text))
                    except Exception:
                        st.error(r.text)
                else:
                    st.success("Job postings analyzed and stored.")
    try:
        lr = http.get(f"{_api_base()}/api/jobs", timeout=30)
        if lr.status_code == 200:
            jobs = lr.json().get("jobs") or []
            st.caption(f"{len(jobs)} posting(s) on file.")
            if jobs:
                with st.expander("Latest parsed summary"):
                    st.json(jobs[0].get("parsed") or {})
    except requests.RequestException:
        pass


def _page_nlp(http: requests.Session) -> None:
    st.markdown("### Language hints")
    st.caption("spaCy analysis of your most recent saved job posting.")
    try:
        jr = http.get(f"{_api_base()}/api/jobs", timeout=30)
        raw = ""
        if jr.status_code == 200:
            jobs = jr.json().get("jobs") or []
            if jobs:
                raw = jobs[0].get("raw_text") or ""
    except requests.RequestException:
        raw = ""
    if not raw.strip():
        st.info("Complete **Job postings** first, then return here.")
    else:
        try:
            nlp = _load_nlp()
        except OSError:
            st.warning("spaCy model not installed.")
            nlp = None
        if nlp:
            hints = _spacy_hints(raw, nlp)
            a, b, c = st.columns(3)
            with a:
                st.markdown("**Noun chunks**")
                st.write(hints["noun_chunks"] or ["—"])
            with b:
                st.markdown("**Entities**")
                st.write(hints["entities"] or ["—"])
            with c:
                st.markdown("**Top lemmas**")
                st.write(hints["lemmas_top"] or ["—"])


def _page_gap(http: requests.Session) -> None:
    st.markdown("### Gap report")
    st.caption("Uses your saved profile and job postings on the server.")
    if st.button("Generate gap report", type="primary"):
        try:
            r = http.post(f"{_api_base()}/api/gap-reports/generate", timeout=180)
        except requests.RequestException as exc:
            st.error(f"Request failed: {exc!s}")
            r = None
        if r is not None:
            if r.status_code != 201:
                try:
                    st.error(r.json().get("error", r.text))
                except Exception:
                    st.error(r.text)
            else:
                st.success("Gap report generated.")
    try:
        gr = http.get(f"{_api_base()}/api/gap-reports/latest", timeout=30)
        if gr.status_code == 200:
            rep = gr.json().get("report")
            if rep:
                st.markdown(f"**Summary**  \n{rep.get('summary', '')}")
                rows = rep.get("rows") or []
                if rows:
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            else:
                st.caption("No report yet.")
    except requests.RequestException:
        st.caption("Could not load latest report.")


def _page_roadmap(http: requests.Session) -> None:
    st.markdown("### Roadmap")
    st.caption("Built from your latest gap report.")
    if st.button("Generate roadmap", type="primary"):
        try:
            r = http.post(f"{_api_base()}/api/roadmap/generate", timeout=180)
        except requests.RequestException as exc:
            st.error(f"Request failed: {exc!s}")
            r = None
        if r is not None and r.status_code != 201:
            try:
                st.error(r.json().get("error", r.text))
            except Exception:
                st.error(r.text)
        elif r is not None:
            st.success("Roadmap updated.")
    try:
        rr = http.get(f"{_api_base()}/api/roadmap", timeout=30)
        if rr.status_code == 200:
            rm = rr.json().get("roadmap")
            if rm and rm.get("milestones"):
                st.markdown(rm.get("intro", ""))
                for m in rm["milestones"]:
                    if not isinstance(m, dict):
                        continue
                    mid = m.get("id", "")
                    title = m.get("title", "Milestone")
                    done = bool(m.get("completed"))
                    with st.expander(f"{'✓ ' if done else ''}{title}"):
                        st.write(m.get("description", ""))
                        if m.get("resource_url"):
                            st.link_button("Resource", m["resource_url"])
                        c1, c2 = st.columns(2)
                        with c1:
                            if not done and st.button("Mark complete", key=f"done_{mid}"):
                                http.patch(
                                    f"{_api_base()}/api/roadmap/milestones/{mid}",
                                    json={"completed": True},
                                    timeout=30,
                                )
                                st.rerun()
                        with c2:
                            if done and st.button("Mark incomplete", key=f"undone_{mid}"):
                                http.patch(
                                    f"{_api_base()}/api/roadmap/milestones/{mid}",
                                    json={"completed": False},
                                    timeout=30,
                                )
                                st.rerun()
            else:
                st.caption("No roadmap yet.")
    except requests.RequestException:
        st.caption("Could not load roadmap.")


def _spacy_hints(text: str, nlp) -> dict[str, Any]:
    if not text.strip():
        return {"noun_chunks": [], "entities": [], "lemmas_top": []}
    doc = nlp(text[:80000])
    chunks = sorted({nc.text.strip() for nc in doc.noun_chunks if 2 < len(nc.text.strip()) < 80})[:35]
    ents = sorted({f"{e.text.strip()} ({e.label_})" for e in doc.ents if e.text.strip()})[:25]
    lemmas: dict[str, int] = {}
    for tok in doc:
        if tok.is_alpha and not tok.is_stop and tok.pos_ in ("NOUN", "PROPN"):
            lemmas[tok.lemma_.lower()] = lemmas.get(tok.lemma_.lower(), 0) + 1
    top = sorted(lemmas, key=lambda k: -lemmas[k])[:25]
    return {"noun_chunks": chunks, "entities": ents, "lemmas_top": top}


def _main_logged_in(ds: dict[str, Any], user: dict[str, Any]) -> None:
    _inject_design_system_css(ds)
    _workflow_init()
    http = _http()

    uid = user.get("id")
    if st.session_state.get("profile_uid_cached") != uid:
        _load_profile_into_editor(http)
        st.session_state.profile_uid_cached = uid

    with st.sidebar:
        st.markdown("**Account**")
        st.caption(user.get("email") or "")
        if st.button("Sign out", use_container_width=True):
            try:
                http.post(f"{_api_base()}/api/auth/logout", timeout=15)
            except requests.RequestException:
                pass
            _reset_http()
            st.session_state.pop("pf_skills_df", None)
            st.session_state.pop("profile_uid_cached", None)
            st.session_state.pop("workflow_step", None)
            st.rerun()
        st.divider()
        _workflow_render_sidebar_nav()
        st.divider()
        st.caption("Session is held in this browser run only.")

    _render_brand_header()
    st.caption("Follow the workflow: profile → jobs → language review → gap analysis → roadmap.")

    step = int(st.session_state.workflow_step)
    slug = _WORKFLOW_STEPS[step][0]
    with st.container():
        if slug == "profile":
            _page_profile(http)
        elif slug == "jobs":
            _page_jobs(http)
        elif slug == "nlp":
            _page_nlp(http)
        elif slug == "gap":
            _page_gap(http)
        else:
            _page_roadmap(http)

    _workflow_footer_nav()


def main() -> None:
    _load_dotenv()
    ds = _load_design_system()
    st.set_page_config(page_title="PostingPal", page_icon="🌿", layout="wide", initial_sidebar_state="expanded")

    http = _http()
    user = _current_user(http)
    if not user:
        _render_auth(ds)
        return

    _main_logged_in(ds, user)


if __name__ == "__main__":
    main()
