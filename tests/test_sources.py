import asyncio
import json

import httpx

from career.models import SourceStatus
from career.sources.lever import LeverSource


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
