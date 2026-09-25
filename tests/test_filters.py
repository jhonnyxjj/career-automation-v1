from career.filters import hard_filter
from career.models import JobListing

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
