import asyncio
from datetime import UTC, datetime

from career.finder import find_jobs
from career.models import FetchResult, RawJob, SourceReport, SourceStatus
from career.sources.base import BaseSource
from .conftest import javascript_profile


def test_equally_scored_jobs_prioritize_recent_dates_and_keep_unknowns():
    class Source(BaseSource):
        name = 'Test'

        async def fetch(self, client):
            jobs = [
                RawJob(source=self.name, title='Backend Developer Junior', company=company,
                       url=f'https://example.com/{company}', description='TypeScript Node.js remote',
                       published_at=published)
                for company, published in [
                    ('Old', datetime(2024, 1, 1)),
                    ('Unknown', None),
                    ('New', datetime(2025, 1, 1, tzinfo=UTC)),
                ]
            ]
            return FetchResult(report=SourceReport(source=self.name, status=SourceStatus.OK, count=len(jobs)), jobs=jobs)

    result = asyncio.run(find_jobs(javascript_profile(), [Source()], 20))
    assert [job.company for job in result.jobs] == ['New', 'Old', 'Unknown']


def test_junior_opportunities_rank_before_mid_level():
    class Source(BaseSource):
        name = 'Test'

        async def fetch(self, client):
            jobs = [
                RawJob(source=self.name, title='Backend Developer Junior', company='Junior',
                       url='https://example.com/junior', description='Backend remote'),
                RawJob(source=self.name, title='Backend Developer Pleno', company='Pleno',
                       url='https://example.com/mid', description='Backend remote TypeScript Node.js PostgreSQL Docker Prisma'),
            ]
            return FetchResult(report=SourceReport(source=self.name, status=SourceStatus.OK, count=2), jobs=jobs)

    result = asyncio.run(find_jobs(javascript_profile(), [Source()], 20))
    assert [job.company for job in result.jobs] == ['Junior', 'Pleno']
    assert result.jobs[0].score < result.jobs[1].score
