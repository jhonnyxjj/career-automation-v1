import json
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from career import profile_store, tracker
from career.models import CandidateProfile, JobListing, ResumePersonalDetails, ReviewJob, SearchResult, SearchStats, SourceReport, SourceStatus
from career.profile_store import save_confirmed
from career.resume_storage import ResumeRepository
from career.tracker_api import router


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setattr("career.resume_storage.RESUMES_DIR", tmp_path / "resumes")
    monkeypatch.setattr(profile_store, "RESUMES_DIR", tmp_path / "resumes")
    monkeypatch.setattr(tracker, "TRACKER_DIR", tmp_path / "tracker")
    profile_id = str(uuid4())
    profile = CandidateProfile(id=profile_id, personal=ResumePersonalDetails(name="Pessoa fictícia"))
    ResumeRepository().save_original(profile)
    save_confirmed(profile_id, profile)
    app = FastAPI()
    app.include_router(router)
    return TestClient(app), profile_id


def test_application_is_deduplicated_and_restored(client):
    api, profile_id = client
    job = {"source": "LinkedIn", "title": "Backend", "company": "Empresa", "url": "https://example.com/job", "score": 70}
    first = api.post(f"/tracker/{profile_id}/jobs", json=job).json()
    duplicate = api.post(f"/tracker/{profile_id}/jobs", json=job).json()
    assert first["id"] == duplicate["id"]
    update = {"status": "applied", "notes": "Enviada manualmente", "favorite": True}
    assert api.post(f"/tracker/{profile_id}/jobs/{first['id']}", json=update).status_code == 200
    assert api.post(f"/tracker/{profile_id}/jobs/{first['id']}", json=update).status_code == 200
    saved = api.get(f"/tracker/{profile_id}").json()["jobs"]
    assert len(saved) == 1
    assert saved[0]["favorite"] and saved[0]["notes"] == update["notes"]
    assert saved[0]["status"] == "applied" and len(saved[0]["history"]) == 1
    assert saved[0]["job"]["score"] == 70


def test_search_is_persisted_without_erasing_application_details(client):
    api, profile_id = client
    job = JobListing(source="Lever", title="Backend", company="Empresa", url="https://example.com/job", score=80)
    entry = tracker.save_job(profile_id, job)
    tracker.update_job(profile_id, entry["id"], status="interview", notes="Nota", favorite=True)
    result = SearchResult(jobs=[job], reports=[SourceReport(source="Lever", status=SourceStatus.OK)], stats=SearchStats())
    tracker.save_search(profile_id, {"regions": ["brazil"]}, result)
    restored = api.get(f"/tracker/{profile_id}").json()
    assert len(restored["searches"]) == 1
    assert restored["searches"][0]["job_ids"] == [entry["id"]]
    assert restored["jobs"][0]["status"] == "interview" and restored["jobs"][0]["notes"] == "Nota"


def test_unknown_eligibility_remains_explicit_in_tracker(client):
    _, profile_id = client
    job = JobListing(source="Teste", title="Backend", company="Empresa", url="https://example.com/unknown")
    result = SearchResult(jobs=[], reports=[], stats=SearchStats(), needs_review=[ReviewJob(job=job, reason="REGION_UNKNOWN")])
    tracker.save_search(profile_id, {}, result)
    stored = tracker.load_tracker(profile_id)["jobs"][0]["job"]
    assert stored["filter_accepted"] is False and stored["filter_reason"] == "REGION_UNKNOWN"


def test_corrupted_tracker_is_not_overwritten(client):
    _, profile_id = client
    tracker.TRACKER_DIR.mkdir(parents=True, exist_ok=True)
    path = tracker.TRACKER_DIR / f"{profile_id}.json"
    path.write_text("{bad json", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        tracker.save_job(profile_id, JobListing(source="Teste", title="Dev", company="Empresa", url="https://example.com"))
    assert path.read_text(encoding="utf-8") == "{bad json"


def test_invalid_stored_job_returns_safe_error_without_overwriting_data(client, caplog):
    from career.api import app

    _, profile_id = client
    tracker.save_job(profile_id, JobListing(source="Teste", title="Backend", company="Empresa", url="https://example.com/job"))
    path = tracker.TRACKER_DIR / f"{profile_id}.json"
    state = json.loads(path.read_text(encoding="utf-8"))
    state['jobs'][0]['job']['url'] = 'synthetic_private_error_marker'
    path.write_text(json.dumps(state), encoding='utf-8')
    before = path.read_bytes()

    with TestClient(app, raise_server_exceptions=False) as api:
        response = api.post('/jobs/import', json={
            'profile_id': profile_id, 'source': 'LinkedIn', 'title': 'Backend Junior',
            'company': 'Outra empresa', 'description': 'Backend remoto',
            'source_url': 'https://example.com/new', 'location': 'Brasil',
        })

    assert response.status_code == 500
    assert response.json()['detail'] == 'Dados de acompanhamento inválidos.'
    assert 'synthetic_private_error_marker' not in caplog.text
    assert path.read_bytes() == before


def test_search_endpoint_records_filters_and_result(client, monkeypatch):
    from career import api as main_api
    _, profile_id = client
    job = JobListing(source="Lever", title="Backend", company="Empresa", url="https://example.com/job", score=75)
    async def fake_search(_profile, _sources, _limit):
        return SearchResult(jobs=[job], reports=[], stats=SearchStats())
    monkeypatch.setattr(main_api, "find_jobs", fake_search)
    monkeypatch.setattr(main_api, "default_sources", list)
    response = TestClient(main_api.app).post('/jobs/search', json={"profile_id": profile_id, "regions": ["brazil"]})
    assert response.status_code == 200
    stored = tracker.load_tracker(profile_id)
    assert stored["searches"][0]["filters"]["regions"] == ["brazil"]
    assert stored["jobs"][0]["job"]["score"] == 75


@pytest.mark.parametrize('source', ['LinkedIn', 'Indeed', 'Gupy', 'Vagas.com.br', 'ProgramaThor', 'InfoJobs'])
def test_manual_import_is_available_in_tracker(client, source):
    from career.api import app
    _, profile_id = client
    response = TestClient(app).post('/jobs/import', json={
        'profile_id': profile_id, 'source': source, 'title': 'Backend Developer Junior',
        'company': 'Empresa', 'description': 'Backend Node.js remoto',
        'source_url': 'https://example.com/indeed/1', 'location': 'Brazil',
    })
    assert response.status_code == 200
    stored = tracker.load_tracker(profile_id)
    assert len(stored['jobs']) == 1
    assert stored['jobs'][0]['job']['source'] == source
    assert stored['jobs'][0]['job']['filter_accepted'] is True


def test_manual_import_reports_hybrid_as_not_allowed(client):
    from career.api import app
    _, profile_id = client
    response = TestClient(app).post('/jobs/import', json={
        'profile_id': profile_id, 'source': 'Indeed', 'title': 'Backend Developer Junior',
        'company': 'Empresa', 'description': 'Backend híbrido Node.js',
        'source_url': 'https://example.com/hybrid', 'location': 'Brazil',
        'work_modes': ['remote'],
    })
    assert response.status_code == 200
    assert response.json()['filter_accepted'] is False
    assert response.json()['filter_reason'] == 'WORKPLACE_NOT_ALLOWED'
