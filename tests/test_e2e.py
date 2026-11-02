from io import BytesIO
import shutil

import httpx
from fastapi.testclient import TestClient
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

from career import api, profile_store, tracker
from career.models import FetchResult, RawJob, SourceReport, SourceStatus
from career.sources.base import BaseSource


def _synthetic_pdf(content: bytes = b'BT /F1 14 Tf 72 720 Td (Pessoa Teste Backend Junior Node.js TypeScript) Tj ET') -> bytes:
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    font = writer._add_object(DictionaryObject({NameObject('/Type'): NameObject('/Font'), NameObject('/Subtype'): NameObject('/Type1'), NameObject('/BaseFont'): NameObject('/Helvetica')}))
    page[NameObject('/Resources')] = DictionaryObject({NameObject('/Font'): DictionaryObject({NameObject('/F1'): font})})
    stream = DecodedStreamObject()
    stream.set_data(content)
    page[NameObject('/Contents')] = writer._add_object(stream)
    output = BytesIO()
    writer.write(output)
    return output.getvalue()


def test_upload_extracts_labeled_portfolio_from_real_pdf(monkeypatch, tmp_path):
    monkeypatch.setattr(api, "RESUMES_DIR", tmp_path / "resumes")
    monkeypatch.setattr("career.resume_storage.RESUMES_DIR", tmp_path / "resumes")
    pdf = _synthetic_pdf(
        b'BT /F1 14 Tf 72 720 Td (Pessoa Teste) Tj 0 -20 Td '
        b'(Portfolio: https://example.com/pessoa) Tj ET'
    )

    with TestClient(api.app) as client:
        response = client.post('/profiles/upload', files={'file': ('resume.pdf', pdf, 'application/pdf')})

    assert response.status_code == 200
    assert response.json()['profile']['personal']['portfolio'] == 'https://example.com/pessoa'


def test_real_text_pdf_sections_can_be_confirmed_and_restored(monkeypatch, tmp_path):
    monkeypatch.setattr(api, "RESUMES_DIR", tmp_path / "resumes")
    monkeypatch.setattr("career.resume_storage.RESUMES_DIR", tmp_path / "resumes")
    monkeypatch.setattr(profile_store, "RESUMES_DIR", tmp_path / "resumes")
    lines = [
        b'Pessoa Teste', b'Resumo', b'Desenvolvedora backend.', b'Experiencia',
        b'Desenvolvedora | Empresa Teste | 2021-2024', b'- Criou APIs.',
        b'Projetos', b'Projeto Exemplo | Aplicacao web', b'- Criou testes.',
        b'Formacao', b'Computacao | Universidade Teste | 2017-2021',
    ]
    content = b'BT /F1 14 Tf 72 720 Td ' + b' 0 -20 Td '.join(b'(' + line + b') Tj' for line in lines) + b' ET'
    pdf = _synthetic_pdf(content)

    with TestClient(api.app) as client:
        response = client.post('/profiles/upload', files={'file': ('resume.pdf', pdf, 'application/pdf')})
        assert response.status_code == 200
        profile = response.json()['profile']
        assert profile['professional_summary'] == 'Desenvolvedora backend.'
        assert profile['experiences'][0]['company'] == 'Empresa Teste'
        assert profile['experiences'][0]['bullets'] == ['Criou APIs.']
        assert profile['projects'][0]['name'] == 'Projeto Exemplo'
        assert profile['education'][0]['institution'] == 'Universidade Teste'
        profile['personal']['name'] = 'Pessoa Confirmada'
        assert client.post(f"/profile/{profile['id']}/confirm", json=profile).status_code == 200
        assert client.get('/profile/current').json()['personal']['name'] == 'Pessoa Confirmada'
        assert (tmp_path / 'resumes' / 'original' / f"{profile['id']}.pdf").read_bytes() == pdf


def test_password_protected_pdf_is_rejected_without_leaving_a_file(monkeypatch, tmp_path):
    monkeypatch.setattr(api, "RESUMES_DIR", tmp_path / "resumes")
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    writer.encrypt("synthetic-test-password")
    output = BytesIO()
    writer.write(output)

    with TestClient(api.app) as client:
        response = client.post('/profiles/upload', files={'file': ('protected.pdf', output.getvalue(), 'application/pdf')})

    assert response.status_code == 422
    assert not list((tmp_path / "resumes" / "original").glob("*.pdf"))


class FixtureSource(BaseSource):
    name = "Fixture"

    async def fetch(self, client: httpx.AsyncClient) -> FetchResult:
        job = RawJob(source=self.name, title="Backend Developer Junior", company="Empresa fictícia", url="https://example.com/job", description="Backend TypeScript Node.js remoto", workplace_type="remote", location="Brazil")
        return FetchResult(report=SourceReport(source=self.name, status=SourceStatus.OK, count=1), jobs=[job, job])


