from career.filters import hard_filter
from career.models import JobListing
import pytest

from .conftest import javascript_profile


def job(**overrides):
    values = {
        "source": "Lever", "title": "Backend Developer", "company": "Acme", "url": "https://example.com/1",
        "description": "Software developer for an API", "seniority": "junior", "workplace_type": "remote",
        "technologies": ["TypeScript", "Node.js"],
    }
    values.update(overrides)
    return JobListing(**values)


def test_rejects_senior_role():
    result = hard_filter(job(title="Senior Backend Developer", seniority="senior"), javascript_profile())
    assert result.model_dump() == {"accepted": False, "reason": "SENIORITY_NOT_ALLOWED"}


def test_rejects_non_development_role():
    result = hard_filter(job(title="Sales Analyst", description="Commercial team", technologies=[]), javascript_profile())
    assert result.reason == "NOT_DEVELOPMENT"


def test_rejects_business_development_even_when_description_mentions_software():
    result = hard_filter(
        job(title="Business Development Representative", description="Sell software to engineering teams"),
        javascript_profile(),
    )
    assert result.reason == "NOT_DEVELOPMENT"


def test_rejects_incompatible_known_stack():
    result = hard_filter(job(technologies=["Java", "Spring"]), javascript_profile())
    assert result.reason == "INCOMPATIBLE_STACK"


def test_rejects_onsite_when_not_selected():
    result = hard_filter(job(workplace_type="onsite"), javascript_profile())
    assert result.reason == "WORKPLACE_NOT_ALLOWED"


def test_filters_by_selected_region():
    profile = javascript_profile(allowed_regions={"brazil"})
    assert hard_filter(job(location="São Paulo, Brazil"), profile).accepted
    assert hard_filter(job(location="Toronto, Canada"), profile).reason == "REGION_NOT_ALLOWED"


def test_global_does_not_admit_other_specific_regions():
    profile = javascript_profile(allowed_regions={"brazil", "global"})
    assert hard_filter(job(location="Toronto, Canada"), profile).reason == "REGION_NOT_ALLOWED"
    assert hard_filter(job(location="Worldwide"), profile).accepted
    assert hard_filter(job(location="Worldwide except Brazil"), profile).reason == "REGION_NOT_ALLOWED"
    assert hard_filter(job(location="Anywhere in the United States"), profile).reason == "REGION_NOT_ALLOWED"


@pytest.mark.parametrize("description", [
    "Backend developer. Applicants must be based in the United States.",
    "Backend developer. US candidates only.",
    "Desenvolvedor backend. Vaga exclusiva para residentes dos Estados Unidos.",
])
def test_global_with_geographic_restrictions_needs_review(description):
    profile = javascript_profile(allowed_regions={"brazil", "global"})
    assert hard_filter(job(location="Worldwide", description=description), profile).reason == "REGION_UNKNOWN"


def test_unrestricted_global_job_remains_eligible():
    profile = javascript_profile(allowed_regions={"brazil", "global"})
    assert hard_filter(job(location="Worldwide", description="Backend developer. We use TypeScript."), profile).accepted


@pytest.mark.parametrize("workplace", ["hybrid", "onsite"])
def test_remote_only_rejects_other_modes(workplace):
    profile = javascript_profile(allowed_workplaces={"remote"})
    assert hard_filter(job(workplace_type=workplace), profile).reason == "WORKPLACE_NOT_ALLOWED"


def test_unknown_values_and_unmatched_area_are_not_eligible():
    profile = javascript_profile(allowed_regions={"brazil", "global"})
    assert hard_filter(job(workplace_type=None), profile).reason == "WORKPLACE_UNKNOWN"
    assert hard_filter(job(location=None), profile).reason == "REGION_UNKNOWN"
    assert hard_filter(job(title="Software Engineer", description="Software developer", location="Brazil"), profile).reason == "ROLE_AREA_UNKNOWN"
    backend_profile = javascript_profile(role_areas={"backend"})
    assert hard_filter(job(title="Frontend Developer", description="Frontend software developer"), backend_profile).reason == "ROLE_AREA_NOT_ALLOWED"


