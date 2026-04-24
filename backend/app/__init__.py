from __future__ import annotations

import os

from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.extensions import db


def create_app(testing: bool = False) -> Flask:
    # Name must not be `app` — it shadows the `app` package and breaks `import app.models`.
    flask_app = Flask(__name__, instance_relative_config=True)
    if testing:
        flask_app.config.update(
            TESTING=True,
            SECRET_KEY="test-secret",
            SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            # Tests use a fixed OTP; no SMTP.
            EMAIL_OTP_BYPASS_CODE="123456",
            EMAIL_OTP_LOG_ONLY=True,
        )
    else:
        flask_app.config.from_object(Config)

    origins = [
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:4173",
        "http://localhost:4173",
    ]
    CORS(
        flask_app,
        resources={r"/api/*": {"origins": origins, "supports_credentials": True}},
        allow_headers=["Content-Type"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        expose_headers=["Content-Type"],
    )

    db.init_app(flask_app)

    import app.models  # noqa: F401 — register models

    with flask_app.app_context():
        if not testing:
            os.makedirs(flask_app.instance_path, exist_ok=True)
        db.create_all()

    from app.routes import register_blueprints

    register_blueprints(flask_app)

    return flask_app
