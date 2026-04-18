def test_jobs_analyze_heuristic_without_openai(client):
    client.post(
        "/api/auth/register",
        json={"email": "jobs@example.com", "password": "password1"},
    )
    r = client.post(
        "/api/jobs/analyze",
        json={"postings": ["Python and SQL required for backend engineering role."]},
    )
    assert r.status_code == 201
    jobs = r.get_json()["jobs"]
    assert len(jobs) == 1
    assert jobs[0]["parsed"] is not None
    assert "required_skills" in jobs[0]["parsed"]
