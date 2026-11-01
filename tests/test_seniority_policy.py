from career.filters import hard_filter
from career.models import JobListing
from .conftest import javascript_profile


def test_mid_level_requires_javascript_or_typescript_stack():
    profile = javascript_profile(allowed_seniorities={'junior', 'mid'}, desired_technologies=set())
    base = dict(source='Teste', title='Backend Developer Pleno', company='Empresa', url='https://example.com', workplace_type='remote', seniority='mid')
    assert hard_filter(JobListing(**base, technologies=['Java']), profile).reason == 'MID_STACK_NOT_ALLOWED'
    assert hard_filter(JobListing(**base, technologies=[]), profile).reason == 'MID_STACK_UNKNOWN'
    assert hard_filter(JobListing(**base, technologies=['TypeScript']), profile).accepted


def test_unknown_mid_stack_is_returned_for_review():
    import asyncio
    from career.finder import find_jobs
    from career.models import FetchResult, RawJob, SourceReport, SourceStatus
    from career.sources.base import BaseSource

    class Source(BaseSource):
        name = 'Teste'

        async def fetch(self, client):
            job = RawJob(source=self.name, title='Backend Developer Pleno', company='Empresa',
                         url='https://example.com', description='Backend remoto', workplace_type='remote')
            return FetchResult(report=SourceReport(source=self.name, status=SourceStatus.OK, count=1), jobs=[job])

    result = asyncio.run(find_jobs(javascript_profile(), [Source()], 20))
    assert not result.jobs
    assert result.needs_review[0].reason == 'MID_STACK_UNKNOWN'
