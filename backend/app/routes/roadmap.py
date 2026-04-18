from __future__ import annotations

import json
import uuid

from flask import Blueprint, g, jsonify, request

from app.extensions import db
from app.models import GapReport, Roadmap
from app.services import llm as llm_service
from app.utils.auth import login_required

bp = Blueprint("roadmap", __name__)


def _normalize_milestones(raw: list) -> list[dict]:
    out = []
    for i, m in enumerate(raw or []):
        if not isinstance(m, dict):
            continue
        mid = m.get("id") or str(uuid.uuid4())
        out.append(
            {
                "id": str(mid),
                "title": (m.get("title") or f"Milestone {i + 1}")[:200],
                "description": (m.get("description") or "")[:4000],
                "resource_url": (m.get("resource_url") or "")[:500],
                "weeks_estimate": float(m.get("weeks_estimate") or 1),
                "completed": bool(m.get("completed")),
            }
        )
    return out


def _load_roadmap_payload(rm: Roadmap) -> dict:
    try:
        raw = json.loads(rm.milestones_json or "{}")
    except json.JSONDecodeError:
        return {"intro": "", "milestones": []}
    if isinstance(raw, list):
        return {"intro": "", "milestones": raw}
    if isinstance(raw, dict):
        return {
            "intro": raw.get("intro") or "",
            "milestones": raw.get("milestones") or [],
        }
    return {"intro": "", "milestones": []}


def _save_roadmap_payload(intro: str, milestones: list[dict]) -> str:
    return json.dumps({"intro": intro, "milestones": milestones}, ensure_ascii=False)


@bp.get("")
@login_required
def get_roadmap():
    rm = Roadmap.query.filter_by(user_id=g.current_user.id).first()
    if not rm:
        return jsonify({"roadmap": None})
    payload = _load_roadmap_payload(rm)
    return jsonify(
        {
            "roadmap": {
                **payload,
                "updated_at": rm.updated_at.isoformat() + "Z",
            }
        }
    )


@bp.post("/generate")
@login_required
def generate():
    rep = (
        GapReport.query.filter_by(user_id=g.current_user.id)
        .order_by(GapReport.created_at.desc())
        .first()
    )
    if not rep:
        return jsonify({"error": "Generate a gap analysis report first"}), 400

    try:
        data = json.loads(rep.report_json)
    except json.JSONDecodeError:
        return jsonify({"error": "Stored gap report is invalid"}), 500

    rows = data.get("rows") or []
    gaps = [r.get("requirement") for r in rows if isinstance(r, dict) and r.get("match") == "gap"]
    summary = data.get("summary") or ""

    use_llm = llm_service._client() is not None  # noqa: SLF001
    milestones_raw: list = []
    intro = ""
    try:
        if use_llm:
            payload = llm_service.build_roadmap(summary, gaps)
            milestones_raw = list(payload.get("milestones") or [])
            intro = (payload.get("intro") or "")[:4000]
        else:
            milestones_raw = [
                {
                    "id": str(uuid.uuid4()),
                    "title": f"Learn: {g}"[:200],
                    "description": "Add coursework or a small project to demonstrate this skill.",
                    "resource_url": "",
                    "weeks_estimate": 2,
                }
                for g in (gaps[:12] or ["Foundational skills for your target role"])
            ]
            intro = "Heuristic roadmap (AI unavailable)."
    except Exception as exc:  # noqa: BLE001
        milestones_raw = []
        intro = f"Fallback roadmap due to error: {str(exc)[:200]}"

    milestones = _normalize_milestones(milestones_raw)

    rm = Roadmap.query.filter_by(user_id=g.current_user.id).first()
    if not rm:
        rm = Roadmap(user_id=g.current_user.id, milestones_json="{}")
        db.session.add(rm)
    rm.milestones_json = _save_roadmap_payload(intro, milestones)
    db.session.commit()
    return jsonify({"roadmap": {"intro": intro, "milestones": milestones}}), 201


@bp.patch("/milestones/<string:milestone_id>")
@login_required
def patch_milestone(milestone_id: str):
    rm = Roadmap.query.filter_by(user_id=g.current_user.id).first()
    if not rm:
        return jsonify({"error": "No roadmap yet"}), 404

    payload = _load_roadmap_payload(rm)
    milestones = payload["milestones"]

    data = request.get_json(silent=True) or {}
    completed = data.get("completed")
    if completed is None:
        return jsonify({"error": "Provide completed (boolean)"}), 400

    found = False
    for m in milestones:
        if isinstance(m, dict) and m.get("id") == milestone_id:
            m["completed"] = bool(completed)
            found = True
            break
    if not found:
        return jsonify({"error": "Milestone not found"}), 404

    rm.milestones_json = _save_roadmap_payload(payload["intro"], milestones)
    db.session.commit()
    return jsonify({"roadmap": {"intro": payload["intro"], "milestones": milestones}})
