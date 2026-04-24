from __future__ import annotations

from flask import Blueprint, g, jsonify, request

from app.extensions import db
from app.models import Skill, StudentProfile
from app.services import llm as llm_service
from app.utils.auth import login_required
from app.utils.resume_pdf import extract_text_from_pdf_bytes

bp = Blueprint("profile", __name__)

_MAX_RESUME_PDF_BYTES = 4 * 1024 * 1024


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


@bp.post("/parse-resume")
@login_required
def parse_resume():
    """Extract text from an uploaded PDF résumé and return suggested profile fields (not saved until PUT)."""
    f = request.files.get("file")
    if not f or not f.filename:
        return jsonify({"error": 'PDF file is required (form field name: "file")'}), 400
    if not f.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported"}), 400
    data = f.read()
    if not data:
        return jsonify({"error": "Empty file"}), 400
    if len(data) > _MAX_RESUME_PDF_BYTES:
        return jsonify({"error": "PDF too large (max 4MB)"}), 413
    try:
        text = extract_text_from_pdf_bytes(data)
    except Exception as exc:
        return jsonify({"error": f"Could not read PDF: {exc!s}"}), 400
    if not text.strip():
        return jsonify({"error": "No readable text found in this PDF"}), 400
    parsed = llm_service.parse_resume_from_text(text)
    return jsonify(parsed)


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
