import pytest

from app import create_app
from app.extensions import db


@pytest.fixture()
def app():
    application = create_app(testing=True)
    with application.app_context():
        db.create_all()
    yield application
    with application.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def register_and_verify_otp(client, email: str, password: str) -> None:
    """Complete register + mandatory email OTP (test bypass code 123456)."""
    r = client.post("/api/auth/register", json={"email": email, "password": password})
    assert r.status_code == 201, r.get_data(as_text=True)
    body = r.get_json()
    assert body.get("otp_required") is True
    r2 = client.post(
        "/api/auth/verify-email-otp",
        json={"challenge_id": body["challenge_id"], "code": "123456"},
    )
    assert r2.status_code == 200, r2.get_data(as_text=True)
