from career.models import JobListing
from career.scorer import score_job
from .conftest import javascript_profile


def test_score_explanation_is_versioned_and_accounts_for_unknowns():
    job = JobListing(source='Teste', title='Backend', company='Empresa', url='https://example.com')
    result = score_job(job, javascript_profile())
    assert result.score_version == '2'
    assert sum(item.points for item in result.score_breakdown) == result.score
    assert all(item.status == 'unknown' for item in result.score_breakdown)
    assert JobListing.model_validate(result.model_dump()).score_breakdown == result.score_breakdown
