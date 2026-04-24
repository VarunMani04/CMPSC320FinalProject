import io
from unittest.mock import patch


def test_parse_resume_returns_profile_shape(client):
    client.post(
        "/api/auth/register",
        json={"email": "resume@example.com", "password": "password1"},
    )
    fake_text = (
        "Jane Doe\n"
        "jane@example.com\n"
        "Python developer with Java and AWS experience at Example Corp.\n"
        "BS Computer Science, State University\n"
    )
    with patch("app.routes.profile.extract_text_from_pdf_bytes", return_value=fake_text):
        r = client.post(
            "/api/profile/parse-resume",
            data={"file": (io.BytesIO(b"%PDF-dummy"), "resume.pdf")},
            content_type="multipart/form-data",
        )
    assert r.status_code == 200, r.get_data(as_text=True)
    body = r.get_json()
    assert "full_name" in body
    assert "education" in body
    assert "experience" in body
    assert "skills" in body
    assert isinstance(body["skills"], list)
    assert len(body["skills"]) >= 1
    assert body["skills"][0].get("name")
    assert body["skills"][0].get("proficiency") in ("beginner", "intermediate", "advanced")


def test_parse_resume_rejects_non_pdf(client):
    client.post(
        "/api/auth/register",
        json={"email": "resume2@example.com", "password": "password1"},
    )
    r = client.post(
        "/api/profile/parse-resume",
        data={"file": (io.BytesIO(b"hello"), "notes.txt")},
        content_type="multipart/form-data",
    )
    assert r.status_code == 400