def test_search_integrates_filters_deduplication_and_source_failure(monkeypatch, tmp_path):
    class SearchSource(BaseSource):
        name = "Synthetic"

        async def fetch(self, client):
            common = dict(source=self.name, company="Empresa fictícia", description="Backend TypeScript Node.js", workplace_type="remote")
            valid = RawJob(**common, title="Junior Backend Developer", url="https://example.com/valid", location="Brazil")
            unknown = RawJob(**common, title="Junior Backend Developer", url="https://example.com/unknown", location="Remote")
            senior = RawJob(**common, title="Senior Backend Developer", url="https://example.com/senior", location="Brazil")
            hybrid = RawJob(**(common | {"workplace_type": "hybrid"}), title="Junior Backend Developer", url="https://example.com/hybrid", location="Rio de Janeiro, Brazil")
            return FetchResult(report=SourceReport(source=self.name, status=SourceStatus.OK, count=5), jobs=[valid, valid, unknown, senior, hybrid])

    class FailingSource(BaseSource):
        name = "Unavailable"

        async def fetch(self, client):
            raise RuntimeError("synthetic failure")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(api, "RESUMES_DIR", tmp_path / "resumes")
    monkeypatch.setattr("career.resume_storage.RESUMES_DIR", tmp_path / "resumes")
    monkeypatch.setattr(api, "default_sources", lambda: [SearchSource(), FailingSource()])
    with TestClient(api.app) as client:
        uploaded = client.post('/profiles/upload', files={'file': ('resume.pdf', _synthetic_pdf(), 'application/pdf')})
        assert uploaded.status_code == 200
        profile_id = uploaded.json()['profile']['id']
        response = client.post('/jobs/search', json={'profile_id': profile_id, 'regions': ['brazil', 'global'], 'work_modes': ['remote']})

    assert response.status_code == 200
    result = response.json()
    assert [job['url'] for job in result['jobs']] == ['https://example.com/valid']
    assert result['jobs'][0]['score'] > 0
    assert [(item['job']['url'], item['reason']) for item in result['needs_review']] == [('https://example.com/unknown', 'REGION_UNKNOWN')]
    assert result['stats']['collected'] == 5
    assert result['stats']['unique'] == 4
    assert [report['status'] for report in result['reports']] == ['OK', 'ERROR']


def test_resume_search_application_and_tailoring_flow(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(api, "RESUMES_DIR", tmp_path / "resumes")
    monkeypatch.setattr("career.resume_storage.RESUMES_DIR", tmp_path / "resumes")
    monkeypatch.setattr(profile_store, "RESUMES_DIR", tmp_path / "resumes")
    monkeypatch.setattr(tracker, "TRACKER_DIR", tmp_path / "tracker")
    monkeypatch.setattr(api, "default_sources", lambda: [FixtureSource()])
    with TestClient(api.app) as client:
        assert client.post('/profiles/upload', files={'file': ('bad.pdf', b'bad', 'application/pdf')}).status_code == 415
        uploaded = client.post('/profiles/upload', files={'file': ('resume.pdf', _synthetic_pdf(), 'application/pdf')})
        assert uploaded.status_code == 200
        profile = uploaded.json()['profile']
        profile['personal']['name'] = 'Pessoa Confirmada'
        assert client.post(f"/profile/{profile['id']}/confirm", json=profile).status_code == 200
        search = client.post('/jobs/search', json={'profile_id': profile['id'], 'regions': ['brazil'], 'work_modes': ['remote']})
        assert search.status_code == 200
        jobs = search.json()['jobs']
        assert len(jobs) == 1 and jobs[0]['score'] > 0
        entries = client.get(f"/tracker/{profile['id']}").json()['jobs']
        assert len(entries) == 1
        update = {'status': 'applied', 'notes': 'Aplicação manual fictícia', 'favorite': True}
        assert client.post(f"/tracker/{profile['id']}/jobs/{entries[0]['id']}", json=update).status_code == 200
        generated = client.post('/resumes/tailor', json={'profile_id': profile['id'], 'job': jobs[0]})
        assert generated.status_code == 200
        resume_id = generated.json()['id']
        tex = client.get(f'/resumes/{resume_id}/download/tex')
        assert tex.status_code == 200 and 'Pessoa Confirmada' in tex.text
        if shutil.which('pdflatex'):
            assert generated.json()['pdf_available']
        if generated.json()['pdf_available']:
            assert client.get(f'/resumes/{resume_id}/download/pdf').content.startswith(b'%PDF-')
    with TestClient(api.app) as restarted:
        assert restarted.get('/profile/current').json()['personal']['name'] == 'Pessoa Confirmada'
        stored = restarted.get(f"/tracker/{profile['id']}").json()
        assert stored['jobs'][0]['status'] == 'applied' and stored['jobs'][0]['favorite']
        assert stored['jobs'][0]['notes'] == 'Aplicação manual fictícia'
