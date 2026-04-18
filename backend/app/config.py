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
