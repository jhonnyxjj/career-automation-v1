import asyncio
import json
from datetime import UTC, datetime

import httpx

from career.models import SourceStatus
from career.sources.lever import LeverSource
from career.sources.primeiravagatech import PrimeiraVagaTechSource
from career.sources.remotinho import RemotinhoSource


def _configure_lever(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    data_dir = tmp_path / ".data"
    data_dir.mkdir()
    (data_dir / "settings.json").write_text(
        json.dumps({"lever_sites": [{"id": "acme", "company": "Acme"}]}), encoding="utf-8"
    )


def test_lever_normalizes_public_json_response(monkeypatch, tmp_path):
    _configure_lever(monkeypatch, tmp_path)

    def handler(request):
        return httpx.Response(200, json=[{
            "id": "1", "text": "Junior Backend Developer", "descriptionPlain": "Node.js PostgreSQL",
            "hostedUrl": "https://jobs.lever.co/acme/1", "applyUrl": "https://jobs.lever.co/acme/1/apply",
            "categories": {"location": "Brazil"}, "workplaceType": "remote", "createdAt": 1_700_000_000_000,
        }])

    async def fetch():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await LeverSource().fetch(client)

    result = asyncio.run(fetch())
    assert result.report.status == SourceStatus.OK
    assert result.jobs[0].company == "Acme"
    assert result.jobs[0].external_id == "1"


def test_lever_reports_unavailable_when_every_site_fails(monkeypatch, tmp_path):
    _configure_lever(monkeypatch, tmp_path)

    async def fetch():
        async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(404))) as client:
            return await LeverSource().fetch(client)

    assert asyncio.run(fetch()).report.status == SourceStatus.UNAVAILABLE


def test_primeira_vaga_tech_fetches_public_listing_details():
    def handler(request):
        if request.url.path.endswith("/paginated"):
            return httpx.Response(200, json={"content": [{
                "id": 1, "slug": "backend-junior", "title": "Backend Júnior", "companyName": "Acme",
                "city": "São Paulo", "state": "SP", "datePosted": "2026-09-26",
            }]})
        if request.url.path.endswith("/backend-junior"):
            return httpx.Response(200, json={
                "id": 1, "slug": "backend-junior", "title": "Backend Júnior", "companyName": "Acme",
                "description": "<h2>Vaga</h2> Python e FastAPI", "city": "São Paulo", "state": "SP",
                "datePosted": "2026-09-26", "originalUrl": "https://careers.example.com/jobs/1",
            })
        return httpx.Response(404)

    async def fetch():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await PrimeiraVagaTechSource().fetch(client)

    result = asyncio.run(fetch())
    assert result.report.status == SourceStatus.OK
    assert result.report.count == 1
    assert result.jobs[0].description == "Vaga Python e FastAPI"
    assert result.jobs[0].apply_url == "https://careers.example.com/jobs/1"
    assert result.jobs[0].url == "https://www.primeiravagatech.com.br/vaga/backend-junior"


def test_primeira_vaga_tech_preserves_publication_timezone():
    from career.sources.primeiravagatech import _date

    assert _date('2026-09-26T10:00:00-03:00') == datetime(2026, 9, 26, 13, tzinfo=UTC)
    assert _date('2026-09-26T10:00:00Z') == datetime(2026, 9, 26, 10, tzinfo=UTC)
    assert _date('2026-09-26') == datetime(2026, 9, 26, tzinfo=UTC)


def test_remotinho_extracts_public_listing_and_destination_url():
    html = """
    <h3 class="font-size-6 mb-3">Backend Engineer</h3>
    <p class="font-size-4 text-gray mb-4">Python, FastAPI e PostgreSQL.</p>
    <a href="/job/c291cmNlfEJhY2tlbmQgRW5naW5lZXJ8aHR0cHM6Ly9qb2JzLmV4YW1wbGUuY29tLzE">Ver vaga</a>
    """

    async def fetch():
        async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(200, text=html))) as client:
            return await RemotinhoSource().fetch(client)

    result = asyncio.run(fetch())
    assert result.report.status == SourceStatus.OK
    assert result.jobs[0].title == "Backend Engineer"
    assert result.jobs[0].description == "Python, FastAPI e PostgreSQL."
    assert result.jobs[0].apply_url == "https://jobs.example.com/1"


def test_remotinho_ignores_link_without_href():
    from career.sources.remotinho import _JobsParser

    parser = _JobsParser()
    parser.feed('<h3 class="font-size-6 mb-3">Backend Junior</h3><a>Sem link</a><a href="/job/fixture">Ver vaga</a>')
    assert len(parser.jobs) == 1
    assert parser.jobs[0]['path'] == '/job/fixture'


def test_greenhouse_update_timestamp_is_not_used_as_publication_date(monkeypatch):
    from career.config.sources import SourceTarget
    from career.sources.greenhouse import GreenhouseSource

    monkeypatch.setattr('career.sources.greenhouse._targets_from_settings', lambda *_: (SourceTarget('fixture', 'Empresa'),))

    async def fetch():
        response = {'jobs': [{'id': 1, 'title': 'Backend Junior', 'absolute_url': 'https://example.com/job',
                              'updated_at': '2026-11-02T12:00:00Z'}]}
        async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(200, json=response))) as client:
            return await GreenhouseSource().fetch(client)

    result = asyncio.run(fetch())
    assert result.report.status == SourceStatus.OK
    assert result.jobs[0].published_at is None


def test_greenhouse_reports_rate_limited_board_without_losing_other_jobs(monkeypatch):
    from career.config.sources import SourceTarget
    from career.sources.greenhouse import GreenhouseSource

    monkeypatch.setattr('career.sources.greenhouse._targets_from_settings', lambda *_: (
        SourceTarget('limited', 'Limitada'), SourceTarget('available', 'Disponível'),
    ))
    calls = []
    def handler(request):
        calls.append(request.url.path)
        if '/limited/' in request.url.path:
            return httpx.Response(429, headers={'Retry-After': '30'})
        return httpx.Response(200, json={'jobs': [{'id': 1, 'title': 'Backend Junior', 'absolute_url': 'https://example.com/job'}]})

    async def fetch():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await GreenhouseSource().fetch(client)

    result = asyncio.run(fetch())
    assert result.report.status == SourceStatus.OK
    assert result.report.message == '1/2 boards failed'
    assert result.report.count == 1 and result.jobs[0].company == 'Disponível'
    assert len(calls) == 2
