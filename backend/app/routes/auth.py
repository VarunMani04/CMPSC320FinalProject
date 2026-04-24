from __future__ import annotations

from flask import Blueprint, jsonify, request, session
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import StudentProfile, User
from app.utils.auth import current_user

bp = Blueprint("auth", __name__)


def _valid_email(email: str) -> bool:
    """Practical check: single @, non-empty local and domain (allows user@localhost)."""
    if email != email.strip() or email.count("@") != 1:
        return False
    local, domain = email.split("@", 1)
    if not local or not domain:
        return False
    if any(c.isspace() for c in email):
        return False
    return True


@bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not email or not _valid_email(email):
        return jsonify({"error": "Valid email is required"}), 400
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "An account with this email already exists"}), 409

    user = User(email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()
    db.session.add(StudentProfile(user_id=user.id))
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "An account with this email already exists"}), 409
    session.clear()
    session["user_id"] = user.id
    return jsonify({"user": {"id": user.id, "email": user.email}}), 201


@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401
    session.clear()
    session["user_id"] = user.id
    return jsonify({"user": {"id": user.id, "email": user.email}})


@bp.post("/logout")
def logout():
    session.clear()
    return jsonify({"ok": True})


@bp.get("/me")
def me():
    user = current_user()
    if not user:
        return jsonify({"user": None}), 200
    return jsonify({"user": {"id": user.id, "email": user.email}})
