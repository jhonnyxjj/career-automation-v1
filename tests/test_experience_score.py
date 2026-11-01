import pytest
from career.models import JobListing
from career.scorer import score_job
from .conftest import javascript_profile


def job(description):
    return JobListing(source='Teste', title='Backend Junior', company='Empresa', url='https://example.com',
                      seniority='junior', workplace_type='remote', technologies=['TypeScript'], description=description)


@pytest.mark.parametrize('description', [
    'Requer 2 anos de experiência em desenvolvimento.',
    'Requer 2 anos de experiência no desenvolvimento de APIs.',
    'Experiência de 2 a 3 anos em APIs.',
    'Requires 3 years of experience with APIs.',
])
def test_explicit_two_to_three_years_has_explained_penalty(description):
    baseline = score_job(job('Desenvolvimento de APIs.'), javascript_profile())
    result = score_job(job(description), javascript_profile())
    assert result.score == baseline.score - 5
    assert result.score_version == '2'
    assert any(item.status == 'penalty' and item.points == -5 for item in result.score_breakdown)
    assert sum(item.points for item in result.score_breakdown) == result.score


@pytest.mark.parametrize('description', [
    'Não exige 2 anos de experiência.',
    '2 anos de experiência não são necessários.',
    'No 3 years of experience required.',
    'Experiência de 1 a 3 anos.',
    'Experiência de 4 anos.',
    'Conhecimento de APIs.',
])
def test_no_penalty_when_requirement_is_negated_or_uncertain(description):
    baseline = score_job(job('Desenvolvimento de APIs.'), javascript_profile())
    assert score_job(job(description), javascript_profile()).score == baseline.score


def test_penalty_never_makes_score_negative():
    empty = JobListing(source='Teste', title='Backend', company='Empresa', url='https://example.com', description='2 anos de experiência')
    result = score_job(empty, javascript_profile())
    assert result.score == 0
    assert sum(item.points for item in result.score_breakdown) == result.score


def test_large_number_in_description_does_not_break_scoring():
    result = score_job(job('Experiência de ' + '9' * 5000 + ' anos.'), javascript_profile())
    assert 0 <= result.score <= 100
