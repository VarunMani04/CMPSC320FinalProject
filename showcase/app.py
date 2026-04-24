"""
PostingPal / Skill Gap — Streamlit showcase (PDF + spaCy + Gemini).
Run: streamlit run showcase/app.py  (from repo root)
"""

from __future__ import annotations

import io
import json
import os
import re
import uuid
from pathlib import Path
from typing import Any

import pdfplumber
import streamlit as st


def _load_showcase_dotenv() -> None:
    """Load persistent local config from showcase/.env (gitignored)."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    env_path = Path(__file__).resolve().parent / ".env"
    if env_path.is_file():
        load_dotenv(env_path)


_load_showcase_dotenv()

# Default model: free-tier friendly; override with GEMINI_MODEL env, Streamlit secret, or sidebar.
def _default_gemini_model() -> str:
    env = (os.environ.get("GEMINI_MODEL") or "").strip()
    if env:
        return env
    try:
        v = st.secrets.get("GEMINI_MODEL", "")
        if v:
            return str(v).strip()
    except Exception:
        pass
    return "gemini-2.0-flash"


def _response_text(resp: Any) -> str:
    try:
        return (resp.text or "").strip()
    except Exception:
        pass
    try:
        c = resp.candidates[0]
        parts = c.content.parts
        return "".join(getattr(p, "text", "") or "" for p in parts).strip()
    except Exception:
        return "{}"


def _parse_json_blob(raw: str) -> dict[str, Any]:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
        raw = re.sub(r"\s*```\s*$", "", raw)
    return json.loads(raw or "{}")


@st.cache_resource
def load_nlp():
    import spacy

    return spacy.load("en_core_web_sm")


def extract_pdf_text(file_bytes: bytes) -> str:
    out: list[str] = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            t = page.extract_text() or ""
            if t.strip():
                out.append(t)
    return "\n\n".join(out).strip()


def spacy_language_hints(text: str, nlp) -> dict[str, Any]:
    if not text.strip():
        return {"noun_chunks": [], "entities": [], "lemmas_top": []}
    doc = nlp(text[:80000])
    chunks: set[str] = set()
    for nc in doc.noun_chunks:
        s = nc.text.strip()
        if 2 < len(s) < 80:
            chunks.add(s)
    ents: set[str] = set()
    for ent in doc.ents:
        s = ent.text.strip()
        if s:
            ents.add(f"{s} ({ent.label_})")
    lemmas: dict[str, int] = {}
    for tok in doc:
        if tok.is_alpha and not tok.is_stop and tok.pos_ in ("NOUN", "PROPN"):
            lemmas[tok.lemma_.lower()] = lemmas.get(tok.lemma_.lower(), 0) + 1
    top_lemmas = sorted(lemmas, key=lambda k: -lemmas[k])[:25]
    return {
        "noun_chunks": sorted(chunks)[:35],
        "entities": sorted(ents)[:25],
        "lemmas_top": top_lemmas,
    }


def heuristic_parse(raw_text: str) -> dict[str, Any]:
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9+#.\-]{1,24}", raw_text)
    freq: dict[str, int] = {}
    for t in tokens:
        if len(t) < 3 or t.lower() in {"the", "and", "for", "you", "our", "all", "any"}:
            continue
        freq[t] = freq.get(t, 0) + 1
    top = sorted(freq, key=lambda k: (-freq[k], k))[:15]
    return {
        "title_guess": "",
        "required_skills": top,
        "preferred_skills": [],
        "qualifications": [],
        "vague": len(raw_text.strip()) < 80,
    }


def gemini_json(api_key: str, model_name: str, system: str, user: str) -> dict[str, Any]:
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name,
        generation_config=genai.GenerationConfig(
            temperature=0.2,
            response_mime_type="application/json",
        ),
    )
    prompt = f"{system}\n\nUser content:\n{user}"
    resp = model.generate_content(prompt)
    return _parse_json_blob(_response_text(resp))


def profile_summary_block(profile: dict[str, str]) -> str:
    skills = (profile.get("skills") or "").strip()
    return (
        f"Name: {profile.get('full_name', '').strip()}\n"
        f"Education:\n{profile.get('education', '').strip()}\n"
        f"Experience:\n{profile.get('experience', '').strip()}\n"
        f"Skills (free text):\n{skills or '(none listed)'}\n"
    )


def _postingpal_css() -> None:
    """Match main PostingPal Svelte UI: canvas, sage primary, soft cards, Inter."""
    st.markdown(
        """
