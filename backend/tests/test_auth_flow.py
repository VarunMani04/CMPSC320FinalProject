def test_register_login_profile(client):
    r = client.post(
        "/api/auth/register",
        json={"email": "a@example.com", "password": "password1"},
    )
    assert r.status_code == 201

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
