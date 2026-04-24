from __future__ import annotations

import re
from datetime import datetime

from flask import Blueprint, current_app, jsonify, request, session

from app.extensions import db
from app.models import EmailOtpChallenge, StudentProfile, User
from app.utils.auth import current_user
from app.utils.otp_email import (
    create_email_otp_challenge,
    send_otp_email,
    verify_email_otp_challenge,
)

bp = Blueprint("auth", __name__)

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _otp_meta() -> dict:
    app = current_app
    return {
        "expires_in_seconds": int(app.config.get("EMAIL_OTP_TTL_MINUTES") or 10) * 60,
    }


@bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not email or not _EMAIL_RE.match(email):
        return jsonify({"error": "Valid email is required"}), 400
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "An account with this email already exists"}), 409

    session.clear()
    user = User(email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()
    db.session.add(StudentProfile(user_id=user.id))
    try:
        ch, plain = create_email_otp_challenge(current_app, user.id, "register")
        send_otp_email(current_app, email, plain)
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        current_app.logger.exception("register OTP failed")
        return jsonify({"error": f"Could not complete registration: {exc!s}"}), 503

    return (
        jsonify(
            {
                "otp_required": True,
                "challenge_id": ch.id,
                "email": email,
                **_otp_meta(),
            }
        ),
        201,
    )


@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    session.clear()
    try:
        ch, plain = create_email_otp_challenge(current_app, user.id, "login")
        send_otp_email(current_app, email, plain)
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        current_app.logger.exception("login OTP failed")
        return jsonify({"error": f"Could not send verification email: {exc!s}"}), 503

    return jsonify(
        {
            "otp_required": True,
            "challenge_id": ch.id,
            "email": email,
            **_otp_meta(),
        }
    )


@bp.post("/verify-email-otp")
def verify_email_otp():
    data = request.get_json(silent=True) or {}
    challenge_id = (data.get("challenge_id") or "").strip()
    code = (data.get("code") or "").strip()
    if not challenge_id or not code:
        return jsonify({"error": "challenge_id and code are required"}), 400

    user = verify_email_otp_challenge(current_app, challenge_id, code)
    if not user:
        return jsonify({"error": "Invalid or expired code"}), 401

    session.clear()
    session["user_id"] = user.id
    return jsonify({"user": {"id": user.id, "email": user.email}})


@bp.post("/resend-email-otp")
def resend_email_otp():
    data = request.get_json(silent=True) or {}
    challenge_id = (data.get("challenge_id") or "").strip()
    if not challenge_id:
        return jsonify({"error": "challenge_id is required"}), 400

    old = db.session.get(EmailOtpChallenge, challenge_id)
    if not old:
        return jsonify({"error": "Unknown or expired challenge"}), 404
    if old.expires_at < datetime.utcnow():
        db.session.delete(old)
        db.session.commit()
        return jsonify({"error": "Challenge expired"}), 404

    user = db.session.get(User, old.user_id)
    if not user:
        db.session.delete(old)
        db.session.commit()
        return jsonify({"error": "User not found"}), 404

    purpose = old.purpose
    email = user.email
    session.clear()
    db.session.delete(old)
    db.session.flush()

    try:
        ch, plain = create_email_otp_challenge(current_app, user.id, purpose)
        send_otp_email(current_app, email, plain)
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        current_app.logger.exception("resend OTP failed")
        return jsonify({"error": f"Could not send email: {exc!s}"}), 503

    return jsonify({"challenge_id": ch.id, "email": email, **_otp_meta()})


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
