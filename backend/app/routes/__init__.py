from __future__ import annotations

from flask import Flask

from app.routes.auth import bp as auth_bp
from app.routes.gap import bp as gap_bp
from app.routes.health import bp as health_bp
from app.routes.jobs import bp as jobs_bp
from app.routes.profile import bp as profile_bp
from app.routes.roadmap import bp as roadmap_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(profile_bp, url_prefix="/api/profile")
    app.register_blueprint(jobs_bp, url_prefix="/api/jobs")
    app.register_blueprint(gap_bp, url_prefix="/api/gap-reports")
    app.register_blueprint(roadmap_bp, url_prefix="/api/roadmap")


__all__ = [
    "register_blueprints",
    "health_bp",
    "auth_bp",
    "profile_bp",
    "jobs_bp",
    "gap_bp",
    "roadmap_bp",
]
