from __future__ import annotations

import logging
import secrets
import smtplib
from datetime import datetime, timedelta
from email.message import EmailMessage
from typing import TYPE_CHECKING

from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models import EmailOtpChallenge, User

if TYPE_CHECKING:
    from flask import Flask

logger = logging.getLogger(__name__)


def _otp_plain_code(app: Flask) -> str:
    bypass = (app.config.get("EMAIL_OTP_BYPASS_CODE") or "").strip()
    if bypass:
        return bypass
    return f"{secrets.randbelow(1_000_000):06d}"


def _ttl(app: Flask) -> timedelta:
    minutes = int(app.config.get("EMAIL_OTP_TTL_MINUTES") or 10)
    return timedelta(minutes=max(3, min(minutes, 60)))


def invalidate_open_challenges(user_id: int, purpose: str) -> None:
    EmailOtpChallenge.query.filter_by(user_id=user_id, purpose=purpose).delete(synchronize_session=False)
    db.session.flush()


def create_email_otp_challenge(app: Flask, user_id: int, purpose: str) -> tuple[EmailOtpChallenge, str]:
    """Create a new challenge row and return (challenge, plaintext_code) for sending only."""
    if purpose not in ("login", "register"):
        raise ValueError("purpose must be login or register")
    invalidate_open_challenges(user_id, purpose)
    plain = _otp_plain_code(app)
    ch = EmailOtpChallenge(
        id=secrets.token_urlsafe(24)[:36],
        user_id=user_id,
        purpose=purpose,
        code_hash=generate_password_hash(plain),
        expires_at=datetime.utcnow() + _ttl(app),
        attempts=0,
    )
    db.session.add(ch)
    db.session.flush()
    return ch, plain


def send_otp_email(app: Flask, to_addr: str, code: str) -> None:
    if app.config.get("EMAIL_OTP_LOG_ONLY"):
        logger.warning("EMAIL_OTP (log only) to=%s code=%s", to_addr, code)
        return

    host = (app.config.get("MAIL_SERVER") or "").strip()
    if not host:
        raise RuntimeError("MAIL_SERVER is not configured")

    port = int(app.config.get("MAIL_PORT") or 587)
    user = (app.config.get("MAIL_USERNAME") or "").strip()
    password = (app.config.get("MAIL_PASSWORD") or "")
    sender = (app.config.get("MAIL_DEFAULT_SENDER") or user).strip()
    use_ssl = bool(app.config.get("MAIL_USE_SSL"))
    use_tls = bool(app.config.get("MAIL_USE_TLS", True))

    minutes = int(app.config.get("EMAIL_OTP_TTL_MINUTES") or 10)
    body = (
        f"Your PostingPal verification code is: {code}\n\n"
        f"It expires in about {minutes} minutes.\n"
        "If you did not request this, you can ignore this email.\n"
    )

    msg = EmailMessage()
    msg["Subject"] = "Your PostingPal verification code"
    msg["From"] = sender
    msg["To"] = to_addr
    msg.set_content(body)

    if use_ssl:
        with smtplib.SMTP_SSL(host, port, timeout=30) as smtp:
            if user:
                smtp.login(user, password)
            smtp.send_message(msg)
    else:
        with smtplib.SMTP(host, port, timeout=30) as smtp:
            if use_tls:
                smtp.starttls()
            if user:
                smtp.login(user, password)
            smtp.send_message(msg)


def verify_email_otp_challenge(app: Flask, challenge_id: str, code: str) -> User | None:
    """Validate code, consume challenge, return user or None."""
    ch = db.session.get(EmailOtpChallenge, challenge_id)
    if not ch:
        return None
    if ch.expires_at < datetime.utcnow():
        db.session.delete(ch)
        db.session.commit()
        return None

    max_attempts = int(app.config.get("EMAIL_OTP_MAX_ATTEMPTS") or 5)
    if ch.attempts >= max_attempts:
        db.session.delete(ch)
        db.session.commit()
        return None

    ch.attempts += 1
    db.session.add(ch)
    db.session.flush()

    bypass = (app.config.get("EMAIL_OTP_BYPASS_CODE") or "").strip()
    c = code.strip()
    ok = False
    if bypass and len(c) == len(bypass) and secrets.compare_digest(c, bypass):
        ok = True
    elif check_password_hash(ch.code_hash, c):
        ok = True

    if not ok:
        db.session.commit()
        return None

    user = db.session.get(User, ch.user_id)
    db.session.delete(ch)
    db.session.commit()
    return user