<link rel="preconnect" href="https://fonts.googleapis.com" crossorigin>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  .stApp, [data-testid="stAppViewContainer"] {
    font-family: "Inter", system-ui, sans-serif !important;
  }
  .main .block-container {
    max-width: 52rem;
    padding-top: 1.75rem;
    padding-bottom: 3rem;
  }
  h1, h2, h3 {
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    color: #1a1a1a !important;
  }
  [data-testid="stSidebar"] {
    background-color: #f5f4f0 !important;
    border-right: 1px solid #e8e6e0 !important;
  }
  [data-testid="stSidebar"] .stMarkdown a {
    color: #4a6741 !important;
  }
  .stButton > button[kind="primary"] {
    background-color: #4a6741 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 8px rgba(74, 103, 65, 0.25) !important;
  }
  .stButton > button[kind="primary"]:hover {
    filter: brightness(1.06);
  }
  .stButton > button[kind="secondary"] {
    border-radius: 12px !important;
    border: 1px solid #dddddd !important;
    background: transparent !important;
    color: #3a3a3a !important;
    font-weight: 600 !important;
  }
  .stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: #f5f4f0;
    padding: 8px;
    border-radius: 16px;
    border: none;
  }
  .stTabs [data-baseweb="tab"] {
    border-radius: 12px;
    padding: 10px 18px;
    font-weight: 500;
    color: #6a6a6a;
  }
  .stTabs [aria-selected="true"] {
    background: #4a6741 !important;
    color: #ffffff !important;
  }
  div[data-testid="stExpander"] {
    background: #ffffff;
    border-radius: 16px !important;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
    border: none !important;
  }
  .stTextInput input, .stTextArea textarea {
    border-radius: 12px !important;
    border: none !important;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06) !important;
    color: #3a3a3a !important;
  }
  div[data-testid="stAlert"] {
    border-radius: 12px !important;
  }
  [data-testid="stHeader"] {
    background: rgba(236, 234, 228, 0.92);
    border-bottom: 1px solid #e0ddd6;
  }
