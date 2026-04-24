def test_gap_and_roadmap_without_llm(client):
    client.post(
        "/api/auth/register",
        json={"email": "gap@example.com", "password": "password1"},
    )
    client.put(
        "/api/profile",
        json={
            "full_name": "Test User",
            "education": "BS",
            "experience": "Projects",
            "skills": [{"name": "Python", "proficiency": "beginner"}],
        },
    )
    client.post(
        "/api/jobs/analyze",
        json={"postings": ["We need Python, Docker, and teamwork."]},
    )
    r = client.post("/api/gap-reports/generate")
    assert r.status_code == 201
    assert "report" in r.get_json()

    r2 = client.post("/api/roadmap/generate")
    assert r2.status_code == 201
    body = r2.get_json()
    assert "milestones" in body["roadmap"]

    r3 = client.get("/api/roadmap")
    assert r3.status_code == 200
    assert r3.get_json()["roadmap"]["milestones"]
