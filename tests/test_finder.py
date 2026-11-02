import asyncio

import httpx

from career.finder import find_jobs
from career.models import FetchResult, RawJob, SourceReport, SourceStatus
from career.sources.base import BaseSource

from .conftest import javascript_profile


class GoodSource(BaseSource):
    name = "Good"

    async def fetch(self, client: httpx.AsyncClient) -> FetchResult:
        return FetchResult(
            report=SourceReport(source=self.name, status=SourceStatus.OK, count=1),
            jobs=[RawJob(
                source=self.name, external_id="1", title="Junior Backend Developer", company="Acme",
                description="TypeScript Node.js PostgreSQL", workplace_type="remote", url="https://example.com/1",
            )],
        )


class BrokenSource(BaseSource):
    name = "Broken"

    async def fetch(self, client: httpx.AsyncClient) -> FetchResult:
        raise RuntimeError("source unavailable")


def test_source_failure_does_not_stop_the_pipeline(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    profile = javascript_profile()
    result = asyncio.run(find_jobs(profile, [GoodSource(), BrokenSource()], limit=50))

    assert len(result.jobs) == 1
    assert result.reports[0].status == SourceStatus.OK
    assert result.reports[1].status == SourceStatus.ERROR
    assert not (tmp_path / ".data" / "seen_jobs.json").exists()


def test_unknown_location_is_separate_from_eligible_jobs():
    result = asyncio.run(find_jobs(javascript_profile(allowed_regions={"brazil"}), [GoodSource()], limit=20))
    assert result.jobs == []
    assert len(result.needs_review) == 1
    assert result.needs_review[0].reason == "REGION_UNKNOWN"


def test_remote_only_location_is_returned_for_review():
    class RemoteOnlySource(GoodSource):
        async def fetch(self, client):
            result = await super().fetch(client)
            result.jobs[0].location = "Remote"
            return result

    result = asyncio.run(find_jobs(javascript_profile(allowed_regions={"brazil", "global"}), [RemoteOnlySource()], limit=20))
    assert result.jobs == []
    assert len(result.needs_review) == 1
    assert result.needs_review[0].reason == "REGION_UNKNOWN"


def test_slow_source_times_out_without_stopping_other_sources(monkeypatch):
    class SlowSource(BaseSource):
        name = "Slow"

        async def fetch(self, client: httpx.AsyncClient) -> FetchResult:
            await asyncio.sleep(1)
            raise AssertionError("timeout should cancel this source")

    monkeypatch.setattr("career.finder.SOURCE_TIMEOUT_SECONDS", 0.05)
    result = asyncio.run(find_jobs(javascript_profile(), [GoodSource(), SlowSource()], limit=20))
    assert len(result.jobs) == 1
    assert result.reports[0].status == SourceStatus.OK
    assert result.reports[1].status == SourceStatus.ERROR
