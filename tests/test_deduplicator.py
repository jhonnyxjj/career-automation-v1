from career.deduplicator import deduplicate
from career.models import JobListing


def job(**overrides):
    values = {"source": "Lever", "external_id": "1", "title": "Backend Developer", "company": "Acme", "location": "Brazil", "url": "https://example.com/jobs/1"}
    values.update(overrides)
    return JobListing(**values)


def test_deduplicates_by_source_external_id_first():
    assert len(deduplicate([job(), job(url="https://example.com/jobs/updated")])) == 1


def test_deduplicates_by_canonical_url_across_sources():
    duplicate = job(source="Greenhouse", external_id="99", url="https://example.com/jobs/1/?utm_source=x")
    assert len(deduplicate([job(), duplicate])) == 1


def test_deduplicates_by_company_title_and_location_fingerprint():
    duplicate = job(source="Greenhouse", external_id="99", url="https://another.example/jobs/99")
    assert len(deduplicate([job(), duplicate])) == 1
