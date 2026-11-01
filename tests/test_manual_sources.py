from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from career.api import app
from career.models import CandidateProfile, ResumePersonalDetails, TechnicalSkillGroup
from career.resume_storage import ResumeRepository


@pytest.mark.parametrize('source', ['LinkedIn', 'Indeed', 'Gupy', 'Vagas.com.br', 'ProgramaThor', 'InfoJobs'])
def test_manual_import_uses_common_pipeline_and_deduplicates(source, monkeypatch, tmp_path):
    monkeypatch.setattr('career.resume_storage.RESUMES_DIR', tmp_path / 'resumes')
    monkeypatch.setattr('career.tracker.TRACKER_DIR', tmp_path / 'tracker')
    profile_id = str(uuid4())
    ResumeRepository().save_original(CandidateProfile(
        id=profile_id, personal=ResumePersonalDetails(name='Pessoa Teste'),
        technical_skills=[TechnicalSkillGroup(category='Linguagens', items=['TypeScript'])],
    ))
    payload = {
        'profile_id': profile_id, 'source': source, 'title': 'Backend Developer Junior',
        'company': 'Empresa fictícia', 'description': 'Backend remoto com TypeScript no Brasil',
        'source_url': 'https://example.com/vacancy?utm_source=test', 'location': 'Brasil',
    }
    with TestClient(app) as client:
        first = client.post('/jobs/import', json=payload)
        second = client.post('/jobs/import', json=payload)
    assert first.status_code == second.status_code == 200
    assert first.json()['source'] == source
    assert first.json()['url'] == 'https://example.com/vacancy'
    assert first.json()['filter_accepted'] is True
    assert first.json()['score'] > 0
    from career.tracker import load_tracker
    assert len(load_tracker(profile_id)['jobs']) == 1
