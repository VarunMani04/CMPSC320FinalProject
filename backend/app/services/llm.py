from __future__ import annotations

import json
import os
import re
from typing import Any

from openai import OpenAI

DEFAULT_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")


def _client() -> OpenAI | None:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        return None
    return OpenAI(api_key=key)


def _chat_json(system: str, user: str, *, max_tokens: int = 4096) -> dict[str, Any]:
    client = _client()
    if client is None:
        raise RuntimeError("OPENAI_API_KEY is not set")

    resp = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
        max_tokens=max_tokens,
    )
    content = resp.choices[0].message.content or "{}"
    return json.loads(content)


def parse_job_description(raw_text: str) -> dict[str, Any]:
    system = (
        "You extract structured hiring requirements from job postings. "
        "Return ONLY valid JSON with keys: "
        "title_guess (string), required_skills (array of strings), "
        "preferred_skills (array of strings), qualifications (array of strings), "
        "vague (boolean, true if the posting is too short or ambiguous to extract reliably). "
        "Skills should be concise noun phrases (e.g. Python, SQL, teamwork)."
    )
    user = f"Job posting text:\n\n{raw_text[:12000]}"
    data = _chat_json(system, user, max_tokens=2048)
    for key in ("required_skills", "preferred_skills", "qualifications"):
        if key not in data:
            data[key] = []
    if "title_guess" not in data:
        data["title_guess"] = ""
    data["vague"] = bool(data.get("vague"))
    return data


def build_gap_report(profile_summary: str, jobs_payload: list[dict[str, Any]]) -> dict[str, Any]:
    system = (
        "You compare a candidate profile to job requirements. Return ONLY valid JSON with keys: "
        "rows (array of objects with: requirement (string), match (one of gap, partial, strong), "
        "rationale (string)), comparison (optional object with overlap_skills, unique_per_job as array "
        "of {job_index, skills} when multiple jobs), summary (string). "
        "Be conservative: use gap when evidence is weak."
    )
    user = json.dumps({"profile": profile_summary, "jobs": jobs_payload}, ensure_ascii=False)
    return _chat_json(system, user, max_tokens=4096)


def build_roadmap(gap_summary: str, gaps_list: list[str]) -> dict[str, Any]:
    system = (
        "You create a concise learning roadmap. Return ONLY valid JSON with keys: "
        "milestones (array of {id (string uuid), title, description, resource_url (https URL or empty), "
        "weeks_estimate (number 0.5-8)}), intro (string). "
        "Order milestones by dependency (basics first). Use credible public resources when possible."
    )
    user = json.dumps({"gap_summary": gap_summary, "gaps": gaps_list}, ensure_ascii=False)
    return _chat_json(system, user, max_tokens=4096)


def rule_based_gap_fallback(profile_summary: str, jobs: list[dict[str, Any]]) -> dict[str, Any]:
    rows = []
    for job in jobs:
        for i in job.get("required_skills") or []:
            if isinstance(i, str) and i.strip():
                rows.append(
                    {
                        "requirement": i.strip(),
                        "match": "partial",
                        "rationale": "Heuristic fallback: verify against your profile manually.",
                    }
                )
    return {
        "rows": rows[:40],
        "comparison": {"overlap_skills": [], "unique_per_job": []},
        "summary": "Simplified rule-based report (AI unavailable). Treat items as a checklist, not grades.",
    }


def heuristic_parse(raw_text: str) -> dict[str, Any]:
    """Very rough keyword extraction without API."""
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


def _normalize_resume_profile(data: dict[str, Any]) -> dict[str, Any]:
    skills_out: list[dict[str, str]] = []
    for s in data.get("skills") or []:
        if isinstance(s, str) and s.strip():
            skills_out.append({"name": s.strip()[:120], "proficiency": "beginner"})
            continue
        if not isinstance(s, dict):
            continue
        name = (s.get("name") or "").strip()[:120]
        if not name:
            continue
        prof = (s.get("proficiency") or "beginner").lower()
        if prof not in ("beginner", "intermediate", "advanced"):
            prof = "beginner"
        skills_out.append({"name": name, "proficiency": prof})
    return {
        "full_name": (data.get("full_name") or "")[:200],
        "education": (data.get("education") or "")[:20000],
        "experience": (data.get("experience") or "")[:20000],
        "skills": skills_out[:40],
        "source": str(data.get("source") or "llm"),
    }


def _parse_resume_llm(raw_text: str) -> dict[str, Any]:
    system = (
        "You extract structured profile fields from a résumé or CV. "
        "Return ONLY valid JSON with keys: "
        "full_name (string), education (string, degrees/schools), "
        "experience (string, concise summary of roles and projects), "
        "skills (array of objects with name (string) and proficiency, one of beginner, intermediate, advanced). "
        "Use beginner when unsure. Skills should be technologies or clear competencies (e.g. Python, leadership)."
    )
    user = f"Résumé text:\n\n{raw_text[:14000]}"
    data = _chat_json(system, user, max_tokens=4096)
    data["source"] = "llm"
    return _normalize_resume_profile(data)


def heuristic_resume_profile(raw_text: str) -> dict[str, Any]:
    """Rough extraction when OpenAI is unavailable."""
    hp = heuristic_parse(raw_text)
    skill_names = [s for s in hp.get("required_skills") or [] if isinstance(s, str)][:20]
    skills = [{"name": n, "proficiency": "beginner"} for n in skill_names]
    lines = [ln.strip() for ln in raw_text.splitlines() if ln.strip()]
    full_name = ""
    if lines and "@" not in lines[0] and len(lines[0]) < 120:
        full_name = lines[0]
    experience = raw_text.strip()[:8000]
    return _normalize_resume_profile(
        {
            "full_name": full_name,
            "education": "",
            "experience": experience,
            "skills": skills,
            "source": "heuristic",
        }
    )


def parse_resume_from_text(raw_text: str) -> dict[str, Any]:
    """Parse résumé plain text into profile-shaped fields (LLM or heuristic)."""
    text = (raw_text or "").strip()
    if not text:
        return _normalize_resume_profile(
            {"full_name": "", "education": "", "experience": "", "skills": [], "source": "empty"}
        )
    if _client() is not None:
        try:
            return _parse_resume_llm(text)
        except Exception:
            return heuristic_resume_profile(text)
    return heuristic_resume_profile(text)
