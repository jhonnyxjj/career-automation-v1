import pytest
from career.filters import hard_filter
from career.models import JobListing
from .conftest import javascript_profile


@pytest.mark.parametrize(('location', 'reason'), [
    ('Rio de Janeiro, RJ', None),
    ('Petrópolis - RJ', None),
    ('São Paulo, Brazil', 'LOCALITY_NOT_ALLOWED'),
    ('Brazil', 'LOCALITY_UNKNOWN'),
    ('Brasil - RJ', 'LOCALITY_UNKNOWN'),
])
def test_brazilian_hybrid_jobs_require_allowed_city(location, reason):
    profile = javascript_profile(allowed_regions={'brazil'}, allowed_workplaces={'hybrid'})
    job = JobListing(source='Teste', title='Backend Developer Junior', company='Empresa',
                     url='https://example.com', workplace_type='hybrid', seniority='junior',
                     location=location, technologies=['TypeScript'])
    result = hard_filter(job, profile)
    assert result.reason == reason
    assert result.accepted == (reason is None)
