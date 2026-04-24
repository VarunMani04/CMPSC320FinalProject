from __future__ import annotations

import json

from flask import Blueprint, g, jsonify, request

from app.extensions import db
from app.models import JobPosting
from app.services import llm as llm_service
from app.utils.auth import login_required

bp = Blueprint("jobs", __name__)


def _job_dict(j: JobPosting) -> dict:
    parsed = None
    if j.parsed_json:
        try:
            parsed = json.loads(j.parsed_json)
        except json.JSONDecodeError:
            parsed = None
    return {
        "id": j.id,
        "raw_text": j.raw_text,
        "parsed": parsed,
        "vague": j.vague,
        "parse_error": j.parse_error,
        "created_at": j.created_at.isoformat() + "Z",
    }


@bp.get("")
@login_required
def list_jobs():
    rows = (
        JobPosting.query.filter_by(user_id=g.current_user.id)
        .order_by(JobPosting.created_at.desc())
        .all()
    )
    return jsonify({"jobs": [_job_dict(j) for j in rows]})


@bp.post("/analyze")
@login_required
def analyze_batch():
    """Replace user's postings with a new batch, parse each (LLM or heuristic)."""
    data = request.get_json(silent=True) or {}
    texts = data.get("postings") or data.get("texts")
    if not texts or not isinstance(texts, list):
        return jsonify({"error": "Provide postings as a non-empty array of strings"}), 400
    cleaned = []
    for t in texts:
        if isinstance(t, str) and t.strip():
            cleaned.append(t.strip())
    if not cleaned:
        return jsonify({"error": "No non-empty job descriptions"}), 400

    JobPosting.query.filter_by(user_id=g.current_user.id).delete(synchronize_session=False)
    db.session.commit()

    use_llm = llm_service.is_llm_available()
    results = []
    for raw in cleaned:
        job = JobPosting(user_id=g.current_user.id, raw_text=raw)
        db.session.add(job)
        db.session.flush()
        try:
            if use_llm:
                parsed = llm_service.parse_job_description(raw)
            else:
                parsed = llm_service.heuristic_parse(raw)
            job.parsed_json = json.dumps(parsed, ensure_ascii=False)
            job.vague = bool(parsed.get("vague"))
            job.parse_error = None
        except Exception as exc:  # noqa: BLE001
            job.parse_error = str(exc)[:500]
            job.parsed_json = json.dumps(llm_service.heuristic_parse(raw), ensure_ascii=False)
            job.vague = True
        results.append(job)

    db.session.commit()
    return jsonify({"jobs": [_job_dict(j) for j in results]}), 201
