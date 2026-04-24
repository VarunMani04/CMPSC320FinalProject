import os
from pathlib import Path


def _default_sqlite_uri() -> str:
    instance = Path(__file__).resolve().parent.parent / "instance"
    instance.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{instance / 'app.db'}"


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", _default_sqlite_uri())
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "").lower() in ("1", "true", "yes")

    # Mandatory email OTP (2FA). SMTP required unless EMAIL_OTP_LOG_ONLY=1 (dev).
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", "587"))
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "")
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() in ("1", "true", "yes")
    MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL", "").lower() in ("1", "true", "yes")
    EMAIL_OTP_TTL_MINUTES = int(os.environ.get("EMAIL_OTP_TTL_MINUTES", "10"))
    EMAIL_OTP_MAX_ATTEMPTS = int(os.environ.get("EMAIL_OTP_MAX_ATTEMPTS", "5"))
    EMAIL_OTP_LOG_ONLY = os.environ.get("EMAIL_OTP_LOG_ONLY", "").lower() in ("1", "true", "yes")
    # Dev / automated tests only — never set in production.
    EMAIL_OTP_BYPASS_CODE = os.environ.get("EMAIL_OTP_BYPASS_CODE", "").strip()
