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


@pytest.mark.parametrize(('source', 'url', 'title', 'description'), [
    ('LinkedIn', 'https://www.linkedin.com/jobs/view/12345', 'Desenvolvedor Backend Junior', 'Vaga remota no Brasil. Backend com TypeScript.'),
    ('Indeed', 'https://br.indeed.com/viewjob?jk=fixture123', 'Backend Developer Jr', 'Home office no Brasil. TypeScript e APIs backend.'),
    ('Gupy', 'https://empresa.gupy.io/jobs/12345', 'Pessoa Desenvolvedora Backend Junior', 'Modelo remoto. Backend TypeScript.'),
    ('Vagas.com.br', 'https://www.vagas.com.br/vagas/v12345', 'Programador Backend Junior', 'Trabalho remoto no Brasil com TypeScript.'),
    ('ProgramaThor', 'https://programathor.com.br/jobs/12345', 'Backend Developer Junior', 'Remote no Brasil. APIs TypeScript.'),
    ('InfoJobs', 'https://www.infojobs.com.br/vaga-de-backend__12345.aspx', 'Desenvolvedor Backend Jr', 'Home office Brasil, TypeScript e backend.'),
])
def test_synthetic_platform_examples_use_the_same_import_pipeline(source, url, title, description, monkeypatch, tmp_path):
    monkeypatch.setattr('career.resume_storage.RESUMES_DIR', tmp_path / 'resumes')
    monkeypatch.setattr('career.tracker.TRACKER_DIR', tmp_path / 'tracker')
    profile_id = str(uuid4())
    ResumeRepository().save_original(CandidateProfile(
        id=profile_id, personal=ResumePersonalDetails(name='Pessoa Teste'),
        technical_skills=[TechnicalSkillGroup(category='Linguagens', items=['TypeScript'])],
    ))
    payload = {'profile_id': profile_id, 'source': source, 'title': title, 'company': 'Empresa fictícia',
               'description': description, 'source_url': url, 'location': 'Brasil'}
    with TestClient(app) as client:
        response = client.post('/jobs/import', json=payload)
    assert response.status_code == 200
    job = response.json()
    assert job['source'] == source and job['filter_accepted'] is True
    assert job['workplace_type'] == 'remote' and 'TypeScript' in job['technologies']
    assert job['score'] > 0


def test_same_manual_vacancy_from_two_platforms_keeps_one_application(monkeypatch, tmp_path):
    from career import profile_store

    monkeypatch.setattr('career.resume_storage.RESUMES_DIR', tmp_path / 'resumes')
    monkeypatch.setattr(profile_store, 'RESUMES_DIR', tmp_path / 'resumes')
    monkeypatch.setattr('career.tracker.TRACKER_DIR', tmp_path / 'tracker')
    profile_id = str(uuid4())
    profile = CandidateProfile(id=profile_id, personal=ResumePersonalDetails(name='Pessoa Teste'))
    ResumeRepository().save_original(profile)
    profile_store.save_confirmed(profile_id, profile)
    payload = {'profile_id': profile_id, 'source': 'LinkedIn', 'title': 'Backend Junior',
               'company': 'Empresa fictícia', 'description': 'Backend remoto no Brasil',
               'source_url': 'https://www.linkedin.com/jobs/view/12345', 'location': 'Brasil'}
    with TestClient(app) as client:
        assert client.post('/jobs/import', json=payload).status_code == 200
        entries = client.get(f'/tracker/{profile_id}').json()['jobs']
        entry_id = entries[0]['id']
        assert client.post(f'/tracker/{profile_id}/jobs/{entry_id}', json={
            'status': 'applied', 'notes': 'Nota fictícia', 'favorite': True,
        }).status_code == 200
        payload.update(source='Indeed', source_url='https://br.indeed.com/viewjob?jk=fixture123')
        assert client.post('/jobs/import', json=payload).status_code == 200
        saved = client.get(f'/tracker/{profile_id}').json()['jobs']

    assert len(saved) == 1 and saved[0]['id'] == entry_id
    assert saved[0]['status'] == 'applied' and saved[0]['notes'] == 'Nota fictícia' and saved[0]['favorite']
