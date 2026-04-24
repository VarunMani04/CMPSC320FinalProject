from tests.conftest import register_and_verify_otp


def test_register_login_profile(client):
    register_and_verify_otp(client, "a@example.com", "password1")

    r = client.get("/api/auth/me")
    assert r.status_code == 200
    assert r.get_json()["user"]["email"] == "a@example.com"

    r = client.put(
        "/api/profile",
        json={
            "full_name": "Ada",
            "education": "BS CS",
            "experience": "Intern",
            "skills": [{"name": "Python", "proficiency": "intermediate"}],
        },
    )
    assert r.status_code == 200
    body = r.get_json()
    assert body["full_name"] == "Ada"
    assert len(body["skills"]) == 1


def test_login_requires_otp(client):
    register_and_verify_otp(client, "b@example.com", "password1")
    client.post("/api/auth/logout")

    r = client.post("/api/auth/login", json={"email": "b@example.com", "password": "password1"})
    assert r.status_code == 200
    assert r.get_json().get("otp_required") is True

    r = client.get("/api/auth/me")
    assert r.get_json()["user"] is None

    r2 = client.post(
        "/api/auth/login",
        json={"email": "b@example.com", "password": "password1"},
    )
    ch_id = r2.get_json()["challenge_id"]
    r3 = client.post("/api/auth/verify-email-otp", json={"challenge_id": ch_id, "code": "123456"})
    assert r3.status_code == 200
    r4 = client.get("/api/auth/me")
    assert r4.get_json()["user"]["email"] == "b@example.com"
