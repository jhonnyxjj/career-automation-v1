from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

from career import api
from career.models import CandidateProfile, ResumePersonalDetails, TechnicalSkillGroup


def test_health() -> None:
    assert TestClient(api.app).get("/health").json() == {"ok": True}


def test_upload_stores_profile_without_exposing_local_path(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("career.api.RESUMES_DIR", tmp_path)
    monkeypatch.setattr("career.resume_storage.RESUMES_DIR", tmp_path)

    def parse(_: bytes, profile_id: str, path: Path) -> CandidateProfile:
        return CandidateProfile(id=profile_id, original_resume_path=str(path), personal=ResumePersonalDetails(name="Pessoa"))

    monkeypatch.setattr(api, "parse_candidate_profile", parse)
    response = TestClient(api.app).post("/profiles/upload", files={"file": ("resume.pdf", b"%PDF-1.7", "application/pdf")})

    assert response.status_code == 200
    assert response.json()["profile"]["personal"]["name"] == "Pessoa"
    assert "original_resume_path" not in response.json()["profile"]
    assert list(tmp_path.joinpath("original").glob("*.pdf"))


def test_imported_recruiter_post_is_normalized_and_scored(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr("career.tracker.TRACKER_DIR", tmp_path)
    profile_id = str(uuid4())
    profile = CandidateProfile(
        id=profile_id,
        personal=ResumePersonalDetails(name="Pessoa"),
        technical_skills=[TechnicalSkillGroup(category="Frontend", items=["React", "PostgreSQL"])],
    )

    class Repository:
        def load_original(self, _: str) -> CandidateProfile:
            return profile

    monkeypatch.setattr(api, "ResumeRepository", lambda: Repository())
    response = TestClient(api.app).post("/jobs/import", json={
        "profile_id": profile_id,
        "source": "LinkedIn",
        "listing_type": "recruiter_post",
        "title": "Backend Developer Júnior",
        "company": "Acme",
        "description": "React e PostgreSQL para uma aplicação remota.",
        "source_url": "https://www.linkedin.com/posts/example",
        "apply_url": "https://careers.example.com/jobs/1",
    })

    assert response.status_code == 200
    assert response.json()["listing_type"] == "recruiter_post"
    assert response.json()["apply_url"] == "https://careers.example.com/jobs/1"
    assert response.json()["technologies"] == ["React", "PostgreSQL"]


def test_import_rejects_non_http_source_url() -> None:
    response = TestClient(api.app).post("/jobs/import", json={
        "profile_id": str(uuid4()),
        "source": "LinkedIn",
        "title": "Backend Developer",
        "company": "Acme",
        "description": "React e PostgreSQL.",
        "source_url": "javascript:alert(1)",
    })

    assert response.status_code == 422
