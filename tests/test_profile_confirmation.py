from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from career import profile_store
from career.models import CandidateProfile, ResumePersonalDetails
from career.profile_api import router
from career.resume_storage import ResumeRepository


def test_confirmed_profile_restores_and_preserves_original(monkeypatch, tmp_path):
    monkeypatch.setattr("career.resume_storage.RESUMES_DIR", tmp_path)
    monkeypatch.setattr(profile_store, "RESUMES_DIR", tmp_path)
    profile_id = str(uuid4())
    original = CandidateProfile(id=profile_id, original_resume_path="original.pdf", personal=ResumePersonalDetails(name="Original"))
    original_path = ResumeRepository().save_original(original)
    before = original_path.read_bytes()
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    response = client.post(f"/profile/{profile_id}/confirm", json={"personal": {"name": "Nome corrigido"}, "professional_summary": "Resumo confirmado"})
    assert response.status_code == 200
    assert "original_resume_path" not in response.json()
    assert client.get("/profile/current").json()["personal"]["name"] == "Nome corrigido"
    assert ResumeRepository().load_original(profile_id).professional_summary == "Resumo confirmado"
    assert original_path.read_bytes() == before


def test_confirm_rejects_unknown_or_invalid_profile(monkeypatch, tmp_path):
    monkeypatch.setattr("career.resume_storage.RESUMES_DIR", tmp_path)
    monkeypatch.setattr(profile_store, "RESUMES_DIR", tmp_path)
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    assert client.get("/profile/current").status_code == 404
    assert client.post("/profile/../../bad/confirm", json={"personal": {"name": "Teste"}}).status_code == 404
    assert client.post(f"/profile/{uuid4()}/confirm", json={"personal": {"name": "Teste"}}).status_code == 404
