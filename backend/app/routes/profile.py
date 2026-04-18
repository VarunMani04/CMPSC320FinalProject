from __future__ import annotations

from flask import Blueprint, g, jsonify, request

from app.extensions import db
from app.models import Skill, StudentProfile
from app.utils.auth import login_required

bp = Blueprint("profile", __name__)


def _profile_dict(p: StudentProfile) -> dict:
    return {
        "full_name": p.full_name,
        "education": p.education,
        "experience": p.experience,
        "skills": [
            {"id": s.id, "name": s.name, "proficiency": s.proficiency}
            for s in p.skills
        ],
        "completeness": {
            "has_name": bool(p.full_name.strip()),
            "has_education": bool(p.education.strip()),
            "has_experience": bool(p.experience.strip()),
            "skill_count": len(p.skills),
        },
    }


@bp.get("")
@login_required
def get_profile():
    p = g.current_user.profile
    if not p:
        return jsonify({"error": "Profile missing"}), 404
    return jsonify(_profile_dict(p))


@bp.put("")
@login_required
def put_profile():
    p = g.current_user.profile
    if not p:
        p = StudentProfile(user_id=g.current_user.id)
        db.session.add(p)
        db.session.flush()

    data = request.get_json(silent=True) or {}
    if "full_name" in data:
        p.full_name = (data.get("full_name") or "")[:200]
    if "education" in data:
        p.education = (data.get("education") or "")[:20000]
    if "experience" in data:
        p.experience = (data.get("experience") or "")[:20000]

    if "skills" in data:
        skills_in = data.get("skills") or []
        if not isinstance(skills_in, list):
            return jsonify({"error": "skills must be a list"}), 400
        Skill.query.filter_by(profile_id=p.id).delete()
        for item in skills_in:
            if not isinstance(item, dict):
                continue
            name = (item.get("name") or "").strip()[:120]
            prof = (item.get("proficiency") or "beginner").lower()
            if prof not in ("beginner", "intermediate", "advanced"):
                prof = "beginner"
            if name:
                db.session.add(Skill(profile_id=p.id, name=name, proficiency=prof))

    db.session.commit()
    db.session.refresh(p)
    return jsonify(_profile_dict(p))
