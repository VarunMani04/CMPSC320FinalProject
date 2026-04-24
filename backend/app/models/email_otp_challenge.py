from __future__ import annotations

from datetime import datetime

from app.extensions import db


class EmailOtpChallenge(db.Model):
    """Single-use email OTP for mandatory 2FA on login and register."""

    __tablename__ = "email_otp_challenges"

    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    purpose = db.Column(db.String(20), nullable=False)  # "login" | "register"
    code_hash = db.Column(db.String(255), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    attempts = db.Column(db.Integer, default=0, nullable=False)

    user = db.relationship("User", backref=db.backref("otp_challenges", lazy="dynamic"))
