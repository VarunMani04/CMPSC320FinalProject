from __future__ import annotations

import json

from flask import Blueprint, g, jsonify

from app.extensions import db
from app.models import GapReport, JobPosting, StudentProfile
from app.services import llm as llm_service
from app.utils.auth import login_required

bp = Blueprint("gap", __name__)


def _profile_text(profile: StudentProfile) -> str:
    skills = ", ".join(f"{s.name} ({s.proficiency})" for s in profile.skills)
    return (
        f"Name: {profile.full_name}\n"
        f"Education:\n{profile.education}\n"
        f"Experience:\n{profile.experience}\n"
        f"Skills: {skills or '(none listed)'}\n"
    )


@bp.get("/latest")
@login_required
def latest():
    rep = (
        GapReport.query.filter_by(user_id=g.current_user.id)
        .order_by(GapReport.created_at.desc())
        .first()
    )
    if not rep:
        return jsonify({"report": None})
    return jsonify({"report": json.loads(rep.report_json), "created_at": rep.created_at.isoformat() + "Z"})


@bp.post("/generate")
@login_required
def generate():
    profile = g.current_user.profile
    if not profile or not profile.full_name.strip():
        return jsonify({"error": "Complete your profile (including name) first"}), 400

    jobs = (
        JobPosting.query.filter_by(user_id=g.current_user.id)
        .filter(JobPosting.parsed_json.isnot(None))
        .order_by(JobPosting.created_at.asc())
        .all()
    )
    if not jobs:
        return jsonify({"error": "Parse at least one job description first"}), 400

    jobs_payload = []
    for j in jobs:
        try:
            parsed = json.loads(j.parsed_json or "{}")
        except json.JSONDecodeError:
            parsed = {}
        jobs_payload.append({"job_id": j.id, **parsed})

    profile_summary = _profile_text(profile)
    use_llm = llm_service.is_llm_available()
    try:
        if use_llm:
            report = llm_service.build_gap_report(profile_summary, jobs_payload)
        else:
            report = llm_service.rule_based_gap_fallback(profile_summary, jobs_payload)
    except Exception as exc:  # noqa: BLE001
        report = llm_service.rule_based_gap_fallback(profile_summary, jobs_payload)
        report["llm_error"] = str(exc)[:500]

    body = json.dumps(report, ensure_ascii=False)
    rep = GapReport(user_id=g.current_user.id, report_json=body)
    db.session.add(rep)
    db.session.commit()
    return jsonify({"report": report}), 201
