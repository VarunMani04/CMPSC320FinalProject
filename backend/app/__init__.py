from flask import Flask
from flask_cors import CORS


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    from app.routes import health_bp

    app.register_blueprint(health_bp, url_prefix="/api")

    return app
