from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

from career import api
from career.models import CandidateProfile, ResumePersonalDetails


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