</style>
        """,
        unsafe_allow_html=True,
    )


def init_state() -> None:
    defaults = {
        "profile": {
            "full_name": "",
            "education": "",
            "experience": "",
            "skills": "",
        },
        "jd_text": "",
        "parsed_job": None,
        "gap_report": None,
        "roadmap": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def main() -> None:
    st.set_page_config(page_title="Skill Gap Showcase", page_icon="📊", layout="wide")
    init_state()

    st.title("Student skill gap analyzer — showcase")
    st.caption("PDF job postings (pdfplumber) · linguistic hints (spaCy) · structured AI (Google Gemini, free tier)")

    def _gemini_key_from_env_or_secrets() -> str:
        env = (os.environ.get("GEMINI_API_KEY") or "").strip()
        if env:
            return env
        try:
            return str(st.secrets["GEMINI_API_KEY"]).strip()
        except Exception:
            return ""

    key_from_env_or_secrets = _gemini_key_from_env_or_secrets()

    with st.sidebar:
        st.markdown("**Gemini**")
        st.caption(
            "Free key: [Google AI Studio](https://aistudio.google.com/apikey). "
            "Cloud deploy: set secret `GEMINI_API_KEY`."
        )
        api_key = st.text_input(
            "API key (optional paste for local demo)",
            value="" if key_from_env_or_secrets else "",
            type="password",
            help="Not stored on disk. Prefer secrets/env for deployed apps.",
        )
        if key_from_env_or_secrets:
            api_key = key_from_env_or_secrets
        elif not (api_key or "").strip():
            api_key = ""

        model_name = st.text_input("Gemini model id", value=_default_gemini_model())
        has_key = bool(api_key.strip())

    nlp = None
    try:
        nlp = load_nlp()
    except OSError:
        st.warning("spaCy model missing. Run: `python -m spacy download en_core_web_sm`")

    tabs = st.tabs(["Profile", "Job posting", "NLP hints", "Gap report", "Roadmap"])

    with tabs[0]:
        st.session_state.profile["full_name"] = st.text_input(
            "Full name", value=st.session_state.profile["full_name"]
        )
        st.session_state.profile["education"] = st.text_area(
            "Education", value=st.session_state.profile["education"], height=100
        )
        st.session_state.profile["experience"] = st.text_area(
            "Experience", value=st.session_state.profile["experience"], height=120
        )
        st.session_state.profile["skills"] = st.text_area(
            "Skills (one per line or comma-separated)",
            value=st.session_state.profile["skills"],
            height=120,
        )

    with tabs[1]:
        up = st.file_uploader("Upload job description PDF", type=["pdf"])
        if up is not None:
            raw_bytes = up.getvalue()
            extracted = extract_pdf_text(raw_bytes)
            st.success(f"Extracted **{len(extracted)}** characters from PDF.")
            st.session_state.jd_text = extracted
        st.session_state.jd_text = st.text_area(
            "Job description text (paste or from PDF)",
            value=st.session_state.jd_text,
            height=280,
        )

    with tabs[2]:
        text = st.session_state.jd_text.strip()
        if not text:
            st.info("Add job text in the **Job posting** tab.")
        else:
            if nlp:
                hints = spacy_language_hints(text, nlp)
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown("**Noun chunks** (skill-like phrases)")
                    st.write(hints["noun_chunks"] or ["—"])
                with c2:
                    st.markdown("**Named entities**")
                    st.write(hints["entities"] or ["—"])
                with c3:
                    st.markdown("**Frequent content lemmas**")
                    st.write(hints["lemmas_top"] or ["—"])

            if st.button("Run JD parse (Gemini or heuristic)", type="primary"):
                if has_key:
                    try:
                        system = (
                            "You extract structured hiring requirements from job postings. "
                            "Return ONLY valid JSON with keys: "
                            "title_guess (string), required_skills (array of strings), "
                            "preferred_skills (array of strings), qualifications (array of strings), "
                            "vague (boolean, true if the posting is too short or ambiguous). "
                            "Skills should be concise noun phrases (e.g. Python, SQL, teamwork)."
                        )
                        data = gemini_json(api_key.strip(), model_name, system, text[:12000])
                        for key in ("required_skills", "preferred_skills", "qualifications"):
                            if key not in data:
                                data[key] = []
                        if "title_guess" not in data:
                            data["title_guess"] = ""
                        data["vague"] = bool(data.get("vague"))
                        st.session_state.parsed_job = data
                        st.success("Parsed with Gemini.")
                    except Exception as exc:
                        st.error(f"Gemini error: {exc}")
                        st.session_state.parsed_job = heuristic_parse(text)
                        st.warning("Fell back to heuristic parse.")
                else:
                    st.session_state.parsed_job = heuristic_parse(text)
                    st.warning("No API key — heuristic parse only.")

            if st.session_state.parsed_job:
                with st.expander("Parsed structure (JSON)", expanded=False):
                    st.json(st.session_state.parsed_job)

    with tabs[3]:
        prof = st.session_state.profile
        if not (prof.get("full_name") or "").strip():
            st.warning("Enter at least a **full name** on **Profile**.")
        elif not st.session_state.parsed_job:
            st.warning("Parse a job description in **NLP hints** first.")
        else:
            if st.button("Generate gap report", type="primary"):
                profile_summary = profile_summary_block(prof)
                jobs_payload = [{"job_id": 1, **st.session_state.parsed_job}]
                if has_key:
                    try:
                        system = (
                            "You compare a candidate profile to job requirements. Return ONLY valid JSON with keys: "
                            "rows (array of objects with: requirement (string), match (one of gap, partial, strong), "
                            "rationale (string)), comparison (optional object with overlap_skills, unique_per_job), "
                            "summary (string). Be conservative: use gap when evidence is weak."
                        )
                        user = json.dumps({"profile": profile_summary, "jobs": jobs_payload}, ensure_ascii=False)
                        st.session_state.gap_report = gemini_json(
                            api_key.strip(), model_name, system, user
                        )
                        st.success("Gap report from Gemini.")
                    except Exception as exc:
                        st.error(f"Gemini error: {exc}")
                        st.session_state.gap_report = None
                else:
                    rows = []
                    for s in st.session_state.parsed_job.get("required_skills") or []:
                        if isinstance(s, str) and s.strip():
                            rows.append(
                                {
                                    "requirement": s.strip(),
                                    "match": "partial",
                                    "rationale": "Heuristic: add Gemini key for AI match labels.",
                                }
                            )
                    st.session_state.gap_report = {
                        "rows": rows[:40],
                        "comparison": {"overlap_skills": [], "unique_per_job": []},
                        "summary": "Heuristic checklist (set GEMINI_API_KEY for full analysis).",
                    }
                    st.warning("No API key — checklist-style fallback.")

            if st.session_state.gap_report:
                st.subheader("Summary")
                st.write(st.session_state.gap_report.get("summary", ""))
                st.subheader("Rows")
                st.dataframe(st.session_state.gap_report.get("rows", []), use_container_width=True)

    with tabs[4]:
        gr = st.session_state.gap_report
        if not gr:
            st.warning("Generate a gap report first.")
        else:
            rows = gr.get("rows") or []
            gaps = [r.get("requirement") for r in rows if isinstance(r, dict) and r.get("match") == "gap"]
            summary = gr.get("summary") or ""

            if st.button("Generate roadmap", type="primary"):
                if has_key:
                    try:
                        system = (
                            "You create a concise learning roadmap. Return ONLY valid JSON with keys: "
                            "milestones (array of {id (string uuid), title, description, resource_url (https URL or empty), "
                            "weeks_estimate (number 0.5-8)}), intro (string). "
                            "Order milestones by dependency (basics first). Use credible public resources when possible."
                        )
                        user = json.dumps({"gap_summary": summary, "gaps": gaps}, ensure_ascii=False)
                        st.session_state.roadmap = gemini_json(api_key.strip(), model_name, system, user)
                        st.success("Roadmap from Gemini.")
                    except Exception as exc:
                        st.error(f"Gemini error: {exc}")
                        st.session_state.roadmap = None
                else:
                    ms = [
                        {
                            "id": str(uuid.uuid4()),
                            "title": f"Learn: {g}"[:200],
                            "description": "Add coursework or a small project to demonstrate this skill.",
                            "resource_url": "",
                            "weeks_estimate": 2,
                        }
                        for g in (gaps[:12] or ["Foundational skills for your target role"])
                    ]
                    st.session_state.roadmap = {
                        "intro": "Heuristic roadmap (add Gemini key for richer milestones).",
                        "milestones": ms,
                    }
                    st.warning("No API key — simple milestone list from gaps.")

            if st.session_state.roadmap:
                st.markdown(st.session_state.roadmap.get("intro", ""))
                for m in st.session_state.roadmap.get("milestones") or []:
                    if not isinstance(m, dict):
                        continue
                    with st.expander(m.get("title", "Milestone")):
                        st.write(m.get("description", ""))
                        if m.get("resource_url"):
                            st.link_button("Resource", m["resource_url"])
                        st.caption(f"~{m.get('weeks_estimate', '?')} week(s)")


if __name__ == "__main__":
    main()