@pytest.mark.parametrize('location', ['Remote outside Brazil', 'Remoto fora do Brasil'])
def test_locations_excluding_brazil_do_not_match_brazil(location):
    profile = javascript_profile(allowed_regions={'brazil', 'global'})
    assert hard_filter(job(location=location), profile).reason == 'REGION_NOT_ALLOWED'


@pytest.mark.parametrize('description', ['Backend developer. Applicants outside Brazil.', 'Desenvolvedor backend. Candidatos fora do Brasil.'])
def test_global_jobs_with_brazil_exclusion_in_description_need_review(description):
    profile = javascript_profile(allowed_regions={'brazil', 'global'})
    assert hard_filter(job(location='Worldwide', description=description), profile).reason == 'REGION_UNKNOWN'


@pytest.mark.parametrize('location', ['Remote', 'Remoto', 'Home office', 'Work from home', '(Remote)', '   '])
def test_work_mode_alone_does_not_imply_a_known_region(location):
    profile = javascript_profile(allowed_regions={'brazil', 'global'})
    assert hard_filter(job(location=location), profile).reason == 'REGION_UNKNOWN'


@pytest.mark.parametrize('description', [
    'Requer experiência sênior em desenvolvimento de APIs.',
    'Exige perfil sênior para desenvolvimento backend.',
    'Requires senior-level experience in backend development.',
    'Senior experience required for backend development.',
])
def test_explicit_senior_requirement_is_rejected(description):
    assert hard_filter(job(title='Backend Developer Junior', seniority='junior', description=description), javascript_profile()).reason == 'SENIORITY_NOT_ALLOWED'


@pytest.mark.parametrize('description', [
    'A pessoa júnior trabalhará com desenvolvedores sênior.',
    'Requer colaboração com a equipe sênior de backend.',
    'Junior developer mentored by senior engineers.',
    'Não requer experiência sênior em desenvolvimento.',
    'Senior experience is not required for this position.',
])
def test_senior_coworker_mention_is_not_a_requirement(description):
    assert hard_filter(job(title='Backend Developer Junior', seniority='junior', description=description), javascript_profile()).accepted


@pytest.mark.parametrize('description', [
    'Exige perfil de arquiteto para desenvolvimento backend.',
    'Requires staff-level experience in backend development.',
    'Requires lead experience in backend development.',
])
def test_explicit_staff_lead_or_architect_requirement_is_rejected(description):
    result = hard_filter(job(title='Backend Developer Junior', seniority='junior', description=description), javascript_profile())
    assert result.reason == 'SENIORITY_NOT_ALLOWED'


@pytest.mark.parametrize('description', [
    'Colaboração com a liderança e o arquiteto da equipe backend.',
    'Junior developer works with staff and lead engineers.',
])
def test_staff_lead_or_architect_coworker_mention_remains_eligible(description):
    assert hard_filter(job(title='Backend Developer Junior', seniority='junior', description=description), javascript_profile()).accepted


@pytest.mark.parametrize('location', ['Lisboa', 'Toronto', 'Não informado', 'Niterói, RJ', 'Tuktoyaktuk'])
def test_unrecognized_location_is_reviewed_instead_of_rejected(location):
    profile = javascript_profile(allowed_regions={'brazil', 'global'})
    assert hard_filter(job(location=location), profile).reason == 'REGION_UNKNOWN'


@pytest.mark.parametrize('location', ['Worldwide except Canada', 'Global excluding United States'])
def test_restriction_on_another_region_is_reviewed(location):
    profile = javascript_profile(allowed_regions={'brazil', 'global'})
    assert hard_filter(job(location=location), profile).reason == 'REGION_UNKNOWN'


@pytest.mark.parametrize('location', [
    'Brazil except Rio de Janeiro',
    'Brazil excluding Canada',
    'Worldwide except Brazil and Canada',
])
def test_compound_geographic_restrictions_need_review(location):
    profile = javascript_profile(allowed_regions={'brazil', 'global'})
    assert hard_filter(job(location=location), profile).reason == 'REGION_UNKNOWN'


def test_exclusion_of_one_of_multiple_preferred_regions_needs_review():
    profile = javascript_profile(allowed_regions={'brazil', 'canada', 'global'})
    assert hard_filter(job(location='Worldwide except Brazil'), profile).reason == 'REGION_UNKNOWN'
